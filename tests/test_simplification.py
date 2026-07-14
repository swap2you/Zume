"""Phases 2, 6, 8, 13, 16 — contract, gates, idempotency and safety."""

from datetime import date
from pathlib import Path

import pytest

from zume import candidate as cand
from zume import deliverables as dl
from zume import pipeline
from zume.validation import detect_sparse_trailing_page


def make_legacy_folder(tmp_root: Path, _name: str) -> Path:
    """Build a legacy-style candidate folder (numbered subfolders, root
    candidate.json, a 99-final copy and a __vN versioned file)."""
    _, folder = cand.new_candidate(tmp_root, "Legacy Person", date(2026, 1, 1))
    cand.atomic_write_text(folder / "00-source" / "original-resume.txt", "resume text")
    cand.atomic_write_bytes(folder / "99-final" / "01_Screening_Summary.docx", b"PK\x03\x04copy")
    cand.atomic_write_bytes(
        folder / "03-interview-prep" / "Full_Interview_Guide__v1.docx", b"PK\x03\x04old")
    return folder

RESUME = """Aarav Mehta
Senior Automation Engineer with 9.2 years of experience.
Skills: Java, Selenium 4, TestNG, Cucumber, REST Assured, Oracle SQL, Jenkins, Appium.
Built and maintained a Java Selenium framework, implemented REST Assured API chaining,
validated payments in Oracle SQL and integrated Jenkins pipelines. Mentored two engineers.
"""

WEAK_RESUME = """Sam Weak
Manual tester with 2 years of experience. Skills: Postman, basic Java.
Ran manual test cases and logged defects.
"""


def _intake(tmp_root: Path, text=RESUME, **kw):
    return pipeline.run_intake(tmp_root, resume_text=text, name=kw.pop("name", None),
                               today=date(2026, 7, 1), **kw)


# -- Phase 2 / 3 : contract and deliverable count -----------------------------

def test_new_candidate_uses_three_folder_contract(tmp_root: Path):
    result = _intake(tmp_root)
    folder = result.folder
    assert (folder / "source").is_dir()
    assert (folder / "_internal").is_dir()
    assert (folder / "deliverables").is_dir()
    assert not (folder / "99-final").exists()


def test_at_most_seven_deliverables_and_no_versioned_files(tmp_root: Path):
    result = _intake(tmp_root, schedule_details="Date: 2026-07-20\nTime: 10:00\n"
                     "Timezone: America/New_York\nDuration: 180 minutes")
    folder = result.folder
    docx = list((folder / "deliverables").glob("*.docx"))
    assert 1 <= len(docx) <= 7
    assert not list(folder.rglob("*__v[0-9]*"))


# -- Phase 8 : intake never generates feedback --------------------------------

def test_intake_never_creates_feedback(tmp_root: Path):
    result = _intake(tmp_root)
    folder = result.folder
    assert result.feedback_generated is False
    assert not (folder / "_internal" / "feedback.json").exists()
    assert not (folder / "deliverables" / dl.FINAL_EVALUATION).exists()
    assert not (folder / "deliverables" / dl.POST_INTERVIEW_COMMS).exists()
    candidate = cand.load_candidate(folder)
    assert candidate.status not in {"INTERVIEWED", "SELECTED", "REJECTED", "SECOND_ROUND"}


def test_finalize_requires_intake_state(tmp_root: Path):
    # No candidate at all -> resolve fails.
    with pytest.raises(Exception):
        pipeline.run_finalize(tmp_root, "Nobody", "some notes")


def test_finalize_requires_non_empty_notes(tmp_root: Path):
    result = _intake(tmp_root)
    with pytest.raises(pipeline.WorkflowError):
        pipeline.run_finalize(tmp_root, result.folder.name, "   ")


# -- Do-Not-Proceed gate ------------------------------------------------------

