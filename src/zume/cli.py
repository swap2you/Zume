"""Zume command-line interface and workflow orchestration."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from zume import candidate as cand
from zume import config as cfg
from zume import pipeline
from zume.storage import Storage
from zume.validation import check_privacy, validate_candidate_folder

app = typer.Typer(name="zume", help="Local-first Senior SDET hiring operations toolkit.",
                  no_args_is_help=True)
console = Console(soft_wrap=True)


def _root() -> Path:
    return cfg.find_root()


# ---------------------------------------------------------------------------
# Legacy command lockdown (Lockdown Part 2)
#
# The v1 workflow commands used to create numbered candidate folders, versioned
# files and a 99-final folder. They are now hidden, print a deprecation notice,
# and either delegate to the v2 intake/finalize path where the mapping is
# unambiguous or refuse to run. No legacy command creates a v1 candidate folder.

LEGACY_DEPRECATION = (
    "[yellow]Deprecated command.[/] Zume now uses two commands: "
    "'zume intake' (pre-interview package) and 'zume finalize' (after notes). "
    "See CURSOR_START_HERE.md.")


def _deprecation_notice(old: str, guidance: str) -> None:
    console.print(LEGACY_DEPRECATION)
    console.print(f"[yellow]'{old}' is retired.[/] {guidance}")


# ---------------------------------------------------------------------------
# Commands


@app.command("filter-resume", hidden=True)
def filter_resume_cmd(
    input: Optional[Path] = typer.Option(None, "--input", help="Resume PDF/DOCX/TXT path."),
    text_file: Optional[Path] = typer.Option(None, "--text-file",
                                             help="File containing pasted resume text."),
    name: Optional[str] = typer.Option(None, "--name", help="Candidate name override."),
) -> None:
    """(Deprecated) Delegates to 'zume intake'. Never creates a v1 folder."""
    _deprecation_notice("filter-resume", "Delegating to 'zume intake' (v2 contract).")
    intake_cmd(resume=input, text_file=text_file, name=name, schedule_image=None,
               schedule_details=None, override=False, override_reason=None,
               rotate_exercises=False, rotation_reason=None, reopen=False, reopen_reason=None)


@app.command("interview-prep", hidden=True)
def interview_prep_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    override: bool = typer.Option(False, "--override"),
    override_reason: Optional[str] = typer.Option(None, "--override-reason"),
) -> None:
    """(Deprecated) 'zume intake' already builds the full pre-interview package."""
    _deprecation_notice(
        "interview-prep",
        "'zume intake' now builds screening, guide, scorecard and exercise sheet in one "
        "step. Re-run: zume intake --resume <file>. No candidate folder was created.")
    raise typer.Exit(code=2)


@app.command("schedule-interview", hidden=True)
def schedule_interview_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    image: Optional[Path] = typer.Option(None, "--image"),
    details: Optional[str] = typer.Option(None, "--details"),
) -> None:
    """(Deprecated) Scheduling is part of 'zume intake --schedule-details'."""
    _deprecation_notice(
        "schedule-interview",
        "Re-run intake with the schedule: "
        'zume intake --resume <file> --schedule-details "<text or file>". '
        "No candidate folder was created.")
    raise typer.Exit(code=2)


@app.command("interview-feedback", hidden=True)
def interview_feedback_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    notes: str = typer.Option(..., "--notes", help="Interview notes: file path or text."),
    leadership: bool = typer.Option(False, "--leadership",
                                    help="Also generate leadership feedback."),
) -> None:
    """(Deprecated) Delegates to 'zume finalize'."""
    _deprecation_notice("interview-feedback", "Delegating to 'zume finalize' (v2 contract).")
    finalize_cmd(candidate=candidate, notes=notes, leadership=leadership)


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


@app.command("scan-secrets")
def scan_secrets_cmd(
    pii: bool = typer.Option(True, "--pii/--no-pii",
                             help="Also scan for emails and phone numbers."),
) -> None:
    """Scan git-tracked text files for secrets and (optionally) PII."""
    from zume.security import scan_repository

    findings = scan_repository(_root(), include_pii=pii)
    if not findings:
        console.print("[green]PASS[/]  no secrets or PII found in tracked files")
        return
    for finding in findings:
        console.print(f"[red]FOUND[/] {finding.kind} in {finding.path}:{finding.line}")
    raise typer.Exit(code=1)


@app.command("intake")
def intake_cmd(
    resume: Optional[Path] = typer.Option(None, "--resume", help="Resume PDF/DOCX/TXT path."),
    text_file: Optional[Path] = typer.Option(None, "--text-file",
                                             help="File with pasted resume text."),
    name: Optional[str] = typer.Option(None, "--name", help="Candidate name override."),
    schedule_image: Optional[Path] = typer.Option(None, "--schedule-image",
                                                  help="Schedule screenshot (untrusted)."),
    schedule_details: Optional[str] = typer.Option(None, "--schedule-details",
                                                   help="Schedule text or file."),
    override: bool = typer.Option(False, "--override",
                                  help="Build a full package for a Do-Not-Proceed candidate."),
    override_reason: Optional[str] = typer.Option(None, "--override-reason"),
    rotate_exercises: bool = typer.Option(False, "--rotate-exercises",
                                          help="Assign fresh exercises (needs a reason)."),
    rotation_reason: Optional[str] = typer.Option(None, "--rotation-reason"),
    reopen: bool = typer.Option(False, "--reopen",
                                help="Regenerate the package for a finalized candidate."),
    reopen_reason: Optional[str] = typer.Option(
        None, "--reopen-reason", help="Required justification when using --reopen."),
) -> None:
    """Screen a resume and build the complete pre-interview package, then stop."""
    resume_text = text_file.read_text(encoding="utf-8", errors="replace") if text_file else None
    try:
        result = pipeline.run_intake(
            _root(), resume_path=resume, resume_text=resume_text, name=name,
            schedule_image=schedule_image, schedule_details=schedule_details,
            override=override, override_reason=override_reason,
            rotate_exercises=rotate_exercises, rotation_reason=rotation_reason,
            reopen=reopen, reopen_reason=reopen_reason)
    except pipeline.WorkflowError as exc:
        console.print(f"[red]Blocked:[/] {exc}")
        raise typer.Exit(code=2) from exc
    console.print(f"Decision: {result.screening.decision.value} "
                  f"(resume evidence coverage {result.screening.score_percent:g}%)")
    console.print(f"Status: {result.status}")
    console.print("Deliverables: " + ", ".join(result.deliverables))
    if result.export_zip:
        console.print(f"Package: {result.export_zip}")
    if result.schedule_needs_confirmation:
        console.print("[yellow]Schedule needs confirmation before it can be relied on.[/]")
    for err in result.validation_errors:
        console.print(f"[red]DOCX issue:[/] {err}")
    console.print(f"Candidate folder: {result.folder}")
    if result.status != pipeline.DO_NOT_PROCEED:
        console.print(f"[bold]{pipeline.WAIT_MESSAGE}[/]")


@app.command("finalize")
def finalize_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    notes: str = typer.Option(..., "--notes", help="Interview notes: file path or text."),
    leadership: bool = typer.Option(False, "--leadership",
                                    help="Also include a leadership draft."),
) -> None:
    """After the interview: generate the final evaluation and communications."""
    try:
        result = pipeline.run_finalize(_root(), candidate, notes, leadership=leadership)
    except pipeline.WorkflowError as exc:
        console.print(f"[red]Blocked:[/] {exc}")
        raise typer.Exit(code=2) from exc
    console.print(f"Status: {result.status}")
    console.print("Deliverables: " + ", ".join(result.deliverables))
    if result.export_zip:
        console.print(f"Package: {result.export_zip}")
    for err in result.validation_errors:
        console.print(f"[red]DOCX issue:[/] {err}")
    console.print(f"Candidate folder: {result.folder}")


@app.command("demo")
def demo_cmd() -> None:
    """Run the fictional end-to-end sample: intake, then finalize."""
    root = _root()
    examples = root / "examples" / "fictional-candidate"
    # The demo is a throwaway fictional sample; start clean so it is repeatable
    # even after a previous run finalized the candidate (Part 3 intake guard).
    demo_folder = cand.candidates_root(root) / cand.folder_name_for(
        *cand.normalize_name("Aarav Mehta"))
    if demo_folder.exists():
        shutil.rmtree(demo_folder, ignore_errors=True)
    console.rule("1/2 Intake (pre-interview package)")
    intake = pipeline.run_intake(
        root, resume_path=examples / "resume.txt",
        schedule_details=str(examples / "schedule.txt"))
    console.print(f"Status: {intake.status}; deliverables: {', '.join(intake.deliverables)}")
    console.rule("2/2 Finalize (after interview notes)")
    final = pipeline.run_finalize(root, intake.folder.name,
                                  str(examples / "interview-notes.txt"), leadership=True)
    console.rule("Demo complete")
    console.print(f"Demo candidate folder: {intake.folder.name}")
    console.print(f"Final status: {final.status}")
    console.print(f"Validate with: zume validate --candidate {intake.folder.name}")


@app.command("run", hidden=True)
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
    override: bool = typer.Option(False, "--override"),
    override_reason: Optional[str] = typer.Option(None, "--override-reason"),
) -> None:
    """(Deprecated) Natural-language trigger flow. Delegates to intake/finalize only."""
    workflow = match_trigger(_root(), trigger)
    if workflow is None:
        known = "\n  ".join(cfg.load_triggers(_root()).values())
        raise typer.BadParameter(f"Unknown trigger: {trigger!r}. Known triggers:\n  {known}")
    if workflow == "filter_resume":
        _deprecation_notice("run --trigger 'Filter Resume …'", "Delegating to 'zume intake'.")
        intake_cmd(resume=input, text_file=text_file, name=name, schedule_image=None,
                   schedule_details=None, override=override, override_reason=override_reason,
                   rotate_exercises=False, rotation_reason=None, reopen=False, reopen_reason=None)
        return
    if workflow == "interview_feedback":
        if candidate is None or notes is None:
            raise typer.BadParameter("This trigger requires --candidate and --notes.")
        _deprecation_notice("run --trigger 'Interview Feedback …'",
                            "Delegating to 'zume finalize'.")
        finalize_cmd(candidate=candidate, notes=notes, leadership=leadership)
        return
    # interview_prep / schedule_interview have no unambiguous v2 delegate.
    _deprecation_notice(
        f"run --trigger {trigger!r}",
        "Interview prep and scheduling are now part of 'zume intake'. "
        "Re-run: zume intake --resume <file> [--schedule-details \"<...>\"]. "
        "No candidate folder was created.")
    raise typer.Exit(code=2)


candidate_app = typer.Typer(name="candidate", help="Candidate privacy lifecycle commands.",
                            no_args_is_help=True)
app.add_typer(candidate_app)


@candidate_app.command("export")
def candidate_export_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    include_source: bool = typer.Option(False, "--include-source",
                                        help="Also include the original resume."),
    include_internal: bool = typer.Option(False, "--include-internal",
                                          help="Also include internal working files (audit)."),
) -> None:
    """Export a clean, deliverables-only zip (interviewer + candidate copies)."""
    root = _root()
    folder = cand.resolve_candidate(root, candidate)
    privacy = cfg.load_privacy(root)
    if include_internal:
        console.print("[yellow]Warning:[/] including internal files; do not share externally.")
    package = cand.export_deliverables(root, folder, privacy.get("export_dir", "output"),
                                       include_source=include_source,
                                       include_internal=include_internal)
    record = cand.load_candidate(folder)
    # Record the export as an audit event only; never overwrite the workflow
    # status, otherwise a later finalize (ready/scheduled only) would be blocked.
    cand.record_event(record, f"Exported package: {package.name}", kind="EXPORTED")
    cand.save_candidate(folder, record)
    with Storage(root) as storage:
        storage.upsert_candidate(record)
    console.print(f"[green]Exported[/] {folder.name} -> {package} "
                  f"(workflow status unchanged: {record.status})")


@candidate_app.command("migrate")
def candidate_migrate_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    preview: bool = typer.Option(False, "--preview", help="Show planned changes only."),
    apply: bool = typer.Option(False, "--apply", help="Apply the migration."),
) -> None:
    """Migrate a legacy candidate folder to the v2 three-folder contract."""
    root = _root()
    folder = cand.resolve_candidate(root, candidate)
    if apply and not preview:
        done = cand.apply_migration(folder)
        console.print(f"[green]Migrated[/] {folder.name}")
        for label, items in done.items():
            for item in items:
                console.print(f"  {label}: {item}")
        return
    plan = cand.plan_migration(folder)
    console.print(f"[bold]Migration plan for {folder.name}:[/]")
    for label, items in plan.items():
        for item in items:
            console.print(f"  {label}: {item}")
    console.print("[yellow]Preview only.[/] Re-run with --apply to migrate. "
                  "Source files are moved, never deleted.")


@candidate_app.command("cleanup")
def candidate_cleanup_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    preview: bool = typer.Option(False, "--preview", help="Show removable files only."),
    apply: bool = typer.Option(False, "--apply", help="Remove redundant versioned files."),
) -> None:
    """Remove redundant __vN and 99-final copies after previewing them."""
    root = _root()
    folder = cand.resolve_candidate(root, candidate)
    if apply and not preview:
        removed = cand.apply_cleanup(folder)
        console.print(f"[green]Cleaned[/] {folder.name}: removed {len(removed)} file(s).")
        for item in removed:
            console.print(f"  removed: {item}")
        return
    targets = cand.plan_cleanup(folder)
    console.print(f"[bold]Cleanup plan for {folder.name}:[/]")
    for item in targets or ["(nothing to clean)"]:
        console.print(f"  {item}")
    console.print("[yellow]Preview only.[/] Re-run with --apply to remove.")


@candidate_app.command("archive")
def candidate_archive_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
) -> None:
    """Archive a candidate folder (moved under the git-ignored archive subdir)."""
    root = _root()
    folder = cand.resolve_candidate(root, candidate)
    record = cand.load_candidate(folder)
    cand.record_status(record, "ARCHIVED", "Candidate archived.")
    cand.save_candidate(folder, record)
    with Storage(root) as storage:
        storage.set_status(folder.name, "ARCHIVED")
    privacy = cfg.load_privacy(root)
    target = cand.archive_candidate(root, folder, privacy.get("archive_subdir", "_archive"))
    console.print(f"[green]Archived[/] {folder.name} -> {target}")


@candidate_app.command("delete")
def candidate_delete_cmd(
    candidate: str = typer.Option(..., "--candidate", help="Candidate name or folder."),
    confirm: bool = typer.Option(False, "--confirm",
                                 help="Required to actually delete. Omit to preview."),
) -> None:
    """Delete a candidate folder AND all associated SQLite rows (transactional)."""
    root = _root()
    folder = cand.resolve_candidate(root, candidate)
    with Storage(root) as storage:
        plan = storage.deletion_plan(folder.name)
    console.print(f"[bold]Deletion plan for {folder.name}:[/]")
    console.print(f"  candidate folder: {folder}")
    if plan:
        for table, count in plan.items():
            console.print(f"  db {table}: {count} row(s)")
    else:
        console.print("  (no database rows found for this candidate)")
    if not confirm:
        console.print("[yellow]Preview only.[/] Re-run with --confirm to permanently delete.")
        raise typer.Exit(code=0)
    with Storage(root) as storage:
        storage.delete_candidate(folder.name)
    shutil.rmtree(folder, ignore_errors=False)
    console.print(f"[red]Deleted[/] {folder.name} (folder and database rows removed).")


@candidate_app.command("list")
def candidate_list_cmd() -> None:
    """List indexed candidates with status."""
    root = _root()
    with Storage(root) as storage:
        rows = storage.search_candidates("")
    if not rows:
        console.print("No candidates indexed.")
        return
    for display, folder_name, status in rows:
        console.print(f"  {status:<24} {folder_name}  ({display})")


db_app = typer.Typer(name="db", help="Database reliability commands.", no_args_is_help=True)
app.add_typer(db_app)


@db_app.command("check")
def db_check_cmd() -> None:
    """Run integrity + foreign-key checks and report duplicates and schema version."""
    root = _root()
    with Storage(root) as storage:
        console.print(f"Schema version: {storage.schema_version}")
        ok, messages = storage.integrity_check()
        if ok:
            console.print("[green]PASS[/]  database integrity + foreign keys OK")
        else:
            for msg in messages:
                console.print(f"[red]FAIL[/]  {msg}")
        duplicates = storage.find_duplicate_candidates()
    if duplicates:
        console.print("[yellow]Possible duplicate candidates:[/]")
        for reason, folders in duplicates:
            console.print(f"  {reason}: {', '.join(f for f in folders if f)}")
    else:
        console.print("[green]PASS[/]  no duplicate candidates detected")
    if not ok:
        raise typer.Exit(code=1)


@db_app.command("backup")
def db_backup_cmd(
    output: Optional[Path] = typer.Option(None, "--output", help="Backup file path."),
) -> None:
    """Create a validated backup of the SQLite index."""
    root = _root()
    dest = output or (root / "data" / f"zume-backup-{_timestamp()}.db")
    with Storage(root) as storage:
        storage.backup(dest)
    ok, messages = Storage.validate_backup(dest)
    if ok:
        console.print(f"[green]Backup validated[/] -> {dest}")
    else:
        for msg in messages:
            console.print(f"[red]Backup invalid:[/] {msg}")
        raise typer.Exit(code=1)


def _timestamp() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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
