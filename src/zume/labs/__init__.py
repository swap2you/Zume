"""Lab providers. SQL/API work offline; Java/Selenium require Docker flags."""

from __future__ import annotations

from zume.labs.api_lab import ApiLabProvider
from zume.labs.base import LabCapabilities, LabProvider, LabRunResult
from zume.labs.java_lab import JavaLabProvider
from zume.labs.selenium_lab import SeleniumLabProvider
from zume.labs.sql_lab import SqlLabProvider


def get_lab_provider(runner: str) -> LabProvider:
    mapping: dict[str, LabProvider] = {
        "sql": SqlLabProvider(),
        "api": ApiLabProvider(),
        "java": JavaLabProvider(),
        "selenium": SeleniumLabProvider(),
    }
    try:
        return mapping[runner]
    except KeyError as exc:
        raise KeyError(f"Unknown lab runner: {runner}") from exc


def list_lab_capabilities() -> list[LabCapabilities]:
    return [get_lab_provider(name).capabilities() for name in ("sql", "api", "java", "selenium")]


__all__ = [
    "LabCapabilities",
    "LabProvider",
    "LabRunResult",
    "get_lab_provider",
    "list_lab_capabilities",
]
