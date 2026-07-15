"""System doctor — reports provider state without secret values."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any

from zume.labs import list_lab_capabilities
from zume.runtime_settings import load_runtime_settings


def collect_doctor_report() -> dict[str, Any]:
    settings = load_runtime_settings()
    docker = _docker_status()
    return {
        "openai_provider": "configured" if settings.openai_api_key_configured else "not configured",
        "web_search": "enabled" if settings.enable_web_search else "disabled",
        "tts": (
            "OpenAI configured"
            if settings.openai_api_key_configured
            else "browser available"
        ),
        "realtime_voice": "enabled flag" if settings.enable_realtime else "disabled",
        "docker_labs": "available" if docker["available"] and settings.enable_docker_labs else "unavailable",
        "secrets_source": "external secret source configured" if settings.secrets_dir_configured else "environment/offline",
        "bind_host": settings.bind_host,
        "openai_model_alias": settings.openai_model if settings.openai_api_key_configured else None,
        "labs": [c.model_dump() for c in list_lab_capabilities()],
        "java_on_host": shutil.which("java") is not None,
        "node_on_host": shutil.which("node") is not None,
        "docker": docker,
        # Explicitly never include key material.
        "notes": [
            "Doctor never prints API key prefixes or suffixes.",
            "Candidate processing does not call AI providers by default.",
        ],
    }


def format_doctor_text(report: dict[str, Any] | None = None) -> str:
    report = report or collect_doctor_report()
    lines = [
        f"OpenAI provider: {report['openai_provider']}",
        f"Web search: {report['web_search']}",
        f"TTS: {report['tts']}",
        f"Realtime voice: {report['realtime_voice']}",
        f"Docker labs: {report['docker_labs']}",
        f"Secrets: {report['secrets_source']}",
        f"Bind host: {report['bind_host']}",
    ]
    return "\n".join(lines)


def _docker_status() -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return {
            "available": proc.returncode == 0,
            "server_version": proc.stdout.strip() if proc.returncode == 0 else "",
        }
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return {"available": False, "server_version": ""}
