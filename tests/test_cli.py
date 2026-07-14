"""CLI integration coverage for the intake/finalize/candidate/db commands.

Drives the Typer app end-to-end in an isolated repo (the ``tmp_root`` fixture
chdirs into a temp copy of config + examples), exercising the command wiring
that the unit tests bypass by calling the pipeline directly.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from zume.cli import app

runner = CliRunner()


def _examples(tmp_root: Path) -> Path:
    return tmp_root / "examples" / "fictional-candidate"


def _intake(tmp_root: Path):
    ex = _examples(tmp_root)
    result = runner.invoke(app, [
        "intake", "--resume", str(ex / "resume.txt"),
        "--schedule-details", str(ex / "schedule.txt"),
    ])
    assert result.exit_code == 0, result.output
    folder = next(p for p in (tmp_root / "candidates").iterdir()
                  if (p / "_internal" / "candidate.json").exists())
    return folder, result


def test_intake_then_validate_and_finalize(tmp_root: Path):
    folder, result = _intake(tmp_root)
    assert "Deliverables:" in result.output
    assert "waiting for interview notes" in result.output.lower()

    # The temp repo is not a git repo, so the privacy (git check-ignore) portion
    # of validate cannot pass; the structural checks still run and must pass.
    validated = runner.invoke(app, ["validate", "--candidate", folder.name, "--no-render"])
    assert "deliverables present" in validated.output
    assert "passed," in validated.output

    ex = _examples(tmp_root)
    final = runner.invoke(app, [
        "finalize", "--candidate", folder.name,
        "--notes", str(ex / "interview-notes.txt"), "--leadership",
    ])
    assert final.exit_code == 0, final.output
    assert (folder / "deliverables" / "06_Final_Interview_Evaluation.docx").exists()


def test_finalize_blocks_without_prior_intake(tmp_root: Path):
    (tmp_root / "candidates").mkdir(exist_ok=True)
    result = runner.invoke(app, [
        "finalize", "--candidate", "Nobody_2026-01-01", "--notes", "some notes",
    ])
    assert result.exit_code != 0


def test_candidate_list_export_and_cleanup(tmp_root: Path):
    folder, _ = _intake(tmp_root)

    listed = runner.invoke(app, ["candidate", "list"])
    assert listed.exit_code == 0
    assert folder.name in listed.output

    exported = runner.invoke(app, ["candidate", "export", "--candidate", folder.name])
    assert exported.exit_code == 0, exported.output
    assert "Exported" in exported.output
    assert list((tmp_root / "output").glob("*.zip"))

    cleanup = runner.invoke(app, ["candidate", "cleanup", "--candidate", folder.name, "--preview"])
    assert cleanup.exit_code == 0
    assert "Cleanup plan" in cleanup.output


def test_candidate_migrate_preview_on_legacy(tmp_root: Path):
    from datetime import date

    from zume import candidate as cand

    _, folder = cand.new_candidate(tmp_root, "Legacy Person", date(2026, 1, 1))
    cand.atomic_write_text(folder / "00-source" / "resume.txt", "text")

    preview = runner.invoke(app, ["candidate", "migrate", "--candidate", folder.name, "--preview"])
    assert preview.exit_code == 0, preview.output
    assert "Migration plan" in preview.output

    applied = runner.invoke(app, ["candidate", "migrate", "--candidate", folder.name, "--apply"])
    assert applied.exit_code == 0, applied.output
    assert (folder / "_internal").is_dir()


def test_db_check_and_backup(tmp_root: Path):
    _intake(tmp_root)

    check = runner.invoke(app, ["db", "check"])
    assert check.exit_code == 0, check.output
    assert "integrity" in check.output.lower()

    backup = runner.invoke(app, ["db", "backup"])
    assert backup.exit_code == 0, backup.output
    assert "validated" in backup.output.lower()
    assert list((tmp_root / "data").glob("zume-backup-*.db"))


def test_intake_do_not_proceed_stops_early(tmp_root: Path):
    weak = tmp_root / "weak.txt"
    weak.write_text("Sam Weak\nManual tester, 2 years. Skills: Postman.\n", encoding="utf-8")
    result = runner.invoke(app, ["intake", "--text-file", str(weak), "--name", "Sam Weak"])
    assert result.exit_code == 0, result.output
    assert "Decision:" in result.output
