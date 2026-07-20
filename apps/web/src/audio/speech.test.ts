import { describe, expect, test } from 'vitest'
import { isSpeechAvailable, textForMode } from './speech'

describe('speech helper', () => {
  test('selects text for each narration mode', () => {
    expect(textForMode('question', 'Question', 'Answer')).toBe('Question')
    expect(textForMode('answer', 'Question', 'Answer')).toBe('Answer')
    expect(textForMode('both', 'Question', 'Answer')).toBe('Question. Answer')
  })
  test('detects unavailable browser speech support', () => {
    expect(typeof isSpeechAvailable()).toBe('boolean')
  })
})
