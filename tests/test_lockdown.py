"""Final Lockdown regression tests (Parts 2, 3, 4, 5, 7)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from zume import candidate as cand
from zume import deliverables as dl
from zume import feedback as fb
from zume import pipeline
from zume import scheduling as sched
from zume.cli import app

runner = CliRunner()

STRONG_RESUME = """Aarav Mehta
Senior Automation Engineer with 9.2 years of experience.
Skills: Java, Selenium 4, TestNG, Cucumber, REST Assured, Oracle SQL, Jenkins, Appium.
Built and maintained a Java Selenium framework, implemented REST Assured API chaining,
validated payments in Oracle SQL and integrated Jenkins pipelines. Mentored two engineers.
"""

SCHEDULE = ("Date: 2026-07-20\nTime: 10:00 AM\nTimezone: America/New_York\n"
            "Duration: 180 minutes\nInterviewers: Panel\nMeeting: Zoom")

STRONG_NOTES = (
    "Strong Java fundamentals; explained collections and streams clearly and coded "
    "independently. Selenium waits and locators were solid. REST Assured API chaining was "
    "correct. SQL Oracle joins were good. Modified the solution when the requirement changed. "
    "Confident, independent candidate.")


def _intake(tmp_root: Path, **kw):
    return pipeline.run_intake(tmp_root, resume_text=STRONG_RESUME, name="Aarav Mehta",
                               today=date(2026, 7, 1), **kw)


# -- Part 2 : candidate-creation entry points only produce the v2 contract -----

def test_intake_only_creates_three_folder_contract(tmp_root: Path):
    folder = _intake(tmp_root).folder
    subdirs = {p.name for p in folder.iterdir() if p.is_dir()}
    assert subdirs <= {"source", "_internal", "deliverables"}
    assert not (folder / "99-final").exists()
    assert not list(folder.rglob("*__v[0-9]*"))
    for legacy in ("00-source", "01-screening", "03-interview-prep", "05-feedback"):
        assert not (folder / legacy).exists()


def test_legacy_commands_are_deprecated_and_make_no_v1_folder(tmp_root: Path):
    # interview-prep / schedule-interview refuse and create nothing.
    for args in (["interview-prep", "--candidate", "Whoever"],
                 ["schedule-interview", "--candidate", "Whoever"]):
        result = runner.invoke(app, args)
        assert result.exit_code != 0
        assert "Deprecated" in result.output or "retired" in result.output
    assert not (tmp_root / "candidates").exists() or \
        not any((tmp_root / "candidates").iterdir())


def test_legacy_filter_resume_delegates_to_intake_v2(tmp_root: Path):
    resume = tmp_root / "r.txt"
    resume.write_text(STRONG_RESUME, encoding="utf-8")
    result = runner.invoke(app, ["filter-resume", "--input", str(resume)])
    assert result.exit_code == 0, result.output
    assert "Deprecated" in result.output
    folders = [p for p in (tmp_root / "candidates").iterdir()
               if (p / "_internal" / "candidate.json").exists()]
    assert folders, "intake delegation should create a v2 folder"
    for folder in folders:
        assert not (folder / "99-final").exists()


def _cli_intake(tmp_root: Path) -> Path:
    resume = tmp_root / "r.txt"
    resume.write_text(STRONG_RESUME, encoding="utf-8")
    result = runner.invoke(app, ["intake", "--resume", str(resume), "--schedule-details", SCHEDULE])
    assert result.exit_code == 0, result.output
    return next(p for p in (tmp_root / "candidates").iterdir()
               if (p / "_internal" / "candidate.json").exists())


def test_legacy_interview_feedback_delegates_to_finalize(tmp_root: Path):
    folder = _cli_intake(tmp_root)
    notes = tmp_root / "n.txt"
    notes.write_text(STRONG_NOTES, encoding="utf-8")
    result = runner.invoke(app, ["interview-feedback", "--candidate", folder.name,
                                 "--notes", str(notes)])
    assert result.exit_code == 0, result.output
    assert "Deprecated" in result.output
    assert (folder / "deliverables" / dl.FINAL_EVALUATION).exists()


def test_run_trigger_delegates_filter_and_blocks_prep(tmp_root: Path):
    resume = tmp_root / "r.txt"
    resume.write_text(STRONG_RESUME, encoding="utf-8")
    fr = runner.invoke(app, ["run", "--trigger", "Filter Resume - Automation Hiring",
                             "--input", str(resume)])
    assert fr.exit_code == 0, fr.output
    assert "Deprecated" in fr.output

    prep = runner.invoke(app, ["run", "--trigger", "Interview Prep - Automation Hiring",
                               "--candidate", "X"])
    assert prep.exit_code != 0
    assert not (tmp_root / "candidates" / "X").exists()


# -- Part 3 : finalized candidates are protected from intake reruns -----------

def _intake_then_finalize(tmp_root: Path):
    intake = _intake(tmp_root, schedule_details=SCHEDULE)
    assert intake.status == pipeline.SCHEDULED
    final = pipeline.run_finalize(tmp_root, intake.folder.name, STRONG_NOTES)
    return intake.folder, final


def test_intake_after_finalize_is_blocked(tmp_root: Path):
    folder, final = _intake_then_finalize(tmp_root)
    assert final.status in pipeline.TERMINAL_STATES
    with pytest.raises(pipeline.WorkflowError):
        _intake(tmp_root, schedule_details=SCHEDULE)


def test_blocked_intake_leaves_deliverables_unchanged(tmp_root: Path):
    folder, _ = _intake_then_finalize(tmp_root)
    before = {p.name: cand.sha256_file(p)
              for p in (folder / "deliverables").glob("*.docx")}
    assert dl.FINAL_EVALUATION in before and dl.POST_INTERVIEW_COMMS in before
    with pytest.raises(pipeline.WorkflowError):
        _intake(tmp_root, schedule_details=SCHEDULE)
    after = {p.name: cand.sha256_file(p)
             for p in (folder / "deliverables").glob("*.docx")}
    assert before == after


def test_reopen_without_reason_is_blocked(tmp_root: Path):
    _intake_then_finalize(tmp_root)
    with pytest.raises(pipeline.WorkflowError):
        _intake(tmp_root, schedule_details=SCHEDULE, reopen=True)


def test_reopen_records_reason_and_preserves_final_artifacts(tmp_root: Path):
    folder, _ = _intake_then_finalize(tmp_root)
    final_before = cand.sha256_file(folder / "deliverables" / dl.FINAL_EVALUATION)
    comms_before = cand.sha256_file(folder / "deliverables" / dl.POST_INTERVIEW_COMMS)

    result = _intake(tmp_root, schedule_details=SCHEDULE, reopen=True,
                     reopen_reason="Candidate requested a re-run of the take-home")
    candidate = cand.load_candidate(folder)
    assert candidate.status in pipeline.TERMINAL_STATES  # not reset to ready/scheduled
    assert result.status == candidate.status
    assert any("requested" in r for r in candidate.reopen_reasons)
    assert any(e.status == "REOPENED" for e in candidate.status_history)
    # Final artifacts are preserved byte-for-byte.
    assert (folder / "deliverables" / dl.FINAL_EVALUATION).exists()
    assert (folder / "deliverables" / dl.POST_INTERVIEW_COMMS).exists()
    assert cand.sha256_file(folder / "deliverables" / dl.FINAL_EVALUATION) == final_before
    assert cand.sha256_file(folder / "deliverables" / dl.POST_INTERVIEW_COMMS) == comms_before


# -- Part 4 : export records an event without replacing workflow status -------

def test_export_preserves_workflow_status_and_finalize_still_works(tmp_root: Path):
    intake = _intake(tmp_root, schedule_details=SCHEDULE)
    assert intake.status in pipeline.FINALIZE_ALLOWED_STATES

    exported = runner.invoke(app, ["candidate", "export", "--candidate", intake.folder.name])
    assert exported.exit_code == 0, exported.output

    candidate = cand.load_candidate(intake.folder)
    assert candidate.status in {pipeline.READY, pipeline.SCHEDULED}
    assert candidate.status != "EXPORTED"
    assert any(e.status == "EXPORTED" for e in candidate.status_history)

    final = pipeline.run_finalize(tmp_root, intake.folder.name, STRONG_NOTES)
    assert final.status in pipeline.TERMINAL_STATES
    assert final.status != "EXPORTED"


# -- Part 5 : incomplete interview notes cannot yield a final selection -------

JAVA_ONLY = "Strong Java fundamentals; explained collections clearly."
JAVA_SELENIUM = ("Java collections were correct and explained well. Selenium locators and "
                 "waits were solid.")
ALL_NO_INDEPENDENCE = ("Java collections were correct. Selenium locators and waits were solid. "
                       "REST Assured API chaining worked. SQL Oracle joins were correct.")
WEAK_ALL = ("Could not explain Java equals and hashCode. Selenium locators were incorrect. "
            "REST Assured API chaining failed. SQL Oracle joins were wrong. Could not modify "
            "the code when asked.")
NO_ASSESSMENT = "The candidate arrived on time and we chatted about the weather and commute."


def test_java_only_notes_do_not_select(tmp_root: Path):
    r = fb.evaluate_notes("A", JAVA_ONLY)
    assert r.decision_permitted is False
    assert r.status != "SELECTED"
    assert "Incomplete interview evidence" in r.recommendation
    assert any("Selenium" in m for m in r.missing_areas)


def test_java_selenium_only_is_incomplete(tmp_root: Path):
    r = fb.evaluate_notes("A", JAVA_SELENIUM)
    assert r.decision_permitted is False
    assert fb.MANDATORY_LABELS["rest_assured"] in r.missing_areas
    assert fb.MANDATORY_LABELS["sql_oracle"] in r.missing_areas


def test_all_areas_but_no_independence_is_incomplete(tmp_root: Path):
    r = fb.evaluate_notes("A", ALL_NO_INDEPENDENCE)
    assert r.decision_permitted is False
    assert fb.INDEPENDENCE_AREA in r.missing_areas


def test_complete_strong_notes_permit_selection(tmp_root: Path):
    r = fb.evaluate_notes("A", STRONG_NOTES)
    assert r.decision_permitted is True
    assert r.missing_areas == []
    assert r.status == "SELECTED"


def test_complete_weak_notes_do_not_proceed(tmp_root: Path):
    r = fb.evaluate_notes("A", WEAK_ALL)
    # A decision is permitted (all areas assessed) and it is a firm Do Not Proceed.
    assert r.status == "REJECTED"
    assert r.decision.value == "Do Not Proceed"


def test_no_recognizable_assessment_is_incomplete(tmp_root: Path):
    r = fb.evaluate_notes("A", NO_ASSESSMENT)
    assert r.decision_permitted is False
    assert r.status != "SELECTED"
    assert len(r.missing_areas) >= 4


# -- Part 7 : schedule communications include the timezone --------------------

def test_all_drafts_include_timezone_and_platform(tmp_root: Path):
    record = sched.build_schedule("Aarav Mehta", None, SCHEDULE, today=date(2026, 7, 1))
    assert not record.needs_confirmation
    drafts = sched.build_communication_drafts(record)
    kinds = {d.kind for d in drafts}
    assert {"join", "reschedule", "cancel", "no-show"} <= kinds
    join = next(d for d in drafts if d.kind == "join")
    assert join.subject == "Interview Confirmation – Aarav Mehta"
    for draft in drafts:
        assert "America/New_York" in draft.body
        assert "DRAFT — schedule is NOT confirmed" not in draft.body


def test_unconfirmed_schedule_is_not_presented_as_confirmed():
    record = sched.build_schedule(
        "Aarav Mehta", None, "Date: 2026-07-20\nTime: 10:00 AM", today=date(2026, 7, 1))
    assert record.needs_confirmation
    drafts = sched.build_communication_drafts(record)
    join = next(d for d in drafts if d.kind == "join")
    assert join.subject == "Proposed Interview Schedule – Aarav Mehta"
    assert "Interview Confirmation" not in join.subject
    for draft in drafts:
        assert "NOT confirmed" in draft.body
        assert "Confirming the interview" not in draft.body
    for draft in drafts:
        if draft.kind != "join":
            assert "Proposed Interview Schedule" not in draft.subject
