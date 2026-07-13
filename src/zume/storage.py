"""SQLite metadata index. Source files remain in candidate folders."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from zume.models import (
    Candidate,
    ExerciseSelection,
    FeedbackResult,
    InterviewKit,
    ScreeningResult,
    utc_now_iso,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY,
    folder_name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    status TEXT NOT NULL,
    experience_years REAL,
    created_date TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS source_files (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    original_name TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    kind TEXT NOT NULL,
    added_at TEXT NOT NULL,
    UNIQUE(candidate_id, stored_path, sha256)
);
CREATE TABLE IF NOT EXISTS screenings (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    score_percent REAL NOT NULL,
    decision TEXT NOT NULL,
    gate_passed INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    kind TEXT NOT NULL,
    exercise_count INTEGER NOT NULL DEFAULT 0,
    override_reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    skill TEXT NOT NULL,
    score INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS communications (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    kind TEXT NOT NULL,
    subject TEXT NOT NULL,
    relative_path TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS status_history (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    status TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    relative_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(candidate_id, relative_path, sha256)
);
CREATE TABLE IF NOT EXISTS exercise_usage (
    exercise_id TEXT PRIMARY KEY,
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used TEXT
);
CREATE TABLE IF NOT EXISTS candidate_exercises (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES candidates(id),
    exercise_id TEXT NOT NULL,
    fingerprint TEXT NOT NULL DEFAULT '',
    assigned_at TEXT NOT NULL,
    UNIQUE(candidate_id, exercise_id)
);
"""

INDEXES = """
CREATE INDEX IF NOT EXISTS idx_candidates_display_name ON candidates(display_name);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_created_date ON candidates(created_date);
CREATE INDEX IF NOT EXISTS idx_source_files_sha256 ON source_files(sha256);
CREATE INDEX IF NOT EXISTS idx_candidate_exercises_ex ON candidate_exercises(exercise_id);
"""

SCHEMA_VERSION = 2


