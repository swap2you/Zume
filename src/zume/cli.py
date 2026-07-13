"""Zume command-line interface and workflow orchestration."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from zume import candidate as cand
from zume import config as cfg
from zume import feedback as fb
from zume import interview as iv
from zume import scheduling as sched
from zume import screening as scr
from zume.ingest import extract_text, parse_resume
from zume.models import Decision, ScreeningResult
from zume.storage import Storage
from zume.validation import check_privacy, validate_candidate_folder, validate_docx

app = typer.Typer(name="zume", help="Local-first Senior SDET hiring operations toolkit.",
                  no_args_is_help=True)
console = Console(soft_wrap=True)


def _root() -> Path:
    return cfg.find_root()


def _promote_if_valid(folder: Path, artifacts: list[Path]) -> list[str]:
    """Copy structurally valid DOCX artifacts into 99-final."""
    issues: list[str] = []
    for artifact in artifacts:
        if artifact.suffix != ".docx":
            continue
        report = validate_docx(artifact)
        if report.ok:
            cand.versioned_write_bytes(folder / "99-final" / artifact.name,
                                       artifact.read_bytes())
        else:
            issues.extend(report.errors)
    return issues


def _finish(folder: Path, candidate, artifacts: list[Path]) -> None:
    for artifact in artifacts:
        cand.record_artifact(candidate, folder, artifact)
    issues = _promote_if_valid(folder, artifacts)
    cand.save_candidate(folder, candidate)
    with Storage(_root()) as storage:
        storage.sync_candidate(candidate, folder)
    for issue in issues:
        console.print(f"[yellow]Not promoted to 99-final:[/] {issue}")


def _read_text_argument(value: str) -> str:
    path = Path(value)
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return value


# ---------------------------------------------------------------------------
# Workflows


def run_filter_resume(input_path: Optional[Path], text_file: Optional[Path],
                      name: Optional[str]) -> Path:
    root = _root()
    if input_path is None and text_file is None:
        raise typer.BadParameter("Provide --input <resume file> and/or --text-file <pasted text>.")
    if input_path is not None and not input_path.exists():
        raise typer.BadParameter(f"Input file not found: {input_path}")
    text = ""
    if input_path is not None:
        text = extract_text(input_path)
    if text_file is not None:
        text = (text + "\n" + text_file.read_text(encoding="utf-8", errors="replace")).strip()
    profile = parse_resume(text, name_override=name)

    candidate, folder = cand.new_candidate(root, profile.name)
    if input_path is not None:
        source = cand.copy_source_file(folder, input_path, kind="resume")
        if source.stored_path not in {s.stored_path for s in candidate.source_files}:
            candidate.source_files.append(source)
    else:
        pasted = folder / "00-source" / "resume-pasted.txt"
        cand.atomic_write_text(pasted, text)
        source = cand.copy_source_file(folder, pasted, kind="pasted-text")
        if source.stored_path not in {s.stored_path for s in candidate.source_files}:
            candidate.source_files.append(source)
    candidate.experience_years = profile.experience_years

    standard = cfg.load_hiring_standard(root)
    theme = cfg.load_theme(root)
    result = scr.screen_resume(profile, standard)

    screening_dir = folder / "01-screening"
    comms_dir = folder / "06-communications"
    artifacts = [
        screening_dir / "Standardized_Resume.docx",
        screening_dir / "ATS_Screening.docx",
        screening_dir / "Recruiter_Feedback.docx",
    ]
    scr.generate_standardized_resume(theme, profile, result, artifacts[0])
    scr.generate_ats_screening(theme, result, artifacts[1])
    scr.generate_recruiter_feedback(theme, result, artifacts[2],
                                    comms_dir / "Recruiter_Feedback.md")
    cand.atomic_write_text(screening_dir / "screening.json",
                           json.dumps(result.model_dump(), indent=2, ensure_ascii=False))

    status = {
        Decision.PROCEED: ("SCREENING", "Screening passed: proceed to technical screen."),
        Decision.CONDITIONAL: ("CONDITIONAL_SCREEN", "Conditional technical screen required."),
        Decision.DO_NOT_PROCEED: ("DO_NOT_PROCEED", "Screening decision: do not proceed."),
    }[result.decision]
    cand.record_status(candidate, status[0], status[1])
    _finish(folder, candidate, artifacts + [comms_dir / "Recruiter_Feedback.md"])
    with Storage(root) as storage:
        cid = storage.upsert_candidate(candidate)
        storage.record_screening(cid, result)
        storage.record_communication(cid, "recruiter-screening",
                                     f"Profile Screening Feedback - {profile.name}",
                                     "06-communications/Recruiter_Feedback.md")

    console.print(f"Decision: {result.decision.value} (score {result.score_percent:g}%)")
    console.print(f"Candidate folder: {folder}")
    return folder


def _load_screening(folder: Path) -> ScreeningResult:
    path = folder / "01-screening" / "screening.json"
    if not path.exists():
        raise typer.BadParameter(
            "No screening found for this candidate. Run 'zume filter-resume' first.")
    return ScreeningResult.model_validate_json(path.read_text(encoding="utf-8"))


def run_interview_prep(candidate_ref: str) -> Path:
    root = _root()
    folder = cand.resolve_candidate(root, candidate_ref)
    candidate = cand.load_candidate(folder)
    result = _load_screening(folder)
    theme = cfg.load_theme(root)
    library = cfg.load_exercise_library(root)

    kit = iv.build_kit(library, result)
    prep_dir = folder / "03-interview-prep"
    artifacts = [
        prep_dir / "Candidate_Focus_Sheet.docx",
        prep_dir / "Full_Interview_Guide.docx",
        prep_dir / "Scorecard.docx",
        prep_dir / "Exercise_Pack.docx",
    ]
    iv.generate_focus_sheet(theme, kit, result, artifacts[0])
    iv.generate_interview_guide(theme, kit, library, artifacts[1])
    iv.generate_scorecard(theme, kit, artifacts[2])
    iv.generate_exercise_pack(theme, kit, artifacts[3])
    cand.atomic_write_text(prep_dir / "interview-kit.json",
                           json.dumps(kit.model_dump(), indent=2, ensure_ascii=False))
    _finish(folder, candidate, artifacts)
    with Storage(root) as storage:
        cid = storage.upsert_candidate(candidate)
        storage.record_interview_kit(cid, kit)
    console.print(f"Interview kit generated with {len(kit.exercises)} exercises.")
    console.print(f"Candidate folder: {folder}")
    return folder


def run_schedule_interview(candidate_ref: str, image: Optional[Path],
                           details: Optional[str]) -> Path:
    root = _root()
    folder = cand.resolve_candidate(root, candidate_ref)
    candidate = cand.load_candidate(folder)
    theme = cfg.load_theme(root)

    if image is not None:
        if not image.exists():
            raise typer.BadParameter(f"Screenshot not found: {image}")
        source = cand.copy_source_file(folder, image, kind="schedule-image")
        if source.stored_path not in {s.stored_path for s in candidate.source_files}:
            candidate.source_files.append(source)

    details_text = _read_text_argument(details) if details else None
    record = sched.build_schedule(candidate.display_name, image, details_text)

    schedule_dir = folder / "02-schedule"
    comms_dir = folder / "06-communications"
    schedule_doc = schedule_dir / "Interview_Schedule.docx"
    sched.generate_schedule_doc(theme, record, schedule_doc)
    cand.atomic_write_text(schedule_dir / "schedule.json",
                           json.dumps(record.model_dump(), indent=2, ensure_ascii=False))
    drafts = sched.build_communication_drafts(record)
    drafts_md = comms_dir / "Schedule_Drafts.md"
    sched.write_draft_markdown(drafts, drafts_md)

    if not record.needs_confirmation:
        cand.record_status(candidate, "INTERVIEW_SCHEDULED",
                           f"Interview scheduled for {record.date} {record.time}.")
    _finish(folder, candidate, [schedule_doc, drafts_md])
    with Storage(root) as storage:
        cid = storage.upsert_candidate(candidate)
        for draft in drafts:
            storage.record_communication(cid, draft.kind, draft.subject,
                                         "06-communications/Schedule_Drafts.md")
    if record.needs_confirmation:
        console.print("[yellow]Schedule details are incomplete. Re-run with --details "
                      "(text or file with 'Date:', 'Time:', ... lines) to confirm.[/]")
    console.print(f"Candidate folder: {folder}")
    return folder


def run_interview_feedback(candidate_ref: str, notes: str, leadership: bool) -> Path:
    root = _root()
    folder = cand.resolve_candidate(root, candidate_ref)
    candidate = cand.load_candidate(folder)
    theme = cfg.load_theme(root)

    notes_text = _read_text_argument(notes)
    notes_path = folder / "04-interview" / "interviewer-notes.txt"
    cand.versioned_write_bytes(notes_path, notes_text.encode("utf-8"))

    result = fb.evaluate_notes(candidate.display_name, notes_text)
    feedback_dir = folder / "05-feedback"
    comms_dir = folder / "06-communications"
    artifacts = [
        feedback_dir / "Final_Evaluation.docx",
        feedback_dir / "Completed_Scorecard.docx",
        feedback_dir / "Recruiter_Feedback_Post_Interview.docx",
    ]
    fb.generate_final_evaluation(theme, result, notes_text, artifacts[0])
    fb.generate_completed_scorecard(theme, result, artifacts[1])
    fb.generate_recruiter_feedback(theme, result, artifacts[2],
                                   comms_dir / "Recruiter_Feedback_Post_Interview.md")
    if leadership:
        leadership_doc = feedback_dir / "Leadership_Feedback.docx"
        fb.generate_leadership_feedback(theme, result, leadership_doc,
                                        comms_dir / "Leadership_Feedback.md")
        artifacts.append(leadership_doc)
    cand.atomic_write_text(feedback_dir / "feedback.json",
                           json.dumps(result.model_dump(), indent=2, ensure_ascii=False))

    cand.record_status(candidate, "INTERVIEWED", "Interview feedback recorded.")
    cand.record_status(candidate, result.status, result.recommendation)
    _finish(folder, candidate, artifacts)
    with Storage(root) as storage:
        cid = storage.upsert_candidate(candidate)
        storage.record_feedback(cid, result)
        storage.record_communication(cid, "recruiter-final",
                                     f"Interview Feedback - {candidate.display_name}",
                                     "06-communications/Recruiter_Feedback_Post_Interview.md")

    console.print(f"Decision: {result.decision.value} (score {result.total_percent:g}%)")
    console.print(f"Status update: {result.status}")
    console.print(f"Candidate folder: {folder}")
    return folder


# ---------------------------------------------------------------------------
# Commands


@app.command("filter-resume")
def filter_resume_cmd(
    input: Optional[Path] = typer.Option(None, "--input", help="Resume PDF/DOCX/TXT path."),
    text_file: Optional[Path] = typer.Option(None, "--text-file",
                                             help="File containing pasted resume text."),
    name: Optional[str] = typer.Option(None, "--name", help="Candidate name override."),
) -> None:
    """Trigger: Filter Resume - Automation Hiring."""
    run_filter_resume(input, text_file, name)


@app.command("interview-prep")
def interview_prep_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
) -> None:
    """Trigger: Interview Prep - Automation Hiring."""
    run_interview_prep(candidate)


@app.command("schedule-interview")
def schedule_interview_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    image: Optional[Path] = typer.Option(None, "--image", help="Schedule screenshot path."),
    details: Optional[str] = typer.Option(
        None, "--details",
        help="Confirmed schedule details: text or a file with 'Date:', 'Time:', ... lines."),
) -> None:
    """Trigger: Schedule Interview - Automation Hiring."""
    run_schedule_interview(candidate, image, details)


@app.command("interview-feedback")
def interview_feedback_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    notes: str = typer.Option(..., "--notes", help="Interview notes: file path or text."),
    leadership: bool = typer.Option(False, "--leadership",
                                    help="Also generate leadership feedback."),
) -> None:
    """Trigger: Interview Feedback - Automation Hiring."""
    run_interview_feedback(candidate, notes, leadership)


@app.command("validate")
def validate_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    render: bool = typer.Option(True, "--render/--no-render",
                                help="Render DOCX via LibreOffice when available."),
) -> None:
    """Validate a candidate folder, its DOCX artifacts and git privacy."""
    root = _root()
    folder = cand.resolve_candidate(root, candidate)
    report = validate_candidate_folder(folder, render=render)
    report.merge(check_privacy(root))
    for line in report.passed:
        console.print(f"[green]PASS[/]  {line}")
    for line in report.warnings:
        console.print(f"[yellow]WARN[/]  {line}")
    for line in report.errors:
        console.print(f"[red]FAIL[/]  {line}")
    console.print(f"\n{len(report.passed)} passed, {len(report.warnings)} warnings, "
                  f"{len(report.errors)} errors")
    if not report.ok:
        raise typer.Exit(code=1)


@app.command("demo")
def demo_cmd() -> None:
    """Run the fictional end-to-end sample through every workflow."""
    root = _root()
    examples = root / "examples" / "fictional-candidate"
    console.rule("1/4 Filter Resume")
    folder = run_filter_resume(examples / "resume.txt", None, None)
    ref = folder.name
    console.rule("2/4 Interview Prep")
    run_interview_prep(ref)
    console.rule("3/4 Schedule Interview")
    run_schedule_interview(ref, None, str(examples / "schedule.txt"))
    console.rule("4/4 Interview Feedback")
    run_interview_feedback(ref, str(examples / "interview-notes.txt"), leadership=True)
    console.rule("Demo complete")
    console.print(f"Demo candidate folder: {folder.name}")
    console.print(f"Validate with: zume validate --candidate {folder.name}")


@app.command("run")
def run_cmd(
    trigger: str = typer.Option(..., "--trigger", help="Exact natural-language trigger."),
    input: Optional[Path] = typer.Option(None, "--input"),
    text_file: Optional[Path] = typer.Option(None, "--text-file"),
    name: Optional[str] = typer.Option(None, "--name"),
    candidate: Optional[str] = typer.Option(None, "--candidate"),
    image: Optional[Path] = typer.Option(None, "--image"),
    details: Optional[str] = typer.Option(None, "--details"),
    notes: Optional[str] = typer.Option(None, "--notes"),
    leadership: bool = typer.Option(False, "--leadership"),
) -> None:
    """Map an exact natural-language trigger to its workflow."""
    workflow = match_trigger(_root(), trigger)
    if workflow is None:
        known = "\n  ".join(cfg.load_triggers(_root()).values())
        raise typer.BadParameter(f"Unknown trigger: {trigger!r}. Known triggers:\n  {known}")
    if workflow == "filter_resume":
        run_filter_resume(input, text_file, name)
        return
    if candidate is None:
        raise typer.BadParameter(f"The '{trigger}' trigger requires --candidate.")
    if workflow == "interview_prep":
        run_interview_prep(candidate)
    elif workflow == "schedule_interview":
        run_schedule_interview(candidate, image, details)
    elif workflow == "interview_feedback":
        if notes is None:
            raise typer.BadParameter("This trigger requires --notes.")
        run_interview_feedback(candidate, notes, leadership)


def _normalize_trigger(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", text).strip().lower()


def match_trigger(root: Path, text: str) -> Optional[str]:
    normalized = _normalize_trigger(text)
    for workflow, phrase in cfg.load_triggers(root).items():
        if _normalize_trigger(phrase) == normalized:
            return workflow
    return None


def main() -> None:
    app()


if __name__ == "__main__":
    main()
