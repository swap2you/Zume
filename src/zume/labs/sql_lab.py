"""In-process SQLite SQL lab with fixtures, timeouts, and row limits."""

from __future__ import annotations

import shutil
import sqlite3
import time
from pathlib import Path

from zume.labs.base import LabCapabilities, LabProvider, LabRunResult, TestCaseResult

_MAX_ROWS = 200
_TIMEOUT_SECONDS = 5.0


class SqlLabProvider(LabProvider):
    name = "sql"

    def capabilities(self) -> LabCapabilities:
        return LabCapabilities(
            runner="sql",
            languages=["sql"],
            requires_docker=False,
            available=True,
            detail="Temporary SQLite database with bundled fixtures. Oracle dialect differences are labeled.",
        )

    def prepare(self, exercise_id: str, workspace: str) -> None:
        root = Path(workspace)
        root.mkdir(parents=True, exist_ok=True)
        db = root / "lab.sqlite"
        if db.exists():
            db.unlink()
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
        del exercise_id
        started = time.perf_counter()
        db = Path(workspace) / "lab.sqlite"
        if not db.exists():
            self.prepare("ad-hoc", workspace)
        conn = sqlite3.connect(db, timeout=_TIMEOUT_SECONDS)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute(code)
            if cur.description:
                rows = cur.fetchmany(_MAX_ROWS + 1)
                truncated = len(rows) > _MAX_ROWS
                rows = rows[:_MAX_ROWS]
                headers = [d[0] for d in cur.description]
                lines = ["\t".join(headers)]
                for row in rows:
                    lines.append("\t".join(str(row[h]) for h in headers))
                stdout = "\n".join(lines)
            else:
                conn.commit()
                stdout = f"OK (rowcount={cur.rowcount})"
                truncated = False
            return LabRunResult(
                stdout=stdout,
                exit_code=0,
                duration_ms=int((time.perf_counter() - started) * 1000),
                truncated=truncated,
            )
        except Exception as exc:  # noqa: BLE001
            return LabRunResult(
                stderr=f"{type(exc).__name__}: {exc}",
                exit_code=1,
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        finally:
            conn.close()

    def test(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        result = self.run(exercise_id, workspace, code)
        # Minimal smoke assertion when query succeeds.
        passed = result.exit_code == 0 and bool(result.stdout.strip())
        result.test_results = [
            TestCaseResult(
                name="query_returns_or_executes",
                passed=passed,
                message="Query executed" if passed else result.stderr,
            )
        ]
        return result

    def cleanup(self, workspace: str) -> None:
        path = Path(workspace)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
