"""Pydantic models for Zume records."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class EvidenceLevel(str, Enum):
    EXPLICIT = "explicit"
    INFERRED = "inferred"
    MISSING = "missing"


class Decision(str, Enum):
    PROCEED = "Proceed"
    CONDITIONAL = "Conditional Technical Screen"
    DO_NOT_PROCEED = "Do Not Proceed"


class SourceFile(BaseModel):
    original_name: str
    stored_path: str
    sha256: str
    kind: str  # resume | schedule-image | notes | pasted-text
    added_at: str = Field(default_factory=utc_now_iso)


class EvidenceItem(BaseModel):
    skill: str
    label: str
    level: EvidenceLevel
    weight: int = 0
    mandatory: bool = True
    quotes: list[str] = Field(default_factory=list)
    note: str = ""


class ScreeningResult(BaseModel):
    candidate_name: str
    experience_years: float | None
    experience_gate_passed: bool
    evidence: list[EvidenceItem]
    reject_signals: list[str] = Field(default_factory=list)
    score_percent: float
    decision: Decision
    risks: list[str] = Field(default_factory=list)
    validation_questions: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)


class ScheduleRecord(BaseModel):
    candidate_name: str
    date: str = ""
    time: str = ""
    duration: str = ""
    interviewers: str = ""
    platform: str = ""
    extraction_source: str = "manual"  # manual | image-metadata | text
    needs_confirmation: bool = True
    notes: str = ""
    created_at: str = Field(default_factory=utc_now_iso)


class ExerciseSelection(BaseModel):
    area: str
    area_label: str
    exercise_id: str
    title: str
    task: str
    expected_answer: str
    reference_solution: str
    follow_up: str
    red_flags: list[str] = Field(default_factory=list)


class InterviewKit(BaseModel):
    candidate_name: str
    focus_areas: list[str]
    validation_questions: list[str]
    exercises: list[ExerciseSelection]
    created_at: str = Field(default_factory=utc_now_iso)


class IndependenceObservations(BaseModel):
    unexplained_pauses: str = "Not observed"
    audible_device_activity: str = "Not observed"
    sudden_quality_shift: str = "Not observed"
    can_explain_solution: str = "Not assessed"
    can_modify_solution: str = "Not assessed"
    confidence_independent_execution: str = "Not assessed"


class SkillScore(BaseModel):
    skill: str
    label: str
    score: int  # 0-10
    evidence: str = ""


class FeedbackResult(BaseModel):
    candidate_name: str
    skill_scores: list[SkillScore]
    total_percent: float
    mandatory_override_failed: list[str] = Field(default_factory=list)
    recommendation: str
    decision: Decision
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    observations: IndependenceObservations = Field(default_factory=IndependenceObservations)
    status: str = "INTERVIEWED"
    created_at: str = Field(default_factory=utc_now_iso)


class CommunicationDraft(BaseModel):
    kind: str  # proceed | do-not-proceed | join | reschedule | cancel | no-show | leadership
    subject: str
    body: str
    created_at: str = Field(default_factory=utc_now_iso)


class StatusEvent(BaseModel):
    status: str
    at: str = Field(default_factory=utc_now_iso)
    note: str = ""


class Candidate(BaseModel):
    first_name: str
    last_name: str
    display_name: str
    folder_name: str
    created_date: str
    status: str = "RECEIVED"
    experience_years: float | None = None
    source_files: list[SourceFile] = Field(default_factory=list)
    status_history: list[StatusEvent] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=utc_now_iso)
