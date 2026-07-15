import { NavLink, Outlet } from 'react-router-dom'

const navigation = [
  ['/', 'Overview'],
  ['/intake', 'Candidate intake'],
  ['/finalize', 'Finalize interview'],
  ['/library', 'Question library'],
  ['/practice', 'Practice session'],
  ['/builder', 'Interview builder'],
  ['/lab', 'Exercise lab'],
  ['/ask', 'Ask Zume'],
  ['/settings', 'Settings & doctor'],
]

export function Layout() {
  return (
    <div className="shell">
      <a className="skip-link" href="#main">Skip to content</a>
      <aside className="sidebar">
        <NavLink className="brand" to="/" aria-label="Zume overview">
          <span className="brand-mark">Z</span><span>Zume <small>1.0</small></span>
        </NavLink>
        <nav aria-label="Primary navigation">
          {navigation.map(([to, label]) => <NavLink key={to} to={to} end={to === '/'}>{label}</NavLink>)}
        </nav>
        <p className="local-note">Local workspace<br />Interviewer tools stay on this device.</p>
      </aside>
      <main id="main"><Outlet /></main>
    </div>
  )
}

export function PageHeader({ title, eyebrow, children }: { title: string; eyebrow: string; children?: React.ReactNode }) {
  return <header className="page-header"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1>{children}</header>
}

export function AudienceTag({ candidate = false }: { candidate?: boolean }) {
  return <span className={`audience ${candidate ? 'candidate' : ''}`}>{candidate ? 'Candidate-shareable' : 'Interviewer-only'}</span>
}
