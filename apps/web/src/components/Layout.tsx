import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { NavIcons } from './icons'

const navigation: [string, string, string][] = [
  ['/', 'Overview', 'Workspace'],
  ['/intake', 'Candidate intake', 'Hiring'],
  ['/finalize', 'Finalize interview', 'Hiring'],
  ['/builder', 'Interview builder', 'Hiring'],
  ['/library', 'Question library', 'Knowledge'],
  ['/practice', 'Practice session', 'Knowledge'],
  ['/lab', 'Exercise lab', 'Knowledge'],
  ['/ask', 'Ask Zume', 'Assist'],
  ['/settings', 'Settings & doctor', 'Assist'],
]

const groups = ['Workspace', 'Hiring', 'Knowledge', 'Assist']

export function Layout() {
  const location = useLocation()
  return (
    <div className="shell">
      <a className="skip-link" href="#main">Skip to content</a>
      <aside className="sidebar">
        <NavLink className="brand" to="/" aria-label="Zume overview">
          <span className="brand-mark">Z</span>
          <span className="brand-word">Zume <small>Workspace 1.0</small></span>
        </NavLink>
        <nav aria-label="Primary navigation">
          {groups.map((group) => (
            <div className="nav-group" key={group}>
              <p className="nav-group-label">{group}</p>
              {navigation.filter(([, , g]) => g === group).map(([to, label]) => {
                const Icon = NavIcons[to]
                return (
                  <NavLink key={to} to={to} end={to === '/'}>
                    <span className="nav-icon">{Icon ? <Icon /> : null}</span>
                    <span>{label}</span>
                  </NavLink>
                )
              })}
            </div>
          ))}
        </nav>
        <p className="local-note">
          <span className="local-dot" aria-hidden="true" />
          Local workspace — interviewer tools stay on this device.
        </p>
      </aside>
      <main id="main">
        <div className="page-transition" key={location.pathname}>
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export function PageHeader({ title, eyebrow, children }: { title: string; eyebrow: string; children?: React.ReactNode }) {
  return (
    <header className="page-header">
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      {children}
    </header>
  )
}

export function AudienceTag({ candidate = false }: { candidate?: boolean }) {
  return <span className={`audience ${candidate ? 'candidate' : ''}`}>{candidate ? 'Candidate-shareable' : 'Interviewer-only'}</span>
}
