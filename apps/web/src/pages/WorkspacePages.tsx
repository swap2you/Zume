import { useEffect, useState } from 'react'
import Editor from '@monaco-editor/react'
import { post, request } from '../api'
import { AudienceTag, PageHeader } from '../components/Layout'
import { SpeechControls } from '../components/SpeechControls'

export { Library } from './Library'

type Question = { id: string; title?: string; question?: string; domain?: string; subdomain?: string; level?: string; priority?: string; concise_answer?: string; recommended_answer?: string; deep_dive?: string; follow_ups?: { question: string }[]; strong_signals?: string[]; weak_signals?: string[]; references?: { source_id: string; locator?: string; source_url?: string; source_name?: string }[]; last_verified?: string; role_tracks?: string[] }
type IntakeResult = { decision: string; score_percent: number; deliverables: string[]; wait_message?: string; validation_errors?: string[] }

function useSubmit<T>(path: string) {
  const [result, setResult] = useState<T | null>(null); const [error, setError] = useState('')
  return { result, error, submit: async (body: unknown) => { setError(''); try { setResult(await post<T>(path, body)) } catch (e) { setError((e as Error).message) } } }
}
function IntakeSummary({ result }: { result: IntakeResult }) {
  return <div className="summary-cards"><article><b>Screening decision</b><strong>{result.decision}</strong><p>Resume evidence coverage: {result.score_percent}%</p></article><article><b>Package deliverables</b><ul>{result.deliverables.map(item => <li key={item}>{item}</li>)}</ul></article>{result.wait_message && <article><b>Next required action</b><p>{result.wait_message}</p></article>}{Boolean(result.validation_errors?.length) && <article><b>Validation warnings</b><ul>{result.validation_errors?.map(item => <li key={item}>{item}</li>)}</ul></article>}</div>
}

export function Intake() {
  const [resume, setResume] = useState(''); const [name, setName] = useState(''); const [schedule, setSchedule] = useState(''); const [file, setFile] = useState<File | null>(null)
  const { result, error, submit } = useSubmit<IntakeResult>('/api/candidates/intake'); const [uploadResult, setUploadResult] = useState<IntakeResult | null>(null); const [uploadError, setUploadError] = useState('')
  async function upload() { if (!file) return; setUploadError(''); const form = new FormData(); form.append('resume', file); if (name) form.append('name', name); if (schedule) form.append('schedule_details', schedule); try { setUploadResult(await request<IntakeResult>('/api/candidates/intake-upload', { method: 'POST', body: form })) } catch (e) { setUploadError((e as Error).message) } }
  const response = uploadResult ?? result
  return <section><PageHeader eyebrow="Pre-interview" title="Candidate intake"><p className="lede">Add resume text or a local file. Intake stops before interview feedback.</p></PageHeader><AudienceTag />
    <form className="workspace-form" onSubmit={e => { e.preventDefault(); if (file) void upload(); else void submit({ resume_text: resume, name: name || undefined, schedule_details: schedule || undefined }) }}>
      <label>Candidate name <small>optional</small><input value={name} onChange={e => setName(e.target.value)} /></label>
      <label>Resume file <small>optional: PDF, DOCX, or TXT</small><input aria-label="Resume file" type="file" accept=".pdf,.docx,.txt" onChange={e => setFile(e.target.files?.[0] ?? null)} /></label>
      <label>Resume text <small>use when no file is selected</small><textarea value={resume} onChange={e => setResume(e.target.value)} required={!file} /></label>
      <label>Schedule details <small>optional</small><textarea value={schedule} onChange={e => setSchedule(e.target.value)} /></label>
      <button>Build pre-interview package</button>{(error || uploadError) && <p className="error" role="alert">{error || uploadError}</p>}{response && <IntakeSummary result={response} />}
    </form></section>
}

