"""Deterministic offline AI provider — retrieval summaries only, no network."""

from __future__ import annotations

from typing import Any

from zume.ai.base import AIAnswer, AIProvider, Citation


class OfflineAIProvider(AIProvider):
    name = "offline"

    def available(self) -> bool:
        return True

    def answer(
        self,
        question: str,
        *,
        context: list[dict[str, Any]] | None = None,
        enable_web_search: bool = False,
    ) -> AIAnswer:
        del enable_web_search  # offline never uses web search
        context = context or []
        if not context:
            return AIAnswer(
                answer=(
                    "No matching local library records were found. "
                    "Refine the query or enable optional web research when a provider is configured."
                ),
                confidence="low",
                source_mode="offline_unavailable",
                model="offline",
            )
        parts: list[str] = []
        citations: list[Citation] = []
        for item in context[:5]:
            title = str(item.get("title") or item.get("id") or "record")
            concise = str(item.get("concise_answer") or item.get("recommended_answer") or "").strip()
            if concise:
                parts.append(f"**{title}**: {concise}")
            references = item.get("references") or []
            first_url = next(
                (str(ref.get("source_url")) for ref in references
                 if isinstance(ref, dict) and str(ref.get("source_url", "")).startswith("https://")),
                "",
            )
            citations.append(
                Citation(
                    source_id=str(item.get("id") or ""),
                    title=title,
                    locator=str(item.get("domain") or ""),
                    url=first_url,
                )
            )
        answer = (
            "Answer grounded only in the local Zume knowledge library "
            f"(query: {question.strip()[:160]}):\n\n" + "\n\n".join(parts)
        )
        return AIAnswer(
            answer=answer,
            citations=citations,
            confidence="medium" if parts else "low",
            source_mode="local_library",
            model="offline",
        )
