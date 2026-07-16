"""Record enrichment shared by the API: resolved sources and freshness states."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from zume.knowledge.loader import load_sources
from zume.knowledge.models import ExerciseRecord, QuestionRecord

DUE_SOON_DAYS = 45


def freshness_state(record: QuestionRecord | ExerciseRecord, *, today: date | None = None) -> str:
    """current / due_soon / stale from last_verified + freshness_days."""
    today = today or date.today()
    try:
        verified = datetime.strptime(record.last_verified, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return "stale"
    age = (today - verified).days
    if age > record.freshness_days:
        return "stale"
    if age > record.freshness_days - DUE_SOON_DAYS:
        return "due_soon"
    return "current"


def resolve_references(
    record: QuestionRecord | ExerciseRecord,
    sources: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve source_id references through knowledge/sources.yaml.

    The frontend must always use `source_url` as the link, never the locator.
    """
    resolved: list[dict[str, Any]] = []
    for ref in record.references:
        source = sources.get(ref.source_id, {})
        resolved.append(
            {
                "source_id": ref.source_id,
                "source_name": str(source.get("name") or ref.source_id),
                "source_url": str(source.get("url") or ""),
                "source_family": str(source.get("family") or ""),
                "locator": ref.locator,
                "last_verified": record.last_verified,
                "freshness_state": freshness_state(record),
            }
        )
    return resolved


def question_payload(
    record: QuestionRecord,
    sources: dict[str, dict[str, Any]],
    *,
    exercise_domains: set[str] | None = None,
) -> dict[str, Any]:
    """Full API projection of a question with resolved citations."""
    payload = record.model_dump()
    payload["references"] = resolve_references(record, sources)
    payload["freshness_state"] = freshness_state(record)
    payload["has_followups"] = bool(record.follow_ups)
    payload["has_code_example"] = bool(record.code_examples)
    if exercise_domains is not None:
        payload["has_exercise"] = record.domain in exercise_domains
    return payload


def load_sources_for(root: Path) -> dict[str, dict[str, Any]]:
    return load_sources(root / "knowledge")
