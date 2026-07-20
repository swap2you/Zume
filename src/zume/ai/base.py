"""AI provider interfaces. External providers are never imported at startup."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source_id: str = ""
    title: str = ""
    locator: str = ""
    url: str = ""


class AIAnswer(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: str = "medium"
    source_mode: str = "local_library"  # local_library | mixed | web | offline_unavailable
    model: str = "offline"


class AIProvider(ABC):
    """Optional grounded-answer provider."""

    name: str = "base"

    @abstractmethod
    def available(self) -> bool:
        ...

    @abstractmethod
    def answer(
        self,
        question: str,
        *,
        context: list[dict[str, Any]] | None = None,
        enable_web_search: bool = False,
    ) -> AIAnswer:
        ...
