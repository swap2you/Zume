"""Phase 5 — interview-prep workflow gates and override."""

import json
from pathlib import Path

import pytest
import typer

from zume import cli

REJECT_RESUME = """Nikhil Rao
QA Engineer with 4 years experience.
Skills: Java, Selenium.
"""

PROCEED_RESUME = """Aarav Mehta
Senior Automation Engineer with 9.2 years of experience.
Skills: Java, Selenium 4, TestNG, Cucumber, REST Assured, Oracle SQL, Jenkins.
Built and maintained a Java Selenium framework, implemented REST Assured API chaining,
validated payments in Oracle SQL and integrated Jenkins. Mentored two engineers.
"""


def _screen(tmp_root: Path, resume_text: str) -> Path:
    src = tmp_root / "input"
    src.mkdir(exist_ok=True)
    resume = src / "resume.txt"
    resume.write_text(resume_text, encoding="utf-8")
    return cli.run_filter_resume(resume, None, None)


def test_interview_prep_blocked_for_rejected_candidate(tmp_root: Path):
    folder = _screen(tmp_root, REJECT_RESUME)
    with pytest.raises(typer.Exit) as exc:
        cli.run_interview_prep(folder.name)
    assert exc.value.exit_code == 2
    # no kit artifacts were produced
    assert not list((folder / "03-interview-prep").glob("*.docx"))


def test_override_requires_reason(tmp_root: Path):
    folder = _screen(tmp_root, REJECT_RESUME)
    with pytest.raises(typer.BadParameter):
        cli.run_interview_prep(folder.name, override=True, override_reason="   ")


def test_override_records_reason_everywhere(tmp_root: Path):
    folder = _screen(tmp_root, REJECT_RESUME)
    reason = "Hiring manager requested a courtesy technical screen."
    cli.run_interview_prep(folder.name, override=True, override_reason=reason)

    kit = json.loads((folder / "03-interview-prep" / "interview-kit.json").read_text("utf-8"))
    assert kit["override_reason"] == reason

    candidate = json.loads((folder / "candidate.json").read_text("utf-8"))
    assert reason in candidate["override_reasons"]
    assert any(e["status"] == "INTERVIEW_PREP_OVERRIDE" for e in candidate["status_history"])

    from zume.storage import Storage

    with Storage(tmp_root) as storage:
        row = storage.conn.execute(
            "SELECT override_reason FROM interviews WHERE override_reason != ''").fetchone()
        assert row is not None and row[0] == reason


def test_proceed_candidate_generates_kit(tmp_root: Path):
    folder = _screen(tmp_root, PROCEED_RESUME)
    cli.run_interview_prep(folder.name)
    assert (folder / "03-interview-prep" / "Full_Interview_Guide.docx").exists()
