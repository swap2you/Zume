"""Runtime configuration. Never log or expose secret values."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


_OPENAI_FILENAMES = (
    "OPENAI_API_KEY",
    "OPENAI_API_KEY.txt",
    "openai_api_key",
    "openai_api_key.txt",
    "openai.key",
    ".openai_api_key",
)


@dataclass(frozen=True)
class RuntimeSettings:
    openai_api_key_configured: bool
    openai_api_key: str | None
    openai_model: str
    openai_tts_model: str
    openai_tts_voice: str
    enable_web_search: bool
    enable_realtime: bool
    enable_docker_labs: bool
    secrets_dir_configured: bool
    bind_host: str = "127.0.0.1"


def load_runtime_settings() -> RuntimeSettings:
    key = (os.environ.get("OPENAI_API_KEY") or "").strip() or None
    secrets_dir = (os.environ.get("ZUME_SECRETS_DIR") or "").strip()
    secrets_configured = False
    if not key and secrets_dir:
        secrets_configured = True
        key = _read_openai_key_from_dir(Path(secrets_dir))
    elif not key:
        # Approved local default location — inspect filenames only, never recurse projects.
        default = Path(r"C:\AarohanSecrets")
        if default.is_dir():
            secrets_configured = True
            key = _read_openai_key_from_dir(default)
    return RuntimeSettings(
        openai_api_key_configured=bool(key),
        openai_api_key=key,
        openai_model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        openai_tts_model=os.environ.get("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
        openai_tts_voice=os.environ.get("OPENAI_TTS_VOICE", "alloy"),
        enable_web_search=_env_bool("ZUME_ENABLE_WEB_SEARCH", False),
        enable_realtime=_env_bool("ZUME_ENABLE_REALTIME", False),
        enable_docker_labs=_env_bool("ZUME_ENABLE_DOCKER_LABS", False),
        secrets_dir_configured=secrets_configured or bool(secrets_dir),
    )


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_openai_key_from_dir(directory: Path) -> str | None:
    """Read only a clearly named OpenAI credential file. Never print the value."""
    try:
        if not directory.is_dir():
            return None
        # Do not recurse; only immediate children with exact approved names.
        for name in _OPENAI_FILENAMES:
            path = directory / name
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="replace").strip()
                # Support KEY=value files without echoing contents elsewhere.
                if "=" in text and "\n" not in text.strip().split("=", 1)[0]:
                    maybe = text.split("=", 1)[1].strip().strip('"').strip("'")
                    return maybe or None
                lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
                return lines[0] if lines else None
    except OSError:
        return None
    return None
