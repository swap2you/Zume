"""SQLite metadata index. Source files remain in candidate folders."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from zume.models import (
    Candidate,
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
"""


class Storage:
    def __init__(self, root: Path) -> None:
        db_dir = root / "data"
        db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_dir / "zume.db"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

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
            "INSERT INTO interviews (candidate_id, kind, exercise_count, created_at)"
            " VALUES (?, ?, ?, ?)",
            (cid, "prep", len(kit.exercises), kit.created_at),
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

    # -- queries --------------------------------------------------------------

    def search_candidates(self, needle: str = "") -> list[tuple[str, str, str]]:
        rows = self.conn.execute(
            "SELECT display_name, folder_name, status FROM candidates"
            " WHERE display_name LIKE ? ORDER BY updated_at DESC",
            (f"%{needle}%",),
        ).fetchall()
        return [(r[0], r[1], r[2]) for r in rows]
