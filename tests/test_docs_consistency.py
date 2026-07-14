"""Lockdown Part 9 — canonical current documentation must not reintroduce the
retired v1 workflow. Legacy reference files under docs/reference/legacy/ are
explicitly allowed to contain historical terminology and are NOT scanned."""

from __future__ import annotations

from pathlib import Path

import pytest

CANONICAL_DOCS = [
    "README.md",
    "AGENTS.md",
    "CURSOR_START_HERE.md",
    "docs/ZUME_DAILY_USE_GUIDE.md",
    "docs/ZUME_TROUBLESHOOTING_GUIDE.md",
]

# Phrases that must not appear in current operating instructions.
FORBIDDEN = [
    "99-final",
    "Duration: 90 minutes",
    "90-minute",
    "90 minute",
    # Retired numbered candidate-workflow folders.
    "00-source",
    "01-screening",
    "02-schedule",
    "03-interview-prep",
    "04-interview",
    "05-feedback",
    "06-communications",
    # Retired four-step commands recommended as daily use (invocation form).
    "zume filter-resume",
    "zume interview-prep",
    "zume schedule-interview",
    "zume interview-feedback",
]


@pytest.mark.parametrize("rel", CANONICAL_DOCS)
def test_canonical_doc_has_no_forbidden_legacy_phrase(repo_root: Path, rel: str):
    path = repo_root / rel
    assert path.exists(), f"canonical doc missing: {rel}"
    text = path.read_text(encoding="utf-8")
    offenders = [phrase for phrase in FORBIDDEN if phrase in text]
    assert offenders == [], f"{rel} contains forbidden legacy phrase(s): {offenders}"


def test_canonical_docs_point_to_the_two_command_workflow(repo_root: Path):
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    assert "zume intake" in readme
    assert "zume finalize" in readme
    assert "CURSOR_START_HERE.md" in readme
