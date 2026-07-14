"""Phase 7 — candidate privacy lifecycle (export / archive / delete). Fictional data only."""

import zipfile
from datetime import date
from pathlib import Path

import pytest
import typer

from zume import candidate as cand
from zume import cli
from zume import pipeline
from zume.storage import Storage

RESUME = """Test Person
Senior Automation Engineer with 9 years of experience.
Skills: Java, Selenium, TestNG, REST Assured, Oracle SQL, Jenkins.
Built and maintained a Java Selenium framework and owned delivery.
"""


def _make_candidate(tmp_root: Path) -> Path:
    result = pipeline.run_intake(tmp_root, resume_text=RESUME, name="Test Person",
                                 today=date(2026, 7, 1))
    return result.folder


def test_export_creates_zip_package(tmp_root: Path):
    folder = _make_candidate(tmp_root)
    package = cand.export_candidate(tmp_root, folder, "output")
    assert package.exists()
    with zipfile.ZipFile(package) as zf:
        assert any(name.endswith("candidate.json") for name in zf.namelist())


def test_archive_moves_folder_under_ignored_tree(tmp_root: Path):
    folder = _make_candidate(tmp_root)
    target = cand.archive_candidate(tmp_root, folder, "_archive")
    assert not folder.exists()
    assert target.exists()
    assert "_archive" in str(target)


def test_delete_preview_does_not_delete(tmp_root: Path):
    folder = _make_candidate(tmp_root)
    with pytest.raises(typer.Exit) as exc:
        cli.candidate_delete_cmd(candidate=folder.name, confirm=False)
    assert exc.value.exit_code == 0
    assert folder.exists()  # preview must not delete


def test_delete_confirm_removes_folder_and_db_rows(tmp_root: Path):
    folder = _make_candidate(tmp_root)
    with Storage(tmp_root) as storage:
        cid = storage.find_candidate_id(folder.name)
        assert cid is not None
        plan = storage.deletion_plan(folder.name)
        assert plan["candidates"] == 1

    cli.candidate_delete_cmd(candidate=folder.name, confirm=True)

    assert not folder.exists()
    with Storage(tmp_root) as storage:
        assert storage.find_candidate_id(folder.name) is None
        # all child rows gone as well
        for table in Storage.CHILD_TABLES:
            rows = storage.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            assert rows == 0
