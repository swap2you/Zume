import { useEffect, useState } from 'react'
import Editor from '@monaco-editor/react'
import { post, request } from '../api'
import { AudienceTag, PageHeader } from '../components/Layout'

function Result({ value }: { value: unknown }) { return value ? <pre className="result">{JSON.stringify(value, null, 2)}</pre> : null }
function useSubmit<T>(path: string) {
  const [result, setResult] = useState<T | null>(null); const [error, setError] = useState('')
  return { result, error, submit: async (body: unknown) => { setError(''); try { setResult(await post<T>(path, body)) } catch (e) { setError((e as Error).message) } } }
}

export function Intake() {
  const [resume, setResume] = useState(''); const [name, setName] = useState(''); const [schedule, setSchedule] = useState(''); const [fileMessage, setFileMessage] = useState('')
  const { result, error, submit } = useSubmit('/api/candidates/intake')
  return <section><PageHeader eyebrow="Pre-interview" title="Candidate intake"><p className="lede">Add resume text and optional schedule details. Intake stops before interview feedback.</p></PageHeader><AudienceTag />
    <form className="workspace-form" onSubmit={(e) => { e.preventDefault(); void submit({ resume_text: resume, name: name || undefined, schedule_details: schedule || undefined }) }}>
      <label htmlFor="candidate-name">Candidate name <small>optional</small></label><input id="candidate-name" value={name} onChange={e => setName(e.target.value)} />
      <label htmlFor="resume-file">Resume text file <small>optional: .txt or .md</small></label><input id="resume-file" type="file" accept=".txt,.md,text/plain,text/markdown" onChange={async e => { const file = e.target.files?.[0]; if (!file) return; setResume(await file.text()); setFileMessage(`${file.name} loaded into resume text.`) }} />{fileMessage && <p className="muted">{fileMessage}</p>}
      <label htmlFor="resume">Resume text</label><textarea id="resume" value={resume} onChange={e => setResume(e.target.value)} required placeholder="Paste resume content, or load a text file above." />
      <label htmlFor="schedule">Schedule details <small>optional</small></label><textarea id="schedule" value={schedule} onChange={e => setSchedule(e.target.value)} />
      <button>Build pre-interview package</button>{error && <p className="error" role="alert">{error}</p>}<Result value={result} />
    </form></section>
}

export function Finalize() {
  const [candidate, setCandidate] = useState(''); const [notes, setNotes] = useState(''); const { result, error, submit } = useSubmit('/api/candidates/finalize')
  return <section><PageHeader eyebrow="After the interview" title="Finalize candidate"><p className="lede">Submit only real interviewer notes. Incomplete evidence is routed to manual review.</p></PageHeader><AudienceTag />
    <form className="workspace-form" onSubmit={e => { e.preventDefault(); void submit({ candidate, notes }) }}><label htmlFor="candidate">Candidate ID or name</label><input id="candidate" value={candidate} onChange={e => setCandidate(e.target.value)} required /><label htmlFor="notes">Interviewer notes</label><textarea id="notes" value={notes} onChange={e => setNotes(e.target.value)} required /><button>Finalize evaluation</button>{error && <p className="error" role="alert">{error}</p>}<Result value={result} /></form>
  </section>
}

type Question = { id: string; question?: string; prompt?: string; domain?: string; level?: string; priority?: string }
export function Library() {
  const [q, setQ] = useState(''); const [domain, setDomain] = useState(''); const [level, setLevel] = useState(''); const [priority, setPriority] = useState(''); const [items, setItems] = useState<Question[]>([]); const [page, setPage] = useState(0)
  useEffect(() => { const timer = setTimeout(() => {
    const filters = `domain=${encodeURIComponent(domain)}&level=${encodeURIComponent(level)}&priority=${encodeURIComponent(priority)}&limit=10`
    const endpoint = q ? `/api/knowledge/search?q=${encodeURIComponent(q)}&${filters}` : `/api/knowledge/questions?${filters}&offset=${page * 10}`
    request<{ items?: Question[]; questions?: Question[] }>(endpoint).then(r => setItems(r.items ?? r.questions ?? [])).catch(() => setItems([]))
  }, 200); return () => clearTimeout(timer) }, [q, domain, level, priority, page])
  return <section><PageHeader eyebrow="Structured library" title="Question library" /><div className="filter-bar"><label>Search<input value={q} onChange={e => { setQ(e.target.value); setPage(0) }} /></label><label>Domain<input value={domain} onChange={e => setDomain(e.target.value)} placeholder="e.g. selenium" /></label><label>Level<select value={level} onChange={e => setLevel(e.target.value)}><option value="">All levels</option><option>basic</option><option>intermediate</option><option>advanced</option></select></label><label>Priority<select value={priority} onChange={e => setPriority(e.target.value)}><option value="">All priorities</option><option>high</option><option>medium</option><option>low</option></select></label></div>
    <p className="muted">{items.length} results · page {page + 1}</p><div className="question-list">{items.map(item => <article key={item.id}><span>{item.domain} · {item.level} · {item.priority}</span><h3>{item.question ?? item.prompt ?? item.id}</h3><AudienceTag /></article>)}</div><div className="pagination"><button disabled={page === 0 || Boolean(q)} onClick={() => setPage(page - 1)}>Previous</button><button disabled={items.length < 10 || Boolean(q)} onClick={() => setPage(page + 1)}>Next</button></div></section>
}