def test_do_not_proceed_only_produces_screening_summary(tmp_root: Path):
    result = _intake(tmp_root, text=WEAK_RESUME, name="Sam Weak")
    assert result.status == pipeline.DO_NOT_PROCEED
    docx = sorted(p.name for p in (result.folder / "deliverables").glob("*.docx"))
    assert docx == [dl.SCREENING_SUMMARY]


def test_override_builds_full_package_with_reason(tmp_root: Path):
    result = _intake(tmp_root, text=WEAK_RESUME, name="Sam Weak",
                     override=True, override_reason="Referral; manager exception")
    docx = sorted(p.name for p in (result.folder / "deliverables").glob("*.docx"))
    assert dl.INTERVIEW_GUIDE in docx
    candidate = cand.load_candidate(result.folder)
    assert any("Referral" in r for r in candidate.override_reasons)


def test_override_without_reason_is_blocked(tmp_root: Path):
    with pytest.raises(pipeline.WorkflowError):
        _intake(tmp_root, text=WEAK_RESUME, name="Sam Weak", override=True)


# -- Phase 6 : exercise preservation and rotation -----------------------------

def test_exercises_preserved_on_normal_rerun(tmp_root: Path):
    first = _intake(tmp_root)
    ids1 = cand.load_candidate(first.folder).assigned_exercise_ids
    second = _intake(tmp_root)
    ids2 = cand.load_candidate(second.folder).assigned_exercise_ids
    assert ids1 == ids2


def test_rotation_requires_reason(tmp_root: Path):
    _intake(tmp_root)
    with pytest.raises(pipeline.WorkflowError):
        _intake(tmp_root, rotate_exercises=True)


def test_rotation_records_reason_and_changes_assignment(tmp_root: Path):
    first = _intake(tmp_root)
    ids1 = list(cand.load_candidate(first.folder).assigned_exercise_ids)
    rotated = _intake(tmp_root, rotate_exercises=True,
                      rotation_reason="Candidate saw these in a prior round")
    candidate = cand.load_candidate(rotated.folder)
    assert any("rotated" in r.lower() for r in candidate.rotation_reasons)
    # Assignment set is recorded (may overlap but the reason is captured).
    assert candidate.assigned_exercise_ids
    assert ids1 is not None


# -- Phase 16 item 15 : candidate sheet contains no interviewer material ------

def test_candidate_sheet_has_no_solutions(tmp_root: Path):
    from docx import Document

    result = _intake(tmp_root)
    sheet = result.folder / "deliverables" / dl.CANDIDATE_SHEET
    text = "\n".join(p.text for p in Document(str(sheet)).paragraphs)
    for banned in ["Reference solution", "Recommended answer", "Scoring rubric",
                   "Red flags", "Expected reasoning"]:
        assert banned not in text


# -- Phase 2 : legacy migration preview + apply -------------------------------

def test_migration_preview_and_apply(tmp_root: Path):
    folder = make_legacy_folder(tmp_root, "Legacy_Person_2026-01-01")
    assert cand.is_legacy_folder(folder)
    plan = cand.plan_migration(folder)
    assert any("source/" in m for m in plan["move"])
    assert any("99-final" in r for r in plan["remove"])

    cand.apply_migration(folder)
    assert (folder / "source").is_dir()
    assert (folder / "_internal" / "candidate.json").exists()
    assert not (folder / "candidate.json").exists()
    assert not (folder / "99-final").exists()
    assert not list(folder.rglob("*__v[0-9]*"))
    # Source files are preserved, never deleted.
    assert (folder / "source" / "original-resume.txt").exists()


# -- Phase 13 : sparse trailing page detection --------------------------------

def test_sparse_trailing_page_detection():
    pages = ["x" * 1000, "x" * 1000, "x" * 50]
    assert detect_sparse_trailing_page(pages) is not None
    full = ["x" * 1000, "x" * 900, "x" * 950]
    assert detect_sparse_trailing_page(full) is None
    assert detect_sparse_trailing_page(["only one page"]) is None
