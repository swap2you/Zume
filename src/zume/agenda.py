"""Canonical 180-minute interview operating model (Phase 4).

Defines the exact agenda, the 20-minute knockout round, and the decision rule.
:func:`validate_agenda` guarantees the timeline totals 180 minutes and the
knockout is exactly 20 minutes; tests assert on these invariants.
"""

from __future__ import annotations

from zume.models import AgendaSegment, KnockoutItem
from zume.questions import Area

STANDARD_MINUTES = 180
KNOCKOUT_MINUTES = 20

# (minutes, title, focus). Order is fixed; the final 5-minute close is fixed.
_PLAN: list[tuple[int, str, str]] = [
    (20, "Knockout round", "Resume authenticity and mandatory fundamentals gate"),
    (20, "Resume validation and framework ownership", "Claimed work, ownership, depth"),
    (30, "Java fundamentals and live coding", "Collections, OOP, independent implementation"),
    (30, "Selenium + TestNG + Cucumber", "Locators, waits, parallelism, BDD"),
    (25, "REST Assured / API automation", "Chaining, assertions, contracts"),
    (20, "SQL / Oracle", "Joins, aggregation, latest-record queries"),
    (20, "Framework design + CI/CD + debugging", "Architecture, pipelines, diagnosis"),
    (10, "Optional / candidate-specific area", "Mobile, performance, or highest-risk area"),
    (5, "Candidate questions and close", "Close and next steps"),
]

KNOCKOUT_DECISION_RULE = [
    "Continue normally when mandatory fundamentals and resume ownership are credible.",
    "Continue conditionally when one area is weak but the candidate reasons independently.",
    "Knockout FAIL when two or more mandatory areas are materially weak, the candidate "
    "cannot explain claimed work, or cannot reason through a basic modification.",
    "Record observable evidence only. Never accuse the candidate of cheating.",
]

# Areas probed in the knockout, in order. framework_design falls back to debugging.
_KNOCKOUT_AREAS = ["java", "selenium", "rest_assured", "sql_oracle", "framework_design"]


def _minutes_to_clock(total: int) -> str:
    return f"{total // 60}:{total % 60:02d}"


def build_agenda() -> list[AgendaSegment]:
    segments: list[AgendaSegment] = []
    cursor = 0
    for minutes, title, focus in _PLAN:
        start = _minutes_to_clock(cursor)
        cursor += minutes
        end = _minutes_to_clock(cursor)
        segments.append(AgendaSegment(start=start, end=end, minutes=minutes,
                                      title=title, focus=focus))
    return segments


def build_knockout(areas: dict[str, Area]) -> list[KnockoutItem]:
    """Assemble the 20-minute knockout from a resume-ownership check plus one
    basic question per mandatory area (each carries a recommended answer)."""
    items: list[KnockoutItem] = [
        KnockoutItem(
            area_label="Resume authenticity and ownership",
            question="Walk me through a project on your resume you personally owned: "
                     "what did YOU build, what decisions did you make, and what broke?",
            recommended_answer="Specific, first-person ownership: concrete decisions, "
                               "trade-offs, and failures they personally resolved, "
                               "consistent with the resume dates and scope.",
            strong_indicator="Detailed first-person decisions and honest failure stories.",
            weak_indicator="Vague 'we' answers, cannot explain decisions or specifics.",
        ),
    ]
    for area_key in _KNOCKOUT_AREAS:
        area = areas.get(area_key)
        if area is None and area_key == "framework_design":
            area = areas.get("debugging")
        if area is None:
            continue
        basics = area.by_level("basic")
        if not basics:
            continue
        q = basics[0]
        items.append(KnockoutItem(
            area_label=area.label,
            question=q.question,
            recommended_answer=q.recommended_answer,
            strong_indicator="; ".join(q.strong_signals) or "Clear, correct reasoning.",
            weak_indicator="; ".join(q.weak_signals) or "Cannot explain fundamentals.",
        ))
    return items


def validate_agenda(segments: list[AgendaSegment], knockout_minutes: int) -> list[str]:
    """Return contract violations; empty means the model is valid."""
    problems: list[str] = []
    total = sum(s.minutes for s in segments)
    if total != STANDARD_MINUTES:
        problems.append(f"agenda totals {total} minutes, expected {STANDARD_MINUTES}")
    if knockout_minutes != KNOCKOUT_MINUTES:
        problems.append(f"knockout is {knockout_minutes} minutes, expected {KNOCKOUT_MINUTES}")
    if segments and segments[0].minutes != KNOCKOUT_MINUTES:
        problems.append("first segment must be the 20-minute knockout round")
    if segments and segments[-1].minutes != 5:
        problems.append("final close must be a fixed 5-minute segment")
    return problems
