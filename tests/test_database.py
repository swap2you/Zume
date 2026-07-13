"""Phase 8 — database reliability (versioning, integrity, backup, duplicates)."""

from datetime import date
from pathlib import Path

from zume import candidate as cand
from zume.storage import Storage


def test_schema_version_and_foreign_keys(tmp_root: Path):
    with Storage(tmp_root) as storage:
        assert storage.schema_version == 2
        fk = storage.conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1


def test_expected_indexes_exist(tmp_root: Path):
    with Storage(tmp_root) as storage:
        names = {r[0] for r in storage.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
    for expected in ("idx_candidates_display_name", "idx_candidates_status",
                     "idx_candidates_created_date", "idx_source_files_sha256"):
        assert expected in names


def test_integrity_check_passes(tmp_root: Path):
    with Storage(tmp_root) as storage:
        ok, messages = storage.integrity_check()
        assert ok, messages


def test_backup_is_created_and_validated(tmp_root: Path):
    candidate, _ = cand.new_candidate(tmp_root, "Fixture Person")
    with Storage(tmp_root) as storage:
        storage.upsert_candidate(candidate)
        dest = storage.backup(tmp_root / "data" / "backup.db")
    ok, messages = Storage.validate_backup(dest)
    assert ok, messages


def test_backup_validation_rejects_empty_file(tmp_root: Path):
    bad = tmp_root / "data" / "empty.db"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_bytes(b"")
    ok, _ = Storage.validate_backup(bad)
    assert not ok


def test_duplicate_candidates_detected_by_name(tmp_root: Path):
    c1, f1 = cand.new_candidate(tmp_root, "Dup Person", on_date=date(2026, 1, 1))
    c2, f2 = cand.new_candidate(tmp_root, "Dup Person", on_date=date(2026, 2, 2))
    with Storage(tmp_root) as storage:
        storage.sync_candidate(c1, f1)
        storage.sync_candidate(c2, f2)
        dupes = storage.find_duplicate_candidates()
    reasons = [reason for reason, _folders in dupes]
    assert any("Dup Person" in reason for reason in reasons)
