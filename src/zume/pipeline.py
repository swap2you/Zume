"""High-level intake and finalize orchestration (Phases 7, 8, 15).

`run_intake` builds the complete pre-interview package and STOPS. It never
generates interview feedback. `run_finalize` only runs after explicit notes.
Both use the v2 three-folder contract and idempotent, versionless writes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date as date_cls
from pathlib import Path
from typing import Optional

from zume import candidate as cand
from zume import config as cfg
from zume import deliverables as dl
from zume import exercises as ex_lib
from zume import feedback as fb
from zume import interview as iv
from zume import questions as q_lib
from zume import scheduling as sched
from zume import screening as scr
from zume.ingest import extract_text, parse_resume
from zume.models import Decision, ScreeningResult
from zume.providers import get_provider
from zume.storage import Storage
from zume.validation import validate_docx

READY = "READY_FOR_INTERVIEW"
SCHEDULED = "INTERVIEW_SCHEDULED"
DO_NOT_PROCEED = "DO_NOT_PROCEED"
FINALIZE_ALLOWED_STATES = {READY, SCHEDULED}

WAIT_MESSAGE = ("Pre-interview package is ready. Zume is waiting for interview notes. "
                "No feedback has been generated.")


class WorkflowError(RuntimeError):
    """Raised when a workflow gate blocks progress."""


@dataclass
class IntakeResult:
    folder: Path
    screening: ScreeningResult
    status: str
    deliverables: list[str] = field(default_factory=list)
    export_zip: Optional[Path] = None
    validation_errors: list[str] = field(default_factory=list)
    schedule_needs_confirmation: bool = False
    feedback_generated: bool = False  # invariant: always False after intake


@dataclass
class FinalizeResult:
    folder: Path
    status: str
    deliverables: list[str] = field(default_factory=list)
    export_zip: Optional[Path] = None
    validation_errors: list[str] = field(default_factory=list)


def _write_source_resume(folder: Path, resume_path: Path | None, text: str) -> str:
    source_dir = folder / cand.SOURCE_DIR
    source_dir.mkdir(parents=True, exist_ok=True)
    if resume_path is not None:
        target = source_dir / f"original-resume{resume_path.suffix.lower()}"
        cand.atomic_write_bytes(target, resume_path.read_bytes())
        return target.name
    target = source_dir / "original-resume.txt"
    cand.atomic_write_text(target, text)
    return target.name


def _write_internal_json(folder: Path, name: str, payload: object) -> None:
    cand.atomic_write_text(folder / cand.INTERNAL_DIR / name,
                           json.dumps(payload, indent=2, ensure_ascii=False,
                                      default=lambda o: o.model_dump()))


def _validate_docx_files(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        report = validate_docx(path)
        if not report.ok:
            errors.extend(f"{path.name}: {e}" for e in report.errors)
    return errors


def run_intake(root: Path, resume_path: Path | None = None,
               resume_text: str | None = None, name: str | None = None,
               schedule_image: Path | None = None,
               schedule_details: str | None = None,
               override: bool = False, override_reason: str | None = None,
               rotate_exercises: bool = False, rotation_reason: str | None = None,
               keep_history: bool = False,
               today: date_cls | None = None) -> IntakeResult:
    if resume_path is None and not resume_text:
        raise WorkflowError("Provide a resume file or resume text.")
    text = extract_text(resume_path) if resume_path is not None else ""
    if resume_text:
        text = (text + "\n" + resume_text).strip()
    profile = parse_resume(text, name_override=name)

    standard = cfg.load_hiring_standard(root)
    theme = cfg.load_theme(root)
    exercise_cfg = cfg.load_exercise_library(root)
    question_areas = q_lib.load_library(cfg.load_question_library(root))
    privacy = cfg.load_privacy(root)

    candidate, folder = cand.new_package_candidate(root, profile.name, on_date=today)
    candidate.experience_years = profile.experience_years
    source_name = _write_source_resume(folder, resume_path, text)
    if source_name not in {s.stored_path for s in candidate.source_files}:
        candidate.source_files.append(cand.copy_source_file(
            folder, folder / cand.SOURCE_DIR / source_name, kind="resume",
            subdir=cand.SOURCE_DIR))

    result = scr.screen_resume(profile, standard)
    _write_internal_json(folder, "screening.json", result)

    written: list[Path] = []

    summary_bytes = dl.screening_summary(
        theme, result, get_provider().summarize_resume(profile.text), source_name)
    written.append(cand.write_deliverable(folder, dl.SCREENING_SUMMARY, summary_bytes,
                                          keep_history=keep_history))

    blocked = result.decision == Decision.DO_NOT_PROCEED and not override
    if result.decision == Decision.DO_NOT_PROCEED and override:
        if not override_reason or not override_reason.strip():
            raise WorkflowError("--override requires a non-empty --override-reason.")
    effective_override = override_reason.strip() if (override and override_reason) else ""

    keep: set[str] = {dl.SCREENING_SUMMARY}
    schedule_needs_confirmation = False

    if not blocked:
        kit = _build_kit(exercise_cfg, question_areas, result, candidate,
                         effective_override, rotate_exercises, rotation_reason, root)
        _write_internal_json(folder, "interview-plan.json", kit)
        written.append(cand.write_deliverable(
            folder, dl.INTERVIEW_GUIDE,
            dl.three_hour_guide(theme, kit, exercise_cfg.get("scoring_dimensions", {})),
            keep_history=keep_history))
        written.append(cand.write_deliverable(
            folder, dl.SCORECARD, dl.interview_scorecard(theme, kit),
            keep_history=keep_history))
        written.append(cand.write_deliverable(
            folder, dl.CANDIDATE_SHEET, dl.candidate_exercise_sheet(theme, kit),
            keep_history=keep_history))
        keep |= {dl.INTERVIEW_GUIDE, dl.SCORECARD, dl.CANDIDATE_SHEET}

        if schedule_image is not None or schedule_details is not None:
            record = sched.build_schedule(candidate.display_name, schedule_image,
                                          _read_arg(schedule_details), today=today)
            _write_internal_json(folder, "schedule.json", record)
            drafts = sched.build_communication_drafts(record)
            written.append(cand.write_deliverable(
                folder, dl.SCHEDULE_COMMS, dl.schedule_and_comms(theme, record, drafts),
                keep_history=keep_history))
            keep.add(dl.SCHEDULE_COMMS)
            schedule_needs_confirmation = record.needs_confirmation

    # Feedback deliverables must never exist after intake.
    cand.clean_deliverables(folder, keep)

    if blocked:
        status = DO_NOT_PROCEED
        cand.record_status_once(candidate, status,
                                "Screening decision: do not proceed (no interview package).")
    else:
        if effective_override:
            if effective_override not in candidate.override_reasons:
                candidate.override_reasons.append(effective_override)
            cand.record_status_once(candidate, "INTERVIEW_PREP_OVERRIDE",
                                    f"Interview package generated over a Do-Not-Proceed "
                                    f"decision. Reason: {effective_override}")
        status = SCHEDULED if (dl.SCHEDULE_COMMS in keep and not schedule_needs_confirmation) \
            else READY
        cand.record_status_once(candidate, status, "Pre-interview package ready.")

    validation_errors = _validate_docx_files(written)
    cand.save_candidate(folder, candidate)
    with Storage(root) as storage:
        cid = storage.upsert_candidate(candidate)
        storage.record_screening(cid, result)

    export_zip = None
    if not blocked:
        export_zip = cand.export_deliverables(root, folder,
                                              privacy.get("export_dir", "output"))
    return IntakeResult(
        folder=folder, screening=result, status=status,
        deliverables=[p.name for p in written], export_zip=export_zip,
        validation_errors=validation_errors,
        schedule_needs_confirmation=schedule_needs_confirmation,
        feedback_generated=False,
    )


def _build_kit(exercise_cfg, question_areas, result, candidate,
               effective_override, rotate_exercises, rotation_reason, root):
    preassigned = candidate.assigned_exercise_ids or None
    if rotate_exercises:
        if not rotation_reason or not rotation_reason.strip():
            raise WorkflowError("--rotate-exercises requires a non-empty --rotation-reason.")
        preassigned = None  # force fresh rotation
    if preassigned is None:
        exercises_by_area = ex_lib.load_exercises(exercise_cfg)
        with Storage(root) as storage:
            cid = storage.upsert_candidate(candidate)
            usage = storage.get_exercise_usage()
            history = storage.get_candidate_exercise_history(cid)
        selector = ex_lib.ExerciseSelector(exercises_by_area, usage=usage,
                                           candidate_history=history)
        kit = iv.build_kit(exercise_cfg, result, override_reason=effective_override,
                           selector=selector, question_areas=question_areas)
        new_ids = [e.exercise_id for e in kit.exercises]
        if rotate_exercises and candidate.assigned_exercise_ids:
            note = (f"Exercises rotated. Reason: {rotation_reason.strip()}. "
                    f"Old: {candidate.assigned_exercise_ids}. New: {new_ids}.")
            candidate.rotation_reasons.append(note)
            cand.record_status(candidate, "EXERCISES_ROTATED", note)
        candidate.assigned_exercise_ids = new_ids
        with Storage(root) as storage:
            cid = storage.upsert_candidate(candidate)
            storage.record_exercise_assignments(cid, kit.exercises)
        return kit
    # Preserve the exact prior assignment on normal reruns (idempotent).
    return iv.build_kit(exercise_cfg, result, override_reason=effective_override,
                        question_areas=question_areas, preassigned_ids=preassigned)


def run_finalize(root: Path, candidate_ref: str, notes: str,
                 leadership: bool = False, keep_history: bool = False) -> FinalizeResult:
    folder = cand.resolve_candidate(root, candidate_ref)
    candidate = cand.load_candidate(folder)
    if candidate.status not in FINALIZE_ALLOWED_STATES:
        raise WorkflowError(
            f"Candidate status is {candidate.status!r}; finalize requires one of "
            f"{sorted(FINALIZE_ALLOWED_STATES)}. Run intake first.")
    notes_text = _read_arg(notes) or ""
    if not notes_text.strip():
        raise WorkflowError("Finalize requires non-empty interview notes.")

    theme = cfg.load_theme(root)
    privacy = cfg.load_privacy(root)
    cand.atomic_write_text(folder / cand.INTERNAL_DIR / "interviewer-notes.txt", notes_text)

    result = fb.evaluate_notes(candidate.display_name, notes_text)
    _write_internal_json(folder, "feedback.json", result)

    written = [
        cand.write_deliverable(folder, dl.FINAL_EVALUATION,
                               dl.final_evaluation(theme, result, notes_text),
                               keep_history=keep_history),
        cand.write_deliverable(folder, dl.POST_INTERVIEW_COMMS,
                               dl.post_interview_comms(theme, result, include_leadership=leadership),
                               keep_history=keep_history),
    ]
    validation_errors = _validate_docx_files(written)

    cand.record_status_once(candidate, "INTERVIEWED", "Interview feedback recorded.")
    cand.record_status_once(candidate, result.status, result.recommendation)
    cand.save_candidate(folder, candidate)
    with Storage(root) as storage:
        cid = storage.upsert_candidate(candidate)
        storage.record_feedback(cid, result)

    export_zip = cand.export_deliverables(root, folder, privacy.get("export_dir", "output"))
    return FinalizeResult(folder=folder, status=result.status,
                          deliverables=[p.name for p in written], export_zip=export_zip,
                          validation_errors=validation_errors)


def _read_arg(value: str | None) -> str | None:
    if value is None:
        return None
    path = Path(value)
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return value