export function Finalize() {
  const [candidate, setCandidate] = useState(''); const [notes, setNotes] = useState(''); const [candidates, setCandidates] = useState<{ folder: string; status: string; display_name: string }[]>([])
  const { result, error, submit } = useSubmit<{ missing_areas: string[]; decision_permitted: boolean; deliverables: string[] }>('/api/candidates/finalize')
  useEffect(() => { request<{ items: { folder: string; status: string; display_name: string }[] }>('/api/candidates').then(data => setCandidates(data.items)).catch(() => setCandidates([])) }, [])
  return <section><PageHeader eyebrow="After the interview" title="Finalize candidate"><p className="lede">Submit only real interviewer notes. Incomplete evidence is routed to manual review.</p></PageHeader><AudienceTag />
    <form className="workspace-form" onSubmit={e => { e.preventDefault(); void submit({ candidate, notes }) }}><label>Candidate<select value={candidate} onChange={e => setCandidate(e.target.value)} required><option value="">Select a candidate</option>{candidates.map(item => <option value={item.folder} key={item.folder}>{item.display_name} — {item.status}</option>)}</select></label><label>Interviewer notes<textarea value={notes} onChange={e => setNotes(e.target.value)} required /></label><button>Finalize evaluation</button>{error && <p className="error" role="alert">{error}</p>}{result && <div className="summary-cards"><article><b>Decision permitted</b><strong>{result.decision_permitted ? 'Yes' : 'Manual review required'}</strong></article><article><b>Missing areas</b><p>{result.missing_areas.join(', ') || 'None reported'}</p></article><article><b>Deliverables</b><ul>{result.deliverables.map(item => <li key={item}>{item}</li>)}</ul></article></div>}</form></section>
}

function PracticeCard({ item, index, total, onPrev, onNext, onRandom }: { item: Question; index: number; total: number; onPrev: () => void; onNext: () => void; onRandom: () => void }) {
  const [revealed, setRevealed] = useState(false)
  const [rating, setRating] = useState(() => localStorage.getItem(`zume-practice-rating-${item.id}`) ?? '')
  const save = (value: string) => { setRating(value); localStorage.setItem(`zume-practice-rating-${item.id}`, value) }
  return <article className="practice-card"><p className="eyebrow">{item.domain} · {item.level} · {index + 1} of {total}</p><h2>{item.question}</h2><button onClick={() => setRevealed(!revealed)}>{revealed ? 'Hide answer' : 'Reveal answer'}</button>{revealed && <div className="answer"><b>Suggested approach</b><p>{item.recommended_answer ?? item.concise_answer}</p></div>}<SpeechControls question={item.question ?? ''} answer={item.recommended_answer ?? item.concise_answer ?? ''} /><fieldset><legend>How confident are you?</legend>{['Need review', 'Getting there', 'Comfortable'].map(value => <label className="rating" key={value}><input type="radio" checked={rating === value} onChange={() => save(value)} /> {value}</label>)}</fieldset><div className="pagination"><button disabled={index === 0} onClick={onPrev}>Previous</button><button onClick={onRandom}>Random</button><button disabled={index === total - 1} onClick={onNext}>Next</button></div></article>
}

export function Practice() {
  const [items, setItems] = useState<Question[]>([]); const [index, setIndex] = useState(0); const [error, setError] = useState(''); const item = items[index]
  useEffect(() => { request<{ items?: Question[]; results?: Question[] }>('/api/knowledge/practice?limit=20').then(data => setItems(data.items ?? data.results ?? [])).catch(e => setError((e as Error).message)) }, [])
  const move = (next: number) => setIndex(Math.max(0, Math.min(items.length - 1, next)))
  return <section><PageHeader eyebrow="Private study" title="Practice session"><p className="lede">A local study aid. Your self-rating stays in this browser.</p></PageHeader>{error && <p className="error">{error}</p>}{!error && !item && <p className="empty-state">No published practice questions are available.</p>}{item && <PracticeCard key={item.id} item={item} index={index} total={items.length} onPrev={() => move(index - 1)} onNext={() => move(index + 1)} onRandom={() => move(Math.floor(Math.random() * items.length))} />}</section>
}

