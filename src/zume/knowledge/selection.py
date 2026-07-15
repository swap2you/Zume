"""Candidate-specific interview selection from the expanded knowledge library."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from zume.knowledge.models import ExerciseRecord, QuestionRecord

# Domains preferred for the Senior SDET knockout / mandatory core.
MANDATORY_DOMAINS = (
    "java",
    "selenium",
    "rest-assured",
    "sql-oracle",
    "api-openapi",
    "debugging-reliability",
)


def select_interview_plan(
    questions: list[QuestionRecord],
    exercises: list[ExerciseRecord],
    *,
    resume_text: str = "",
    role_track: str = "Senior SDET",
    previous_question_ids: list[str] | None = None,
    previous_exercise_ids: list[str] | None = None,
    rotate: bool = False,
) -> dict[str, Any]:
    """Select a compact 180-minute plan. Does not dump the library into documents."""
    published_q = [q for q in questions if q.status == "published"]
    published_e = [e for e in exercises if e.status == "published"]
    if previous_question_ids and not rotate:
        by_id = {q.id: q for q in published_q}
        kept = [by_id[i] for i in previous_question_ids if i in by_id]
        if kept:
            ex_by = {e.id: e for e in published_e}
            kept_ex = [ex_by[i] for i in (previous_exercise_ids or []) if i in ex_by]
            return _plan_from(kept, kept_ex, role_track, preserved=True)

    tags = _resume_tags(resume_text)
    scored = sorted(
        published_q,
        key=lambda q: (
            0 if q.priority == "P0" else 1 if q.priority == "P1" else 2 if q.priority == "P2" else 3,
            0 if q.domain in MANDATORY_DOMAINS else 1,
            0 if _domain_matches_resume(q.domain, tags) else 1,
            0 if role_track in q.role_tracks else 1,
            q.id,
        ),
    )

    knockout: list[QuestionRecord] = []
    for q in scored:
        if q.priority != "P0":
            continue
        if q.domain in MANDATORY_DOMAINS or _domain_matches_resume(q.domain, tags):
            knockout.append(q)
        if len(knockout) >= 6:
            break

    by_domain_level: dict[str, dict[str, list[QuestionRecord]]] = defaultdict(lambda: defaultdict(list))
    for q in scored:
        if q in knockout:
            continue
        if len(by_domain_level[q.domain][q.level]) < 2:
            by_domain_level[q.domain][q.level].append(q)

    selected: list[QuestionRecord] = list(knockout)
    preferred_domains = [d for d in MANDATORY_DOMAINS if d in by_domain_level] + [
        d for d in by_domain_level if d not in MANDATORY_DOMAINS
    ]
    for domain in preferred_domains[:8]:
        for level in ("basic", "intermediate", "advanced"):
            selected.extend(by_domain_level[domain].get(level, [])[:1])
        if len(selected) >= 28:
            break
    selected = selected[:28]

    # Exercises: prefer previous or choose one per mandatory area.
    selected_ex: list[ExerciseRecord] = []
    if previous_exercise_ids and not rotate:
        ex_by = {e.id: e for e in published_e}
        selected_ex = [ex_by[i] for i in previous_exercise_ids if i in ex_by]
    if not selected_ex:
        used_domains: set[str] = set()
        for domain in preferred_domains:
            for ex in sorted(published_e, key=lambda e: (e.priority, e.id)):
                if ex.domain == domain and domain not in used_domains:
                    selected_ex.append(ex)
                    used_domains.add(domain)
                    break
            if len(selected_ex) >= 4:
                break

    return _plan_from(selected, selected_ex, role_track, preserved=False)


def _plan_from(
    questions: list[QuestionRecord],
    exercises: list[ExerciseRecord],
    role_track: str,
    *,
    preserved: bool,
) -> dict[str, Any]:
    return {
        "role_track": role_track,
        "preserved_prior_selection": preserved,
        "knockout_question_ids": [q.id for q in questions if q.priority == "P0"][:6],
        "question_ids": [q.id for q in questions],
        "exercise_ids": [e.id for e in exercises],
        "why": [
            {
                "id": q.id,
                "reason": (
                    f"{q.priority} {q.level} {q.domain}"
                    + ("; resume-aligned" if q.domain in MANDATORY_DOMAINS else "")
                ),
            }
            for q in questions
        ],
        "agenda_fit_minutes": 180,
        "knockout_minutes": 20,
        "questions": [q.model_dump() for q in questions],
        "exercises": [e.model_dump() for e in exercises],
        "candidate_exercises": [e.candidate_projection() for e in exercises],
    }


def _resume_tags(text: str) -> set[str]:
    text = text.lower()
    tags = set()
    mapping = {
        "java": ["java"],
        "selenium": ["selenium", "webdriver"],
        "rest-assured": ["rest assured", "rest-assured"],
        "sql-oracle": ["oracle", "sql", "pl/sql"],
        "api-openapi": ["api", "openapi", "rest"],
        "appium": ["appium", "mobile"],
        "performance": ["jmeter", "gatling", "k6", "performance"],
        "llm-generative": ["llm", "openai", "rag", "generative"],
        "agentic-ai": ["agent", "mcp", "tool calling"],
        "cucumber": ["cucumber", "gherkin", "bdd"],
        "testng": ["testng"],
        "cicd": ["jenkins", "github actions", "ci/cd", "pipeline"],
    }
    for domain, needles in mapping.items():
        if any(n in text for n in needles):
            tags.add(domain)
    return tags


def _domain_matches_resume(domain: str, tags: set[str]) -> bool:
    if domain in tags:
        return True
    # soft match hyphens
    return any(re.sub(r"[^a-z]", "", domain) == re.sub(r"[^a-z]", "", t) for t in tags)
