import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { request } from '../api'
import { AudienceTag, PageHeader } from '../components/Layout'
import { SpeechControls } from '../components/SpeechControls'

type FacetOption = { value: string; label: string; count: number; subdomains?: FacetOption[] }
type Facets = {
  mode: string
  counts: { questions: number; exercises: number; domains: number; gaps: number }
  domains: FacetOption[]
  levels: FacetOption[]
  priorities: FacetOption[]
  frequencies: FacetOption[]
  roles: FacetOption[]
  question_types: FacetOption[]
  source_families: FacetOption[]
  freshness_states: FacetOption[]
  tags: FacetOption[]
  gap_summary?: { domain: string; level: string; kind: string; have: number; target: number; missing: number }[] | null
}
type Reference = {
  source_id: string; source_name?: string; source_url?: string; locator?: string
  last_verified?: string; freshness_state?: string
}
type FollowUp = { question: string; recommended_answer?: string }
type Question = {
  id: string; title?: string; question?: string; domain?: string; subdomain?: string
  level?: string; priority?: string; frequency?: string; role_tracks?: string[]
  estimated_minutes?: number; last_verified?: string; freshness_state?: string
  concise_answer?: string; recommended_answer?: string; deep_dive?: string
  key_points?: string[]; examples?: string[]; code_examples?: string[]
  strong_signals?: string[]; weak_signals?: string[]; red_flags?: string[]
  common_mistakes?: string[]; follow_ups?: FollowUp[]; references?: Reference[]
  question_type?: string; tags?: string[]
}

type Mode = 'reviewed' | 'draft' | 'gaps'
type Filters = {
  q: string; domain: string; subdomain: string; level: string; priority: string
  role: string; frequency: string; question_type: string; source_family: string
  freshness_state: string; tag: string; has_exercise: string; has_followups: string
  has_code_example: string; sort: string
}

const EMPTY: Filters = {
  q: '', domain: '', subdomain: '', level: '', priority: '', role: '',
  frequency: '', question_type: '', source_family: '', freshness_state: '',
  tag: '', has_exercise: '', has_followups: '', has_code_example: '', sort: 'recommended',
}

const PAGE_SIZE = 10
const HISTORY_KEY = 'zume-library-search-history'

function omitEmpty(params: Record<string, string>): URLSearchParams {
  return new URLSearchParams(Object.fromEntries(Object.entries(params).filter(([, v]) => v !== '')))
}

function optionLabel(opt: FacetOption) {
  return `${opt.label} (${opt.count})`
}

function FacetSelect({
  id, label, value, options, onChange, disabled, allLabel = 'All',
}: {
  id: string; label: string; value: string; options: FacetOption[]
  onChange: (v: string) => void; disabled?: boolean; allLabel?: string
}) {
  return (
    <label htmlFor={id}>
      {label}
      <select id={id} aria-label={label} value={value} disabled={disabled} onChange={(e) => onChange(e.target.value)}>
        <option value="">{allLabel}</option>
        {options.map((opt) => <option key={opt.value} value={opt.value}>{optionLabel(opt)}</option>)}
      </select>
    </label>
  )
}

