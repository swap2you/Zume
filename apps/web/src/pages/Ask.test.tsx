import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { Ask } from './Ask'

test('sends a question and displays the answer', async () => {
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ answer: 'Start with evidence.' }) })))
  const user = userEvent.setup()
  render(<Ask />)
  await user.type(screen.getByLabelText('Your question'), 'How should I prepare?')
  await user.click(screen.getByRole('button', { name: 'Ask Zume' }))
  expect(await screen.findByText('Start with evidence.')).toBeInTheDocument()
  expect(screen.getByText('How should I prepare?')).toBeInTheDocument()
})

test('renders answer citations and source mode', async () => {
  vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ answer: 'Use primary evidence.', source_mode: 'web', citations: [{ title: 'OWASP', source_id: 'owasp', url: 'https://owasp.org' }] }) })))
  const user = userEvent.setup()
  render(<Ask />)
  await user.type(screen.getByLabelText('Your question'), 'Where should I look?')
  await user.click(screen.getByRole('button', { name: 'Ask Zume' }))
  expect(await screen.findByText('OWASP')).toBeInTheDocument()
  expect(screen.getByText('Web sources')).toBeInTheDocument()
})
