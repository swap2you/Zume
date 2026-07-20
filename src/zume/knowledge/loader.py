"""Load question/exercise YAML records from the knowledge tree."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from zume.knowledge.models import ExerciseRecord, QuestionRecord


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def iter_yaml_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.yaml") if p.is_file() and "proposals" not in p.parts)


def load_all_questions(knowledge_root: Path) -> list[QuestionRecord]:
    return list(_cached_questions(str(knowledge_root.resolve())))


def load_all_exercises(knowledge_root: Path) -> list[ExerciseRecord]:
    return list(_cached_exercises(str(knowledge_root.resolve())))


@lru_cache(maxsize=4)
def _cached_questions(knowledge_root: str) -> tuple[QuestionRecord, ...]:
    records: list[QuestionRecord] = []
    for path in iter_yaml_files(Path(knowledge_root) / "questions"):
        data = load_yaml(path)
        items = _records_list(data, "questions")
        for raw in items:
            if isinstance(raw, dict):
                records.append(QuestionRecord.model_validate(raw))
    return tuple(records)


@lru_cache(maxsize=4)
def _cached_exercises(knowledge_root: str) -> tuple[ExerciseRecord, ...]:
    records: list[ExerciseRecord] = []
    for path in iter_yaml_files(Path(knowledge_root) / "exercises"):
        data = load_yaml(path)
        items = _records_list(data, "exercises")
        for raw in items:
            if isinstance(raw, dict):
                records.append(ExerciseRecord.model_validate(raw))
    return tuple(records)


def clear_loader_cache() -> None:
    _cached_questions.cache_clear()
    _cached_exercises.cache_clear()


def _records_list(data: Any, preferred_key: str) -> list[Any]:
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    for key in (preferred_key, "records", "items"):
        items = data.get(key)
        if isinstance(items, list):
            return items
    return []


def load_sources(knowledge_root: Path) -> dict[str, dict[str, Any]]:
    path = knowledge_root / "sources.yaml"
    if not path.exists():
        return {}
    data = load_yaml(path)
    sources = data.get("sources") if isinstance(data, dict) else data
    if isinstance(sources, list):
        return {str(s.get("id")): s for s in sources if isinstance(s, dict) and s.get("id")}
    if isinstance(sources, dict):
        return {str(k): (v if isinstance(v, dict) else {"id": k}) for k, v in sources.items()}
    return {}


def load_taxonomy(knowledge_root: Path) -> dict[str, Any]:
    path = knowledge_root / "taxonomy.yaml"
    if not path.exists():
        return {}
    data = load_yaml(path)
    return data if isinstance(data, dict) else {}
