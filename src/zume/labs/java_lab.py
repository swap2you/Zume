"""Docker-isolated Java lab. Never runs submitted code on the host."""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from zume.labs.base import LabCapabilities, LabProvider, LabRunResult, TestCaseResult
from zume.runtime_settings import load_runtime_settings


class JavaLabProvider(LabProvider):
    name = "java"

    def capabilities(self) -> LabCapabilities:
        docker_ok = _docker_available() and load_runtime_settings().enable_docker_labs
        return LabCapabilities(
            runner="java",
            languages=["java"],
            requires_docker=True,
            available=docker_ok,
            detail=(
                "Docker-isolated compile/run with network=none, non-root, limits."
                if docker_ok
                else "Unavailable: enable ZUME_ENABLE_DOCKER_LABS and install Docker."
            ),
        )

    def prepare(self, exercise_id: str, workspace: str) -> None:
        root = Path(workspace)
        root.mkdir(parents=True, exist_ok=True)
        (root / "exercise_id.txt").write_text(exercise_id, encoding="utf-8")
        src = root / "src"
        src.mkdir(exist_ok=True)

    def run(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        del exercise_id
        caps = self.capabilities()
        if not caps.available:
            return LabRunResult(stderr=caps.detail, exit_code=4)
        started = time.perf_counter()
        root = Path(workspace)
        main = root / "src" / "Main.java"
        main.write_text(code, encoding="utf-8")
        # Pin a public image tag; digest pinning can be supplied via docker/labs later.
        image = "eclipse-temurin:17-jdk-jammy"
        cmd = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--user",
            "1000:1000",
            "--memory",
            "512m",
            "--cpus",
            "1.0",
            "--pids-limit",
            "256",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "-v",
            f"{root.resolve()}:/work:rw",
            "-w",
            "/work",
            image,
            "bash",
            "-lc",
            "javac src/Main.java && java -cp src Main",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
            return LabRunResult(
                stdout=proc.stdout[-8000:],
                stderr=proc.stderr[-8000:],
                exit_code=proc.returncode,
                duration_ms=int((time.perf_counter() - started) * 1000),
                truncated=len(proc.stdout) > 8000 or len(proc.stderr) > 8000,
            )
        except subprocess.TimeoutExpired:
            return LabRunResult(stderr="Java lab timed out; container removed via --rm.", exit_code=124)
        except FileNotFoundError:
            return LabRunResult(stderr="Docker binary not found.", exit_code=4)

    def test(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        result = self.run(exercise_id, workspace, code)
        result.test_results = [
            TestCaseResult(name="compile_and_run", passed=result.exit_code == 0, message=result.stderr or "ok")
        ]
        return result

    def cleanup(self, workspace: str) -> None:
        path = Path(workspace)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def _docker_available() -> bool:
    try:
        proc = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return proc.returncode == 0 and bool(proc.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False
