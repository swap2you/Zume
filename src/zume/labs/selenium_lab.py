"""Optional Docker Compose Selenium lab against the bundled training page."""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from zume.labs.base import LabCapabilities, LabProvider, LabRunResult, TestCaseResult
from zume.labs.java_lab import _docker_available
from zume.runtime_settings import load_runtime_settings

_COMPOSE = Path("docker/labs/selenium-compose.yml")


class SeleniumLabProvider(LabProvider):
    name = "selenium"

    def capabilities(self) -> LabCapabilities:
        enabled = load_runtime_settings().enable_docker_labs
        available = enabled and _docker_available() and _COMPOSE.exists()
        detail = ("Docker Compose runs the training-page assertion."
                  if available else
                  "Unavailable: enable ZUME_ENABLE_DOCKER_LABS, install Docker, and retain the Selenium compose file.")
        return LabCapabilities(runner="selenium", languages=["java"], requires_docker=True,
                               available=available, detail=detail)

    def prepare(self, exercise_id: str, workspace: str) -> None:
        root = Path(workspace)
        root.mkdir(parents=True, exist_ok=True)
        (root / "exercise_id.txt").write_text(exercise_id, encoding="utf-8")

    def run(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        del exercise_id, workspace, code
        caps = self.capabilities()
        if not caps.available:
            return LabRunResult(stderr=caps.detail, exit_code=4)
        started = time.perf_counter()
        cmd = ["docker", "compose", "-f", str(_COMPOSE), "--profile", "runner",
               "run", "--rm", "java-runner"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
            return LabRunResult(
                stdout=proc.stdout[-8000:], stderr=proc.stderr[-8000:], exit_code=proc.returncode,
                duration_ms=int((time.perf_counter() - started) * 1000),
                truncated=len(proc.stdout) > 8000 or len(proc.stderr) > 8000,
            )
        except subprocess.TimeoutExpired:
            return LabRunResult(stderr="Selenium lab timed out.", exit_code=124,
                                duration_ms=int((time.perf_counter() - started) * 1000))
        except (FileNotFoundError, OSError) as exc:
            return LabRunResult(stderr=f"Selenium Docker Compose unavailable: {type(exc).__name__}.",
                                exit_code=4, duration_ms=int((time.perf_counter() - started) * 1000))

    def test(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        result = self.run(exercise_id, workspace, code)
        result.test_results = [TestCaseResult(
            name="training_page_assertion", passed=result.exit_code == 0,
            message=result.stderr or result.stdout,
        )]
        return result

    def cleanup(self, workspace: str) -> None:
        shutil.rmtree(Path(workspace), ignore_errors=True)
