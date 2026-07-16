import { render, screen } from '@testing-library/react'
import { vi } from 'vitest'
import { Library } from './WorkspacePages'

test('offers canonical priority filters', async () => {
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ items: [], total: 0 }) })))
  render(<Library />)
  const priority = await screen.findByLabelText('Priority')
  expect(priority).toHaveTextContent('P0')
  expect(priority).toHaveTextContent('P1')
  expect(priority).toHaveTextContent('P2')
  expect(priority).toHaveTextContent('P3')
})
