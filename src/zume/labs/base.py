"""Exercise lab provider interfaces and structured run results."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class LabCapabilities(BaseModel):
    runner: str
    languages: list[str] = Field(default_factory=list)
    requires_docker: bool = False
    available: bool = False
    detail: str = ""


class TestCaseResult(BaseModel):
    name: str
    passed: bool
    message: str = ""


class LabRunResult(BaseModel):
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_ms: int = 0
    truncated: bool = False
    test_results: list[TestCaseResult] = Field(default_factory=list)
    extras: dict[str, Any] = Field(default_factory=dict)


class LabProvider(ABC):
    name: str = "base"

    @abstractmethod
    def capabilities(self) -> LabCapabilities:
        ...

    @abstractmethod
    def prepare(self, exercise_id: str, workspace: str) -> None:
        ...

    @abstractmethod
    def run(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        ...

    @abstractmethod
    def test(self, exercise_id: str, workspace: str, code: str) -> LabRunResult:
        ...

    @abstractmethod
    def cleanup(self, workspace: str) -> None:
        ...
