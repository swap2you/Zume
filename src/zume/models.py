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


class EvidenceType(str, Enum):
    """Deterministic classification of how strong a piece of evidence is."""

    SKILLS_LIST = "skills_list"
    RESPONSIBILITY = "responsibility"
    PROJECT = "project"
    QUANTIFIED = "quantified"
    INFERRED = "inferred"
    MISSING = "missing"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ExperienceState(str, Enum):
    """Explicit state for the overall-experience gate."""

    PASSED = "passed"
    FAILED = "failed"
    UNKNOWN = "unknown"


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
    # Phase 4 — deterministic evidence quality signals.
    evidence_type: EvidenceType = EvidenceType.MISSING
    confidence: Confidence = Confidence.NONE
    credit: float = 0.0
    recency: str = ""
    duration: str = ""
    ownership_present: bool = False
    summary_or_skills_only: bool = False
    source_hint: str = ""


class ScreeningResult(BaseModel):
    candidate_name: str
    experience_years: float | None
    experience_state: ExperienceState = ExperienceState.UNKNOWN
    experience_detail: str = ""
    experience_claims: list[float] = Field(default_factory=list)
    # Retained for backward compatibility; True only when state is PASSED.
    experience_gate_passed: bool = False
    evidence: list[EvidenceItem]
    reject_signals: list[str] = Field(default_factory=list)
    # Resume evidence coverage (NOT a competency score). See screening docs.
    score_percent: float
    decision: Decision
    manual_review_required: bool = False
    risks: list[str] = Field(default_factory=list)
    validation_questions: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)


class ScheduleRecord(BaseModel):
    candidate_name: str
    date: str = ""
    time: str = ""
    timezone: str = ""
    duration: str = ""
    duration_minutes: int | None = None
    # confirmed | missing | mismatch — drives whether the schedule can be trusted.
    duration_status: str = "missing"
    interviewers: str = ""
    platform: str = ""  # meeting method
    extraction_source: str = "manual"  # manual | image-metadata | text
    needs_confirmation: bool = True
    # Per-field provenance and confidence (Phase 13).
    field_sources: dict[str, str] = Field(default_factory=dict)
    field_confidence: dict[str, str] = Field(default_factory=dict)
    validation_issues: list[str] = Field(default_factory=list)
    notes: str = ""
    created_at: str = Field(default_factory=utc_now_iso)


class IndependenceQuestion(BaseModel):
    """An interviewer independence-verification question with its expected answer."""

    question: str
    recommended_answer: str = ""


class ExerciseSelection(BaseModel):
    area: str
    area_label: str
    exercise_id: str
    title: str
    skill_area: str = ""
    variant_family: str = ""
    difficulty: str = ""
    status: str = "active"
    rotation_group: str = ""
    fingerprint: str = ""
    task: str = ""
    requirement_change_follow_up: str = ""
    requirement_change_recommended_answer: str = ""
    debugging_follow_up: str = ""
    debugging_recommended_answer: str = ""
    expected_reasoning: str = ""
    reference_solution: str = ""
    scoring_rubric: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    independence_questions: list[IndependenceQuestion] = Field(default_factory=list)


class GuideFollowUp(BaseModel):
    question: str
    recommended_answer: str


class GuideQuestion(BaseModel):
    id: str
    area: str
    area_label: str
    level: str
    question: str
    recommended_answer: str
    key_points: list[str] = Field(default_factory=list)
    strong_signals: list[str] = Field(default_factory=list)
    weak_signals: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    follow_ups: list[GuideFollowUp] = Field(default_factory=list)
    score_guidance: str = ""
    time_minutes: int = 5


class KnockoutItem(BaseModel):
    area_label: str
    question: str
    recommended_answer: str
    strong_indicator: str = ""
    weak_indicator: str = ""


class AgendaSegment(BaseModel):
    start: str
    end: str
    minutes: int
    title: str
    focus: str = ""


class InterviewKit(BaseModel):
    candidate_name: str
    focus_areas: list[str]
    validation_questions: list[str]
    exercises: list[ExerciseSelection]
    screening_decision: str = ""
    unverified_mandatory: list[str] = Field(default_factory=list)
    override_reason: str = ""
    # Phase 4 — real 180-minute operating model.
    duration_minutes: int = 180
    agenda: list[AgendaSegment] = Field(default_factory=list)
    knockout: list[KnockoutItem] = Field(default_factory=list)
    knockout_minutes: int = 20
    knockout_decision_rule: list[str] = Field(default_factory=list)
    question_sections: dict[str, list[GuideQuestion]] = Field(default_factory=dict)
    reserve_questions: list[GuideQuestion] = Field(default_factory=list)
    optional_area: str = ""
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
    # Part 5 — interview-evidence completeness gate.
    assessed_areas: list[str] = Field(default_factory=list)
    missing_areas: list[str] = Field(default_factory=list)
    decision_permitted: bool = True
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
    override_reasons: list[str] = Field(default_factory=list)
    # Phase 6 — exercises assigned on the first prep; preserved across reruns.
    assigned_exercise_ids: list[str] = Field(default_factory=list)
    rotation_reasons: list[str] = Field(default_factory=list)
    # Lockdown Part 3 — reasons recorded when a finalized candidate is reopened.
    reopen_reasons: list[str] = Field(default_factory=list)
    contract_version: int = 1
    updated_at: str = Field(default_factory=utc_now_iso)
