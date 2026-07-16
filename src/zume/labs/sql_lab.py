"""Read-only SQLite SQL lab with per-run fixtures and resource limits."""

from __future__ import annotations

import shutil
import sqlite3
import time
from pathlib import Path

from zume.labs.base import LabCapabilities, LabProvider, LabRunResult, TestCaseResult

_MAX_ROWS = 200
_MAX_OUTPUT_BYTES = 32_000
_TIMEOUT_SECONDS = 2.5
_DENIED_ACTIONS = {
    sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_DELETE,
    sqlite3.SQLITE_DROP_TABLE, sqlite3.SQLITE_DROP_INDEX, sqlite3.SQLITE_DROP_TRIGGER,
    sqlite3.SQLITE_ALTER_TABLE, sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH,
    sqlite3.SQLITE_PRAGMA,
}
_DENIED_ACTIONS.update(
    getattr(sqlite3, action)
    for action in ("SQLITE_DROP_VIEW", "SQLITE_DROP_TEMP_TABLE", "SQLITE_DROP_TEMP_INDEX",
                   "SQLITE_DROP_TEMP_TRIGGER", "SQLITE_DROP_VTABLE", "SQLITE_ALTER_VTABLE")
    if hasattr(sqlite3, action)
)


class SqlLabProvider(LabProvider):
    name = "sql"

    def capabilities(self) -> LabCapabilities:
        return LabCapabilities(
            runner="sql", languages=["sql"], requires_docker=False, available=True,
            detail="Read-only temporary SQLite fixtures with query deadline and output limits.",
        )

    def prepare(self, exercise_id: str, workspace: str) -> None:
        root = Path(workspace)
        root.mkdir(parents=True, exist_ok=True)
        db = root / "lab.sqlite"
        db.unlink(missing_ok=True)
        conn = sqlite3.connect(db)
        try:
            fixture = Path("training/sql-fixtures/demo.sql")
            if fixture.exists():
                conn.executescript(fixture.read_text(encoding="utf-8"))
            else:
                conn.executescript(
                    "CREATE TABLE employees (id INTEGER PRIMARY KEY, name TEXT, dept TEXT, salary INTEGER);"
                    "INSERT INTO employees VALUES (1,'Ada','QA',120),(2,'Grace','Eng',140),(3,'Alan','QA',110);"
                )
            conn.commit()
        finally:
            conn.close()
        (root / "exercise_id.txt").write_text(exercise_id, encoding="utf-8")

    def run(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        started = time.monotonic()
        # Each invocation gets fresh data so no query can contaminate a later run.
        self.prepare(exercise_id, workspace)
        conn = sqlite3.connect(Path(workspace) / "lab.sqlite", timeout=_TIMEOUT_SECONDS)
        conn.row_factory = sqlite3.Row
        deadline = started + _TIMEOUT_SECONDS

        def authorizer(action: int, _arg1: str | None, _arg2: str | None,
                       _database: str | None, _source: str | None) -> int:
            if action in _DENIED_ACTIONS or (
                action == sqlite3.SQLITE_FUNCTION and (_arg2 or "").lower() == "load_extension"
            ):
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK

        def progress() -> int:
            return int(time.monotonic() >= deadline)

        conn.set_authorizer(authorizer)
        conn.set_progress_handler(progress, 1_000)
        try:
            cur = conn.execute(code)
            if not cur.description:
                return self._failure("Only SELECT statements are allowed.", started)
            rows = cur.fetchmany(_MAX_ROWS + 1)
            truncated = len(rows) > _MAX_ROWS
            headers = [column[0] for column in cur.description]
            lines = ["\t".join(headers)]
            for row in rows[:_MAX_ROWS]:
                lines.append("\t".join(str(row[column]) for column in headers))
            stdout = "\n".join(lines)
            encoded = stdout.encode("utf-8")
            if len(encoded) > _MAX_OUTPUT_BYTES:
                stdout = encoded[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="ignore")
                truncated = True
            return LabRunResult(stdout=stdout, exit_code=0,
                                duration_ms=int((time.monotonic() - started) * 1000),
                                truncated=truncated)
        except sqlite3.DatabaseError as exc:
            message = str(exc)
            if "interrupted" in message.lower():
                message = "Query timeout after %.1f seconds." % _TIMEOUT_SECONDS
            return self._failure(message, started)
        except Exception as exc:  # noqa: BLE001
            return self._failure(f"{type(exc).__name__}: {exc}", started)
        finally:
            conn.close()

    @staticmethod
    def _failure(message: str, started: float) -> LabRunResult:
        return LabRunResult(stderr=message, exit_code=1,
                            duration_ms=int((time.monotonic() - started) * 1000))

    def test(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        result = self.run(exercise_id, workspace, code)
        result.test_results = [TestCaseResult(
            name="read_only_query", passed=result.exit_code == 0 and bool(result.stdout.strip()),
            message="Query executed" if result.exit_code == 0 else result.stderr,
        )]
        return result

    def cleanup(self, workspace: str) -> None:
        shutil.rmtree(Path(workspace), ignore_errors=True)
