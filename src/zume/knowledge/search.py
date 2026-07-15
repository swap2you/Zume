"""Full-text search over the generated knowledge index."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from zume.knowledge.index import build_index, index_path
from zume.knowledge.loader import load_all_questions


def search(
    root: Path,
    query: str,
    *,
    limit: int = 20,
    domain: str | None = None,
    rebuild_if_missing: bool = True,
) -> list[dict[str, Any]]:
    path = index_path(root)
    if not path.exists():
        if not rebuild_if_missing:
            return []
        build_index(root, path)
    safe = _sanitize_fts_query(query)
    if not safe:
        return []
    sql = (
        "SELECT d.id, d.kind, d.domain, d.level, d.priority, d.title, "
        "snippet(documents_fts, 1, '[', ']', '…', 12) AS snippet "
        "FROM documents_fts JOIN documents d ON d.id = documents_fts.id "
        "WHERE documents_fts MATCH ? "
    )
    params: list[Any] = [safe]
    if domain:
        sql += "AND d.domain = ? "
        params.append(domain)
    sql += "ORDER BY rank LIMIT ?"
    params.append(limit)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    results = [dict(r) for r in rows]
    # Enrich with concise answers for Ask Zume.
    by_id = {q.id: q for q in load_all_questions(root / "knowledge")}
    for item in results:
        rec = by_id.get(item["id"])
        if rec:
            item["concise_answer"] = rec.concise_answer
            item["recommended_answer"] = rec.recommended_answer
            item["references"] = [r.model_dump() for r in rec.references]
    return results


def _sanitize_fts_query(query: str) -> str:
    tokens = [t for t in re_split(query) if t]
    if not tokens:
        return ""
    return " AND ".join(f'"{t}"' for t in tokens[:12])


def re_split(query: str) -> list[str]:
    import re

    return re.findall(r"[A-Za-z0-9_+/.-]+", query)
