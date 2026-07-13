"""Provider abstraction for optional AI-assisted generation.

Zume never requires a model API. The deterministic TemplateProvider is the
default and only built-in implementation; an API-backed provider can be added
later by implementing the same protocol.
"""

from __future__ import annotations

import os
from typing import Protocol, runtime_checkable


@runtime_checkable
class Provider(Protocol):
    """Interface every generation provider must implement."""

    name: str

    def summarize_resume(self, resume_text: str) -> str:
        """Return a short factual summary grounded in the resume text."""
        ...

    def draft_communication(self, template_body: str, replacements: dict[str, str]) -> str:
        """Fill a communication template with concrete values."""
        ...


def get_provider() -> Provider:
    """Select a provider. Without a configured API, use the template provider."""
    from zume.providers.template import TemplateProvider

    if os.environ.get("ZUME_MODEL_API_KEY"):
        # No API-backed provider is bundled; fall back deterministically and
        # keep behavior identical rather than failing.
        return TemplateProvider()
    return TemplateProvider()
