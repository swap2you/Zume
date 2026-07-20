"""Coverage for Question Library correction modules (facets, enrich, review mode)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from zume.knowledge.enrich import freshness_state, question_payload, resolve_references
from zume.knowledge.facets import collect_facets
from zume.knowledge.loader import load_all_questions, load_sources
from zume.review_mode import apply_review_environment, prepare_review_workspace, reset_review_workspace
from zume.server.app import create_app


def test_collect_facets_draft_and_gaps_modes(repo_root: Path):
    reviewed = collect_facets(repo_root, "reviewed")
    draft = collect_facets(repo_root, "draft")
    gaps = collect_facets(repo_root, "gaps")
    assert reviewed["mode"] == "reviewed"
    assert draft["mode"] == "draft"
    assert draft["counts"]["questions"] >= 0
    assert gaps["gap_summary"] is not None
    assert reviewed["domains"]
    client = TestClient(create_app(repo_root))
    assert client.get("/api/knowledge/facets", params={"mode": "reviewed"}).status_code == 200
    for sort in ("priority", "frequency", "recently_verified", "basic_to_advanced",
                 "advanced_to_basic", "domain_az", "recommended"):
        listed = client.get(
            "/api/knowledge/questions",
            params={"mode": "reviewed", "sort": sort, "has_followups": "true", "limit": 3},
        )
        assert listed.status_code == 200, sort
        assert "request_id" in listed.json()
    domain = reviewed["domains"][0]["value"]
    filtered = client.get(
        "/api/knowledge/questions",
        params={
            "mode": "reviewed", "domain": domain, "priority": "P0",
            "freshness": "", "level": "", "limit": 5,
        },
    )
    assert filtered.status_code == 200
    detail = client.get(f"/api/knowledge/questions/{listed.json()['items'][0]['id']}")
    assert detail.status_code == 200
    assert detail.json()["references"][0]["source_url"].startswith("https://")
    search = client.get("/api/knowledge/search", params={"q": "explicit wait Selenium", "limit": 5})
    assert search.status_code == 200
    assert search.json()["items"]
    gaps_api = client.get("/api/knowledge/gaps")
    assert gaps_api.status_code == 200
    assert gaps_api.json()["complete_claim"] is False
    from zume.serve import ensure_local_bind, port_available
    ensure_local_bind("127.0.0.1")
    assert port_available("127.0.0.1", 65530) is True


def test_resolve_references_are_absolute(repo_root: Path):
    sources = load_sources(repo_root / "knowledge")
    questions = [
        q for q in load_all_questions(repo_root / "knowledge")
        if q.status == "published" and q.review_status == "reviewed" and q.references
    ]
    assert questions
    payload = question_payload(questions[0], sources)
    assert payload["freshness_state"] in {"current", "due_soon", "stale"}
    for ref in resolve_references(questions[0], sources):
        assert ref["source_url"].startswith("https://")
        assert ref["source_name"]
    assert freshness_state(questions[0]) in {"current", "due_soon", "stale"}


def test_review_workspace_is_isolated(repo_root: Path, tmp_path: Path, monkeypatch):
    monkeypatch.setattr("zume.review_mode.review_workspace", lambda _root: tmp_path / "review-workspace")
    apply_review_environment()
    workspace = prepare_review_workspace(repo_root, reset=True)
    assert (workspace / ".zume-review-mode").exists()
    assert (workspace / "candidates").is_dir()
    assert (workspace / "knowledge").exists()
    assert not (workspace / "apps" / "web" / "node_modules").exists()
    reset = reset_review_workspace(repo_root)
    assert reset.exists()
    client = TestClient(create_app(workspace, review_mode=True))
    health = client.get("/api/health").json()
    assert health["review_mode"] is True
    assert "X-Robots-Tag" in client.get("/api/health").headers
    assert client.get("/api/knowledge/facets").status_code == 200
    assert client.get("/api/candidates").json()["items"] == []


def test_build_info_endpoint(repo_root: Path):
    client = TestClient(create_app(repo_root, review_mode=True))
    response = client.get("/api/build-info")
    assert response.status_code == 200
    payload = response.json()
    assert payload["version"]
    assert payload["reviewed_questions"] >= 1
    assert payload["reviewed_exercises"] >= 1
    assert len(payload["knowledge_digest"]) == 64
    assert payload["git_sha"]
