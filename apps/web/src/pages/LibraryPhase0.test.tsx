/**
 * Phase 0 — Question Library correction regressions (frontend).
 * These encode the binding UI spec and fail against the uncorrected baseline.
 */
import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { Home } from './Home'
import { MemoryRouter } from 'react-router-dom'
import { Library } from './WorkspacePages'

const FACETS = {
  mode: 'reviewed',
  counts: { questions: 2, exercises: 1, domains: 1, gaps: 3 },
  domains: [{ value: 'java', label: 'Java', count: 2, subdomains: [{ value: 'collections', label: 'Collections', count: 1 }] }],
  levels: [{ value: 'basic', label: 'Basic', count: 2 }],
  priorities: [{ value: 'P0', label: 'P0', count: 2 }],
  frequencies: [{ value: 'very_common', label: 'Very common', count: 2 }],
  roles: [{ value: 'Senior SDET', label: 'Senior SDET', count: 2 }],
  question_types: [{ value: 'concept', label: 'Concept', count: 2 }],
  source_families: [], freshness_states: [], tags: [],
}

afterEach(() => vi.unstubAllGlobals())

test('library API failure shows an error with retry, never zero results', async () => {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    if (String(url).includes('/api/knowledge/facets')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(FACETS) })
    }
    return Promise.resolve({ ok: false, status: 500, json: () => Promise.resolve({ detail: 'boom' }) })
  }))
  render(<MemoryRouter><Library /></MemoryRouter>)
  await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())
  expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument()
  expect(screen.queryByText(/0 reviewed questions/i)).not.toBeInTheDocument()
})

test('library dropdown facets come from the facets API, not hardcoded text inputs', async () => {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    if (String(url).includes('/api/knowledge/facets')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(FACETS) })
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], total: 0, request_id: 'x' }) })
  }))
  render(<MemoryRouter><Library /></MemoryRouter>)
  const domain = await screen.findByRole('combobox', { name: /^domain$/i })
  expect(domain.tagName).toBe('SELECT')
  await waitFor(() => expect(domain).toHaveTextContent('Java (2)'))
  // Subdomain stays disabled until a domain is chosen.
  expect(screen.getByRole('combobox', { name: /^subdomain$/i })).toBeDisabled()
})

test('home distinguishes reviewed questions from draft proposals', async () => {
  vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(String(url).includes('health')
      ? { status: 'ok' }
      : { questions: 1988, reviewed_published_questions: 66, draft_questions: 1899, exercises: 289, published_exercises: 4, domains: 20 }),
  })))
  render(<MemoryRouter><Home /></MemoryRouter>)
  expect(await screen.findByText('66')).toBeInTheDocument()
  expect(screen.getAllByText(/reviewed questions/i).length).toBeGreaterThan(0)
  expect(screen.getAllByText(/draft/i).length).toBeGreaterThan(0)
  // The misleading combined figure must not be the headline metric.
  expect(screen.queryByText(/^library questions$/i)).not.toBeInTheDocument()
})
