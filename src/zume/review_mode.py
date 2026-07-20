"""Cowork / local validation review mode helpers.

Review mode:
- binds localhost only (enforced by serve);
- uses a fictional/demo data root under data/review-workspace;
- disables OpenAI live calls unless explicitly enabled;
- disables Docker labs by default;
- never touches real candidate data.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


REVIEW_MARKER = ".zume-review-mode"
# Never deep-copy apps/web (node_modules) into the review workspace.
SHARED_LINKS = (
    "knowledge",
    "config",
    "examples",
    "docs",
    "src",
    "pyproject.toml",
    "apps/web/dist",
)


def review_workspace(root: Path) -> Path:
    return (root / "data" / "review-workspace").resolve()


def prepare_review_workspace(root: Path, *, reset: bool = False) -> Path:
    """Create (or reset) a fictional data root for Cowork validation."""
    workspace = review_workspace(root)
    if reset and workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / REVIEW_MARKER).write_text("review\n", encoding="utf-8")
    for name in ("candidates", "input", "output", "data"):
        (workspace / name).mkdir(parents=True, exist_ok=True)
    for shared in SHARED_LINKS:
        source = root / shared
        target = workspace / shared
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            continue
        try:
            target.symlink_to(source, target_is_directory=source.is_dir())
        except OSError:
            if source.is_dir():
                shutil.copytree(
                    source,
                    target,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("node_modules", ".git", "__pycache__"),
                )
            else:
                shutil.copy2(source, target)
    return workspace


def apply_review_environment() -> None:
    """Force-safe defaults for review validation sessions."""
    os.environ.setdefault("ZUME_ENABLE_DOCKER_LABS", "0")
    os.environ.setdefault("ZUME_ENABLE_OPENAI", "0")
    os.environ.setdefault("ZUME_ENABLE_WEB_SEARCH", "0")


def reset_review_workspace(root: Path) -> Path:
    return prepare_review_workspace(root, reset=True)
