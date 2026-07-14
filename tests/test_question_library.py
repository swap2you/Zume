"""Phase 5 — interview question library depth and answer-completeness contract."""

from __future__ import annotations

from zume import config as cfg
from zume import questions as q


def _load(repo_root):
    return q.load_library(cfg.load_question_library(repo_root))


def test_library_loads_and_is_valid(repo_root):
    areas = _load(repo_root)
    assert areas, "question library must define areas"
    problems = q.validate_library(areas)
    assert not problems, "library contract violations:\n" + "\n".join(problems)


def test_core_areas_have_full_depth(repo_root):
    areas = _load(repo_root)
    required_core = {"java", "selenium", "rest_assured", "sql_oracle",
                     "framework_design", "debugging"}
    present_core = {k for k, a in areas.items() if a.core}
    assert required_core <= present_core, f"missing core areas: {required_core - present_core}"
    for key in required_core:
        area = areas[key]
        for level in ("basic", "intermediate", "advanced"):
            assert len(area.by_level(level)) >= 3, f"{key} needs >=3 {level} questions"


def test_every_question_and_follow_up_has_recommended_answer(repo_root):
    areas = _load(repo_root)
    for area in areas.values():
        for question in area.questions:
            assert question.recommended_answer, f"{question.id} missing recommended answer"
            for follow in question.follow_ups:
                assert follow.recommended_answer, f"{question.id} follow-up missing answer"


def test_selection_returns_one_question_per_level(repo_root):
    areas = _load(repo_root)
    selected, reserve = q.select_for_area(areas["java"], {"java", "streams"})
    levels = {question.level for question in selected}
    assert levels == {"basic", "intermediate", "advanced"}
    assert all(r.id not in {s.id for s in selected} for r in reserve)
