"""Ask Zume and workspace API tests (mocked providers, no live keys)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from zume.server.app import create_app


def test_ask_offline_retrieval(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.post("/api/ask", json={"question": "What is a HashMap key equality contract in Java?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"]
    assert body["source_mode"] in {"local_library", "offline_unavailable", "mixed"}


def test_ask_rejects_candidate_pii(repo_root: Path):
    client = TestClient(create_app(repo_root))
    resp = client.post(
        "/api/ask",
        json={"question": "Resume: Jane Doe jane@example.com notes from interview"},
    )
    assert resp.status_code == 400


def test_path_traversal_rejected(repo_root: Path):
    from zume.server import routes_workspace as rw

    try:
        rw._safe_candidate_root(repo_root, "../secrets")
        assert False, "expected rejection"
    except Exception as exc:  # noqa: BLE001
        assert "traversal" in str(exc).lower() or "invalid" in str(exc).lower()


def test_labs_and_audio_endpoints(repo_root: Path):
    client = TestClient(create_app(repo_root))
    assert client.get("/api/labs").status_code == 200
    speak = client.post("/api/audio/speak", json={"text": "Explain waiting strategies"})
    assert speak.status_code == 200
    assert "disclosure" in speak.json()
    rt = client.get("/api/audio/realtime/session")
    assert rt.status_code == 200
    assert "sk-" not in str(rt.json()).lower()


def test_sql_lab_runs_offline(repo_root: Path, tmp_path: Path):
    from zume.labs import get_lab_provider

    lab = get_lab_provider("sql")
    ws = str(tmp_path / "sqlws")
    lab.prepare("demo", ws)
    result = lab.run("demo", ws, "SELECT name FROM employees ORDER BY id")
    assert result.exit_code == 0
    assert "Ada" in result.stdout
    lab.cleanup(ws)
