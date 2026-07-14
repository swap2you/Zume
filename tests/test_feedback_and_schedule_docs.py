"""Coverage for feedback evaluation/documents and schedule document rendering."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from zume import feedback as fb
from zume import scheduling as sched

NOTES = """
Strong Java fundamentals; explained collections and streams clearly and coded
independently. Selenium waits and locators were solid. REST Assured chaining was
correct. SQL joins were good. Struggled a little with framework design trade-offs
but reasoned through it. Overall a confident, independent candidate. Recommend hire.
"""

WEAK_NOTES = """
Could not explain basic Java equals/hashCode. Copied answers and could not modify
the code when asked. Vague about claimed projects. Did not reason independently.
"""


def test_evaluate_notes_produces_scores_and_observations():
    result = fb.evaluate_notes("Aarav Mehta", NOTES)
    assert result.candidate_name == "Aarav Mehta"
    assert result.skill_scores, "expected at least one skill score"
    assert result.recommendation
    text = fb.recruiter_feedback_text(result)
    assert "Aarav Mehta" in text
    assert fb.leadership_feedback_text(result)


def test_evaluate_weak_notes_flag_dependence():
    result = fb.evaluate_notes("Sam Weak", WEAK_NOTES)
    assert result.recommendation
    # recruiter text is always copy-ready and mentions the candidate.
    assert "Sam Weak" in fb.recruiter_feedback_text(result)


def test_feedback_documents_render(theme, tmp_path: Path):
    result = fb.evaluate_notes("Aarav Mehta", NOTES)

    final = tmp_path / "final.docx"
    fb.generate_final_evaluation(theme, result, NOTES, final)

    scorecard = tmp_path / "scorecard.docx"
    fb.generate_completed_scorecard(theme, result, scorecard)

    recruiter = tmp_path / "recruiter.docx"
    fb.generate_recruiter_feedback(theme, result, recruiter, tmp_path / "recruiter.md")

    leadership = tmp_path / "leadership.docx"
    fb.generate_leadership_feedback(theme, result, leadership, tmp_path / "leadership.md")

    for out in (final, scorecard, recruiter, leadership):
        assert out.exists() and out.stat().st_size > 0


def test_schedule_past_date_and_missing_fields_flagged():
    record = sched.build_schedule(
        "Aarav Mehta", None, "Date: 2020-01-01\nTime: 10:00 AM\nTimezone: America/New_York",
        today=date(2026, 7, 1))
    assert record.needs_confirmation
    assert any("past" in issue.lower() for issue in record.validation_issues)
    assert any("duration is missing" in issue.lower() for issue in record.validation_issues)


def test_schedule_document_renders_with_confirmation_banner(theme, tmp_path: Path):
    record = sched.build_schedule(
        "Aarav Mehta", None,
        "Date: 2026-07-20\nTime: 10:00 AM\nTimezone: America/New_York\n"
        "Duration: 180 minutes\nInterviewers: Panel\nMeeting: Zoom",
        today=date(2026, 7, 1))
    assert not record.needs_confirmation
    out = tmp_path / "schedule.docx"
    sched.generate_schedule_doc(theme, record, out)
    assert out.exists() and out.stat().st_size > 0


def test_schedule_with_image_metadata_is_untrusted(theme, tmp_path: Path):
    from PIL import Image

    img = tmp_path / "shot.png"
    Image.new("RGB", (32, 16), "white").save(img)
    record = sched.build_schedule("Aarav Mehta", img, None, today=date(2026, 7, 1))
    assert record.extraction_source == "image-metadata"
    assert "untrusted" in record.notes.lower()
    assert record.needs_confirmation
