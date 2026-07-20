import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import { Library } from './Library'

const FACETS = {
  mode: 'reviewed',
  counts: { questions: 2, exercises: 1, domains: 1, gaps: 3 },
  domains: [{ value: 'java', label: 'Java', count: 2, subdomains: [{ value: 'collections', label: 'Collections', count: 1 }] }],
  levels: [{ value: 'basic', label: 'Basic', count: 1 }, { value: 'intermediate', label: 'Intermediate', count: 1 }],
  priorities: [{ value: 'P0', label: 'P0', count: 1 }, { value: 'P1', label: 'P1', count: 1 }, { value: 'P2', label: 'P2', count: 0 }, { value: 'P3', label: 'P3', count: 0 }],
  frequencies: [], roles: [], question_types: [], source_families: [], freshness_states: [], tags: [],
}

afterEach(() => vi.unstubAllGlobals())

test('offers canonical priority filters from facets', async () => {
  vi.stubGlobal('fetch', vi.fn((url: string) => {
    if (String(url).includes('/api/knowledge/facets')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(FACETS) })
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], total: 0, request_id: 'x' }) })
  }))
  render(<MemoryRouter><Library /></MemoryRouter>)
  const priority = await screen.findByLabelText('Priority')
  await waitFor(() => expect(priority).toHaveTextContent('P0'))
  expect(priority).toHaveTextContent('P1')
  expect(priority).toHaveTextContent('P2')
  expect(priority).toHaveTextContent('P3')
})
