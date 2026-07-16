"""Knowledge library validation."""

from __future__ import annotations

import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from zume.knowledge.loader import load_all_exercises, load_all_questions, load_sources, load_taxonomy
from zume.knowledge.models import ExerciseRecord, QuestionRecord

FORBIDDEN_PLACEHOLDERS = (
    "TODO",
    "TBD",
    "lorem ipsum",
    "it depends",
    "as appropriate",
    "fill in later",
)


def validate_library(root: Path) -> list[str]:
    knowledge_root = root / "knowledge"
    errors: list[str] = []
    questions = load_all_questions(knowledge_root)
    exercises = load_all_exercises(knowledge_root)
    sources = load_sources(knowledge_root)
    taxonomy = load_taxonomy(knowledge_root)
    domains = _taxonomy_domain_ids(taxonomy)

    ids = [q.id for q in questions] + [e.id for e in exercises]
    dup_ids = [i for i, n in Counter(ids).items() if n > 1]
    for item in dup_ids:
        errors.append(f"duplicate id: {item}")

    for q in questions:
        errors.extend(_validate_question(q, sources, domains))
    for ex in exercises:
        errors.extend(_validate_exercise(ex, sources, domains))

    # Near-duplicate check within domain+level buckets (bounded comparisons).
    buckets: dict[tuple[str, str], list[QuestionRecord]] = {}
    for q in questions:
        if q.status != "published":
            continue
        buckets.setdefault((q.domain, q.level), []).append(q)
    for bucket in buckets.values():
        ordered = sorted(bucket, key=lambda item: item.id)
        for i, a in enumerate(ordered):
            for b in ordered[i + 1 : i + 25]:
                ratio = SequenceMatcher(None, a.question.lower(), b.question.lower()).ratio()
                if ratio >= 0.97:
                    errors.append(f"near-duplicate questions: {a.id} ~ {b.id} ({ratio:.2f})")

    return errors


def _taxonomy_domain_ids(taxonomy: dict) -> set[str]:
    domains = taxonomy.get("domains") if isinstance(taxonomy, dict) else None
    if isinstance(domains, dict):
        return set(domains.keys())
    if isinstance(domains, list):
        ids: set[str] = set()
        for item in domains:
            if isinstance(item, dict) and item.get("id"):
                ids.add(str(item["id"]))
            elif isinstance(item, str):
                ids.add(item)
        return ids
    return set()


def _validate_question(q: QuestionRecord, sources: dict, domains: set[str]) -> list[str]:
    errors: list[str] = []
    if domains and q.domain not in domains:
        errors.append(f"{q.id}: unknown domain {q.domain}")
    if q.status != "published":
        return errors
    if not q.concise_answer.strip() or not q.recommended_answer.strip():
        errors.append(f"{q.id}: missing concise/recommended answer")
    if not q.references:
        errors.append(f"{q.id}: missing references")
    for ref in q.references:
        if sources and ref.source_id not in sources:
            errors.append(f"{q.id}: unknown source_id {ref.source_id}")
    if q.priority in {"P0", "P1"} and not q.follow_ups:
        errors.append(f"{q.id}: P0/P1 requires at least one follow-up")
    for fu in q.follow_ups:
        if not fu.recommended_answer.strip():
            errors.append(f"{q.id}: follow-up missing recommended_answer")
    blob = " ".join(
        [
            q.question,
            q.concise_answer,
            q.recommended_answer,
            q.deep_dive,
        ]
    ).lower()
    for token in FORBIDDEN_PLACEHOLDERS:
        if token.lower() in blob:
            # Allow "it depends" only when nuance explains factors — still flag bare phrase as error if alone.
            if token.lower() == "it depends" and "depends on" in blob and len(q.recommended_answer) > 80:
                continue
            errors.append(f"{q.id}: forbidden placeholder/language: {token}")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", q.last_verified or ""):
        errors.append(f"{q.id}: last_verified must be YYYY-MM-DD")
    return errors


def _validate_exercise(ex: ExerciseRecord, sources: dict, domains: set[str]) -> list[str]:
    errors: list[str] = []
    if domains and ex.domain not in domains:
        errors.append(f"{ex.id}: unknown domain {ex.domain}")
    if ex.status != "published":
        return errors
    required = [
        ex.task,
        ex.expected_reasoning,
        ex.reference_solution,
        ex.requirement_change_follow_up,
        ex.requirement_change_recommended_answer,
        ex.debugging_follow_up,
        ex.debugging_recommended_answer,
    ]
    if not all(str(x).strip() for x in required):
        errors.append(f"{ex.id}: incomplete exercise answer set")
    if not ex.scoring_rubric:
        errors.append(f"{ex.id}: missing scoring_rubric")
    if not ex.independence_questions:
        errors.append(f"{ex.id}: missing independence_questions")
    for item in ex.independence_questions:
        if not item.recommended_answer.strip():
            errors.append(f"{ex.id}: independence question missing answer")
    proj = ex.candidate_projection()
    forbidden_keys = {"reference_solution", "recommended_answer", "scoring_rubric", "expected_reasoning"}
    leaked = forbidden_keys.intersection(proj)
    if leaked:
        errors.append(f"{ex.id}: candidate projection leaked {sorted(leaked)}")
    text = " ".join(str(v) for v in proj.values()).lower()
    if "reference solution" in text or "recommended answer" in text:
        errors.append(f"{ex.id}: candidate projection appears to contain answer language")
    for ref in ex.references:
        if sources and ref.source_id not in sources:
            errors.append(f"{ex.id}: unknown source_id {ref.source_id}")
    return errors
