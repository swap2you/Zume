"""End-to-end Cursor workflow: intake (pre-interview) then finalize (Phase 16)."""

import json
from datetime import date
from pathlib import Path

from zume import deliverables as dl
from zume import pipeline
from zume.storage import Storage
from zume.validation import validate_candidate_folder


def _examples(tmp_root: Path) -> Path:
    return tmp_root / "examples" / "fictional-candidate"


def test_intake_builds_pre_interview_package_and_stops(tmp_root: Path):
    examples = _examples(tmp_root)
    result = pipeline.run_intake(
        tmp_root, resume_path=examples / "resume.txt",
        schedule_details=str(examples / "schedule.txt"), today=date(2026, 7, 1))

    folder = result.folder
    assert folder.name.startswith("Mehta_Aarav_")
    # v2 three-folder contract.
    assert (folder / "source").is_dir()
    assert (folder / "_internal" / "candidate.json").exists()
    deliverables = sorted(p.name for p in (folder / "deliverables").glob("*.docx"))
    assert len(deliverables) <= 7
    assert dl.SCREENING_SUMMARY in deliverables
    assert dl.INTERVIEW_GUIDE in deliverables
    assert dl.SCHEDULE_COMMS in deliverables

    # Phase 8 — intake NEVER generates feedback.
    assert result.feedback_generated is False
    assert not (folder / "deliverables" / dl.FINAL_EVALUATION).exists()
    assert not (folder / "deliverables" / dl.POST_INTERVIEW_COMMS).exists()
    assert not (folder / "_internal" / "feedback.json").exists()
    candidate = json.loads((folder / "_internal" / "candidate.json").read_text("utf-8"))
    assert candidate["status"] in {"READY_FOR_INTERVIEW", "INTERVIEW_SCHEDULED"}
    assert candidate["status"] not in {"INTERVIEWED", "SELECTED", "REJECTED"}

    # Phase 4 — the plan totals exactly 180 minutes with a 20-minute knockout.
    plan = json.loads((folder / "_internal" / "interview-plan.json").read_text("utf-8"))
    assert sum(s["minutes"] for s in plan["agenda"]) == 180
    assert plan["agenda"][0]["minutes"] == 20
    assert plan["knockout_minutes"] == 20

    assert not result.validation_errors
    report = validate_candidate_folder(folder, render=False)
    assert report.ok, report.errors


def test_finalize_after_notes_completes_the_package(tmp_root: Path):
    examples = _examples(tmp_root)
    intake = pipeline.run_intake(
        tmp_root, resume_path=examples / "resume.txt",
        schedule_details=str(examples / "schedule.txt"), today=date(2026, 7, 1))

    final = pipeline.run_finalize(
        tmp_root, intake.folder.name, str(examples / "interview-notes.txt"), leadership=True)

    folder = final.folder
    assert (folder / "deliverables" / dl.FINAL_EVALUATION).exists()
    assert (folder / "deliverables" / dl.POST_INTERVIEW_COMMS).exists()
    assert (folder / "_internal" / "feedback.json").exists()
    assert not final.validation_errors

    candidate = json.loads((folder / "_internal" / "candidate.json").read_text("utf-8"))
    assert candidate["status"] in {"SELECTED", "SECOND_ROUND", "REJECTED"}
    statuses = [e["status"] for e in candidate["status_history"]]
    assert statuses[0] == "RECEIVED"
    assert "INTERVIEWED" in statuses

    # No versioned files and no 99-final in the v2 package.
    assert not list(folder.rglob("*__v[0-9]*"))
    assert not (folder / "99-final").exists()

    with Storage(tmp_root) as storage:
        rows = storage.search_candidates("Aarav")
        assert rows
        screenings = storage.conn.execute("SELECT COUNT(*) FROM screenings").fetchone()[0]
        assert screenings >= 1


def test_rerun_intake_is_idempotent(tmp_root: Path):
    examples = _examples(tmp_root)
    first = pipeline.run_intake(
        tmp_root, resume_path=examples / "resume.txt",
        schedule_details=str(examples / "schedule.txt"), today=date(2026, 7, 1))
    folder = first.folder
    plan1 = json.loads((folder / "_internal" / "interview-plan.json").read_text("utf-8"))
    exercises1 = [e["exercise_id"] for e in plan1["exercises"]]
    candidate1 = json.loads((folder / "_internal" / "candidate.json").read_text("utf-8"))
    history1 = len(candidate1["status_history"])

    second = pipeline.run_intake(
        tmp_root, resume_path=examples / "resume.txt",
        schedule_details=str(examples / "schedule.txt"), today=date(2026, 7, 1))
    assert second.folder == folder
    plan2 = json.loads((folder / "_internal" / "interview-plan.json").read_text("utf-8"))
    exercises2 = [e["exercise_id"] for e in plan2["exercises"]]

    # Same assigned exercises; no versioned files; status history did not balloon.
    assert exercises1 == exercises2
    assert not list(folder.rglob("*__v[0-9]*"))
    candidate2 = json.loads((folder / "_internal" / "candidate.json").read_text("utf-8"))
    assert len(candidate2["status_history"]) == history1
    deliverables = sorted(p.name for p in (folder / "deliverables").glob("*.docx"))
    assert len(deliverables) <= 7