class Storage:
    def __init__(self, root: Path) -> None:
        db_dir = root / "data"
        db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_dir / "zume.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.executescript(INDEXES)
        self.conn.commit()
        self._migrate()

    def _has_column(self, table: str, column: str) -> bool:
        rows = self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        return any(r[1] == column for r in rows)

    def _migrate(self) -> None:
        """Idempotent schema migrations keyed on PRAGMA user_version."""
        version = int(self.conn.execute("PRAGMA user_version").fetchone()[0])
        if version < 2:
            if not self._has_column("interviews", "override_reason"):
                self.conn.execute(
                    "ALTER TABLE interviews ADD COLUMN override_reason TEXT NOT NULL DEFAULT ''")
            self.conn.executescript(INDEXES)
            self.conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            self.conn.commit()

    @property
    def schema_version(self) -> int:
        return int(self.conn.execute("PRAGMA user_version").fetchone()[0])

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Storage":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- candidates ---------------------------------------------------------

    def upsert_candidate(self, candidate: Candidate) -> int:
        self.conn.execute(
            """
            INSERT INTO candidates (folder_name, display_name, status,
                                    experience_years, created_date, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(folder_name) DO UPDATE SET
                display_name = excluded.display_name,
                status = excluded.status,
                experience_years = excluded.experience_years,
                updated_at = excluded.updated_at
            """,
            (candidate.folder_name, candidate.display_name, candidate.status,
             candidate.experience_years, candidate.created_date, utc_now_iso()),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT id FROM candidates WHERE folder_name = ?",
            (candidate.folder_name,),
        ).fetchone()
        if row is None:
            raise RuntimeError("Failed to upsert candidate")
        return int(row[0])

    def sync_candidate(self, candidate: Candidate, folder: Path) -> int:
        """Mirror the candidate.json audit record into the index."""
        cid = self.upsert_candidate(candidate)
        for source in candidate.source_files:
            self.conn.execute(
                """
                INSERT OR IGNORE INTO source_files
                    (candidate_id, original_name, stored_path, sha256, kind, added_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cid, source.original_name, source.stored_path, source.sha256,
                 source.kind, source.added_at),
            )
        existing = {
            (row[0], row[1]) for row in self.conn.execute(
                "SELECT status, at FROM status_history WHERE candidate_id = ?", (cid,))
        }
        for event in candidate.status_history:
            if (event.status, event.at) not in existing:
                self.conn.execute(
                    "INSERT INTO status_history (candidate_id, status, note, at)"
                    " VALUES (?, ?, ?, ?)",
                    (cid, event.status, event.note, event.at),
                )
        for rel in candidate.artifacts:
            artifact = folder / rel
            if artifact.exists():
                from zume.candidate import sha256_file
                self.conn.execute(
                    """
                    INSERT OR IGNORE INTO artifacts
                        (candidate_id, relative_path, sha256, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (cid, rel, sha256_file(artifact), utc_now_iso()),
                )
        self.conn.commit()
        return cid

    # -- workflow records ----------------------------------------------------

    def record_screening(self, cid: int, result: ScreeningResult) -> None:
        self.conn.execute(
            "INSERT INTO screenings (candidate_id, score_percent, decision,"
            " gate_passed, created_at) VALUES (?, ?, ?, ?, ?)",
            (cid, result.score_percent, result.decision.value,
             int(result.experience_gate_passed), result.created_at),
        )
        self.conn.commit()

    def record_interview_kit(self, cid: int, kit: InterviewKit) -> None:
        self.conn.execute(
            "INSERT INTO interviews (candidate_id, kind, exercise_count, override_reason,"
            " created_at) VALUES (?, ?, ?, ?, ?)",
            (cid, "prep", len(kit.exercises), kit.override_reason, kit.created_at),
        )
        self.conn.commit()

    def record_feedback(self, cid: int, result: FeedbackResult) -> None:
        self.conn.execute(
            "INSERT INTO interviews (candidate_id, kind, exercise_count, created_at)"
            " VALUES (?, ?, ?, ?)",
            (cid, "feedback", 0, result.created_at),
        )
        for score in result.skill_scores:
            self.conn.execute(
                "INSERT INTO scores (candidate_id, skill, score, created_at)"
                " VALUES (?, ?, ?, ?)",
                (cid, score.skill, score.score, result.created_at),
            )
        self.conn.commit()

    def record_communication(self, cid: int, kind: str, subject: str,
                             relative_path: str | None) -> None:
        self.conn.execute(
            "INSERT INTO communications (candidate_id, kind, subject,"
            " relative_path, created_at) VALUES (?, ?, ?, ?, ?)",
            (cid, kind, subject, relative_path, utc_now_iso()),
        )
        self.conn.commit()

    # -- reliability ---------------------------------------------------------

    def integrity_check(self) -> tuple[bool, list[str]]:
        """Run PRAGMA integrity_check and foreign_key_check."""
        messages: list[str] = []
        integrity = [r[0] for r in self.conn.execute("PRAGMA integrity_check").fetchall()]
        ok = integrity == ["ok"]
        if not ok:
            messages.extend(f"integrity: {m}" for m in integrity)
        fk_rows = self.conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk_rows:
            ok = False
            messages.extend(f"foreign_key_check: {tuple(r)}" for r in fk_rows)
        return ok, messages

    def backup(self, dest: Path) -> Path:
        """Create a consistent backup via the SQLite online-backup API."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(dest) as target:
            self.conn.backup(target)
        return dest

    @staticmethod
    def validate_backup(path: Path) -> tuple[bool, list[str]]:
        """Open a backup file read-only and verify it is a healthy database."""
        if not path.exists() or path.stat().st_size == 0:
            return False, [f"backup missing or empty: {path}"]
        conn = sqlite3.connect(path)
        try:
            integrity = [r[0] for r in conn.execute("PRAGMA integrity_check").fetchall()]
            has_candidates = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='candidates'"
            ).fetchone() is not None
        finally:
            conn.close()
        if integrity != ["ok"]:
            return False, [f"backup integrity: {integrity}"]
        if not has_candidates:
            return False, ["backup is missing the candidates table"]
        return True, []

    def find_duplicate_candidates(self) -> list[tuple[str, list[str]]]:
        """Detect likely duplicate candidates by shared source hash or display name."""
        dupes: list[tuple[str, list[str]]] = []
        by_hash = self.conn.execute(
            """
            SELECT sha256, GROUP_CONCAT(DISTINCT c.folder_name)
            FROM source_files sf JOIN candidates c ON c.id = sf.candidate_id
            GROUP BY sha256 HAVING COUNT(DISTINCT c.id) > 1
            """
        ).fetchall()
        for sha, folders in by_hash:
            dupes.append((f"source hash {sha[:12]}", (folders or "").split(",")))
        by_name = self.conn.execute(
            "SELECT display_name, GROUP_CONCAT(folder_name) FROM candidates"
            " GROUP BY display_name HAVING COUNT(*) > 1"
        ).fetchall()
        for name, folders in by_name:
            dupes.append((f"name {name}", (folders or "").split(",")))
        return dupes

    # -- lifecycle -----------------------------------------------------------

    CHILD_TABLES = (
        "source_files", "screenings", "interviews", "scores",
        "communications", "status_history", "artifacts", "candidate_exercises",
    )

    def find_candidate_id(self, folder_name: str) -> int | None:
        row = self.conn.execute(
            "SELECT id FROM candidates WHERE folder_name = ?", (folder_name,)).fetchone()
        return int(row[0]) if row else None

    def set_status(self, folder_name: str, status: str) -> None:
        self.conn.execute(
            "UPDATE candidates SET status = ?, updated_at = ? WHERE folder_name = ?",
            (status, utc_now_iso(), folder_name))
        self.conn.commit()

    def deletion_plan(self, folder_name: str) -> dict[str, int]:
        """Row counts that a delete would remove (for confirmation display)."""
        plan: dict[str, int] = {}
        cid = self.find_candidate_id(folder_name)
        if cid is None:
            return plan
        plan["candidates"] = 1
        for table in self.CHILD_TABLES:
            row = self.conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE candidate_id = ?", (cid,)).fetchone()
            plan[table] = int(row[0])
        return plan

    def delete_candidate(self, folder_name: str) -> dict[str, int]:
        """Delete a candidate and all child rows inside one transaction."""
        cid = self.find_candidate_id(folder_name)
        if cid is None:
            return {}
        plan = self.deletion_plan(folder_name)
        with self.conn:  # transactional: commits on success, rolls back on error
            for table in self.CHILD_TABLES:
                self.conn.execute(f"DELETE FROM {table} WHERE candidate_id = ?", (cid,))
            self.conn.execute("DELETE FROM candidates WHERE id = ?", (cid,))
        return plan

    # -- exercise rotation ---------------------------------------------------

    def get_exercise_usage(self) -> dict[str, dict[str, object]]:
        rows = self.conn.execute(
            "SELECT exercise_id, usage_count, last_used FROM exercise_usage").fetchall()
        return {r[0]: {"count": r[1], "last_used": r[2]} for r in rows}

    def get_candidate_exercise_history(self, cid: int) -> set[str]:
        rows = self.conn.execute(
            "SELECT exercise_id FROM candidate_exercises WHERE candidate_id = ?",
            (cid,)).fetchall()
        return {r[0] for r in rows}

    def record_exercise_assignments(self, cid: int,
                                    selections: list["ExerciseSelection"]) -> None:
        now = utc_now_iso()
        for sel in selections:
            self.conn.execute(
                """
                INSERT INTO exercise_usage (exercise_id, usage_count, last_used)
                VALUES (?, 1, ?)
                ON CONFLICT(exercise_id) DO UPDATE SET
                    usage_count = usage_count + 1,
                    last_used = excluded.last_used
                """,
                (sel.exercise_id, now),
            )
            self.conn.execute(
                """
                INSERT OR IGNORE INTO candidate_exercises
                    (candidate_id, exercise_id, fingerprint, assigned_at)
                VALUES (?, ?, ?, ?)
                """,
                (cid, sel.exercise_id, sel.fingerprint, now),
            )
        self.conn.commit()

    # -- queries --------------------------------------------------------------

    def search_candidates(self, needle: str = "") -> list[tuple[str, str, str]]:
        rows = self.conn.execute(
            "SELECT display_name, folder_name, status FROM candidates"
            " WHERE display_name LIKE ? ORDER BY updated_at DESC",
            (f"%{needle}%",),
        ).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]
