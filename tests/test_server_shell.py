"""Phase 1 server shell and provider interface tests."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from zume.ai import OfflineAIProvider, get_ai_provider
from zume.audio import get_realtime_provider, get_speech_provider
from zume.doctor import collect_doctor_report, format_doctor_text
from zume.labs import list_lab_capabilities
from zume.serve import ensure_local_bind, port_available
from zume.server.app import create_app


def test_health_version_doctor(tmp_path: Path):
    client = TestClient(create_app(tmp_path))
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/version").json()["name"] == "zume"
    doctor = client.get("/api/doctor").json()
    assert doctor["openai_provider"] in {"configured", "not configured"}
    assert "sk-" not in str(doctor).lower()
    assert "api_key" not in str(doctor).lower() or doctor.get("openai_provider")


def test_offline_providers_need_no_keys():
    assert isinstance(get_ai_provider(), OfflineAIProvider) or get_ai_provider().available()
    assert get_speech_provider().available()
    session = get_realtime_provider().create_ephemeral_session()
    assert session.enabled is False or isinstance(session.client_secret, str)


def test_lab_capabilities_list():
    caps = list_lab_capabilities()
    names = {c.runner for c in caps}
    assert {"sql", "api", "java", "selenium"} <= names


def test_refuse_non_local_bind():
    try:
        ensure_local_bind("0.0.0.0")
        assert False, "expected ValueError"
    except ValueError:
        pass
    ensure_local_bind("127.0.0.1")


def test_doctor_text_has_no_secret_material():
    text = format_doctor_text(collect_doctor_report())
    assert "OpenAI provider:" in text
    assert "sk-" not in text


def test_port_probe():
    assert isinstance(port_available("127.0.0.1", 9), bool)
