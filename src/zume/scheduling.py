"""Interview scheduling: screenshot handling, schedule record and drafts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from zume.candidate import atomic_write_text
from zume.documents import ZumeDocument
from zume.ingest import image_metadata, parse_schedule_text
from zume.models import CommunicationDraft, ScheduleRecord


def build_schedule(candidate_name: str, image_path: Path | None,
                   details_text: str | None) -> ScheduleRecord:
    """Build a schedule record.

    Screenshot content is never OCR-trusted silently: only image metadata is
    read automatically, and the user supplies/confirms the actual details as
    `Key: Value` text. Records stay flagged for confirmation until details
    are provided.
    """
    record = ScheduleRecord(candidate_name=candidate_name)
    if image_path is not None:
        meta = image_metadata(image_path)
        record.extraction_source = "image-metadata"
        note_bits = [f"Screenshot: {meta['file']} ({meta.get('size', '?')})"]
        if "captured_at" in meta:
            note_bits.append(f"captured {meta['captured_at']}")
        record.notes = "; ".join(note_bits)
    if details_text:
        details = parse_schedule_text(details_text)
        record.date = details.get("date", record.date)
        record.time = details.get("time", record.time)
        record.duration = details.get("duration", record.duration)
        record.interviewers = details.get("interviewers", record.interviewers)
        record.platform = details.get("platform", record.platform)
        if details.get("notes"):
            record.notes = (record.notes + "; " if record.notes else "") + details["notes"]
        if record.extraction_source == "manual":
            record.extraction_source = "text"
        record.needs_confirmation = not (record.date and record.time)
    return record


def generate_schedule_doc(theme: dict[str, Any], record: ScheduleRecord, out_path: Path) -> None:
    doc = ZumeDocument(theme, "Interview Schedule", f"Candidate: {record.candidate_name}")
    if record.needs_confirmation:
        doc.banner("Schedule details are incomplete or unconfirmed. Confirm with the "
                   "recruiter before relying on this document.", kind="warning", label="CONFIRM")
    else:
        doc.banner("Schedule confirmed from user-provided details.", kind="success", label="CONFIRMED")
    doc.heading("Details", 1)
    doc.table(["Field", "Value"], [
        ["Candidate", record.candidate_name],
        ["Date", record.date or "To be confirmed"],
        ["Time", record.time or "To be confirmed"],
        ["Duration", record.duration or "To be confirmed"],
        ["Interviewers", record.interviewers or "To be confirmed"],
        ["Platform", record.platform or "To be confirmed"],
        ["Extraction source", record.extraction_source],
    ])
    if record.notes:
        doc.heading("Notes", 1)
        doc.paragraph(record.notes)
    doc.heading("Interviewer preparation checklist", 1)
    doc.bullets([
        "Review the candidate focus sheet and exercise pack.",
        "Verify the meeting link and screen-sharing policy.",
        "Have the scorecard open before the session starts.",
        "Confirm date, time and time zone with the recruiter.",
    ])
    doc.save(out_path)


def _when(record: ScheduleRecord) -> str:
    date = record.date or "[date]"
    time = record.time or "[time]"
    return f"{date} at {time}"


def build_communication_drafts(record: ScheduleRecord) -> list[CommunicationDraft]:
    name = record.candidate_name
    when = _when(record)
    return [
        CommunicationDraft(
            kind="join",
            subject=f"Interview Confirmation – {name}",
            body=(f"Hi Team,\n\nConfirming the interview with {name} on {when}"
                  f" ({record.duration or 'duration TBC'}). I will join on time via "
                  f"{record.platform or 'the shared meeting link'}.\n\nThanks."),
        ),
        CommunicationDraft(
            kind="reschedule",
            subject=f"Reschedule Request – {name}",
            body=(f"Hi Team,\n\nI am unavailable for the currently scheduled interview with "
                  f"{name} on {when}. Please reschedule with at least one business day notice "
                  "and share the updated invitation.\n\nThanks."),
        ),
        CommunicationDraft(
            kind="cancel",
            subject=f"Interview Cancellation – {name}",
            body=(f"Hi Team,\n\nPlease cancel the interview with {name} scheduled for {when}. "
                  "I will follow up if a new slot is needed.\n\nThanks."),
        ),
        CommunicationDraft(
            kind="no-show",
            subject=f"Interview No-Show – {name}",
            body=(f"Hi Team,\n\n{name} did not join the interview scheduled for {when}, and I "
                  "waited approximately 10 minutes without receiving an update. Please mark "
                  "this profile as not proceeding from my side.\n\nThanks."),
        ),
    ]


def write_draft_markdown(drafts: list[CommunicationDraft], out_path: Path) -> None:
    lines = ["# Schedule Communication Drafts", ""]
    for draft in drafts:
        lines.append(f"## {draft.kind.title()}")
        lines.append("")
        lines.append("```text")
        lines.append(f"Subject: {draft.subject}")
        lines.append("")
        lines.append(draft.body)
        lines.append("```")
        lines.append("")
    atomic_write_text(out_path, "\n".join(lines))
