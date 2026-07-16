import { FormEvent, useState } from 'react'
import { post, request } from '../api'
import { PageHeader, AudienceTag } from '../components/Layout'

type Citation = { title?: string; source_id?: string; url?: string; locator?: string }
type Message = { role: 'you' | 'zume'; text: string; citations?: Citation[]; sourceMode?: string; confidence?: string | number; model?: string }

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
      const result = await post<{ answer?: string; response?: string; citations?: Citation[]; sources?: Citation[]; source_mode?: string; confidence?: string | number; model?: string }>('/api/ask', { question: text, enable_web_search: web })
      setMessages((items) => [...items, { role: 'zume', text: result.answer ?? result.response ?? 'No response was returned.', citations: result.citations ?? result.sources, sourceMode: result.source_mode, confidence: result.confidence, model: result.model }])
    } catch (error) {
      setMessages((items) => [...items, { role: 'zume', text: `Unable to reach Zume: ${(error as Error).message}` }])
    } finally { setBusy(false) }
  }
  async function clearHistory() {
    try { await request('/api/ask/history', { method: 'DELETE' }); setMessages([]) } catch (error) { setMessages((items) => [...items, { role: 'zume', text: `Unable to clear history: ${(error as Error).message}` }]) }
  }
  return <section className="ask-page">
    <PageHeader eyebrow="Guidance, not a decision" title="Ask Zume"><p className="lede">Use this space to clarify process or prepare for an interview. Verify decisions against evidence and notes.</p></PageHeader>
    <AudienceTag />
    <div className="conversation" aria-live="polite">
      {messages.length === 0 && <p className="empty-state">Ask about interview preparation, a testing concept, or how to use Zume.</p>}
      {messages.map((message, index) => <article className={`message ${message.role}`} key={index}><b>{message.role === 'you' ? 'You' : 'Zume'}</b>{message.sourceMode && <span className="audience">{message.sourceMode === 'web' ? 'Web sources' : 'Offline sources'}</span>}<p>{message.text}</p>{message.role === 'zume' && <p className="muted">Confidence: {message.confidence ?? 'not provided'} · Model: {message.model ?? 'local'}</p>}{Boolean(message.citations?.length) && <ul className="citations">{message.citations?.map((citation, citationIndex) => <li key={`${citation.source_id}-${citationIndex}`}><a href={citation.url ?? citation.locator} target="_blank" rel="noreferrer">{citation.title ?? citation.source_id ?? 'Source'}</a>{citation.source_id && ` (${citation.source_id})`}</li>)}</ul>}</article>)}
    </div>
    <form className="chat-form" onSubmit={submit}>
      <label htmlFor="ask-question">Your question</label>
      <textarea id="ask-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What would you like to work through?" required />
      <label className="checkbox"><input type="checkbox" checked={web} onChange={(event) => setWeb(event.target.checked)} /> Allow web search when available</label>
      <button type="submit" disabled={busy}>{busy ? 'Thinking…' : 'Ask Zume'}</button>
      <button type="button" onClick={() => void clearHistory()}>Clear history</button>
    </form>
  </section>
}
