import { useEffect, useState } from 'react'
import { availableVoices, isSpeechAvailable, pauseSpeech, resumeSpeech, speak, stopSpeech, textForMode, type SpeechMode } from '../audio/speech'

export function SpeechControls({ question, answer }: { question: string; answer: string }) {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  const [voiceIndex, setVoiceIndex] = useState('')
  const [rate, setRate] = useState(1)
  const [mode, setMode] = useState<SpeechMode>('both')

  useEffect(() => {
    if (!isSpeechAvailable()) return
    const refresh = () => setVoices(availableVoices())
    refresh()
    window.speechSynthesis.addEventListener('voiceschanged', refresh)
    return () => window.speechSynthesis.removeEventListener('voiceschanged', refresh)
  }, [])

  if (!isSpeechAvailable()) return <p className="muted">Read-aloud is unavailable in this browser.</p>
  const voice = voiceIndex ? voices[Number(voiceIndex)] : null
  return <div className="speech-controls" aria-label="Read aloud controls">
    <label>Read<select value={mode} onChange={event => setMode(event.target.value as SpeechMode)}><option value="question">Question only</option><option value="answer">Answer only</option><option value="both">Question and answer</option></select></label>
    <label>Voice<select value={voiceIndex} onChange={event => setVoiceIndex(event.target.value)}><option value="">Browser default</option>{voices.map((item, index) => <option value={index} key={`${item.name}-${item.lang}`}>{item.name} ({item.lang})</option>)}</select></label>
    <label>Rate <input aria-label="Speech rate" type="range" min="0.7" max="1.4" step="0.1" value={rate} onChange={event => setRate(Number(event.target.value))} /></label>
    <div><button type="button" onClick={() => speak(textForMode(mode, question, answer), rate, voice)}>Play</button><button type="button" onClick={pauseSpeech}>Pause</button><button type="button" onClick={resumeSpeech}>Resume</button><button type="button" onClick={stopSpeech}>Stop</button></div>
  </div>
}
