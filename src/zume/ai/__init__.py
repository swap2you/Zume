"""Optional AI providers. Offline works without keys; OpenAI loads only when configured."""

from __future__ import annotations

from zume.ai.base import AIAnswer, AIProvider, Citation
from zume.ai.offline import OfflineAIProvider


def get_ai_provider() -> AIProvider:
    from zume.runtime_settings import load_runtime_settings

    settings = load_runtime_settings()
    if settings.openai_api_key_configured and settings.openai_api_key:
        from zume.ai.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)
    return OfflineAIProvider()


__all__ = ["AIAnswer", "AIProvider", "Citation", "OfflineAIProvider", "get_ai_provider"]
