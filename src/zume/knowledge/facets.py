"""Database-driven facet options for the Question Library UI.

Every option is generated from actual records in the selected mode and carries
a real count. The frontend must never hardcode values that conflict with this
endpoint.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from zume.knowledge.enrich import freshness_state
from zume.knowledge.gaps import collect_gaps
from zume.knowledge.loader import (
    load_all_exercises,
    load_all_questions,
    load_sources,
    load_taxonomy,
)
from zume.knowledge.models import QuestionRecord

MODES = ("reviewed", "draft", "gaps")


def _labels(taxonomy: dict[str, Any], key: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in taxonomy.get(key) or []:
        if isinstance(item, dict) and item.get("value"):
            out[str(item["value"])] = str(item.get("label") or item["value"])
        elif isinstance(item, str):
            out[item] = _titleize(item)
    return out


def _titleize(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").strip().capitalize()


def _questions_for_mode(root: Path, mode: str) -> list[QuestionRecord]:
    questions = load_all_questions(root / "knowledge")
    if mode == "draft":
        return [q for q in questions if q.status == "draft"]
    return [q for q in questions if q.status == "published" and q.review_status == "reviewed"]


def _options(counter: Counter[str], labels: dict[str, str], order: list[str] | None = None) -> list[dict[str, Any]]:
    keys = [k for k in (order or sorted(counter))] if order else sorted(counter)
    if order:
        keys = [k for k in order if k in counter] + sorted(set(counter) - set(order))
    return [
        {"value": key, "label": labels.get(key, _titleize(key)), "count": counter[key]}
        for key in keys
        if counter[key] > 0
    ]


def collect_facets(root: Path, mode: str = "reviewed") -> dict[str, Any]:
    if mode not in MODES:
        mode = "reviewed"
    taxonomy = load_taxonomy(root / "knowledge")
    sources = load_sources(root / "knowledge")
    gap_report = collect_gaps(root)
    questions = _questions_for_mode(root, mode if mode != "gaps" else "reviewed")
    exercises = [
        e for e in load_all_exercises(root / "knowledge")
        if (e.status == "draft" if mode == "draft"
            else e.status == "published" and e.review_status == "reviewed")
    ]

    domain_labels: dict[str, str] = {}
    domain_order: list[str] = []
    subdomain_labels: dict[str, dict[str, str]] = {}
    for item in taxonomy.get("domains") or []:
        if not isinstance(item, dict):
            continue
        domain_id = str(item.get("id") or item.get("value") or "")
        if not domain_id:
            continue
        domain_order.append(domain_id)
        domain_labels[domain_id] = str(item.get("label") or _titleize(domain_id))
        subdomain_labels[domain_id] = {
            str(sub): _titleize(str(sub)) for sub in (item.get("subdomains") or [])
        }

    domain_counts: Counter[str] = Counter(q.domain for q in questions)
    sub_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for q in questions:
        if q.subdomain:
            sub_counts[q.domain][q.subdomain] += 1

    domains: list[dict[str, Any]] = []
    ordered = [d for d in domain_order if d in domain_counts] + sorted(
        set(domain_counts) - set(domain_order)
    )
    for domain_id in ordered:
        domains.append(
            {
                "value": domain_id,
                "label": domain_labels.get(domain_id, _titleize(domain_id)),
                "count": domain_counts[domain_id],
                "subdomains": [
                    {
                        "value": sub,
                        "label": subdomain_labels.get(domain_id, {}).get(sub, _titleize(sub)),
                        "count": count,
                    }
                    for sub, count in sorted(sub_counts[domain_id].items())
                ],
            }
        )

    source_families: Counter[str] = Counter()
    for q in questions:
        for ref in q.references:
            family = str(sources.get(ref.source_id, {}).get("family") or "")
            if family:
                source_families[family] += 1

    freshness_counts: Counter[str] = Counter(freshness_state(q) for q in questions)
    tag_counts: Counter[str] = Counter(tag for q in questions for tag in q.tags)

    level_order = ["basic", "intermediate", "advanced"]
    priority_order = ["P0", "P1", "P2", "P3"]
    frequency_order = ["very_common", "common", "occasional", "emerging"]
    freshness_order = ["current", "due_soon", "stale"]

    return {
        "mode": mode,
        "counts": {
            "questions": len(questions),
            "exercises": len(exercises),
            "domains": len(domain_counts),
            "gaps": len(gap_report.get("gaps") or []),
        },
        "domains": domains,
        "levels": _options(Counter(q.level for q in questions), _labels(taxonomy, "levels"), level_order),
        "priorities": _options(Counter(q.priority for q in questions), _labels(taxonomy, "priorities"), priority_order),
        "frequencies": _options(Counter(q.frequency for q in questions), _labels(taxonomy, "frequencies"), frequency_order),
        "roles": _options(Counter(role for q in questions for role in q.role_tracks), {}, None),
        "question_types": _options(Counter(q.question_type for q in questions), {}, None),
        "source_families": _options(source_families, {}, None),
        "freshness_states": _options(freshness_counts, _labels(taxonomy, "freshness_states"), freshness_order),
        "tags": _options(tag_counts, {}, None)[:40],
        "gap_summary": gap_report.get("gaps") if mode == "gaps" else None,
    }
