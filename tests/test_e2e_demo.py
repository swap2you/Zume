import json
from pathlib import Path

from zume import cli
from zume.storage import Storage
from zume.validation import validate_candidate_folder


def test_fictional_demo_end_to_end(tmp_root: Path):
    examples = tmp_root / "examples" / "fictional-candidate"

    folder = cli.run_filter_resume(examples / "resume.txt", None, None)
    assert folder.name.startswith("Mehta_Aarav_")
    screening = json.loads((folder / "01-screening" / "screening.json").read_text("utf-8"))
    assert screening["decision"] == "Proceed"
    assert (folder / "01-screening" / "ATS_Screening.docx").exists()
    assert (folder / "06-communications" / "Recruiter_Feedback.md").exists()

    cli.run_interview_prep(folder.name)
    assert (folder / "03-interview-prep" / "Full_Interview_Guide.docx").exists()
    kit = json.loads((folder / "03-interview-prep" / "interview-kit.json").read_text("utf-8"))
    # Appium exercises included because the resume mentions Appium/BrowserStack
    assert any(e["area"] == "appium" for e in kit["exercises"])

    cli.run_schedule_interview(folder.name, None, str(examples / "schedule.txt"))
    schedule = json.loads((folder / "02-schedule" / "schedule.json").read_text("utf-8"))
    assert schedule["date"] == "2026-07-20"
    assert schedule["needs_confirmation"] is False
    assert (folder / "06-communications" / "Schedule_Drafts.md").exists()

    cli.run_interview_feedback(folder.name, str(examples / "interview-notes.txt"),
                               leadership=True)
    feedback = json.loads((folder / "05-feedback" / "feedback.json").read_text("utf-8"))
    assert feedback["decision"] == "Proceed"
    assert (folder / "05-feedback" / "Leadership_Feedback.docx").exists()

    candidate = json.loads((folder / "candidate.json").read_text("utf-8"))
    assert candidate["status"] == "SELECTED"
    statuses = [e["status"] for e in candidate["status_history"]]
    assert statuses[0] == "RECEIVED"
    assert "INTERVIEW_SCHEDULED" in statuses
    assert statuses[-1] == "SELECTED"

    # validated DOCX artifacts were promoted to 99-final
    final_docs = list((folder / "99-final").glob("*.docx"))
    assert len(final_docs) >= 8

    report = validate_candidate_folder(folder, render=False)
    assert report.ok, report.errors

    with Storage(tmp_root) as storage:
        rows = storage.search_candidates("Aarav")
        assert rows and rows[0][2] == "SELECTED"
        screenings = storage.conn.execute("SELECT COUNT(*) FROM screenings").fetchone()[0]
        assert screenings >= 1
        comms = storage.conn.execute("SELECT COUNT(*) FROM communications").fetchone()[0]
        assert comms >= 5
        scores = storage.conn.execute("SELECT COUNT(*) FROM scores").fetchone()[0]
        assert scores >= 3
        history = storage.conn.execute("SELECT COUNT(*) FROM status_history").fetchone()[0]
        assert history >= 3
