export type SpeechMode = 'question' | 'answer' | 'both'

export function isSpeechAvailable(): boolean {
  return typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window
}

export function availableVoices(): SpeechSynthesisVoice[] {
  return isSpeechAvailable() ? window.speechSynthesis.getVoices() : []
}

export function speak(text: string, rate = 1, voice?: SpeechSynthesisVoice | null): void {
  if (!isSpeechAvailable() || !text.trim()) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.rate = rate
  if (voice) utterance.voice = voice
  window.speechSynthesis.speak(utterance)
}

export function pauseSpeech(): void { if (isSpeechAvailable()) window.speechSynthesis.pause() }
export function resumeSpeech(): void { if (isSpeechAvailable()) window.speechSynthesis.resume() }
export function stopSpeech(): void { if (isSpeechAvailable()) window.speechSynthesis.cancel() }

export function textForMode(mode: SpeechMode, question: string, answer: string): string {
  if (mode === 'question') return question
  if (mode === 'answer') return answer
  return [question, answer].filter(Boolean).join('. ')
}
