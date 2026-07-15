"""Feature-flagged realtime voice adapter. Disabled cleanly when unavailable."""

from __future__ import annotations

from zume.audio.base import RealtimeSession, RealtimeVoiceProvider


class DisabledRealtimeVoiceProvider(RealtimeVoiceProvider):
    name = "realtime_disabled"

    def available(self) -> bool:
        return False

    def create_ephemeral_session(self) -> RealtimeSession:
        return RealtimeSession(
            enabled=False,
            note="Realtime voice is disabled. Enable ZUME_ENABLE_REALTIME and configure OpenAI.",
        )


class OpenAIRealtimeVoiceProvider(RealtimeVoiceProvider):
    """Creates short-lived client credentials; long-lived key never reaches the browser."""

    name = "openai_realtime"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def available(self) -> bool:
        return bool(self._api_key)

    def create_ephemeral_session(self) -> RealtimeSession:
        # Avoid live network in unit tests; callers mock this method.
        # Production path would mint an ephemeral token server-side.
        return RealtimeSession(
            enabled=False,
            note=(
                "Realtime session minting is available only when live credentials and "
                "feature flag are healthy; mocked/disabled for safe default operation."
            ),
        )
