"""Configuration loading for Zume."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR_NAME = "config"


def find_root(start: Path | None = None) -> Path:
    """Locate the repository root by walking up until pyproject.toml is found."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / CONFIG_DIR_NAME).is_dir():
            return candidate
    return current


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return data


@lru_cache(maxsize=32)
def _cached_yaml(path_str: str) -> dict[str, Any]:
    return _load_yaml(Path(path_str))


def load_config(root: Path, name: str) -> dict[str, Any]:
    """Load a YAML config file by base name (e.g. 'triggers')."""
    return _cached_yaml(str(root / CONFIG_DIR_NAME / f"{name}.yaml"))


def load_triggers(root: Path) -> dict[str, str]:
    return dict(load_config(root, "triggers")["triggers"])


def load_hiring_standard(root: Path) -> dict[str, Any]:
    return load_config(root, "hiring-standard")


def load_statuses(root: Path) -> list[str]:
    return list(load_config(root, "statuses")["statuses"])


def load_theme(root: Path) -> dict[str, Any]:
    return load_config(root, "document-theme")


def load_exercise_library(root: Path) -> dict[str, Any]:
    return load_config(root, "exercise-library")


def load_question_library(root: Path) -> dict[str, Any]:
    return load_config(root, "interview-question-library")


def load_privacy(root: Path) -> dict[str, Any]:
    return load_config(root, "privacy")
