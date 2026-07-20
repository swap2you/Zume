import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { request } from '../api'
import { PageHeader } from '../components/Layout'
import { ArrowIcon } from '../components/icons'

type Stats = {
  questions?: number
  exercises?: number
  published_exercises?: number
  domains?: number
  available?: boolean
  reviewed_published_questions?: number
  draft_questions?: number
}

export function Home() {
  const [health, setHealth] = useState<'checking' | 'online' | 'offline'>('checking')
  const [stats, setStats] = useState<Stats>({})
  const [error, setError] = useState('')
  useEffect(() => {
    request<{ status: string }>('/api/health').then(() => setHealth('online')).catch(() => setHealth('offline'))
    request<Stats>('/api/knowledge/stats')
      .then(setStats)
      .catch((err) => { setStats({ available: false }); setError((err as Error).message) })
  }, [])
  return <section>
    <PageHeader eyebrow="Zume local workspace" title="Good work starts with a clear record.">
      <p className="lede">Prepare structured interviews, examine the library, and preserve the distinction between evidence and assessment.</p>
    </PageHeader>
    <div className="status-row" aria-live="polite"><span className={`status-dot ${health}`} /> API {health === 'checking' ? 'checking…' : health}</div>
    {error && <p className="error" role="alert">{error}</p>}
    <div className="stat-grid">
      <article><strong>{stats.reviewed_published_questions ?? '—'}</strong><span>Reviewed questions</span></article>
      <article><strong>{stats.draft_questions ?? '—'}</strong><span>Draft research proposals</span></article>
      <article><strong>{stats.published_exercises ?? stats.exercises ?? '—'}</strong><span>Reviewed exercises</span></article>
    </div>
    <h2>Start a focused task</h2>
    <div className="action-grid">
      <Link to="/intake"><b>Bring in a candidate</b><span>Screen resume evidence and build the pre-interview package.</span><ArrowIcon /></Link>
      <Link to="/builder"><b>Shape an interview</b><span>Preview a three-hour plan before conducting it.</span><ArrowIcon /></Link>
      <Link to="/library"><b>Explore the library</b><span>Find reviewed questions and exercises by skill and depth.</span><ArrowIcon /></Link>
    </div>
  </section>
}
