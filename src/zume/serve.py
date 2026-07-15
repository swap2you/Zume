"""Local server entry helpers for `zume serve`."""

from __future__ import annotations

import socket
import webbrowser
from pathlib import Path

import uvicorn

from zume.server.app import create_app


def ensure_local_bind(host: str) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError(
            f"Refusing non-local bind host {host!r}. "
            "Zume 1.0 serves only localhost unless you intentionally override after review."
        )


def port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host if host != "localhost" else "127.0.0.1", port)) != 0


def run_server(
    root: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8787,
    open_browser: bool = True,
) -> None:
    ensure_local_bind(host)
    if not port_available(host, port):
        raise RuntimeError(
            f"Port {port} on {host} is unavailable. Choose another with --port or free the process."
        )
    app = create_app(root)
    if open_browser:
        webbrowser.open(f"http://{host}:{port}/")
    uvicorn.run(app, host=host, port=port, log_level="info")
