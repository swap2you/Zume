"""Pydantic models for the canonical knowledge library."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

Level = Literal["basic", "intermediate", "advanced"]
Priority = Literal["P0", "P1", "P2", "P3"]
Frequency = Literal["very_common", "common", "occasional", "emerging"]
PublishStatus = Literal["published", "draft", "retired"]


class Reference(BaseModel):
    source_id: str
    locator: str = ""


class FollowUp(BaseModel):
    question: str
    recommended_answer: str


class QuestionRecord(BaseModel):
    id: str
    domain: str
    subdomain: str = ""
    title: str
    level: Level
    priority: Priority
    frequency: Frequency = "common"
    question: str
    concise_answer: str
    recommended_answer: str
    deep_dive: str = ""
    key_points: list[str] = Field(default_factory=list)
    strong_signals: list[str] = Field(default_factory=list)
    weak_signals: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    follow_ups: list[FollowUp] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    code_examples: list[str] = Field(default_factory=list)
    role_tracks: list[str] = Field(default_factory=list)
    years_range: list[int] = Field(default_factory=lambda: [5, 15])
    tags: list[str] = Field(default_factory=list)
    estimated_minutes: int = 4
    references: list[Reference] = Field(default_factory=list)
    last_verified: str
    freshness_days: int = 365
    status: PublishStatus = "published"
    question_type: str = "concept"

    @field_validator("id")
    @classmethod
    def id_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("id must be non-empty")
        return value.strip()


class IndependenceItem(BaseModel):
    question: str
    recommended_answer: str


class ExerciseRecord(BaseModel):
    id: str
    domain: str
    subdomain: str = ""
    title: str
    level: Level
    priority: Priority = "P1"
    task: str
    constraints: list[str] = Field(default_factory=list)
    starter_files: dict[str, str] = Field(default_factory=dict)
    expected_reasoning: str
    reference_solution: str
    test_cases: list[dict[str, Any]] = Field(default_factory=list)
    scoring_rubric: list[str] = Field(default_factory=list)
    requirement_change_follow_up: str = ""
    requirement_change_recommended_answer: str = ""
    debugging_follow_up: str = ""
    debugging_recommended_answer: str = ""
    independence_questions: list[IndependenceItem] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    runner_type: str = "none"
    allowed_languages: list[str] = Field(default_factory=list)
    runtime_limits: dict[str, Any] = Field(default_factory=dict)
    references: list[Reference] = Field(default_factory=list)
    last_verified: str = "2026-07-15"
    freshness_days: int = 365
    status: PublishStatus = "published"
    role_tracks: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    variant_family: str = ""

    def candidate_projection(self) -> dict[str, Any]:
        """Shareable fields only — no answers, rubrics, or interviewer guidance."""
        return {
            "id": self.id,
            "title": self.title,
            "domain": self.domain,
            "level": self.level,
            "task": self.task,
            "constraints": list(self.constraints),
            "starter_files": dict(self.starter_files),
            "allowed_languages": list(self.allowed_languages),
            "hints_available": len(self.hints),
        }

    def interviewer_projection(self) -> dict[str, Any]:
        return self.model_dump()
