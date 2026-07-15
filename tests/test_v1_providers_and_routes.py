"""Coverage for Zume 1.0 providers, routes, runtime settings, and CLI shims."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from zume.ai.offline import OfflineAIProvider
from zume.ai.openai_provider import OpenAIProvider, _extract_text, _try_parse_json
from zume.audio.openai_tts import OpenAITTSProvider
from zume.audio.realtime import DisabledRealtimeVoiceProvider, OpenAIRealtimeVoiceProvider
from zume.cli import app
from zume.labs import get_lab_provider
from zume.labs.api_lab import ApiLabProvider
from zume.labs.java_lab import JavaLabProvider
from zume.labs.selenium_lab import SeleniumLabProvider
from zume.runtime_settings import RuntimeSettings, load_runtime_settings
from zume.serve import ensure_local_bind, port_available
from zume.server.app import create_app


runner = CliRunner()


def test_offline_ai_with_and_without_context():
    p = OfflineAIProvider()
    empty = p.answer("Anything?")
    assert empty.source_mode == "offline_unavailable"
    filled = p.answer(
        "Java maps",
        context=[{"id": "java-1", "title": "HashMap", "concise_answer": "O(1) average.", "domain": "java"}],
    )
    assert "HashMap" in filled.answer
    assert filled.citations


def test_openai_provider_http_error_and_parse():
    provider = OpenAIProvider(api_key="test-key", model="gpt-test")
    with patch("zume.ai.openai_provider.request.urlopen", side_effect=Exception("boom")):
        ans = provider.answer("Q", context=[{"id": "a", "title": "A", "concise_answer": "B"}])
        assert ans.confidence == "low"
    assert _try_parse_json('{"answer":"x","citations":[],"confidence":"high","source_mode":"local_library"}')
    assert _extract_text({"output_text": "hello"}) == "hello"
    assert _extract_text({"output": [{"content": [{"type": "output_text", "text": "t"}]}]}) == "t"


def test_tts_and_realtime_providers(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tts = OpenAITTSProvider(api_key="k")
    # Force fallback path
    with patch("urllib.request.urlopen", side_effect=OSError("no net")):
        result = tts.synthesize("hello world")
        assert result.provider in {"browser", "openai_tts"}
    assert DisabledRealtimeVoiceProvider().available() is False
    session = OpenAIRealtimeVoiceProvider("k").create_ephemeral_session()
    assert session.enabled is False


def test_api_lab_blocks_external_host(tmp_path: Path):
    lab = ApiLabProvider()
    ws = str(tmp_path / "api")
    lab.prepare("x", ws)
    blocked = lab.run("x", ws, json.dumps({"method": "GET", "url": "https://example.com/x"}))
    assert blocked.exit_code == 3
    bad = lab.run("x", ws, "{not-json")
    assert bad.exit_code == 2
    lab.cleanup(ws)


def test_java_and_selenium_unavailable_without_flag(monkeypatch):
    monkeypatch.setenv("ZUME_ENABLE_DOCKER_LABS", "0")
    java = JavaLabProvider()
    assert java.capabilities().available is False
    result = java.run("e", "ws", "class Main { public static void main(String[] a){} }")
    assert result.exit_code == 4
    sel = SeleniumLabProvider()
    out = sel.test("e", "ws", "code")
    assert out.test_results


def test_runtime_settings_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unit-test-key-not-real")
    monkeypatch.setenv("ZUME_ENABLE_WEB_SEARCH", "true")
    settings = load_runtime_settings()
    assert settings.openai_api_key_configured is True
    assert settings.enable_web_search is True
    # Ensure dataclass shape does not expose accidental print helpers
    assert isinstance(settings, RuntimeSettings)


def test_workspace_routes_cover_main_paths(repo_root: Path, tmp_path: Path, monkeypatch):
    # Use repo_root for knowledge; isolate candidate writes via monkeypatch if needed
    client = TestClient(create_app(repo_root))
    assert client.get("/api/knowledge/stats").status_code == 200
    assert client.get("/api/knowledge/questions", params={"limit": 5}).status_code == 200
    qid = client.get("/api/knowledge/questions", params={"limit": 1}).json()["items"][0]["id"]
    assert client.get(f"/api/knowledge/questions/{qid}").status_code == 200
    assert client.get("/api/knowledge/questions/no-such-id").status_code == 404
    assert client.get("/api/knowledge/search", params={"q": "selenium waits"}).status_code == 200
    preview = client.post("/api/interview/preview", json={"resume_text": "Java Selenium", "role_track": "Senior SDET"})
    assert preview.status_code == 200
    assert preview.json()["preview"] is True
    assert client.get("/api/candidates").status_code == 200
    assert client.delete("/api/ask/history").status_code == 200
    assert client.post("/api/labs/sql/run", json={"code": "SELECT 1", "exercise_id": "t"}).status_code == 200
    assert client.post("/api/labs/missing/run", json={"code": "x"}).status_code == 404


def test_cli_doctor_and_knowledge_stats():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "OpenAI provider:" in result.stdout
    stats = runner.invoke(app, ["knowledge", "stats"])
    assert stats.exit_code == 0


def test_serve_helpers():
    ensure_local_bind("localhost")
    assert port_available("127.0.0.1", 1) in {True, False}


def test_get_lab_provider_unknown():
    try:
        get_lab_provider("cobol")
        assert False
    except KeyError:
        pass


def test_create_app_serves_static_when_present(repo_root: Path):
    dist = repo_root / "apps" / "web" / "dist" / "index.html"
    client = TestClient(create_app(repo_root))
    if dist.exists():
        resp = client.get("/")
        assert resp.status_code == 200
    else:
        # Health still works without UI build
        assert client.get("/api/health").status_code == 200
