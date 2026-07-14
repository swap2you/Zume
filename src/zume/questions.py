"""Interview question library: loading, depth validation and agenda selection.

Interviewer-only content. Every question and follow-up carries a recommended
answer; :func:`validate_library` enforces the depth contract used by tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

LEVELS = ("basic", "intermediate", "advanced")

# Minimum question depth per area, keyed by whether the area is a core area.
CORE_MIN = {"basic": 3, "intermediate": 3, "advanced": 3}
OPTIONAL_MIN = {"basic": 2, "intermediate": 2, "advanced": 2}


@dataclass(frozen=True)
class FollowUp:
    question: str
    recommended_answer: str


@dataclass(frozen=True)
class Question:
    id: str
    area: str
    level: str
    question: str
    recommended_answer: str
    key_points: list[str] = field(default_factory=list)
    strong_signals: list[str] = field(default_factory=list)
    weak_signals: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    follow_ups: list[FollowUp] = field(default_factory=list)
    score_guidance: str = ""
    resume_tags: list[str] = field(default_factory=list)
    time_minutes: int = 5


@dataclass(frozen=True)
class Area:
    key: str
    label: str
    core: bool
    questions: list[Question]

    def by_level(self, level: str) -> list[Question]:
        return [q for q in self.questions if q.level == level]


def _as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value]


def _parse_question(raw: dict[str, Any], area_key: str) -> Question:
    follow_ups = [
        FollowUp(question=str(f.get("question", "")).strip(),
                 recommended_answer=str(f.get("recommended_answer", "")).strip())
        for f in (raw.get("follow_ups") or [])
    ]
    return Question(
        id=str(raw.get("id", "")),
        area=str(raw.get("area", area_key)),
        level=str(raw.get("level", "")).strip().lower(),
        question=str(raw.get("question", "")).strip(),
        recommended_answer=str(raw.get("recommended_answer", "")).strip(),
        key_points=_as_list(raw.get("key_points")),
        strong_signals=_as_list(raw.get("strong_signals")),
        weak_signals=_as_list(raw.get("weak_signals")),
        red_flags=_as_list(raw.get("red_flags")),
        follow_ups=follow_ups,
        score_guidance=str(raw.get("score_guidance", "")).strip(),
        resume_tags=[t.lower() for t in _as_list(raw.get("resume_tags"))],
        time_minutes=int(raw.get("time_minutes", 5) or 5),
    )


def load_library(cfg: dict[str, Any]) -> dict[str, Area]:
    """Parse the raw YAML mapping into ordered Area objects."""
    areas: dict[str, Area] = {}
    for key, raw_area in (cfg.get("areas") or {}).items():
        questions = [_parse_question(q, key) for q in (raw_area.get("questions") or [])]
        areas[key] = Area(
            key=key,
            label=str(raw_area.get("label", key)),
            core=bool(raw_area.get("core", False)),
            questions=questions,
        )
    return areas


def validate_library(areas: dict[str, Area]) -> list[str]:
    """Return a list of contract violations; empty means the library is valid."""
    problems: list[str] = []
    seen_ids: set[str] = set()
    for area in areas.values():
        minimums = CORE_MIN if area.core else OPTIONAL_MIN
        for level, need in minimums.items():
            have = len(area.by_level(level))
            if have < need:
                problems.append(
                    f"{area.key}: needs >= {need} {level} questions, has {have}")
        for q in area.questions:
            if q.id in seen_ids:
                problems.append(f"duplicate question id: {q.id}")
            seen_ids.add(q.id)
            if q.level not in LEVELS:
                problems.append(f"{q.id}: invalid level {q.level!r}")
            if not q.question:
                problems.append(f"{q.id}: empty question text")
            if not q.recommended_answer:
                problems.append(f"{q.id}: missing recommended_answer")
            for i, follow in enumerate(q.follow_ups):
                if not follow.recommended_answer:
                    problems.append(f"{q.id}: follow-up {i} missing recommended_answer")
    return problems


def _tag_score(question: Question, resume_tags: set[str]) -> int:
    return len(set(question.resume_tags) & resume_tags)


def select_for_area(area: Area, resume_tags: set[str]) -> tuple[list[Question], list[Question]]:
    """Pick one question per level for the guide; return (selected, reserve).

    Selection prefers questions whose resume_tags overlap the candidate's tags
    (to target claimed skills) while keeping one basic/intermediate/advanced.
    """
    selected: list[Question] = []
    for level in LEVELS:
        candidates = area.by_level(level)
        if not candidates:
            continue
        best = max(candidates, key=lambda q: (_tag_score(q, resume_tags), -len(selected)))
        selected.append(best)
    chosen_ids = {q.id for q in selected}
    reserve = [q for q in area.questions if q.id not in chosen_ids]
    return selected, reserve
