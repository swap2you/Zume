from datetime import date
from pathlib import Path

import pytest

from zume import candidate as cand


def test_normalize_name():
    assert cand.normalize_name("Aarav Mehta") == ("Aarav", "Mehta")
    assert cand.normalize_name("rasmita mishra") == ("Rasmita", "Mishra")
    assert cand.normalize_name("Rajeev Ranjan Pandey") == ("Rajeev Ranjan", "Pandey")
    assert cand.normalize_name("Cher") == ("Cher", "Unknown")
    with pytest.raises(ValueError):
        cand.normalize_name("12345 !!!")


def test_folder_name_contract():
    name = cand.folder_name_for("Aarav", "Mehta", date(2026, 7, 13))
    assert name == "Mehta_Aarav_2026-07-13"
    multi = cand.folder_name_for("Rajeev Ranjan", "Pandey", date(2026, 7, 13))
    assert multi == "Pandey_RajeevRanjan_2026-07-13"


def test_new_candidate_creates_contract_folders(tmp_root: Path):
    candidate, folder = cand.new_candidate(tmp_root, "Aarav Mehta", date(2026, 7, 13))
    assert folder.name == "Mehta_Aarav_2026-07-13"
    for sub in cand.SUBFOLDERS:
        assert (folder / sub).is_dir()
    assert (folder / "candidate.json").exists()
    assert candidate.status == "RECEIVED"
    assert candidate.status_history[0].status == "RECEIVED"


def test_new_candidate_is_idempotent(tmp_root: Path):
    first, folder1 = cand.new_candidate(tmp_root, "Aarav Mehta", date(2026, 7, 13))
    second, folder2 = cand.new_candidate(tmp_root, "Aarav Mehta", date(2026, 7, 13))
    assert folder1 == folder2
    assert second.created_date == first.created_date


def test_atomic_write_and_versioning(tmp_path: Path):
    target = tmp_path / "out" / "report.docx"
    assert cand.versioned_write_bytes(target, b"v1") is True
    assert target.read_bytes() == b"v1"
    # identical content: skipped, no version archive
    assert cand.versioned_write_bytes(target, b"v1") is False
    assert not target.with_name("report__v1.docx").exists()
    # changed content: previous version archived
    assert cand.versioned_write_bytes(target, b"v2") is True
    assert target.read_bytes() == b"v2"
    assert target.with_name("report__v1.docx").read_bytes() == b"v1"
    assert cand.versioned_write_bytes(target, b"v3") is True
    assert target.with_name("report__v2.docx").read_bytes() == b"v2"


def test_copy_source_file_never_overwrites(tmp_root: Path, tmp_path: Path):
    _, folder = cand.new_candidate(tmp_root, "Aarav Mehta", date(2026, 7, 13))
    src = tmp_path / "resume.txt"
    src.write_text("original", encoding="utf-8")
    record1 = cand.copy_source_file(folder, src, kind="resume")
    stored = folder / record1.stored_path
    assert stored.read_text(encoding="utf-8") == "original"
    # same name, different content -> stored under a versioned name
    src.write_text("changed", encoding="utf-8")
    record2 = cand.copy_source_file(folder, src, kind="resume")
    assert record2.stored_path != record1.stored_path
    assert stored.read_text(encoding="utf-8") == "original"
    assert (folder / record2.stored_path).read_text(encoding="utf-8") == "changed"


def test_resolve_candidate_by_name_fragment(tmp_root: Path):
    _, folder = cand.new_candidate(tmp_root, "Aarav Mehta", date(2026, 7, 13))
    assert cand.resolve_candidate(tmp_root, "Aarav Mehta") == folder
    assert cand.resolve_candidate(tmp_root, "aarav") == folder
    assert cand.resolve_candidate(tmp_root, folder.name) == folder
    with pytest.raises(FileNotFoundError):
        cand.resolve_candidate(tmp_root, "Nobody Here")
