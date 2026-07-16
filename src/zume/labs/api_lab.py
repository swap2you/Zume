"""API lab — requests only against the bundled local mock host."""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from urllib import error, request
from urllib.parse import urlparse

from zume.labs.base import LabCapabilities, LabProvider, LabRunResult, TestCaseResult

DEFAULT_MOCK_PORT = 8765
ALLOWED_ORIGIN = f"http://127.0.0.1:{DEFAULT_MOCK_PORT}"


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        del req, fp, code, msg, headers, newurl
        return None


class ApiLabProvider(LabProvider):
    name = "api"

    def capabilities(self) -> LabCapabilities:
        return LabCapabilities(
            runner="api",
            languages=["http", "json"],
            requires_docker=False,
            available=True,
            detail="Local mock API only; arbitrary internet destinations are rejected.",
        )

    def prepare(self, exercise_id: str, workspace: str) -> None:
        root = Path(workspace)
        root.mkdir(parents=True, exist_ok=True)
        (root / "exercise_id.txt").write_text(exercise_id, encoding="utf-8")

    def run(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        del exercise_id, workspace
        started = time.perf_counter()
        try:
            payload = json.loads(code) if code.strip().startswith("{") else {"method": "GET", "path": code.strip()}
        except json.JSONDecodeError as exc:
            return LabRunResult(stderr=f"Invalid request JSON: {exc}", exit_code=2)
        method = str(payload.get("method") or "GET").upper()
        path = str(payload.get("path") or "/health")
        raw_headers = payload.get("headers") or {}
        headers = raw_headers if isinstance(raw_headers, dict) else {}
        body = payload.get("body")
        url = str(payload.get("url") or f"http://127.0.0.1:{DEFAULT_MOCK_PORT}{path}")
        parsed = urlparse(url)
        if not _is_allowed_url(parsed):
            return LabRunResult(
                stderr=(
                    f"Blocked URL {url!r}. Only the exact origin {ALLOWED_ORIGIN} is allowed; "
                    "use http, no credentials or fragment, and port 8765."
                ),
                exit_code=3,
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        data = None
        if body is not None:
            data = body if isinstance(body, (bytes, bytearray)) else json.dumps(body).encode("utf-8")
        req = request.Request(
            url,
            data=data,
            headers={str(k): str(v) for k, v in headers.items()},
            method=method,
        )
        try:
            opener = request.build_opener(_NoRedirect())
            with opener.open(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                return LabRunResult(
                    stdout=raw,
                    exit_code=0,
                    duration_ms=int((time.perf_counter() - started) * 1000),
                    extras={"status": resp.status, "url": url},
                )
        except error.HTTPError as exc:
            if 300 <= exc.code < 400:
                return LabRunResult(
                    stderr="Redirects are blocked; the mock API must respond directly.",
                    exit_code=3, duration_ms=int((time.perf_counter() - started) * 1000),
                    extras={"url": url},
                )
            return LabRunResult(
                stderr=f"Mock API returned HTTP {exc.code}.", exit_code=1,
                duration_ms=int((time.perf_counter() - started) * 1000), extras={"url": url},
            )
        except error.URLError as exc:
            # Mock server may be down — return structured failure, not crash.
            return LabRunResult(
                stderr=f"Mock API unavailable ({type(exc).__name__}). Start training/mock-api or use fixtures.",
                exit_code=1,
                duration_ms=int((time.perf_counter() - started) * 1000),
                extras={"url": url},
            )

    def test(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        result = self.run(exercise_id, workspace, code)
        ok = result.exit_code == 0
        result.test_results = [TestCaseResult(name="local_mock_request", passed=ok, message=result.stderr or "ok")]
        return result

    def cleanup(self, workspace: str) -> None:
        path = Path(workspace)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def _is_allowed_url(parsed) -> bool:
    try:
        return (
            parsed.scheme == "http"
            and parsed.hostname == "127.0.0.1"
            and parsed.port == DEFAULT_MOCK_PORT
            and not parsed.username
            and not parsed.password
            and not parsed.fragment
        )
    except ValueError:
        return False
