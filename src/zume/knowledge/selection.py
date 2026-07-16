"""Candidate-specific, reviewed-only interview selection."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from zume.knowledge.models import ExerciseRecord, QuestionRecord

MANDATORY_DOMAINS = (
    "java", "selenium", "rest-assured", "sql-oracle", "api-openapi",
    "debugging-reliability",
)

# Resume vocabulary always resolves to taxonomy identifiers, never historic aliases.
DOMAIN_ALIASES: dict[str, tuple[str, ...]] = {
    "mobile-appium": ("appium", "mobile", "android", "ios"),
    "performance-observability": ("jmeter", "gatling", "k6", "performance", "apm"),
    "llm-engineering": ("llm", "openai", "rag", "generative"),
    "agentic-ai": ("agent", "agents", "mcp", "tool calling"),
    "postman-newman": ("postman", "newman"),
    "rest-assured": ("rest assured", "rest-assured"),
    "selenium": ("selenium", "webdriver"),
    "java": ("java",),
    "sql-oracle": ("oracle", "sql", "plsql", "pl/sql"),
    "testng": ("testng",),
    "cucumber-gherkin-bdd": ("cucumber", "gherkin", "bdd"),
    "cicd": ("jenkins", "github actions", "ci/cd", "continuous integration"),
    "api-openapi": ("openapi", "rest api", "api testing"),
    "debugging-reliability": ("debugging", "flaky", "reliability"),
    "framework-design": ("architect", "architecture", "framework design"),
    "leadership": ("engineering manager", "mentoring", "stakeholder", "roadmap"),
}
_DOMAIN_NORMALIZATION = {
    "appium": "mobile-appium",
    "mobile": "mobile-appium",
    "performance": "performance-observability",
    "llm-generative": "llm-engineering",
    "rest_assured": "rest-assured",
    "sql_oracle": "sql-oracle",
    "cucumber": "cucumber-gherkin-bdd",
}


def select_interview_plan(
    questions: list[QuestionRecord],
    exercises: list[ExerciseRecord],
    *,
    resume_text: str = "",
    role_track: str = "Senior SDET",
    previous_question_ids: list[str] | None = None,
    previous_exercise_ids: list[str] | None = None,
    rotate: bool = False,
    config_root: Path | None = None,
) -> dict[str, Any]:
    """Select a compact plan from reviewed records, with curated fallback only."""
    reviewed_q = [q for q in questions if _is_reviewed(q)]
    reviewed_e = [e for e in exercises if _is_reviewed(e)]
    if _insufficient_core(reviewed_q):
        reviewed_q, reviewed_e = _load_curated_library(config_root or Path.cwd())

    by_id = {q.id: q for q in reviewed_q}
    ex_by_id = {e.id: e for e in reviewed_e}
    tags = _resume_tags(resume_text)
    if previous_question_ids and not rotate:
        kept = [by_id[item_id] for item_id in previous_question_ids if item_id in by_id]
        if kept:
            kept_ex = [ex_by_id[item_id] for item_id in (previous_exercise_ids or []) if item_id in ex_by_id]
            return _plan_from(kept, kept_ex, role_track, tags, preserved=True)

    scored = sorted(
        reviewed_q,
        key=lambda q: (
            0 if _canonical_domain(q.domain) in MANDATORY_DOMAINS else 1,
            0 if _domain_matches_resume(q.domain, tags) else 1,
            0 if role_track in q.role_tracks else 1,
            {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(q.priority, 4),
            q.id,
        ),
    )
    knockout = [q for q in scored if q.priority == "P0" and (
        _canonical_domain(q.domain) in MANDATORY_DOMAINS or _domain_matches_resume(q.domain, tags)
    )][:6]
    if not knockout:
        knockout = [q for q in scored if _canonical_domain(q.domain) in MANDATORY_DOMAINS][:6]
    selected = list(knockout)
    selected_ids = {q.id for q in selected}
    by_domain: dict[str, list[QuestionRecord]] = defaultdict(list)
    for question in scored:
        if question.id not in selected_ids:
            by_domain[_canonical_domain(question.domain)].append(question)
    preferred = list(dict.fromkeys(
        [domain for domain in MANDATORY_DOMAINS if domain in by_domain]
        + sorted(tags) + list(by_domain)
    ))
    for domain in preferred:
        for level in ("basic", "intermediate", "advanced"):
            match = next((q for q in by_domain.get(domain, []) if q.level == level), None)
            if match and match.id not in selected_ids:
                selected.append(match)
                selected_ids.add(match.id)
            if len(selected) >= 28:
                break
        if len(selected) >= 28:
            break
    selected = selected[:28]
    selected_ex: list[ExerciseRecord] = []
    for domain in preferred:
        exercise = next((e for e in reviewed_e if _canonical_domain(e.domain) == domain), None)
        if exercise is not None:
            selected_ex.append(exercise)
        if len(selected_ex) >= 4:
            break
    return _plan_from(selected, selected_ex, role_track, tags, preserved=False)


def _is_reviewed(record: QuestionRecord | ExerciseRecord) -> bool:
    return record.status == "published" and getattr(record, "review_status", None) == "reviewed"


def _insufficient_core(questions: list[QuestionRecord]) -> bool:
    return not set(MANDATORY_DOMAINS).issubset({_canonical_domain(q.domain) for q in questions})


def _plan_from(questions: list[QuestionRecord], exercises: list[ExerciseRecord],
               role_track: str, tags: set[str], *, preserved: bool) -> dict[str, Any]:
    return {
        "role_track": role_track,
        "preserved_prior_selection": preserved,
        "knockout_question_ids": [q.id for q in questions[:6]],
        "question_ids": [q.id for q in questions],
        "exercise_ids": [e.id for e in exercises],
        "why": [{"id": q.id, "reason": _reason_for(q, tags, role_track, preserved)} for q in questions],
        "agenda_fit_minutes": 180,
        "knockout_minutes": 20,
        "questions": [q.model_dump() for q in questions],
        "exercises": [e.model_dump() for e in exercises],
        "candidate_exercises": [e.candidate_projection() for e in exercises],
    }


def _reason_for(question: QuestionRecord, tags: set[str], role_track: str, preserved: bool) -> str:
    domain = _canonical_domain(question.domain)
    if preserved:
        return f"rotation: preserved prior reviewed selection for {domain}"
    if domain in tags:
        return f"resume-claimed: resume evidence maps to {domain}"
    if domain in MANDATORY_DOMAINS:
        return f"mandatory-core: required {domain} validation"
    if role_track in question.role_tracks:
        return f"role-aligned: {role_track} coverage in {domain}"
    return f"missing-evidence: validate unclaimed {domain} capability"


def _resume_tags(text: str) -> set[str]:
    normalized = text.lower()
    return {domain for domain, aliases in DOMAIN_ALIASES.items()
            if any(alias in normalized for alias in aliases)}


def _canonical_domain(domain: str) -> str:
    normalized = domain.lower().replace(" ", "-").replace("_", "-")
    return _DOMAIN_NORMALIZATION.get(normalized, normalized)


def _domain_matches_resume(domain: str, tags: set[str]) -> bool:
    return _canonical_domain(domain) in tags


def _load_curated_library(root: Path) -> tuple[list[QuestionRecord], list[ExerciseRecord]]:
    """Load the reviewed, versioned configuration library; never use drafts."""
    config_dir = root / "config"
    try:
        question_data = yaml.safe_load((config_dir / "interview-question-library.yaml").read_text(encoding="utf-8")) or {}
        exercise_data = yaml.safe_load((config_dir / "exercise-library.yaml").read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return [], []
    questions: list[QuestionRecord] = []
    for area, section in (question_data.get("areas") or {}).items():
        for raw in (section.get("questions") or []):
            if raw.get("status", "active") != "active":
                continue
            questions.append(QuestionRecord.model_validate({
                **raw, "domain": _canonical_domain(str(raw.get("area") or area)),
                "title": raw.get("title") or raw["id"], "subdomain": "",
                "priority": raw.get("priority", "P0" if section.get("core") else "P1"), "frequency": "common",
                "concise_answer": raw.get("recommended_answer", ""), "last_verified": "2026-07-16",
                "status": "published", "review_status": "reviewed",
            }))
    exercises: list[ExerciseRecord] = []
    for area, section in (exercise_data.get("areas") or {}).items():
        for raw in (section.get("exercises") or []):
            if raw.get("status") != "active":
                continue
            exercises.append(ExerciseRecord.model_validate({
                **raw, "domain": _canonical_domain(str(raw.get("skill_area") or area)),
                "level": {"easy": "basic", "medium": "intermediate", "hard": "advanced"}.get(raw.get("difficulty"), "intermediate"),
                "priority": raw.get("priority", "P1"), "status": "published", "review_status": "reviewed",
                "role_tracks": raw.get("role_tracks", []), "tags": raw.get("resume_tags", []),
            }))
    return questions, exercises
