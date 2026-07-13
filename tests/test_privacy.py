from pathlib import Path

from zume.validation import check_privacy


def test_real_candidate_paths_are_git_ignored(repo_root: Path):
    report = check_privacy(repo_root)
    assert report.ok, report.errors
    assert any("candidates/" in p for p in report.passed)
    assert any("General Docs/" in p for p in report.passed)
    assert any("zume.db" in p for p in report.passed)


def test_gitignore_covers_sensitive_patterns(repo_root: Path):
    content = (repo_root / ".gitignore").read_text(encoding="utf-8")
    for pattern in ("candidates/**", "input/**", "output/**", "data/*.db",
                    "*.pdf", "General Docs/"):
        assert pattern in content
