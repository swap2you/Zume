import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { request } from '../api'
import { PageHeader } from '../components/Layout'

type Stats = { questions?: number; exercises?: number; domains?: number; available?: boolean }

export function Home() {
  const [health, setHealth] = useState<'checking' | 'online' | 'offline'>('checking')
  const [stats, setStats] = useState<Stats>({})
  useEffect(() => {
    request<{ status: string }>('/api/health').then(() => setHealth('online')).catch(() => setHealth('offline'))
    request<Stats>('/api/knowledge/stats').then(setStats).catch(() => setStats({ available: false }))
  }, [])
  return <section>
    <PageHeader eyebrow="Zume local workspace" title="Good work starts with a clear record.">
      <p className="lede">Prepare structured interviews, examine the library, and preserve the distinction between evidence and assessment.</p>
    </PageHeader>
    <div className="status-row" aria-live="polite"><span className={`status-dot ${health}`} /> API {health === 'checking' ? 'checking…' : health}</div>
    <div className="stat-grid">
      <article><strong>{stats.questions ?? '—'}</strong><span>library questions</span></article>
      <article><strong>{stats.exercises ?? '—'}</strong><span>practical exercises</span></article>
      <article><strong>{stats.domains ?? '—'}</strong><span>knowledge domains</span></article>
    </div>
    <h2>Start a focused task</h2>
    <div className="action-grid">
      <Link to="/intake"><b>Bring in a candidate</b><span>Screen resume evidence and build the pre-interview package.</span></Link>
      <Link to="/builder"><b>Shape an interview</b><span>Preview a three-hour plan before conducting it.</span></Link>
      <Link to="/library"><b>Explore the library</b><span>Find questions and exercises by skill and depth.</span></Link>
    </div>
  </section>
}
