"""Pipeline knowledge enrichment and intake API smoke (fictional data)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from zume.models import (
    Decision,
    EvidenceItem,
    EvidenceLevel,
    ExperienceState,
    InterviewKit,
    ScreeningResult,
)
from zume.pipeline import _enrich_kit_from_knowledge
from zume.server.app import create_app


def _screening() -> ScreeningResult:
    return ScreeningResult(
        candidate_name="Fictional Candidate",
        experience_years=10,
        experience_state=ExperienceState.PASSED,
        experience_gate_passed=True,
        evidence=[
            EvidenceItem(skill="java", label="Java", mandatory=True, level=EvidenceLevel.EXPLICIT),
            EvidenceItem(skill="selenium", label="Selenium", mandatory=True, level=EvidenceLevel.EXPLICIT),
        ],
        score_percent=80,
        decision=Decision.PROCEED,
        validation_questions=["Validate Java collections depth"],
    )


def test_enrich_kit_sets_knockout_and_sections(repo_root: Path):
    class Cand:
        assigned_question_ids: list[str] = []

    kit = InterviewKit(
        candidate_name="Fictional Candidate",
        focus_areas=["Java"],
        validation_questions=[],
        exercises=[],
    )
    cand = Cand()
    enriched = _enrich_kit_from_knowledge(repo_root, kit, _screening(), cand, rotate=True)
    assert enriched.knockout
    assert enriched.question_sections
    assert cand.assigned_question_ids
    # Preserve on second pass
    again = _enrich_kit_from_knowledge(repo_root, kit, _screening(), cand, rotate=False)
    assert again.question_sections
    assert cand.assigned_question_ids


def test_intake_api_fictional(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resume = (
        "Fictional Candidate\nSenior SDET with 12 years.\n"
        "Java, Selenium WebDriver, REST Assured, Oracle SQL, TestNG, Cucumber, Jenkins.\n"
        "Built automation frameworks and mentored engineers.\n"
    )
    resp = client.post("/api/candidates/intake", json={"resume_text": resume, "name": "Fictional Candidate"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["folder"]
    assert body["decision"]
    assert "Feedback" not in " ".join(body.get("deliverables") or [])
