"""Exercise library parsing, rotation and interviewer/candidate separation.

Selection avoids re-assigning the same primary exercise while unused active
alternatives exist, never assigns two exercises from the same variant family to
one candidate, and skips retired/draft exercises. Reference solutions and other
interviewer-only fields are carried on the model but must never be rendered into
candidate-facing output (see ``documents``/``interview`` generators).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from zume.models import ExerciseSelection, IndependenceQuestion


@dataclass
class Exercise:
    area: str
    area_label: str
    id: str
    title: str
    skill_area: str
    variant_family: str
    difficulty: str
    status: str
    rotation_group: str
    task: str
    requirement_change_follow_up: str
    debugging_follow_up: str
    expected_reasoning: str
    reference_solution: str
    requirement_change_recommended_answer: str = ""
    debugging_recommended_answer: str = ""
    scoring_rubric: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    independence_questions: list[IndependenceQuestion] = field(default_factory=list)

    @property
    def fingerprint(self) -> str:
        return fingerprint(self.task)

    def to_selection(self) -> ExerciseSelection:
        return ExerciseSelection(
            area=self.area,
            area_label=self.area_label,
            exercise_id=self.id,
            title=self.title,
            skill_area=self.skill_area,
            variant_family=self.variant_family,
            difficulty=self.difficulty,
            status=self.status,
            rotation_group=self.rotation_group,
            fingerprint=self.fingerprint,
            task=self.task,
            requirement_change_follow_up=self.requirement_change_follow_up,
            requirement_change_recommended_answer=self.requirement_change_recommended_answer,
            debugging_follow_up=self.debugging_follow_up,
            debugging_recommended_answer=self.debugging_recommended_answer,
            expected_reasoning=self.expected_reasoning,
            reference_solution=self.reference_solution,
            scoring_rubric=list(self.scoring_rubric),
            red_flags=list(self.red_flags),
            independence_questions=[q.model_copy() for q in self.independence_questions],
        )


def fingerprint(task_text: str) -> str:
    """Stable duplicate-detection fingerprint for an exercise task."""
    normalized = re.sub(r"\s+", " ", task_text or "").strip().lower()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _parse_independence_questions(raw: Any) -> list[IndependenceQuestion]:
    """Accept either legacy plain strings or objects with a recommended answer."""
    parsed: list[IndependenceQuestion] = []
    for item in raw or []:
        if isinstance(item, dict):
            parsed.append(IndependenceQuestion(
                question=_clean(item.get("question")),
                recommended_answer=_clean(item.get("recommended_answer")),
            ))
        else:
            parsed.append(IndependenceQuestion(question=_clean(item), recommended_answer=""))
    return parsed


def load_exercises(library: dict[str, Any]) -> dict[str, list[Exercise]]:
    """Parse the YAML library into Exercise objects keyed by area."""
    out: dict[str, list[Exercise]] = {}
    for area, spec in library.get("areas", {}).items():
        label = spec.get("label", area)
        items: list[Exercise] = []
        for ex in spec.get("exercises", []):
            items.append(Exercise(
                area=area,
                area_label=label,
                id=ex["id"],
                title=ex.get("title", ex["id"]),
                skill_area=ex.get("skill_area", area),
                variant_family=ex.get("variant_family", ex["id"]),
                difficulty=ex.get("difficulty", "medium"),
                status=ex.get("status", "active"),
                rotation_group=ex.get("rotation_group", area),
                task=_clean(ex.get("task")),
                requirement_change_follow_up=_clean(ex.get("requirement_change_follow_up")),
                requirement_change_recommended_answer=_clean(
                    ex.get("requirement_change_recommended_answer")),
                debugging_follow_up=_clean(ex.get("debugging_follow_up")),
                debugging_recommended_answer=_clean(ex.get("debugging_recommended_answer")),
                expected_reasoning=_clean(ex.get("expected_reasoning")),
                reference_solution=_clean(ex.get("reference_solution")),
                scoring_rubric=list(ex.get("scoring_rubric", [])),
                red_flags=list(ex.get("red_flags", [])),
                independence_questions=_parse_independence_questions(
                    ex.get("independence_questions")),
            ))
        out[area] = items
    return out


def validate_exercise_answers(exercises_by_area: dict[str, list[Exercise]]) -> list[str]:
    """Return contract violations: every active exercise must carry non-empty
    requirement-change and debugging recommended answers, and every independence
    question must have a non-empty recommended answer."""
    problems: list[str] = []
    for area_exercises in exercises_by_area.values():
        for ex in area_exercises:
            if ex.status != "active":
                continue
            if not ex.requirement_change_recommended_answer:
                problems.append(f"{ex.id}: missing requirement_change_recommended_answer")
            if not ex.debugging_recommended_answer:
                problems.append(f"{ex.id}: missing debugging_recommended_answer")
            if not ex.independence_questions:
                problems.append(f"{ex.id}: has no independence questions")
            for i, q in enumerate(ex.independence_questions):
                if not q.question:
                    problems.append(f"{ex.id}: independence question {i} has no text")
                if not q.recommended_answer:
                    problems.append(
                        f"{ex.id}: independence question {i} missing recommended_answer")
    return problems


class ExerciseSelector:
    """Rotation-aware selector.

    ``usage`` maps exercise id -> {"count": int, "last_used": iso-str}.
    ``candidate_history`` is the set of exercise ids already assigned to this
    candidate. Both may be empty for a stateless selection.
    """

    def __init__(self, exercises_by_area: dict[str, list[Exercise]],
                 usage: dict[str, dict[str, Any]] | None = None,
                 candidate_history: set[str] | None = None) -> None:
        self.exercises_by_area = exercises_by_area
        self.usage = usage or {}
        self.candidate_history = candidate_history or set()
        self._chosen_families: set[str] = set()
        self._chosen_ids: set[str] = set()

    def _rank_key(self, ex: Exercise) -> tuple[Any, ...]:
        record = self.usage.get(ex.id, {})
        return (
            ex.id in self.candidate_history,          # unseen by candidate first
            int(record.get("count", 0)),               # least used first
            str(record.get("last_used") or ""),        # least recently used first
            ex.id,                                       # stable tiebreak
        )

    def pick(self, area: str, count: int) -> list[Exercise]:
        pool = [e for e in self.exercises_by_area.get(area, []) if e.status == "active"]
        ranked = sorted(pool, key=self._rank_key)
        chosen: list[Exercise] = []
        for ex in ranked:
            if ex.variant_family in self._chosen_families:
                continue
            if ex.id in self._chosen_ids:
                continue
            chosen.append(ex)
            self._chosen_families.add(ex.variant_family)
            self._chosen_ids.add(ex.id)
            if len(chosen) >= count:
                break
        # If variant-family filtering starved the pick, relax it (still active-only).
        if len(chosen) < count:
            for ex in ranked:
                if ex.id in self._chosen_ids:
                    continue
                chosen.append(ex)
                self._chosen_ids.add(ex.id)
                if len(chosen) >= count:
                    break
        return chosen

    @property
    def selected_ids(self) -> list[str]:
        return list(self._chosen_ids)
