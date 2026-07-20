"""Interview selection engine tests across synthetic profiles."""

from __future__ import annotations

from pathlib import Path

from zume.knowledge.loader import load_all_exercises, load_all_questions
from zume.knowledge.selection import select_interview_plan


PROFILES = {
    "strong": "Senior SDET Java Selenium REST Assured Oracle SQL TestNG Cucumber CI",
    "conditional": "Java developer, some Selenium",
    "weak": "Manual tester excel",
    "mobile": "Appium Android iOS mobile automation",
    "performance": "JMeter Gatling k6 performance engineer",
    "ai": "LLM RAG agents MCP evaluation AI QA",
    "architect": "Test automation architect framework design system design",
    "leadership": "Engineering manager mentoring stakeholder conflict roadmap",
}


def test_selection_profiles_are_sensible(repo_root: Path):
    questions = load_all_questions(repo_root / "knowledge")
    exercises = load_all_exercises(repo_root / "knowledge")
    for name, resume in PROFILES.items():
        plan = select_interview_plan(questions, exercises, resume_text=resume, role_track="Senior SDET")
        assert plan["question_ids"], name
        assert plan["knockout_question_ids"], name
        assert plan["agenda_fit_minutes"] == 180
        assert len(plan["question_ids"]) <= 28
        assert all(
            item["reason"].split(":", 1)[0] in {
                "mandatory-core", "resume-claimed", "missing-evidence",
                "risk-validation", "role-aligned", "specialty-depth", "rotation",
            }
            for item in plan["why"]
        ), name
        # Every selected question includes answer content for interviewer guide.
        for q in plan["questions"]:
            assert q["recommended_answer"].strip(), q["id"]


def test_selection_preserves_ids_without_rotation(repo_root: Path):
    questions = load_all_questions(repo_root / "knowledge")
    exercises = load_all_exercises(repo_root / "knowledge")
    first = select_interview_plan(questions, exercises, resume_text=PROFILES["strong"])
    second = select_interview_plan(
        questions,
        exercises,
        resume_text=PROFILES["strong"],
        previous_question_ids=first["question_ids"],
        previous_exercise_ids=first["exercise_ids"],
        rotate=False,
    )
    assert second["preserved_prior_selection"] is True
    assert second["question_ids"] == first["question_ids"]
    assert second["exercise_ids"] == first["exercise_ids"]
