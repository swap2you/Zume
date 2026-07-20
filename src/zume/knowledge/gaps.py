"""Coverage gap reporting against taxonomy targets."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from zume.knowledge.loader import load_all_exercises, load_all_questions, load_taxonomy


def _domain_metas(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    domains = taxonomy.get("domains") or {}
    if isinstance(domains, dict):
        return {str(k): (v if isinstance(v, dict) else {"id": k}) for k, v in domains.items()}
    if isinstance(domains, list):
        out: dict[str, dict[str, Any]] = {}
        for item in domains:
            if isinstance(item, dict) and item.get("id"):
                out[str(item["id"])] = item
        return out
    return {}


def collect_gaps(root: Path) -> dict[str, Any]:
    taxonomy = load_taxonomy(root / "knowledge")
    domain_metas = _domain_metas(taxonomy)
    all_questions = load_all_questions(root / "knowledge")
    all_exercises = load_all_exercises(root / "knowledge")
    questions = [
        q for q in all_questions
        if q.status == "published" and q.review_status == "reviewed"
    ]
    exercises = [
        e for e in all_exercises
        if e.status == "published" and e.review_status == "reviewed"
    ]

    q_counts: dict[tuple[str, str], int] = defaultdict(int)
    for q in questions:
        q_counts[(q.domain, q.level)] += 1
    e_counts: dict[str, int] = defaultdict(int)
    for e in exercises:
        e_counts[e.domain] += 1

    gaps: list[dict[str, Any]] = []
    for domain_id, meta in domain_metas.items():
        tier = str(meta.get("tier") or "C")
        q_target = {"A": 24, "B": 15, "C": 9}.get(tier, 9)
        e_target = {"A": 12, "B": 6, "C": 3}.get(tier, 3)
        for level in ("basic", "intermediate", "advanced"):
            have = q_counts.get((domain_id, level), 0)
            if have < q_target:
                gaps.append(
                    {
                        "domain": domain_id,
                        "level": level,
                        "kind": "questions",
                        "have": have,
                        "target": q_target,
                        "missing": q_target - have,
                    }
                )
        have_e = e_counts.get(domain_id, 0)
        if have_e < e_target:
            gaps.append(
                {
                    "domain": domain_id,
                    "level": "all",
                    "kind": "exercises",
                    "have": have_e,
                    "target": e_target,
                    "missing": e_target - have_e,
                }
            )
    return {
        "published_questions": len(questions),
        "draft_questions": sum(1 for q in all_questions if q.status == "draft"),
        "reviewed_published_questions": len(questions),
        "published_exercises": len(exercises),
        "gaps": gaps,
        "complete_claim": False,
        "note": "Gap report does not claim total internet completeness.",
    }
