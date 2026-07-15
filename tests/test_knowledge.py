"""Knowledge schema, index, and search tests."""

from __future__ import annotations

from pathlib import Path

from zume.knowledge.gaps import collect_gaps
from zume.knowledge.index import build_index
from zume.knowledge.loader import load_all_exercises, load_all_questions
from zume.knowledge.search import search
from zume.knowledge.stats import collect_stats
from zume.knowledge.validate import validate_library


def test_library_loads_and_validates(repo_root: Path):
    questions = load_all_questions(repo_root / "knowledge")
    exercises = load_all_exercises(repo_root / "knowledge")
    assert len(questions) >= 1200
    assert len(exercises) >= 150
    assert validate_library(repo_root) == []


def test_stats_and_gaps(repo_root: Path):
    stats = collect_stats(repo_root)
    assert stats["published_questions"] >= 1200
    gaps = collect_gaps(repo_root)
    assert gaps["complete_claim"] is False


def test_index_and_search(repo_root: Path, tmp_path: Path):
    dest = tmp_path / "fts.sqlite"
    build_index(repo_root, dest)
    # Temporarily point search at rebuilt index by building default then searching.
    build_index(repo_root)
    results = search(repo_root, "HashMap equals hashCode", limit=5)
    assert results
    assert any("java" in (r.get("domain") or "") for r in results)


def test_candidate_projection_hides_answers(repo_root: Path):
    exercises = load_all_exercises(repo_root / "knowledge")
    assert exercises
    proj = exercises[0].candidate_projection()
    blob = str(proj).lower()
    assert "reference_solution" not in proj
    assert "recommended answer" not in blob
