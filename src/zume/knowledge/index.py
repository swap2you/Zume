"""Deterministic SQLite FTS5 index build for the knowledge library."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from zume.knowledge.loader import load_all_exercises, load_all_questions

DEFAULT_INDEX = Path("data") / "knowledge-fts.sqlite"


def index_path(root: Path) -> Path:
    return root / DEFAULT_INDEX


def build_index(root: Path, path: Path | None = None) -> Path:
    dest = path or index_path(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    knowledge_root = root / "knowledge"
    questions = [q for q in load_all_questions(knowledge_root) if q.status == "published"]
    exercises = [e for e in load_all_exercises(knowledge_root) if e.status == "published"]
    # Sort for deterministic inserts.
    questions = sorted(questions, key=lambda q: q.id)
    exercises = sorted(exercises, key=lambda e: e.id)
    conn = sqlite3.connect(dest)
    try:
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.executescript(
            """
            CREATE TABLE documents (
              id TEXT PRIMARY KEY,
              kind TEXT NOT NULL,
              domain TEXT,
              level TEXT,
              priority TEXT,
              title TEXT,
              body TEXT
            );
            CREATE VIRTUAL TABLE documents_fts USING fts5(
              id UNINDEXED,
              title,
              body,
              domain UNINDEXED,
              level UNINDEXED,
              priority UNINDEXED,
              tokenize='porter'
            );
            """
        )
        for q in questions:
            body = "\n".join(
                [
                    q.question,
                    q.concise_answer,
                    q.recommended_answer,
                    " ".join(q.key_points),
                    " ".join(q.tags),
                    q.subdomain,
                ]
            )
            conn.execute(
                "INSERT INTO documents(id, kind, domain, level, priority, title, body) VALUES (?,?,?,?,?,?,?)",
                (q.id, "question", q.domain, q.level, q.priority, q.title, body),
            )
            conn.execute(
                "INSERT INTO documents_fts(id, title, body, domain, level, priority) VALUES (?,?,?,?,?,?)",
                (q.id, q.title, body, q.domain, q.level, q.priority),
            )
        for ex in exercises:
            body = "\n".join([ex.task, ex.expected_reasoning, " ".join(ex.tags), ex.subdomain])
            conn.execute(
                "INSERT INTO documents(id, kind, domain, level, priority, title, body) VALUES (?,?,?,?,?,?,?)",
                (ex.id, "exercise", ex.domain, ex.level, ex.priority, ex.title, body),
            )
            conn.execute(
                "INSERT INTO documents_fts(id, title, body, domain, level, priority) VALUES (?,?,?,?,?,?)",
                (ex.id, ex.title, body, ex.domain, ex.level, ex.priority),
            )
        conn.commit()
    finally:
        conn.close()
    return dest
