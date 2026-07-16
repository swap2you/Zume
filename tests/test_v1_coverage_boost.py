"""Small targeted tests to cover remaining Zume 1.0 branches."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from zume.knowledge.validate import validate_library
from zume.labs.api_lab import ApiLabProvider
from zume.labs.java_lab import JavaLabProvider, _docker_available
from zume.labs.sql_lab import SqlLabProvider
from zume.runtime_settings import _read_openai_key_from_dir, load_runtime_settings
from zume.serve import run_server


def test_runtime_settings_from_secrets_dir(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    secrets = tmp_path / "secs"
    secrets.mkdir()
    (secrets / "OPENAI_API_KEY.txt").write_text("unit-test-key-value\n", encoding="utf-8")
    monkeypatch.setenv("ZUME_SECRETS_DIR", str(secrets))
    settings = load_runtime_settings()
    assert settings.openai_api_key_configured is True
    assert settings.openai_api_key == "unit-test-key-value"
    assert _read_openai_key_from_dir(tmp_path / "missing") is None


def test_api_lab_success_path(tmp_path: Path):
    lab = ApiLabProvider()
    ws = str(tmp_path / "api2")
    lab.prepare("e", ws)

    class Resp:
        status = 200

        def read(self) -> bytes:
            return b'{"ok":true}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    opener = MagicMock()
    opener.open.return_value = Resp()
    with patch("zume.labs.api_lab.request.build_opener", return_value=opener):
        result = lab.run("e", ws, json.dumps({"method": "GET", "path": "/health"}))
        assert result.exit_code == 0
        tested = lab.test("e", ws, json.dumps({"method": "GET", "path": "/health"}))
        assert tested.test_results
    lab.cleanup(ws)


def test_sql_lab_error_and_test(tmp_path: Path):
    lab = SqlLabProvider()
    ws = str(tmp_path / "sql2")
    lab.prepare("e", ws)
    bad = lab.run("e", ws, "SELECT * FROM missing_table")
    assert bad.exit_code == 1
    ok = lab.test("e", ws, "SELECT 1 AS n")
    assert ok.test_results[0].passed
    lab.cleanup(ws)


def test_java_lab_docker_mock_run(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ZUME_ENABLE_DOCKER_LABS", "1")
    with patch("zume.labs.java_lab._docker_available", return_value=True):
        lab = JavaLabProvider()
        assert lab.capabilities().available is True
        ws = str(tmp_path / "java")
        lab.prepare("e", ws)
        proc = MagicMock(returncode=0, stdout="hi", stderr="")
        with patch("zume.labs.java_lab.subprocess.run", return_value=proc):
            result = lab.run("e", ws, "class Main{public static void main(String[]a){}}")
            assert result.exit_code == 0
            tested = lab.test("e", ws, "class Main{public static void main(String[]a){}}")
            assert tested.test_results
        lab.cleanup(ws)
    assert isinstance(_docker_available(), bool)


def test_run_server_mocks_uvicorn(tmp_path: Path):
    with patch("zume.serve.port_available", return_value=True), patch(
        "zume.serve.webbrowser.open"
    ), patch("zume.serve.uvicorn.run") as run:
        run_server(tmp_path, host="127.0.0.1", port=8799, open_browser=True)
        run.assert_called_once()


def test_validate_flags_bad_draft_fixture(tmp_path: Path):
    root = tmp_path
    qdir = root / "knowledge" / "questions" / "java"
    qdir.mkdir(parents=True)
    (root / "knowledge" / "sources.yaml").write_text(
        "sources:\n  - {id: java-oracle-docs, name: x, url: http://example.com, family: f}\n",
        encoding="utf-8",
    )
    (root / "knowledge" / "taxonomy.yaml").write_text(
        "domains:\n  - {id: java, tier: A}\n",
        encoding="utf-8",
    )
    (qdir / "basic.yaml").write_text(
        """
records:
  - id: java-bad
    domain: java
    subdomain: x
    title: bad
    level: basic
    priority: P0
    frequency: common
    question: TODO fill this
    concise_answer: ""
    recommended_answer: ""
    follow_ups: []
    references: []
    last_verified: "not-a-date"
    status: published
""",
        encoding="utf-8",
    )
    from zume.knowledge.loader import clear_loader_cache

    clear_loader_cache()
    errors = validate_library(root)
    assert errors
