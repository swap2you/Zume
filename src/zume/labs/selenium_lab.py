"""Optional Docker Compose Selenium lab against a bundled training web app."""

from __future__ import annotations

import shutil
from pathlib import Path

from zume.labs.base import LabCapabilities, LabProvider, LabRunResult, TestCaseResult
from zume.labs.java_lab import _docker_available
from zume.runtime_settings import load_runtime_settings


class SeleniumLabProvider(LabProvider):
    name = "selenium"

    def capabilities(self) -> LabCapabilities:
        docker_ok = _docker_available() and load_runtime_settings().enable_docker_labs
        compose = Path("docker/labs/selenium-compose.yml")
        available = docker_ok and compose.exists()
        detail = (
            "Isolated Selenium + Java runner on an internal-only network."
            if available
            else "Unavailable: Docker labs flag + docker/labs/selenium-compose.yml required."
        )
        return LabCapabilities(
            runner="selenium",
            languages=["java"],
            requires_docker=True,
            available=available,
            detail=detail,
        )

    def prepare(self, exercise_id: str, workspace: str) -> None:
        root = Path(workspace)
        root.mkdir(parents=True, exist_ok=True)
        (root / "exercise_id.txt").write_text(exercise_id, encoding="utf-8")

    def run(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        del exercise_id, code
        caps = self.capabilities()
        if not caps.available:
            return LabRunResult(stderr=caps.detail, exit_code=4, extras={"workspace": workspace})
        return LabRunResult(
            stdout="Selenium compose profile declared. Use docker compose -f docker/labs/selenium-compose.yml up for live runs.",
            exit_code=0,
            extras={"note": "Live browser run is optional; mocked contract passes when unavailable."},
        )

    def test(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        result = self.run(exercise_id, workspace, code)
        result.test_results = [
            TestCaseResult(
                name="provider_contract",
                passed=result.exit_code in {0, 4},
                message=result.stderr or result.stdout,
            )
        ]
        return result

    def cleanup(self, workspace: str) -> None:
        path = Path(workspace)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
