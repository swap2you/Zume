"""Editorial quality gates for material that is eligible for interviews."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from zume.knowledge.loader import load_all_exercises, load_all_questions
from zume.knowledge.models import ExerciseRecord, QuestionRecord

GENERIC_FINGERPRINTS = (
    "should be applied to a stated outcome, observable evidence",
    "start by naming the decision that",
    "what evidence would make you revise your",
)
VAGUE_LOCATORS = {"", "section", "chapter", "documentation", "docs", "guide"}
DOMAIN_TERMS = {
    "java": {"java", "collection", "exception", "stream", "thread", "hash"},
    "selenium": {"selenium", "webdriver", "locator", "wait", "page"},
    "rest-assured": {"rest", "http", "request", "response", "assured"},
    "sql-oracle": {"sql", "oracle", "query", "join", "table", "aggregate"},
    "api-openapi": {"api", "openapi", "schema", "operation", "contract"},
    "testng": {"testng", "test", "suite", "listener", "data provider"},
    "cucumber": {"cucumber", "gherkin", "feature", "scenario", "step"},
}


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _published(items: Iterable[QuestionRecord | ExerciseRecord]) -> list[QuestionRecord | ExerciseRecord]:
    return [item for item in items if item.status == "published"]


def _generic(blob: str) -> bool:
    lowered = blob.lower()
    return any(marker in lowered for marker in GENERIC_FINGERPRINTS)


def scan_content_quality(root: Path) -> list[str]:
    """Return published-content editorial errors; drafts are intentionally ignored."""
    knowledge_root = root / "knowledge"
    questions = [q for q in load_all_questions(knowledge_root) if q.status == "published"]
    exercises = [e for e in load_all_exercises(knowledge_root) if e.status == "published"]
    errors: list[str] = []

    answers: dict[str, list[str]] = {}
    paragraphs: Counter[str] = Counter()
    for q in questions:
        blob = " ".join((q.question, q.concise_answer, q.recommended_answer, q.deep_dive))
        if _generic(blob):
            errors.append(f"{q.id}: generic template fingerprint")
        answer = _normalise(q.recommended_answer)
        if answer:
            answers.setdefault(answer, []).append(q.id)
        for paragraph in q.recommended_answer.split("\n\n"):
            normal = _normalise(paragraph)
            if len(normal) >= 80:
                paragraphs[normal] += 1
        errors.extend(_question_errors(q))
    for ids in answers.values():
        if len(ids) > 1:
            errors.append(f"duplicate answer fingerprint: {', '.join(sorted(ids))}")
    for paragraph, count in paragraphs.items():
        if count >= 3:
            errors.append(f"high repeated paragraph rate ({count}): {paragraph[:70]}")
    for ex in exercises:
        blob = " ".join((ex.task, ex.expected_reasoning, ex.reference_solution))
        if _generic(blob):
            errors.append(f"{ex.id}: generic template fingerprint")
        errors.extend(_exercise_errors(ex))
    return errors


def _question_errors(question: QuestionRecord) -> list[str]:
    errors: list[str] = []
    if question.priority in {"P0", "P1"} and question.review_status != "reviewed":
        errors.append(f"{question.id}: {question.priority} must be reviewed")
    if question.priority in {"P0", "P1"} and not any(
        item.question.strip() and item.recommended_answer.strip() for item in question.follow_ups
    ):
        errors.append(f"{question.id}: {question.priority} needs a follow-up with an answer")
    for ref in question.references:
        if _normalise(ref.locator) in VAGUE_LOCATORS:
            errors.append(f"{question.id}: vague source locator {ref.locator!r}")
    terms = DOMAIN_TERMS.get(question.domain)
    text = _normalise(" ".join((question.subdomain, question.title, question.question, " ".join(question.tags))))
    if terms and not any(term in text for term in terms):
        errors.append(f"{question.id}: domain/question/tag inconsistency")
    return errors


def _exercise_errors(exercise: ExerciseRecord) -> list[str]:
    errors: list[str] = []
    if exercise.priority in {"P0", "P1"} and exercise.review_status != "reviewed":
        errors.append(f"{exercise.id}: {exercise.priority} must be reviewed")
    for ref in exercise.references:
        if _normalise(ref.locator) in VAGUE_LOCATORS:
            errors.append(f"{exercise.id}: vague source locator {ref.locator!r}")
    projection = exercise.candidate_projection()
    hidden = {"reference_solution", "expected_reasoning", "scoring_rubric", "recommended_answer"}
    if hidden.intersection(projection):
        errors.append(f"{exercise.id}: candidate projection leakage")
    candidate_text = _normalise(" ".join(map(str, projection.values())))
    if "reference solution" in candidate_text or "recommended answer" in candidate_text:
        errors.append(f"{exercise.id}: candidate projection answer leakage")
    return errors
