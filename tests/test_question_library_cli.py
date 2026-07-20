"""CLI coverage for knowledge review-report and review-mode helpers."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from zume.cli import app

runner = CliRunner()


def test_knowledge_review_report_and_content_quality(repo_root: Path, monkeypatch, tmp_path: Path):
    monkeypatch.chdir(repo_root)
    out = tmp_path / "review.md"
    result = runner.invoke(app, ["knowledge", "review-report", "--output", str(out)])
    assert result.exit_code == 0, result.output
    assert out.exists()
    assert "Reviewed published questions" in out.read_text(encoding="utf-8")
    quality = runner.invoke(app, ["knowledge", "content-quality"])
    assert quality.exit_code == 0, quality.output
    assert "PASS" in quality.output


def test_review_reset_command(repo_root: Path, monkeypatch, tmp_path: Path):
    monkeypatch.chdir(repo_root)
    monkeypatch.setattr("zume.review_mode.review_workspace", lambda _root: tmp_path / "rw")
    result = runner.invoke(app, ["review", "reset"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "rw" / ".zume-review-mode").exists()
