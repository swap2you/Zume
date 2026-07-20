"""Editorial quality gates for material that is eligible for interviews.

The publication gate detects:
- concept-substitution templates (same skeleton, substituted concept words);
- normalized repeated questions and answers;
- repeated signals, mistakes and follow-ups;
- metadata/question mismatch;
- invalid role mapping;
- weak or missing source locators; relative or empty source URLs;
- generic executable exercises and missing starter files/tests;
- stale P0/P1 content;
- unreviewed published content.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from zume.knowledge.enrich import freshness_state
from zume.knowledge.loader import (
    load_all_exercises,
    load_all_questions,
    load_sources,
    load_taxonomy,
)
from zume.knowledge.models import ExerciseRecord, QuestionRecord

GENERIC_FINGERPRINTS = (
    "should be applied to a stated outcome, observable evidence",
    "start by naming the decision that",
    "what evidence would make you revise your",
    "explain the purpose and failure boundary of",
    "should be chosen for its documented semantics",
)
VAGUE_LOCATORS = {"", "section", "chapter", "documentation", "docs", "guide", "website", "page"}
DOMAIN_TERMS = {
    "java": {"java", "collection", "exception", "stream", "thread", "hash", "jvm", "record", "memory", "heap", "concurren"},
    "selenium": {"selenium", "webdriver", "locator", "wait", "page", "browser", "grid", "bidi", "cdp", "click"},
    "rest-assured": {"rest", "http", "request", "response", "assured", "specification"},
    "sql-oracle": {"sql", "oracle", "query", "join", "table", "aggregate", "transaction", "isolation", "index", "window", "null", "date"},
    "api-openapi": {"api", "openapi", "schema", "operation", "contract", "http", "idempoten", "status", "retry", "rate limit", "error"},
    "testng": {"testng", "test", "suite", "listener", "data provider", "parallel", "lifecycle", "factory"},
    "cucumber": {"cucumber", "gherkin", "feature", "scenario", "step", "bdd", "hook"},
    "git-maven": {"git", "maven", "merge", "rebase", "surefire", "failsafe", "lifecycle", "branch", "pom"},
    "cicd": {"pipeline", "ci", "gate", "nightly", "release", "pull request", "quarantine", "selection", "jenkins", "github actions"},
    "framework-architecture": {"framework", "layer", "architecture", "parallel", "configuration", "design", "component", "adapter"},
    "debugging-reliability": {"flaky", "failure", "retry", "classification", "evidence", "root cause", "debug", "reliability"},
    "mobile-appium": {"appium", "mobile", "android", "ios", "device", "uiautomator", "xcuitest", "webview", "emulator"},
    "browserstack": {"browserstack", "device cloud", "tunnel", "cloud", "device"},
    "performance-observability": {"performance", "latency", "throughput", "percentile", "load", "soak", "spike", "bottleneck", "workload", "observability", "trace", "metric"},
    "postman-newman": {"postman", "newman", "collection", "variable", "environment"},
    "technical-leadership": {"stakeholder", "prioriti", "conflict", "team", "leader", "mentor", "decision", "roadmap"},
    "qa-strategy-governance": {"metric", "strategy", "roadmap", "governance", "quality", "coverage", "risk"},
    "solution-architecture": {"architecture", "decision", "trade-off", "framework", "platform", "migration", "criteria"},
    "behavioral": {"describe", "failure", "decision", "ownership", "you"},
    "llm-engineering": {"llm", "model", "prompt", "citation", "grounded", "structured", "json", "schema", "output", "retrieval"},
    "agentic-ai": {"agent", "tool", "workflow", "memory", "state", "mcp", "permission", "eval"},
    "ai-quality": {"llm", "ai", "nondetermin", "prompt", "injection", "eval", "classifier", "triage", "dataset", "generated"},
    "ai-governance": {"privacy", "governance", "provider", "policy", "roi", "cost", "pilot", "data", "ai"},
}
TEMPLATE_CLUSTER_THRESHOLD = 3
REPEATED_FRAGMENT_THRESHOLD = 4
RUNNER_TYPES = {"sql", "api", "java", "selenium"}


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _published(items: Iterable[QuestionRecord | ExerciseRecord]) -> list[QuestionRecord | ExerciseRecord]:
    return [item for item in items if item.status == "published"]


def _generic(blob: str) -> bool:
    lowered = blob.lower()
    return any(marker in lowered for marker in GENERIC_FINGERPRINTS)


def _skeleton(question: QuestionRecord) -> str:
    """Question text with record-specific concept words masked out.

    Concept-substitution templates collapse to identical skeletons.
    """
    concept_tokens = set()
    for source in (question.domain, question.subdomain, question.title):
        concept_tokens.update(_normalise(source).split())
    words = _normalise(question.question).split()
    masked = ["◊" if w in concept_tokens else w for w in words]
    return " ".join(masked)


def scan_content_quality(root: Path) -> list[str]:
    """Return published-content editorial errors; drafts are intentionally ignored."""
    knowledge_root = root / "knowledge"
    questions = [q for q in load_all_questions(knowledge_root) if q.status == "published"]
    exercises = [e for e in load_all_exercises(knowledge_root) if e.status == "published"]
    sources = load_sources(knowledge_root)
    taxonomy = load_taxonomy(knowledge_root)
    valid_roles = {str(r) for r in (taxonomy.get("role_tracks") or [])}
    errors: list[str] = []

    answers: dict[str, list[str]] = {}
    question_texts: dict[str, list[str]] = {}
    skeletons: dict[str, list[str]] = defaultdict(list)
    fragments: Counter[str] = Counter()
    fragment_ids: dict[str, set[str]] = defaultdict(set)
    paragraphs: Counter[str] = Counter()

    for q in questions:
        blob = " ".join((q.question, q.concise_answer, q.recommended_answer, q.deep_dive))
        if _generic(blob):
            errors.append(f"{q.id}: generic template fingerprint")
        answer = _normalise(q.recommended_answer)
        if answer:
            answers.setdefault(answer, []).append(q.id)
        text = _normalise(q.question)
        if text:
            question_texts.setdefault(text, []).append(q.id)
        skeletons[_skeleton(q)].append(q.id)
        for fragment in (*q.strong_signals, *q.weak_signals, *q.red_flags,
                         *q.common_mistakes, *(f.question for f in q.follow_ups)):
            normal = _normalise(fragment)
            if len(normal) >= 25:
                fragments[normal] += 1
                fragment_ids[normal].add(q.id)
        for paragraph in q.recommended_answer.split("\n\n"):
            normal = _normalise(paragraph)
            if len(normal) >= 80:
                paragraphs[normal] += 1
        errors.extend(_question_errors(q, sources, valid_roles))

    for ids in answers.values():
        if len(ids) > 1:
            errors.append(f"duplicate answer fingerprint: {', '.join(sorted(ids))}")
    for ids in question_texts.values():
        if len(ids) > 1:
            errors.append(f"duplicate question fingerprint: {', '.join(sorted(ids))}")
    for skeleton, ids in skeletons.items():
        if len(ids) >= TEMPLATE_CLUSTER_THRESHOLD and skeleton.count("◊") >= 1:
            errors.append(
                f"concept-substitution template cluster ({len(ids)}): {', '.join(sorted(ids)[:6])}…"
            )
    for normal, count in fragments.items():
        if count >= REPEATED_FRAGMENT_THRESHOLD and len(fragment_ids[normal]) >= REPEATED_FRAGMENT_THRESHOLD:
            errors.append(
                f"repeated signal/mistake/follow-up across {count} records: {normal[:60]}"
            )
    for paragraph, count in paragraphs.items():
        if count >= 3:
            errors.append(f"high repeated paragraph rate ({count}): {paragraph[:70]}")

    for ex in exercises:
        blob = " ".join((ex.task, ex.expected_reasoning, ex.reference_solution))
        if _generic(blob):
            errors.append(f"{ex.id}: generic template fingerprint")
        errors.extend(_exercise_errors(ex, sources, valid_roles))
    return errors


def _reference_errors(
    record: QuestionRecord | ExerciseRecord,
    sources: dict[str, dict],
) -> list[str]:
    errors: list[str] = []
    if not record.references:
        errors.append(f"{record.id}: published record has no source references")
    for ref in record.references:
        if _normalise(ref.locator) in VAGUE_LOCATORS or len(ref.locator.strip()) < 6:
            errors.append(f"{record.id}: weak source locator {ref.locator!r}")
        source = sources.get(ref.source_id)
        if source is None:
            errors.append(f"{record.id}: unresolvable source_id {ref.source_id!r}")
            continue
        url = str(source.get("url") or "")
        if not url.startswith("https://"):
            errors.append(f"{record.id}: source {ref.source_id} URL is not absolute https ({url!r})")
    return errors


def _question_errors(
    question: QuestionRecord, sources: dict[str, dict], valid_roles: set[str],
) -> list[str]:
    errors: list[str] = []
    if question.review_status != "reviewed":
        errors.append(f"{question.id}: published content must be reviewed")
    if question.priority in {"P0", "P1"} and not any(
        item.question.strip() and item.recommended_answer.strip() for item in question.follow_ups
    ):
        errors.append(f"{question.id}: {question.priority} needs a follow-up with an answer")
    if question.priority in {"P0", "P1"} and freshness_state(question) == "stale":
        errors.append(f"{question.id}: stale {question.priority} content (verify or retire)")
    errors.extend(_reference_errors(question, sources))
    if valid_roles:
        invalid = [r for r in question.role_tracks if r not in valid_roles]
        if invalid:
            errors.append(f"{question.id}: invalid role mapping {invalid}")
    terms = DOMAIN_TERMS.get(question.domain)
    text = _normalise(" ".join((
        question.subdomain, question.title, question.question,
        question.concise_answer, " ".join(question.tags),
    )))
    if terms and not any(_normalise(term) in text for term in terms):
        errors.append(f"{question.id}: domain/question/tag inconsistency")
    return errors


def _exercise_errors(
    exercise: ExerciseRecord, sources: dict[str, dict], valid_roles: set[str],
) -> list[str]:
    errors: list[str] = []
    if exercise.review_status != "reviewed":
        errors.append(f"{exercise.id}: published content must be reviewed")
    if exercise.priority in {"P0", "P1"} and freshness_state(exercise) == "stale":
        errors.append(f"{exercise.id}: stale {exercise.priority} exercise")
    errors.extend(_reference_errors(exercise, sources))
    if valid_roles:
        invalid = [r for r in exercise.role_tracks if r not in valid_roles]
        if invalid:
            errors.append(f"{exercise.id}: invalid role mapping {invalid}")
    if exercise.runner_type in RUNNER_TYPES:
        if not exercise.starter_files:
            errors.append(f"{exercise.id}: executable exercise missing starter files")
        if not exercise.test_cases:
            errors.append(f"{exercise.id}: executable exercise missing test cases")
    projection = exercise.candidate_projection()
    hidden = {"reference_solution", "expected_reasoning", "scoring_rubric", "recommended_answer"}
    if hidden.intersection(projection):
        errors.append(f"{exercise.id}: candidate projection leakage")
    candidate_text = _normalise(" ".join(map(str, projection.values())))
    if "reference solution" in candidate_text or "recommended answer" in candidate_text:
        errors.append(f"{exercise.id}: candidate projection answer leakage")
    return errors
