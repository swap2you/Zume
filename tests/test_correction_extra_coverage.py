"""Extra coverage for finalize path and selection helpers."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from zume.knowledge.loader import load_all_exercises, load_all_questions
from zume.knowledge.selection import _canonical_domain, _reason_for, select_interview_plan
from zume.labs.api_lab import ApiLabProvider
from zume.server.app import create_app


RESUME = (
    "Aarav Mehta\n"
    "Senior Automation Engineer — 9.2 years\n"
    "Skills: Java, Selenium 4, TestNG, Cucumber, REST Assured, Oracle SQL, Maven, Git, Jenkins, "
    "Appium, BrowserStack.\n"
    "Experience: Built and maintained Java Selenium Page Object frameworks, implemented API "
    "chaining with REST Assured, validated payments in Oracle, integrated suites with Jenkins, "
    "mentored two engineers.\n"
)


def test_intake_then_finalize_completeness(tmp_path: Path, repo_root: Path, monkeypatch):
    # Isolated root so we do not collide with real candidate folders.
    shutil.copytree(repo_root / "config", tmp_path / "config")
    shutil.copytree(repo_root / "examples", tmp_path / "examples")
    shutil.copytree(repo_root / "knowledge", tmp_path / "knowledge")
    (tmp_path / "pyproject.toml").write_text((repo_root / "pyproject.toml").read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("zume.config.find_root", lambda: tmp_path)
    monkeypatch.setattr("zume.server.routes_workspace._root", lambda: tmp_path)

    client = TestClient(create_app(tmp_path))
    intake = client.post(
        "/api/candidates/intake",
        json={"resume_text": RESUME, "name": "Aarav Mehta"},
    )
    assert intake.status_code == 200, intake.text
    body = intake.json()
    assert body["status"] != "DO_NOT_PROCEED", body
    folder = body["folder"]
    notes = (
        "Strong Java fundamentals; explained collections and streams clearly and coded "
        "independently. Selenium waits and locators were solid. REST Assured API chaining "
        "was correct. SQL Oracle joins were good. Modified the solution when the "
        "requirement changed. Confident, independent candidate."
    )
    final = client.post("/api/candidates/finalize", json={"candidate": folder, "notes": notes})
    assert final.status_code == 200, final.text
    assert "decision_permitted" in final.json()


def test_selection_reason_helpers(repo_root: Path):
    qs = [q for q in load_all_questions(repo_root / "knowledge") if q.status == "published"]
    assert qs
    q = qs[0]
    assert _canonical_domain("appium") == "mobile-appium"
    assert _canonical_domain("performance") == "performance-observability"
    assert _canonical_domain("llm-generative") == "llm-engineering"
    reason = _reason_for(q, tags=set(), role_track="Senior SDET", preserved=False)
    assert any(
        reason.startswith(prefix)
        for prefix in (
            "mandatory-core",
            "resume-claimed",
            "missing-evidence",
            "risk-validation",
            "role-aligned",
            "specialty-depth",
            "rotation",
        )
    )
    preserved = select_interview_plan(
        qs,
        load_all_exercises(repo_root / "knowledge"),
        resume_text=RESUME,
        previous_question_ids=[q.id for q in qs[:3]],
        rotate=False,
    )
    assert preserved["preserved_prior_selection"] is True


def test_intake_upload_rejects_empty(repo_root: Path, monkeypatch, tmp_path: Path):
    monkeypatch.setattr("zume.server.routes_workspace._root", lambda: repo_root)
    client = TestClient(create_app(repo_root))
    resp = client.post(
        "/api/candidates/intake-upload",
        files={"resume": ("empty.txt", b"", "text/plain")},
    )
    assert resp.status_code in {400, 422}


def test_api_lab_origin_message(tmp_path: Path):
    lab = ApiLabProvider()
    ws = str(tmp_path / "a")
    lab.prepare("t", ws)
    result = lab.run("t", ws, json.dumps({"url": "http://127.0.0.1:9999/x"}))
    assert result.exit_code != 0
    assert "8765" in result.stderr or "origin" in result.stderr.lower() or "Blocked" in result.stderr
    lab.cleanup(ws)


def test_curated_fallback_when_core_missing(repo_root: Path):
    plan = select_interview_plan([], [], resume_text=RESUME, config_root=repo_root)
    assert plan["question_ids"], "curated config library must supply fallback questions"
    assert all(w["reason"].split(":")[0] for w in plan["why"])


def test_content_quality_exercise_projection(repo_root: Path):
    from zume.knowledge.content_quality import _exercise_errors, _published
    from zume.knowledge.gaps import collect_gaps
    from zume.knowledge.loader import load_sources, load_taxonomy
    from zume.knowledge.stats import collect_stats

    exercises = [e for e in load_all_exercises(repo_root / "knowledge") if e.status == "published"]
    assert exercises
    assert _published(exercises)
    sources = load_sources(repo_root / "knowledge")
    roles = {str(r) for r in (load_taxonomy(repo_root / "knowledge").get("role_tracks") or [])}
    for exercise in exercises:
        errs = _exercise_errors(exercise, sources, roles)
        assert not any("leak" in e.lower() for e in errs)
    stats = collect_stats(repo_root)
    gaps = collect_gaps(repo_root)
    assert stats["draft_questions"] >= 0
    assert gaps["complete_claim"] is False
    assert "gaps" in gaps
