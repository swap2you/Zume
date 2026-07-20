"""Audio providers. Browser baseline works offline; OpenAI/TTS/realtime are optional."""

from __future__ import annotations

from zume.audio.base import RealtimeSession, RealtimeVoiceProvider, SpeechProvider, SpeechResult
from zume.audio.browser import BrowserSpeechProvider
from zume.audio.realtime import DisabledRealtimeVoiceProvider


def get_speech_provider() -> SpeechProvider:
    from zume.runtime_settings import load_runtime_settings

    settings = load_runtime_settings()
    if settings.openai_api_key_configured and settings.openai_api_key:
        from zume.audio.openai_tts import OpenAITTSProvider

        return OpenAITTSProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_tts_model,
            voice=settings.openai_tts_voice,
        )
    return BrowserSpeechProvider()


def get_realtime_provider() -> RealtimeVoiceProvider:
    from zume.runtime_settings import load_runtime_settings

    settings = load_runtime_settings()
    if settings.enable_realtime and settings.openai_api_key_configured and settings.openai_api_key:
        from zume.audio.realtime import OpenAIRealtimeVoiceProvider

        return OpenAIRealtimeVoiceProvider(api_key=settings.openai_api_key)
    return DisabledRealtimeVoiceProvider()


__all__ = [
    "RealtimeSession",
    "RealtimeVoiceProvider",
    "SpeechProvider",
    "SpeechResult",
    "BrowserSpeechProvider",
    "get_speech_provider",
    "get_realtime_provider",
]
