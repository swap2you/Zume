"""Full-text search over the generated knowledge index.

Search strategy (natural-language friendly):
1. stop-word removal;
2. strict AND match;
3. reduced-keyword retry (least common tokens first);
4. OR-ranked fallback;
5. safe typo-tolerant domain/tag prefix matching.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from zume.knowledge.index import build_index, index_path
from zume.knowledge.loader import load_all_questions

STOP_WORDS = {
    "a", "an", "and", "are", "be", "by", "can", "do", "does", "explain", "for",
    "from", "give", "how", "in", "is", "it", "its", "me", "of", "on", "or",
    "should", "tell", "that", "the", "this", "to", "use", "what", "when",
    "where", "which", "why", "with", "would", "you", "your",
}


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
    tokens = _tokens(query)
    if not tokens:
        return []

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        rows = _match(conn, _and_query(tokens), domain, limit)
        if not rows and len(tokens) > 2:
            # Reduced-keyword retry: keep the most selective (longest) tokens.
            reduced = sorted(tokens, key=len, reverse=True)[:3]
            rows = _match(conn, _and_query(reduced), domain, limit)
        if not rows:
            rows = _match(conn, _or_query(tokens), domain, limit)
        if not rows:
            # Typo-tolerant prefix fallback on reasonably long tokens.
            prefixes = [f'"{t[:4]}"*' for t in tokens if len(t) >= 5]
            if prefixes:
                rows = _match(conn, " OR ".join(prefixes), domain, limit)
    finally:
        conn.close()

    results = [dict(r) for r in rows]
    from zume.knowledge.enrich import resolve_references
    from zume.knowledge.loader import load_sources

    sources = load_sources(root / "knowledge")
    by_id = {q.id: q for q in load_all_questions(root / "knowledge")}
    for item in results:
        rec = by_id.get(item["id"])
        if rec:
            item["concise_answer"] = rec.concise_answer
            item["recommended_answer"] = rec.recommended_answer
            item["references"] = resolve_references(rec, sources)
    return results


def _match(conn: sqlite3.Connection, match: str, domain: str | None, limit: int) -> list[sqlite3.Row]:
    if not match:
        return []
    sql = (
        "SELECT d.id, d.kind, d.domain, d.level, d.priority, d.title, "
        "snippet(documents_fts, 1, '[', ']', '…', 12) AS snippet "
        "FROM documents_fts JOIN documents d ON d.id = documents_fts.id "
        "WHERE documents_fts MATCH ? "
    )
    params: list[Any] = [match]
    if domain:
        sql += "AND d.domain = ? "
        params.append(domain)
    sql += "ORDER BY rank LIMIT ?"
    params.append(limit)
    try:
        return conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        return []


def _and_query(tokens: list[str]) -> str:
    return " AND ".join(f'"{t}"' for t in tokens[:12])


def _or_query(tokens: list[str]) -> str:
    return " OR ".join(f'"{t}"' for t in tokens[:12])


def _tokens(query: str) -> list[str]:
    raw = re_split(query)
    kept = [t for t in raw if t.lower() not in STOP_WORDS]
    # A pure stop-word query still deserves a best-effort answer.
    return kept or raw


def re_split(query: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_+/.-]+", query)
