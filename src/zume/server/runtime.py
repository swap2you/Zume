"""Request-scoped workspace root for the local API.

Review mode serves from ``data/review-workspace``. Routes must use that root,
not ``find_root()`` (the real repository), or candidate isolation breaks.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from pathlib import Path

from zume import config as cfg

_active_root: ContextVar[Path | None] = ContextVar("zume_api_root", default=None)


def bind_root(root: Path) -> Token[Path | None]:
    return _active_root.set(root.resolve())


def reset_root(token: Token[Path | None]) -> None:
    _active_root.reset(token)


def current_root() -> Path:
    bound = _active_root.get()
    if bound is not None:
        return bound
    return cfg.find_root()
