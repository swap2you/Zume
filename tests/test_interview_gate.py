"""Do-Not-Proceed workflow gate and override (v2 intake pipeline)."""

from datetime import date
from pathlib import Path

import pytest

from zume import candidate as cand
from zume import pipeline

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


def _intake(tmp_root: Path, resume: str, **kw):
    return pipeline.run_intake(tmp_root, resume_text=resume, today=date(2026, 7, 1), **kw)


def test_intake_blocked_builds_only_screening_for_rejected(tmp_root: Path):
    result = _intake(tmp_root, REJECT_RESUME)
    assert result.status == pipeline.DO_NOT_PROCEED
    docx = sorted(p.name for p in (result.folder / "deliverables").glob("*.docx"))
    from zume import deliverables as dl
    assert docx == [dl.SCREENING_SUMMARY]


def test_override_requires_reason(tmp_root: Path):
    with pytest.raises(pipeline.WorkflowError):
        _intake(tmp_root, REJECT_RESUME, override=True, override_reason="   ")


def test_override_records_reason_everywhere(tmp_root: Path):
    reason = "Hiring manager requested a courtesy technical screen."
    result = _intake(tmp_root, REJECT_RESUME, override=True, override_reason=reason)

    candidate = cand.load_candidate(result.folder)
    assert reason in candidate.override_reasons
    assert any(e.status == "INTERVIEW_PREP_OVERRIDE" for e in candidate.status_history)


def test_proceed_candidate_generates_full_package(tmp_root: Path):
    from zume import deliverables as dl

    result = _intake(tmp_root, PROCEED_RESUME)
    assert (result.folder / "deliverables" / dl.INTERVIEW_GUIDE).exists()
