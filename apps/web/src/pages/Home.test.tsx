import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import { Home } from './Home'

vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve({
  ok: true,
  json: () => Promise.resolve(url.includes('health') ? { status: 'ok' } : { questions: 42, exercises: 8, domains: 4 }),
})))

test('shows health and knowledge statistics', async () => {
  render(<MemoryRouter><Home /></MemoryRouter>)
  expect(await screen.findByText('42')).toBeInTheDocument()
  expect(screen.getByText('API online')).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /bring in a candidate/i })).toHaveAttribute('href', '/intake')
})
