"""Speech and realtime voice provider interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class SpeechResult(BaseModel):
    audio_bytes: bytes | None = None
    mime_type: str = "audio/mpeg"
    provider: str = "browser"
    ai_generated: bool = False
    disclosure: str = ""
    cache_path: str = ""


class SpeechProvider(ABC):
    name: str = "base"

    @abstractmethod
    def available(self) -> bool:
        ...

    @abstractmethod
    def synthesize(self, text: str, *, voice: str | None = None, speed: float = 1.0) -> SpeechResult:
        ...


class RealtimeSession(BaseModel):
    enabled: bool = False
    client_secret: str = ""
    expires_at: str = ""
    note: str = Field(default="")


class RealtimeVoiceProvider(ABC):
    name: str = "base"

    @abstractmethod
    def available(self) -> bool:
        ...

    @abstractmethod
    def create_ephemeral_session(self) -> RealtimeSession:
        ...
