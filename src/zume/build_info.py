"""Build/corpus identity for stale-server detection."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any

from zume import __version__
from zume.knowledge.facets import collect_facets
from zume.knowledge.loader import load_all_exercises, load_all_questions


def _git_sha(root: Path) -> str:
    env_sha = (os.environ.get("GITHUB_SHA") or os.environ.get("ZUME_GIT_SHA") or "").strip()
    if env_sha:
        return env_sha
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return completed.stdout.strip()
    except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired):
        return "unknown"


def _digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _knowledge_digest(root: Path) -> str:
    knowledge = root / "knowledge"
    questions = sorted(
        (
            q
            for q in load_all_questions(knowledge)
            if q.status == "published" and q.review_status == "reviewed"
        ),
        key=lambda item: item.id,
    )
    exercises = sorted(
        (
            e
            for e in load_all_exercises(knowledge)
            if e.status == "published" and e.review_status == "reviewed"
        ),
        key=lambda item: item.id,
    )
    lines = [f"q:{q.id}:{q.question}" for q in questions]
    lines.extend(f"e:{e.id}:{e.title}" for e in exercises)
    return _digest_bytes("\n".join(lines).encode("utf-8"))


def _frontend_digest(root: Path) -> str:
    candidates = [
        root / "apps" / "web" / "dist" / "index.html",
        root / "src" / "zume" / "server" / "static" / "index.html",
    ]
    for path in candidates:
        if path.is_file():
            return _digest_bytes(path.read_bytes())
    return "missing"


def collect_build_info(root: Path) -> dict[str, Any]:
    """Return a compact identity payload for Settings and pre-flight checks."""
    # Prefer the real repository root when serving from a review workspace.
    repo_root = root
    marker = root / ".zume-review-mode"
    if marker.is_file():
        # review-workspace lives at <repo>/data/review-workspace
        candidate = root.parent.parent
        if (candidate / "pyproject.toml").is_file():
            repo_root = candidate
    facets = collect_facets(root, "reviewed")
    counts = facets.get("counts") or {}
    return {
        "git_sha": _git_sha(repo_root),
        "version": __version__,
        "reviewed_questions": int(counts.get("questions") or 0),
        "reviewed_exercises": int(counts.get("exercises") or 0),
        "knowledge_digest": _knowledge_digest(root),
        "frontend_build_digest": _frontend_digest(root),
        "review_mode_root": str(root.resolve()),
    }