export function Practice() {
  const [revealed, setRevealed] = useState(false); const [rating, setRating] = useState(localStorage.getItem('zume-practice-rating') ?? '')
  const save = (value: string) => { setRating(value); localStorage.setItem('zume-practice-rating', value) }
  return <section><PageHeader eyebrow="Private study" title="Practice session"><p className="lede">A local study aid. Your self-rating stays in this browser.</p></PageHeader><article className="practice-card"><p className="eyebrow">Sample prompt</p><h2>How would you isolate a flaky UI test?</h2><button onClick={() => setRevealed(!revealed)}>{revealed ? 'Hide answer' : 'Reveal answer'}</button>{revealed && <div className="answer"><b>Suggested approach</b><p>Establish reproducibility, isolate state and timing, inspect observability, then make the test deterministic rather than merely retrying it.</p></div>}<fieldset><legend>How confident are you?</legend>{['Need review', 'Getting there', 'Comfortable'].map(value => <label className="rating" key={value}><input type="radio" checked={rating === value} onChange={() => save(value)} /> {value}</label>)}</fieldset></article></section>
}

export function Builder() {
  const [role, setRole] = useState(''); const [resume, setResume] = useState(''); const { result, error, submit } = useSubmit('/api/interview/preview')
  return <section><PageHeader eyebrow="180-minute standard" title="Interview builder"><p className="lede">Preview the interview plan before creating candidate materials.</p></PageHeader><AudienceTag /><form className="workspace-form" onSubmit={e => { e.preventDefault(); void submit({ role_track: role || undefined, resume_text: resume || undefined }) }}><label>Role track<input value={role} onChange={e => setRole(e.target.value)} /></label><label>Resume context <small>optional</small><textarea value={resume} onChange={e => setResume(e.target.value)} /></label><button>Preview plan</button>{error && <p className="error">{error}</p>}<Result value={result} /></form></section>
}

export function Lab() {
  const [runner, setRunner] = useState('python'); const [code, setCode] = useState('# Write your solution here\n'); const { result, error, submit } = useSubmit(`/api/labs/${runner}/run`)
  return <section><PageHeader eyebrow="Practical evaluation" title="Exercise lab"><p className="lede">Run code in the configured local runner. Never put candidate answers in shared materials.</p></PageHeader><AudienceTag /><div className="lab-controls"><label>Runner<select value={runner} onChange={e => setRunner(e.target.value)}><option value="python">Python</option><option value="javascript">JavaScript</option></select></label><button onClick={() => void submit({ code })}>Run code</button></div><Editor height="480px" defaultLanguage="python" language={runner === 'python' ? 'python' : 'javascript'} value={code} onChange={value => setCode(value ?? '')} theme="vs" options={{ minimap: { enabled: false }, fontSize: 14 }} />{error && <p className="error">{error}</p>}<Result value={result} /></section>
}

export function Settings() {
  const [doctor, setDoctor] = useState<unknown>(null); const [error, setError] = useState('')
  useEffect(() => { request<unknown>('/api/doctor').then(setDoctor).catch(e => setError((e as Error).message)) }, [])
  return <section><PageHeader eyebrow="Local checks" title="Settings & doctor"><p className="lede">Diagnostic information only. Secrets and credentials are intentionally never displayed here.</p></PageHeader><h2>Environment report</h2>{error ? <p className="error">{error}</p> : <Result value={doctor} />}</section>
}
