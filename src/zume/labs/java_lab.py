"""Docker-isolated Java lab. Submitted code never runs on the host."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from zume.labs.base import LabCapabilities, LabProvider, LabRunResult, TestCaseResult
from zume.runtime_settings import load_runtime_settings

_DEFAULT_IMAGE = "eclipse-temurin:17-jdk-jammy"


class JavaLabProvider(LabProvider):
    name = "java"

    def capabilities(self) -> LabCapabilities:
        available = _docker_available() and load_runtime_settings().enable_docker_labs
        detail = ("Docker-isolated Java runner; set ZUME_JAVA_IMAGE to a digest-pinned image."
                  if available else "Unavailable: enable ZUME_ENABLE_DOCKER_LABS and install Docker.")
        return LabCapabilities(runner="java", languages=["java"], requires_docker=True,
                               available=available, detail=detail)

    def prepare(self, exercise_id: str, workspace: str) -> None:
        root = Path(workspace)
        root.mkdir(parents=True, exist_ok=True)
        (root / "exercise_id.txt").write_text(exercise_id, encoding="utf-8")
        (root / "src").mkdir(exist_ok=True)

    def run(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        del exercise_id
        caps = self.capabilities()
        if not caps.available:
            return LabRunResult(stderr=caps.detail, exit_code=4)
        started = time.perf_counter()
        root = Path(workspace).resolve()
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "src" / "Main.java").write_text(code, encoding="utf-8")
        name = f"zume-java-{uuid.uuid4().hex}"
        image = os.environ.get("ZUME_JAVA_IMAGE", _DEFAULT_IMAGE)
        cmd = [
            "docker", "run", "--name", name, "--network", "none", "--user", "1000:1000",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--read-only",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--memory", "512m", "--cpus", "1.0",
            "--pids-limit", "256", "-v", f"{root}:/work:rw", "-w", "/work", image,
            "bash", "-lc", "javac src/Main.java && java -cp src Main",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
            return LabRunResult(
                stdout=proc.stdout[-8000:], stderr=proc.stderr[-8000:], exit_code=proc.returncode,
                duration_ms=int((time.perf_counter() - started) * 1000),
                truncated=len(proc.stdout) > 8000 or len(proc.stderr) > 8000,
            )
        except subprocess.TimeoutExpired:
            return LabRunResult(
                stderr="Java lab timed out; container forcibly removed.", exit_code=124,
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        except FileNotFoundError:
            return LabRunResult(stderr="Docker binary not found.", exit_code=4)
        finally:
            self._remove_container(name)

    @staticmethod
    def _remove_container(name: str) -> None:
        try:
            subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True,
                           timeout=10, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

    def test(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        result = self.run(exercise_id, workspace, code)
        result.test_results = [TestCaseResult(
            name="compile_and_run", passed=result.exit_code == 0, message=result.stderr or "ok",
        )]
        return result

    def cleanup(self, workspace: str) -> None:
        shutil.rmtree(Path(workspace), ignore_errors=True)


def _docker_available() -> bool:
    try:
        proc = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"],
                              capture_output=True, text=True, timeout=5, check=False)
        return proc.returncode == 0 and bool(proc.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False
