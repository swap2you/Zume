import { FormEvent, useState } from 'react'
import { post } from '../api'
import { PageHeader, AudienceTag } from '../components/Layout'

type Message = { role: 'you' | 'zume'; text: string }

export function Ask() {
  const [question, setQuestion] = useState('')
  const [web, setWeb] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [busy, setBusy] = useState(false)
  async function submit(event: FormEvent) {
    event.preventDefault()
    const text = question.trim()
    if (!text || busy) return
    setQuestion(''); setBusy(true); setMessages((items) => [...items, { role: 'you', text }])
    try {
      const result = await post<{ answer?: string; response?: string }>('/api/ask', { question: text, enable_web_search: web })
      setMessages((items) => [...items, { role: 'zume', text: result.answer ?? result.response ?? 'No response was returned.' }])
    } catch (error) {
      setMessages((items) => [...items, { role: 'zume', text: `Unable to reach Zume: ${(error as Error).message}` }])
    } finally { setBusy(false) }
  }
  return <section className="ask-page">
    <PageHeader eyebrow="Guidance, not a decision" title="Ask Zume"><p className="lede">Use this space to clarify process or prepare for an interview. Verify decisions against evidence and notes.</p></PageHeader>
    <AudienceTag />
    <div className="conversation" aria-live="polite">
      {messages.length === 0 && <p className="empty-state">Ask about interview preparation, a testing concept, or how to use Zume.</p>}
      {messages.map((message, index) => <article className={`message ${message.role}`} key={index}><b>{message.role === 'you' ? 'You' : 'Zume'}</b><p>{message.text}</p></article>)}
    </div>
    <form className="chat-form" onSubmit={submit}>
      <label htmlFor="ask-question">Your question</label>
      <textarea id="ask-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What would you like to work through?" required />
      <label className="checkbox"><input type="checkbox" checked={web} onChange={(event) => setWeb(event.target.checked)} /> Allow web search when available</label>
      <button type="submit" disabled={busy}>{busy ? 'Thinking…' : 'Ask Zume'}</button>
    </form>
  </section>
}
