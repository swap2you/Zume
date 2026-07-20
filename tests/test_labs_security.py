"""Security contracts for the local exercise labs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from zume.labs.api_lab import ApiLabProvider
from zume.labs.java_lab import JavaLabProvider
from zume.labs.sql_lab import SqlLabProvider


def test_sql_denies_writes_and_enforces_deadline(tmp_path: Path):
    lab = SqlLabProvider()
    workspace = str(tmp_path / "sql")
    assert lab.run("sql", workspace, "INSERT INTO employees VALUES (99, 'x', 'x', 1)").exit_code == 1
    result = lab.run(
        "sql", workspace,
        "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r WHERE n < 100000000) "
        "SELECT COUNT(*) FROM r",
    )
    assert result.exit_code == 1
    assert "timeout" in result.stderr.lower()


def test_api_rejects_other_local_ports(tmp_path: Path):
    lab = ApiLabProvider()
    result = lab.run("api", str(tmp_path / "api"), json.dumps({
        "url": "http://127.0.0.1:9999/admin",
    }))
    assert result.exit_code == 3
    assert "8765" in result.stderr


def test_java_timeout_removes_named_container(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ZUME_ENABLE_DOCKER_LABS", "1")
    with patch("zume.labs.java_lab._docker_available", return_value=True), patch(
        "zume.labs.java_lab.subprocess.run",
        side_effect=[
            subprocess.TimeoutExpired(cmd="docker", timeout=60),
            MagicMock(returncode=0, stdout="", stderr=""),
            MagicMock(returncode=0, stdout="", stderr=""),
        ],
    ) as run:
        result = JavaLabProvider().run("java", str(tmp_path / "java"), "class Main {}")
    assert result.exit_code == 124
    cleanup = [call.args[0] for call in run.call_args_list if call.args[0][1:3] == ["rm", "-f"]]
    assert cleanup
    assert cleanup[0][-1].startswith("zume-java-")
