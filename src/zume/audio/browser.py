"""Browser speech synthesis baseline — server returns a descriptor only."""

from __future__ import annotations

from zume.audio.base import SpeechProvider, SpeechResult


class BrowserSpeechProvider(SpeechProvider):
    """Server-side marker: actual playback happens in the browser via Web Speech API."""

    name = "browser"

    def available(self) -> bool:
        return True

    def synthesize(self, text: str, *, voice: str | None = None, speed: float = 1.0) -> SpeechResult:
        del voice, speed
        return SpeechResult(
            audio_bytes=None,
            mime_type="text/plain",
            provider="browser",
            ai_generated=False,
            disclosure="Uses the browser built-in speech synthesis (not AI-generated).",
            cache_path="",
        )