function QuestionCard({ item, mode }: { item: Question; mode: Mode }) {
  const [open, setOpen] = useState(false)
  const [tab, setTab] = useState<'answer' | 'guidance' | 'followups' | 'sources' | 'practice'>('answer')
  const [bookmarked, setBookmarked] = useState(() => localStorage.getItem(`zume-bookmark-${item.id}`) === 'true')
  const [revealed, setRevealed] = useState(false)
  const [rating, setRating] = useState(() => localStorage.getItem(`zume-practice-rating-${item.id}`) ?? '')
  const toggleBookmark = () => {
    const next = !bookmarked
    setBookmarked(next)
    localStorage.setItem(`zume-bookmark-${item.id}`, String(next))
  }
  return (
    <article className={`library-card ${mode === 'draft' ? 'draft' : ''}`} data-question-id={item.id}>
      <div className="library-card-meta">
        <span className={`badge priority-${item.priority}`}>{item.priority}</span>
        <span className="badge">{item.level}</span>
        <span className="muted">{item.domain} / {item.subdomain}</span>
        <span className="muted">{item.frequency?.replace('_', ' ')}</span>
        {item.role_tracks?.slice(0, 3).map((role) => <span className="badge role" key={role}>{role}</span>)}
        {mode === 'draft' && <span className="badge draft">Draft research</span>}
      </div>
      <h3>{item.question ?? item.title}</h3>
      <p className="muted">
        {item.estimated_minutes ?? 4} minutes · Verified {item.last_verified}
        {item.freshness_state ? ` · ${item.freshness_state.replace('_', ' ')}` : ''}
      </p>
      <div className="library-card-actions">
        <button type="button" onClick={toggleBookmark}>{bookmarked ? 'Remove bookmark' : 'Bookmark'}</button>
        <button type="button" onClick={() => setOpen(!open)}>{open ? 'Hide details' : 'Open details'}</button>
      </div>
      {open && (
        <div className="library-card-details">
          <div className="tabs" role="tablist" aria-label="Question details">
            {([['answer', 'Interview answer'], ['guidance', 'Interviewer guidance'], ['followups', 'Follow-ups'], ['sources', 'Sources'], ['practice', 'Practice']] as const).map(([key, label]) => (
              <button key={key} type="button" role="tab" aria-selected={tab === key} className={tab === key ? 'active' : ''} onClick={() => setTab(key)}>{label}</button>
            ))}
          </div>
          {tab === 'answer' && (
            <div>
              <p><b>Concise answer</b></p><p>{item.concise_answer}</p>
              <p><b>Complete recommended answer</b></p><p>{item.recommended_answer}</p>
              {Boolean(item.key_points?.length) && <><p><b>Key points</b></p><ul>{item.key_points?.map((p) => <li key={p}>{p}</li>)}</ul></>}
              {Boolean(item.examples?.length) && <><p><b>Examples</b></p><ul>{item.examples?.map((p) => <li key={p}>{p}</li>)}</ul></>}
              {Boolean(item.code_examples?.length) && <><p><b>Code / query examples</b></p>{item.code_examples?.map((c) => <pre key={c.slice(0, 40)}>{c}</pre>)}</>}
              {Boolean(item.common_mistakes?.length) && <><p><b>Common mistakes</b></p><ul>{item.common_mistakes?.map((p) => <li key={p}>{p}</li>)}</ul></>}
            </div>
          )}
          {tab === 'guidance' && (
            <div>
              <p><b>Strong signals</b></p><ul>{item.strong_signals?.map((p) => <li key={p}>{p}</li>) ?? <li>Not recorded</li>}</ul>
              <p><b>Weak signals</b></p><ul>{item.weak_signals?.map((p) => <li key={p}>{p}</li>) ?? <li>Not recorded</li>}</ul>
              <p><b>Red flags</b></p><ul>{item.red_flags?.map((p) => <li key={p}>{p}</li>) ?? <li>Not recorded</li>}</ul>
              <p><b>Scoring anchors</b></p>
              <ul>
                <li>0 — no answer</li>
                <li>1 — superficial</li>
                <li>2 — workable</li>
                <li>3 — strong</li>
                <li>4 — expert / application depth</li>
              </ul>
              <p className="muted">Knockout relevance: {item.priority === 'P0' ? 'Yes — P0' : 'Supporting depth'}</p>
            </div>
          )}
          {tab === 'followups' && (
            <div>
              {(item.follow_ups ?? []).length === 0 && <p className="muted">No follow-ups recorded.</p>}
              {item.follow_ups?.map((fu) => (
                <div className="followup" key={fu.question}>
                  <p><b>{fu.question}</b></p>
                  <p>{fu.recommended_answer}</p>
                </div>
              ))}
            </div>
          )}
          {tab === 'sources' && (
            <div>
              {(item.references ?? []).length === 0 && <p className="muted">No sources recorded.</p>}
              <ul className="source-list">
                {item.references?.map((ref) => (
                  <li key={`${ref.source_id}-${ref.locator}`}>
                    {ref.source_url?.startsWith('https://') ? (
                      <a href={ref.source_url} target="_blank" rel="noreferrer">{ref.source_name || ref.source_id}</a>
                    ) : (
                      <span>{ref.source_name || ref.source_id}</span>
                    )}
                    <span className="muted"> — {ref.locator}</span>
                    <span className="muted"> · verified {ref.last_verified} · {ref.freshness_state}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {tab === 'practice' && (
            <div>
              <button type="button" onClick={() => setRevealed(!revealed)}>{revealed ? 'Hide answer' : 'Reveal answer'}</button>
              {revealed && <p>{item.recommended_answer ?? item.concise_answer}</p>}
              <SpeechControls question={item.question ?? ''} answer={item.recommended_answer ?? item.concise_answer ?? ''} />
              <fieldset>
                <legend>Self-rating</legend>
                {['Need review', 'Getting there', 'Comfortable'].map((value) => (
                  <label className="rating" key={value}>
                    <input type="radio" checked={rating === value} onChange={() => { setRating(value); localStorage.setItem(`zume-practice-rating-${item.id}`, value) }} /> {value}
                  </label>
                ))}
              </fieldset>
            </div>
          )}
        </div>
      )}
      <AudienceTag />
    </article>
  )
}

export function Library() {
  const [mode, setMode] = useState<Mode>('reviewed')
  const [filters, setFilters] = useState<Filters>(EMPTY)
  const [facets, setFacets] = useState<Facets | null>(null)
  const [items, setItems] = useState<Question[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [requestId, setRequestId] = useState('')
  const [moreOpen, setMoreOpen] = useState(false)
  const [history, setHistory] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? '[]') as string[] } catch { return [] }
  })
  const searchRef = useRef<HTMLInputElement>(null)
  const retryToken = useRef(0)

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === '/' && !(event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLSelectElement)) {
        event.preventDefault()
        searchRef.current?.focus()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  const loadFacets = useCallback(async () => {
    const data = await request<Facets>(`/api/knowledge/facets?${omitEmpty({ mode })}`)
    setFacets(data)
  }, [mode])

  const loadQuestions = useCallback(async () => {
    const token = ++retryToken.current
    setLoading(true)
    setError('')
    try {
      const params = omitEmpty({
        mode,
        q: filters.q,
        domain: filters.domain,
        subdomain: filters.subdomain,
        level: filters.level,
        priority: filters.priority,
        role: filters.role,
        frequency: filters.frequency,
        question_type: filters.question_type,
        source_family: filters.source_family,
        freshness_state: filters.freshness_state,
        tag: filters.tag,
        has_exercise: filters.has_exercise,
        has_followups: filters.has_followups,
        has_code_example: filters.has_code_example,
        sort: filters.sort === 'recommended' ? '' : filters.sort,
        limit: String(PAGE_SIZE),
        offset: String(page * PAGE_SIZE),
      })
      const data = await request<{ items: Question[]; total: number; request_id?: string }>(`/api/knowledge/questions?${params}`)
      if (token !== retryToken.current) return
      setItems(data.items)
      setTotal(data.total)
      setRequestId(data.request_id ?? '')
      if (filters.q.trim()) {
        setHistory((prev) => {
          const next = [filters.q.trim(), ...prev.filter((h) => h !== filters.q.trim())].slice(0, 8)
          localStorage.setItem(HISTORY_KEY, JSON.stringify(next))
          return next
        })
      }
    } catch (err) {
      if (token !== retryToken.current) return
      setItems([])
      setTotal(-1)
      setError((err as Error).message)
    } finally {
      if (token === retryToken.current) setLoading(false)
    }
  }, [filters, mode, page])

  useEffect(() => { void loadFacets().catch((err) => setError((err as Error).message)) }, [loadFacets])
  useEffect(() => {
    const timer = setTimeout(() => { void loadQuestions() }, 300)
    return () => clearTimeout(timer)
  }, [loadQuestions])

  const setFilter = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters((current) => {
      const next = { ...current, [key]: value }
      if (key === 'domain') next.subdomain = ''
      return next
    })
    setPage(0)
  }

  const activeChips = useMemo(() => {
    const chips: { key: keyof Filters; label: string }[] = []
    const labels: Partial<Record<keyof Filters, string>> = {
      domain: 'Domain', subdomain: 'Subdomain', level: 'Level', priority: 'Priority',
      role: 'Role', frequency: 'Frequency', question_type: 'Type', source_family: 'Source',
      freshness_state: 'Freshness', tag: 'Tag', has_exercise: 'Has exercise',
      has_followups: 'Has follow-ups', has_code_example: 'Has code',
    }
    ;(Object.keys(labels) as (keyof Filters)[]).forEach((key) => {
      if (filters[key]) chips.push({ key, label: `${labels[key]}: ${filters[key]}` })
    })
    if (filters.q) chips.push({ key: 'q', label: `Search: ${filters.q}` })
    return chips
  }, [filters])

  const subdomains = facets?.domains.find((d) => d.value === filters.domain)?.subdomains ?? []
  const pages = Math.max(1, Math.ceil(Math.max(total, 0) / PAGE_SIZE))
  const counts = facets?.counts

  return (
    <section className="library-page">
      <PageHeader eyebrow="Interview preparation" title="Question Library">
        <p className="lede">Reviewed interview questions, answer guidance, exercises and sources</p>
      </PageHeader>

      <div className="library-badges" aria-live="polite">
        <article><strong>{counts?.questions ?? '—'}</strong><span>Reviewed questions</span></article>
        <article><strong>{counts?.exercises ?? '—'}</strong><span>Reviewed exercises</span></article>
        <article><strong>{counts?.domains ?? '—'}</strong><span>Covered domains</span></article>
        <article><strong>{counts?.gaps ?? '—'}</strong><span>Open gaps</span></article>
        <article>
          <strong className={counts && counts.questions > 0 ? 'ok' : 'warn'}>
            {counts && counts.questions > 0 ? 'Validated' : 'Warnings'}
          </strong>
          <span>Library validation</span>
        </article>
      </div>

      <div className="mode-tabs" role="tablist" aria-label="Library mode">
        {([['reviewed', 'Reviewed Library'], ['draft', 'Draft Research'], ['gaps', 'Coverage & Gaps']] as const).map(([value, label]) => (
          <button key={value} type="button" role="tab" aria-selected={mode === value} className={mode === value ? 'active' : ''} onClick={() => { setMode(value); setPage(0) }}>{label}</button>
        ))}
      </div>
      {mode === 'draft' && <p className="banner warn" role="status">Draft research proposals are never selected into candidate interview packages.</p>}

      <div className="library-search">
        <label htmlFor="library-search">Search questions, answers, tools, scenarios or tags</label>
        <div className="search-row">
          <input
            id="library-search"
            ref={searchRef}
            placeholder="Search questions, answers, tools, scenarios or tags"
            value={filters.q}
            onChange={(e) => setFilter('q', e.target.value)}
          />
          {filters.q && <button type="button" onClick={() => setFilter('q', '')}>Clear</button>}
        </div>
        {history.length > 0 && (
          <p className="muted search-history">Recent: {history.map((h) => (
            <button type="button" key={h} className="chip" onClick={() => setFilter('q', h)}>{h}</button>
          ))}</p>
        )}
      </div>

      <div className="filter-strip" data-facets-ready={facets ? 'true' : 'false'}>
        <FacetSelect id="domain" label="Domain" value={filters.domain} options={facets?.domains ?? []} onChange={(v) => setFilter('domain', v)} />
        <FacetSelect id="subdomain" label="Subdomain" value={filters.subdomain} options={subdomains} onChange={(v) => setFilter('subdomain', v)} disabled={!filters.domain} />
        <FacetSelect id="level" label="Level" value={filters.level} options={facets?.levels ?? []} onChange={(v) => setFilter('level', v)} />
        <FacetSelect id="priority" label="Priority" value={filters.priority} options={facets?.priorities ?? []} onChange={(v) => setFilter('priority', v)} />
        <FacetSelect id="role" label="Role track" value={filters.role} options={facets?.roles ?? []} onChange={(v) => setFilter('role', v)} />
        <label htmlFor="sort">Sort
          <select id="sort" aria-label="Sort" value={filters.sort} onChange={(e) => setFilter('sort', e.target.value)}>
            <option value="recommended">Recommended</option>
            <option value="priority">Priority: P0 → P3</option>
            <option value="frequency">Most frequently asked</option>
            <option value="recently_verified">Recently verified</option>
            <option value="basic_to_advanced">Basic → advanced</option>
            <option value="advanced_to_basic">Advanced → basic</option>
            <option value="domain_az">Domain A → Z</option>
          </select>
        </label>
        <button type="button" className="ghost" onClick={() => setMoreOpen(!moreOpen)}>{moreOpen ? 'Hide filters' : 'More filters'}</button>
      </div>

      {moreOpen && (
        <div className="filter-strip secondary">
          <FacetSelect id="frequency" label="Frequency" value={filters.frequency} options={facets?.frequencies ?? []} onChange={(v) => setFilter('frequency', v)} />
          <FacetSelect id="question_type" label="Question type" value={filters.question_type} options={facets?.question_types ?? []} onChange={(v) => setFilter('question_type', v)} />
          <FacetSelect id="source_family" label="Source family" value={filters.source_family} options={facets?.source_families ?? []} onChange={(v) => setFilter('source_family', v)} />
          <FacetSelect id="freshness_state" label="Freshness status" value={filters.freshness_state} options={facets?.freshness_states ?? []} onChange={(v) => setFilter('freshness_state', v)} />
          <FacetSelect id="tag" label="Tags" value={filters.tag} options={facets?.tags ?? []} onChange={(v) => setFilter('tag', v)} />
          <label><input type="checkbox" checked={filters.has_exercise === 'true'} onChange={(e) => setFilter('has_exercise', e.target.checked ? 'true' : '')} /> Has exercise</label>
          <label><input type="checkbox" checked={filters.has_followups === 'true'} onChange={(e) => setFilter('has_followups', e.target.checked ? 'true' : '')} /> Has follow-ups</label>
          <label><input type="checkbox" checked={filters.has_code_example === 'true'} onChange={(e) => setFilter('has_code_example', e.target.checked ? 'true' : '')} /> Has code example</label>
        </div>
      )}

      {activeChips.length > 0 && (
        <div className="chip-row">
          {activeChips.map((chip) => (
            <button type="button" className="chip" key={chip.key} onClick={() => setFilter(chip.key, '')}>{chip.label} ×</button>
          ))}
          <button type="button" className="chip clear" onClick={() => { setFilters(EMPTY); setPage(0) }}>Clear all</button>
        </div>
      )}

      {error && (
        <div className="banner error" role="alert">
          <p>Library request failed{requestId ? ` (request ${requestId})` : ''}: {error}</p>
          <button type="button" onClick={() => void loadQuestions()}>Retry</button>
        </div>
      )}

      {!error && (
        <p className="results-header" aria-live="polite">
          {loading ? 'Loading…' : `${total} ${mode === 'draft' ? 'draft' : 'reviewed'} questions`}
          {!loading && total >= 0 && ` · page ${page + 1} of ${pages}`}
        </p>
      )}

      {mode === 'gaps' && facets?.gap_summary && (
        <div className="gap-table">
          <h2>Coverage gaps</h2>
          <ul>
            {facets.gap_summary.slice(0, 40).map((gap) => (
              <li key={`${gap.domain}-${gap.level}-${gap.kind}`}>
                {gap.domain} · {gap.level} · {gap.kind}: {gap.have}/{gap.target} (missing {gap.missing})
              </li>
            ))}
          </ul>
        </div>
      )}

      {!error && !loading && total === 0 && (
        <div className="empty-state">
          <p>No {mode === 'draft' ? 'draft' : 'reviewed'} questions match the active filters.</p>
          <p className="muted">Active: {activeChips.map((c) => c.label).join(', ') || 'none'}</p>
          <p>Try removing the most restrictive filter, or clear all filters.</p>
          <button type="button" onClick={() => { setFilters(EMPTY); setPage(0) }}>Clear filters</button>
        </div>
      )}

      <div className="question-list">
        {items.map((item) => <QuestionCard key={item.id} item={item} mode={mode} />)}
      </div>

      {!error && total > PAGE_SIZE && (
        <div className="pagination">
          <button type="button" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
          <button type="button" disabled={(page + 1) * PAGE_SIZE >= total} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}
    </section>
  )
}
