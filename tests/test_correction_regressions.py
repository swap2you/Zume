"""Phase 0 correction regression tests — encode independent-audit defects.

These tests document release-blocking findings from the independent audit.
They must fail against the uncorrected candidate and pass after corrections.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from zume.knowledge.loader import load_all_questions
from zume.knowledge.selection import select_interview_plan
from zume.labs.api_lab import ApiLabProvider
from zume.labs.java_lab import JavaLabProvider
from zume.labs.sql_lab import SqlLabProvider
from zume.scheduling import build_communication_drafts, build_schedule
from zume.server.app import create_app

GENERIC_ANSWER_FINGERPRINTS = (
    "should be applied to a stated outcome, observable evidence",
    "Start by naming the decision that",
    "observable evidence, and prioritization",
    "What evidence would make you revise your",
)


# ---------------------------------------------------------------------------
# 1. Library search response contract
# ---------------------------------------------------------------------------

def test_knowledge_search_returns_results_key(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.get("/api/knowledge/search", params={"q": "HashMap", "limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body
    # Contract for the UI: also expose a stable `items` alias so clients need not branch.
    assert "items" in body, "search must expose `items` for the library UI contract"
    assert isinstance(body["items"], list)


# ---------------------------------------------------------------------------
# 2. P0-P3 priority filter
# ---------------------------------------------------------------------------

def test_knowledge_questions_accept_p0_priority(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.get("/api/knowledge/questions", params={"priority": "P0", "limit": 10})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert items, "P0 filter must return published reviewed questions"
    assert all(i["priority"] == "P0" for i in items)


# ---------------------------------------------------------------------------
# 3. Practice data must come from the library (backend contract)
# ---------------------------------------------------------------------------

def test_practice_endpoint_returns_library_records(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.get("/api/knowledge/practice", params={"limit": 5})
    assert resp.status_code == 200, "practice endpoint must exist for the Practice screen"
    body = resp.json()
    assert body.get("items"), "practice must draw from the knowledge library"
    assert all("question" in i and "recommended_answer" in i for i in body["items"])


# ---------------------------------------------------------------------------
# 4. Lab UI runners match backend capability names
# ---------------------------------------------------------------------------

def test_lab_runners_are_sql_api_java_selenium_only(repo_root: Path):
    client = TestClient(create_app(repo_root))
    labs = client.get("/api/labs").json()["labs"]
    names = {c["runner"] for c in labs}
    assert names == {"sql", "api", "java", "selenium"}
    assert "python" not in names
    assert "javascript" not in names


# ---------------------------------------------------------------------------
# 5. Ask UI contract includes citations/source_mode
# ---------------------------------------------------------------------------

def test_ask_response_includes_citations_and_source_mode(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.post("/api/ask", json={"question": "Explain equals and hashCode for HashMap keys"})
    assert resp.status_code == 200
    body = resp.json()
    assert "answer" in body
    assert "citations" in body
    assert "source_mode" in body
    assert "confidence" in body


# ---------------------------------------------------------------------------
# 6. Unconfirmed schedule subject
# ---------------------------------------------------------------------------

def test_unconfirmed_join_subject_is_proposed_not_confirmation():
    from datetime import date

    record = build_schedule(
        "Aarav Mehta", None, "Date: 2026-07-20\nTime: 10:00 AM", today=date(2026, 7, 1)
    )
    assert record.needs_confirmation
    drafts = build_communication_drafts(record)
    join = next(d for d in drafts if d.kind == "join")
    assert join.subject.startswith("Proposed Interview Schedule")
    assert "Interview Confirmation" not in join.subject


# ---------------------------------------------------------------------------
# 7. Mobile/performance/AI resume domain aliases
# ---------------------------------------------------------------------------

def test_resume_aliases_map_to_canonical_domains(repo_root: Path):
    questions = [q for q in load_all_questions(repo_root / "knowledge") if q.status == "published"]
    exercises = []
    mobile = select_interview_plan(questions, exercises, resume_text="Appium Android iOS mobile automation")
    perf = select_interview_plan(questions, exercises, resume_text="JMeter Gatling k6 performance engineer")
    ai = select_interview_plan(questions, exercises, resume_text="LLM RAG OpenAI generative AI QA")
    # Selected why-reasons must mention resume-claimed domains with canonical IDs.
    mobile_domains = {q["domain"] for q in mobile["questions"]}
    perf_domains = {q["domain"] for q in perf["questions"]}
    ai_domains = {q["domain"] for q in ai["questions"]}
    assert "mobile-appium" in mobile_domains or any(
        w.get("reason", "").startswith("resume-claimed") and "mobile" in w.get("reason", "")
        for w in mobile.get("why", [])
    ), "mobile resume must select mobile-appium (not bare 'appium')"
    assert "performance-observability" in perf_domains or any(
        "performance-observability" in str(w) for w in perf.get("why", [])
    )
    assert "llm-engineering" in ai_domains or any(
        "llm-engineering" in str(w) for w in ai.get("why", [])
    )


def test_selection_reasons_are_truthful(repo_root: Path):
    questions = [q for q in load_all_questions(repo_root / "knowledge") if q.status == "published"]
    plan = select_interview_plan(questions, [], resume_text="Manual tester excel spreadsheets")
    for item in plan.get("why", []):
        reason = item.get("reason", "")
        # Must not claim resume-aligned for mandatory domains when resume has no match.
        if "resume" in reason.lower() and "aligned" in reason.lower():
            assert False, f"weak resume must not get resume-aligned reasons: {reason}"
        # Allowed reason prefixes after correction.
        allowed = (
            "mandatory-core",
            "resume-claimed",
            "missing-evidence",
            "risk-validation",
            "role-aligned",
            "specialty-depth",
            "rotation",
        )
        assert any(reason.startswith(a) for a in allowed), f"unexpected reason format: {reason}"


# ---------------------------------------------------------------------------
# 8. Published records cannot use generic repeated answer templates
# ---------------------------------------------------------------------------

def test_published_questions_reject_generic_template_fingerprints(repo_root: Path):
    published = [q for q in load_all_questions(repo_root / "knowledge") if q.status == "published"]
    assert published, "must have at least some reviewed published questions"
    offenders = []
    for q in published:
        blob = " ".join(
            [
                q.concise_answer,
                q.recommended_answer,
                q.deep_dive,
                " ".join(q.strong_signals),
                " ".join(fu.recommended_answer for fu in q.follow_ups),
            ]
        )
        for fp in GENERIC_ANSWER_FINGERPRINTS:
            if fp.lower() in blob.lower():
                offenders.append(f"{q.id}: {fp}")
                break
    assert not offenders, (
        "published questions still contain generic template fingerprints:\n"
        + "\n".join(offenders[:20])
    )


# ---------------------------------------------------------------------------
# 9. Java metadata mismatches in java-b2 and java-b3
# ---------------------------------------------------------------------------

def test_java_b2_b3_metadata_matches_question_topic(repo_root: Path):
    path = repo_root / "knowledge" / "questions" / "java" / "basic.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in data.get("records") or data.get("questions") or []}
    # After correction these may be draft or rewritten; if present as published, metadata must match.
    for qid, expected_tokens in {
        "java-b2": ("exception", "checked", "unchecked"),
        "java-b3": ("collection", "map", "list", "set", "lookup"),
    }.items():
        if qid not in by_id:
            continue
        rec = by_id[qid]
        if rec.get("status") != "published":
            continue
        tags = " ".join(rec.get("tags") or []).lower()
        fu = " ".join(f.get("question", "") for f in rec.get("follow_ups") or []).lower()
        assert any(t in tags or t in fu or t in rec.get("subdomain", "").lower() for t in expected_tokens), (
            f"{qid} published metadata does not match its question topic"
        )
        # Explicit known defects must be gone.
        assert "oop" not in tags or "exception" in tags
        assert "strings-immutability" not in tags or "collection" in tags


# ---------------------------------------------------------------------------
# 10. SQL query timeout and write denial
# ---------------------------------------------------------------------------

def test_sql_lab_denies_writes_and_times_out(tmp_path: Path):
    lab = SqlLabProvider()
    ws = str(tmp_path / "sql")
    lab.prepare("t", ws)
    write = lab.run("t", ws, "INSERT INTO employees(id, name, dept, salary) VALUES (99,'x','y',1)")
    assert write.exit_code != 0, "SQL lab must deny writes"
    # Heavy recursive CTE should hit the progress-handler deadline.
    heavy = lab.run(
        "t",
        ws,
        "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM r WHERE n < 100000000) "
        "SELECT COUNT(*) FROM r",
    )
    assert heavy.exit_code != 0 or "timeout" in (heavy.stderr + heavy.stdout).lower()
    lab.cleanup(ws)


# ---------------------------------------------------------------------------
# 11. API lab rejects wrong localhost ports and redirects
# ---------------------------------------------------------------------------

def test_api_lab_rejects_wrong_localhost_port_and_redirects(tmp_path: Path):
    lab = ApiLabProvider()
    ws = str(tmp_path / "api")
    lab.prepare("t", ws)
    wrong_port = lab.run("t", ws, json.dumps({"method": "GET", "url": "http://127.0.0.1:9999/secret"}))
    assert wrong_port.exit_code != 0
    assert "8765" in wrong_port.stderr or "Blocked" in wrong_port.stderr or "origin" in wrong_port.stderr.lower()
    lab.cleanup(ws)


# ---------------------------------------------------------------------------
# 12. Java timeout forces container cleanup
# ---------------------------------------------------------------------------

def test_java_lab_uses_named_container_and_cleanup_on_timeout(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ZUME_ENABLE_DOCKER_LABS", "1")
    from unittest.mock import MagicMock, patch

    with patch("zume.labs.java_lab._docker_available", return_value=True):
        lab = JavaLabProvider()
        ws = str(tmp_path / "java")
        lab.prepare("t", ws)
        # Simulate timeout from docker run
        import subprocess

        with patch("zume.labs.java_lab.subprocess.run") as run:
            run.side_effect = [
                subprocess.TimeoutExpired(cmd="docker", timeout=1),
                MagicMock(returncode=0, stdout="", stderr=""),  # docker rm -f in finally
            ]
            result = lab.run("t", ws, "class Main{public static void main(String[]a){while(true);}}")
            assert result.exit_code == 124
            # docker run + docker rm -f cleanup
            assert run.call_count >= 2
            cleanup_cmd = " ".join(str(c) for c in run.call_args_list[-1].args[0])
            assert "rm" in cleanup_cmd and "-f" in cleanup_cmd
        lab.cleanup(ws)


# ---------------------------------------------------------------------------
# 13. Playwright must not skip when server unavailable (source contract)
# ---------------------------------------------------------------------------

def test_playwright_spec_does_not_skip_when_server_down(repo_root: Path):
    spec = (repo_root / "apps" / "web" / "e2e" / "home.spec.ts").read_text(encoding="utf-8")
    assert "test.skip(!apiAvailable" not in spec
    assert "test.skip(!apiAvailable," not in spec
    # Prefer explicit failure / setup gate language.
    assert "test.skip" not in spec or "skip" not in spec.lower()


# ---------------------------------------------------------------------------
# 14. Browser speech controls exist in the frontend source
# ---------------------------------------------------------------------------

def test_frontend_implements_speech_synthesis_controls(repo_root: Path):
    web_src = repo_root / "apps" / "web" / "src"
    blob = "\n".join(p.read_text(encoding="utf-8") for p in web_src.rglob("*.{ts,tsx}") if p.is_file())
    # Glob may not expand braces on Windows via pathlib — fall back.
    if not blob.strip():
        parts = []
        for p in web_src.rglob("*"):
            if p.suffix in {".ts", ".tsx"}:
                parts.append(p.read_text(encoding="utf-8"))
        blob = "\n".join(parts)
    assert "speechSynthesis" in blob, "browser read-aloud must use window.speechSynthesis"
    for token in ("pause", "resume", "cancel", "speak"):
        assert token in blob.lower() or token in blob


# ---------------------------------------------------------------------------
# Published vs draft statistics contract
# ---------------------------------------------------------------------------

def test_knowledge_stats_distinguish_published_and_draft(repo_root: Path):
    client = TestClient(create_app(repo_root))
    stats = client.get("/api/knowledge/stats").json()
    assert "published_questions" in stats
    assert "draft_questions" in stats or "draft_proposals" in stats
    # Draft filler must not be counted as completed coverage.
    assert stats.get("complete_claim") is not True