const ROLE_OPTIONS = [
  'Senior SDET', 'Lead SDET', 'Mobile Automation Engineer', 'Performance Engineer',
  'AI QA Engineer', 'Test Automation Architect', 'QA Manager',
]

type BuilderPlan = {
  knockout_minutes?: number
  knockout_question_ids?: string[]
  agenda_fit_minutes?: number
  warning?: string
  role_policy_label?: string
  role_coverage?: { sufficient?: boolean; missing_core_domains?: string[]; reviewed_role_questions?: number }
  why?: { id: string; reason: string }[]
  questions?: { id?: string; question?: string; level?: string; priority?: string; domain?: string }[]
  candidate_exercises?: { id: string; title: string; domain: string }[]
}

export function Builder() {
  const [role, setRole] = useState('Senior SDET')
  const [resume, setResume] = useState('')
  const { result, error, submit } = useSubmit<{ plan?: BuilderPlan }>('/api/interview/preview')
  const plan = result?.plan
  const reasons = Object.fromEntries((plan?.why ?? []).map((item) => [item.id, item.reason]))
  return (
    <section>
      <PageHeader eyebrow="180-minute standard" title="Interview builder">
        <p className="lede">Preview the interview plan before creating candidate materials.</p>
      </PageHeader>
      <AudienceTag />
      <form className="workspace-form" onSubmit={(e) => { e.preventDefault(); void submit({ role_track: role, resume_text: resume || undefined }) }}>
        <label>Role track
          <select aria-label="Role track" value={role} onChange={(e) => setRole(e.target.value)}>
            {ROLE_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
          </select>
        </label>
        <label>Resume context <small>optional</small><textarea value={resume} onChange={(e) => setResume(e.target.value)} /></label>
        <button>Preview plan</button>
        {error && <p className="error" role="alert">{error}</p>}
        {plan?.warning && <p className="banner warn" role="status">{plan.warning}</p>}
        {plan && (
          <div className="summary-cards">
            <article><b>Role policy</b><strong>{plan.role_policy_label ?? role}</strong><p>{plan.agenda_fit_minutes ?? 180} minute interview</p></article>
            <article><b>Knockout round</b><strong>{plan.knockout_minutes ?? 20} minutes</strong><p>{plan.knockout_question_ids?.length ?? 0} P0 questions</p></article>
            <article><b>Role coverage</b><strong>{plan.role_coverage?.sufficient ? 'Sufficient' : 'Limited'}</strong><p>{plan.role_coverage?.reviewed_role_questions ?? 0} reviewed role questions{plan.role_coverage?.missing_core_domains?.length ? `; missing ${plan.role_coverage.missing_core_domains.join(', ')}` : ''}</p></article>
            <article><b>Selected questions</b><ul>{plan.questions?.map((item, i) => <li key={item.id ?? i}>{item.question} — {reasons[item.id ?? ''] ?? 'selected'} ({item.domain}, {item.level}, {item.priority})</li>)}</ul></article>
            <article><b>Candidate-safe exercises</b><ul>{(plan.candidate_exercises ?? []).map((item) => <li key={item.id}>{item.title} ({item.domain})</li>)}</ul></article>
          </div>
        )}
        <details>{result && <summary>Raw preview JSON</summary>}<pre className="result">{result && JSON.stringify(result, null, 2)}</pre></details>
      </form>
    </section>
  )
}

const LAB_STARTERS: Record<string, string> = { sql: "SELECT name, dept FROM employees WHERE dept = 'QA'", api: '{"method":"GET","path":"/health"}', java: 'public class Main { public static void main(String[] args) { System.out.println("Hello"); } }', selenium: '' }

export function Lab() {
  const [labs, setLabs] = useState<{ runner: string; available: boolean; detail: string }[]>([]); const [runner, setRunner] = useState('sql'); const [code, setCode] = useState(LAB_STARTERS.sql); const [exercise, setExercise] = useState('ad-hoc'); const [exercises, setExercises] = useState<{ id: string; title: string }[]>([])
  const { result, error, submit } = useSubmit<{ stdout: string; stderr: string; exit_code: number; truncated: boolean; test_results: { name: string; passed: boolean; message: string }[] }>(`/api/labs/${runner}/run`)
  useEffect(() => { request<{ labs: { runner: string; available: boolean; detail: string }[] }>('/api/labs').then(data => setLabs(data.labs.filter(item => ['sql', 'api', 'java', 'selenium'].includes(item.runner)))).catch(() => setLabs([])) }, [])
  useEffect(() => { request<{ items: { id: string; title: string }[] }>(`/api/labs/exercises?runner=${runner}`).then(data => setExercises(data.items)).catch(() => setExercises([])) }, [runner])
  const selectRunner = (value: string) => { setRunner(value); setCode(LAB_STARTERS[value] ?? ''); setExercise('ad-hoc') }
  const current = labs.find(item => item.runner === runner)
  return <section><PageHeader eyebrow="Practical evaluation" title="Exercise lab"><p className="lede">Run code in the configured local runner.</p></PageHeader><AudienceTag /><div className="lab-controls"><label>Runner<select value={runner} onChange={e => selectRunner(e.target.value)}>{(labs.length ? labs : ['sql', 'api', 'java', 'selenium'].map(item => ({ runner: item, available: false, detail: '' }))).map(item => <option key={item.runner} value={item.runner}>{item.runner} — {item.available ? 'available' : 'unavailable'}</option>)}</select></label><label>Exercise<select value={exercise} onChange={e => setExercise(e.target.value)}><option value="ad-hoc">Starter exercise</option>{exercises.map(item => <option value={item.id} key={item.id}>{item.title}</option>)}</select></label><button onClick={() => void submit({ code, exercise_id: exercise })}>Run code</button></div><p className="muted">{current?.detail}</p><Editor height="480px" language={runner === 'api' ? 'json' : runner} value={code} onChange={value => setCode(value ?? '')} options={{ minimap: { enabled: false }, fontSize: 14 }} />{error && <p className="error">{error}</p>}{result && <div className="summary-cards"><article><b>Exit code</b><strong>{result.exit_code}</strong><p>Truncated: {String(result.truncated)}</p></article><article><b>Standard output</b><pre>{result.stdout || '—'}</pre></article><article><b>Standard error</b><pre>{result.stderr || '—'}</pre></article><article><b>Tests</b><ul>{result.test_results.map(item => <li key={item.name}>{item.passed ? 'Passed' : 'Failed'}: {item.name} {item.message}</li>)}</ul></article></div>}</section>
}

export function Settings() {
  const [doctor, setDoctor] = useState<Record<string, string> | null>(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  useEffect(() => { request<Record<string, string>>('/api/doctor').then(setDoctor).catch(e => setError((e as Error).message)) }, [])
  const clear = async (path: string, method: 'DELETE' | 'POST') => {
    try {
      if (method === 'DELETE') await request(path, { method: 'DELETE' })
      else await post(path, {})
      setNotice('Local data cleared.')
    } catch (e) { setNotice((e as Error).message) }
  }
  return <section><PageHeader eyebrow="Local checks" title="Settings & doctor"><p className="lede">Diagnostic information only. Secrets and credentials are intentionally never displayed here.</p></PageHeader>{error ? <p className="error">{error}</p> : <div className="summary-cards">{['openai_provider', 'web_search', 'tts', 'docker_labs', 'secrets_source'].map(key => <article key={key}><b>{key.replaceAll('_', ' ')}</b><p>{doctor?.[key] ?? 'Checking…'}</p></article>)}</div>}<div className="pagination"><button onClick={() => void clear('/api/ask/history', 'DELETE')}>Clear Ask history</button><button onClick={() => void clear('/api/audio/cache/clear', 'POST')}>Clear audio cache</button></div>{notice && <p className="muted">{notice}</p>}</section>
}
