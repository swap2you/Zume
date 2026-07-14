"""Interview scheduling: screenshot handling, schedule record and drafts."""

from __future__ import annotations

import re
from datetime import date as date_cls
from datetime import datetime
from pathlib import Path
from typing import Any

from zume.candidate import atomic_write_text
from zume.documents import ZumeDocument
from zume.ingest import image_metadata, parse_schedule_text
from zume.models import CommunicationDraft, ScheduleRecord

_TZ_ABBREV = re.compile(
    r"\b(UTC|GMT|Z|EST|EDT|ET|CST|CDT|CT|MST|MDT|MT|PST|PDT|PT|IST|BST|CET|CEST|"
    r"AEST|AEDT|JST|SGT)\b")
_TZ_IANA = re.compile(r"\b[A-Za-z]+/[A-Za-z_]+\b")
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SLASH_DATE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
_MONTH_DATE = re.compile(
    r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}$",
    re.IGNORECASE)
_TIME = re.compile(r"(\d{1,2}):(\d{2})\s*([ap]\.?m\.?)?", re.IGNORECASE)
_DURATION = re.compile(r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|minutes?|mins?|m\b|h\b)", re.IGNORECASE)

# The configured standard technical interview duration (Phase 9).
STANDARD_INTERVIEW_MINUTES = 180
# Abbreviations that do not resolve to a single zone without the date/convention.
_AMBIGUOUS_TZ = {"ET", "CT", "MT", "PT"}


def extract_timezone(*texts: str) -> str:
    for text in texts:
        if not text:
            continue
        iana = _TZ_IANA.search(text)
        if iana:
            return iana.group(0)
        abbrev = _TZ_ABBREV.search(text)
        if abbrev:
            return abbrev.group(1).upper()
    return ""


def parse_date_value(raw: str) -> tuple[date_cls | None, str]:
    """Return (parsed date, ambiguity note). Ambiguous formats are not parsed."""
    raw = raw.strip()
    if _ISO_DATE.match(raw):
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date(), ""
        except ValueError:
            return None, "invalid ISO date"
    if _MONTH_DATE.match(raw):
        for fmt in ("%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y"):
            try:
                return datetime.strptime(raw, fmt).date(), ""
            except ValueError:
                continue
        return None, "unrecognized month-name date"
    if _SLASH_DATE.match(raw):
        return None, "ambiguous date format (use YYYY-MM-DD)"
    return None, "unrecognized date format (use YYYY-MM-DD)"


def parse_time_value(raw: str) -> tuple[int, int] | None:
    match = _TIME.search(raw)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    meridiem = (match.group(3) or "").lower().replace(".", "")
    if meridiem == "pm" and hour < 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    return hour, minute


def parse_duration_minutes(raw: str) -> int | None:
    match = _DURATION.search(raw)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).lower()
    if unit.startswith(("h", "hr")):
        return int(value * 60)
    return int(value)


def validate_schedule(record: ScheduleRecord, today: date_cls | None = None,
                      standard_minutes: int = STANDARD_INTERVIEW_MINUTES) -> list[str]:
    """Return blocking/confirmation issues; never trust OCR silently."""
    today = today or date_cls.today()
    issues: list[str] = []
    if not record.date:
        issues.append("Date is missing.")
    else:
        parsed, note = parse_date_value(record.date)
        if note:
            issues.append(f"Date problem: {note}.")
        elif parsed and parsed < today:
            issues.append(f"Date {record.date} is in the past.")
    if not record.time:
        issues.append("Time is missing.")
    else:
        parsed_time = parse_time_value(record.time)
        if parsed_time is None:
            issues.append("Time could not be parsed.")
        else:
            hour, minute = parsed_time
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                issues.append(f"Time {record.time} is not a valid clock time.")
    if not record.timezone:
        issues.append("Timezone is missing; confirm the interviewer's timezone.")
    elif record.timezone.upper() in _AMBIGUOUS_TZ:
        issues.append(
            f"Timezone '{record.timezone}' is ambiguous; record the IANA zone "
            "(e.g. America/New_York) and confirm before relying on the time.")
    # Phase 9 — duration is measured against the 180-minute standard.
    if not record.duration:
        issues.append(
            f"Duration is missing; confirm the {standard_minutes}-minute standard interview.")
    else:
        minutes = parse_duration_minutes(record.duration)
        if minutes is None:
            issues.append("Duration could not be parsed.")
        elif minutes <= 0:
            issues.append("Duration must be greater than zero.")
        elif minutes != standard_minutes:
            issues.append(
                f"Duration is {minutes} minutes but the standard interview is "
                f"{standard_minutes} minutes. Confirm a {standard_minutes}-minute schedule "
                "or intentionally generate a shortened/custom interview plan.")
    return issues


def build_schedule(candidate_name: str, image_path: Path | None,
                   details_text: str | None,
                   today: date_cls | None = None) -> ScheduleRecord:
    """Build a schedule record.

    Screenshot content is never OCR-trusted silently: only image metadata is
    read automatically, and the user supplies/confirms the actual details as
    `Key: Value` text. Records stay flagged for confirmation until details are
    provided AND all correctness checks pass.
    """
    record = ScheduleRecord(candidate_name=candidate_name)
    if image_path is not None:
        meta = image_metadata(image_path)
        record.extraction_source = "image-metadata"
        note_bits = [f"Screenshot: {meta['file']} ({meta.get('size', '?')})"]
        if "captured_at" in meta:
            note_bits.append(f"captured {meta['captured_at']}")
        record.notes = "; ".join(note_bits)
        record.notes += "; screenshot content is untrusted until confirmed via --details"

    if details_text:
        details = parse_schedule_text(details_text)
        source = "text"

        def _set(field: str, value: str, confidence: str = "high") -> None:
            setattr(record, field, value)
            record.field_sources[field] = source
            record.field_confidence[field] = confidence

        if details.get("date"):
            _set("date", details["date"])
        if details.get("time"):
            _set("time", details["time"])
        if details.get("duration"):
            _set("duration", details["duration"])
        if details.get("interviewers"):
            _set("interviewers", details["interviewers"])
        if details.get("platform"):
            _set("platform", details["platform"])
        if details.get("timezone"):
            _set("timezone", details["timezone"])
        else:
            tz = extract_timezone(details.get("time", ""), details_text)
            if tz:
                _set("timezone", tz, confidence="medium")
        if details.get("notes"):
            record.notes = (record.notes + "; " if record.notes else "") + details["notes"]
        if record.extraction_source == "manual":
            record.extraction_source = "text"

    record.duration_minutes = parse_duration_minutes(record.duration) if record.duration else None
    if record.duration_minutes is None:
        record.duration_status = "missing"
    elif record.duration_minutes == STANDARD_INTERVIEW_MINUTES:
        record.duration_status = "confirmed"
    else:
        record.duration_status = "mismatch"

    record.validation_issues = validate_schedule(record, today=today)
    record.needs_confirmation = bool(record.validation_issues)
    return record


def generate_schedule_doc(theme: dict[str, Any], record: ScheduleRecord, out_path: Path) -> None:
    doc = ZumeDocument(theme, "Interview Schedule", f"Candidate: {record.candidate_name}")
    if record.needs_confirmation:
        doc.banner("Schedule details are incomplete or unconfirmed. Confirm with the "
                   "recruiter before relying on this document.", kind="warning", label="CONFIRM")
    else:
        doc.banner("Schedule confirmed from user-provided details.", kind="success", label="CONFIRMED")
    doc.heading("Details", 1)

    def _cell(field: str, value: str) -> list[str]:
        return [
            field.replace("_", " ").title(),
            value or "To be confirmed",
            record.field_sources.get(field, record.extraction_source),
            record.field_confidence.get(field, "-" if value else "n/a"),
        ]

    doc.table(["Field", "Value", "Source", "Confidence"], [
        ["Candidate", record.candidate_name, "manual", "high"],
        _cell("date", record.date),
        _cell("time", record.time),
        _cell("timezone", record.timezone),
        _cell("duration", record.duration),
        _cell("interviewers", record.interviewers),
        _cell("platform", record.platform),
    ])
    if record.validation_issues:
        doc.heading("Validation issues (resolve before relying on this schedule)", 1)
        doc.banner("This schedule needs confirmation: " + str(len(record.validation_issues))
                   + " issue(s).", kind="warning", label="CONFIRM")
        doc.bullets(record.validation_issues)
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
    """Human-readable timestamp including the timezone (Part 7).

    The timezone is always rendered so a reader is never left guessing the zone;
    a missing zone is shown as an explicit placeholder rather than omitted.
    """
    date = record.date or "[date]"
    time = record.time or "[time]"
    timezone = record.timezone or "[timezone — confirm]"
    return f"{date} at {time} {timezone}"


def _unconfirmed_prefix(record: ScheduleRecord) -> str:
    """Never present an unconfirmed schedule as confirmed (Part 7)."""
    if record.needs_confirmation:
        return ("[DRAFT — schedule is NOT confirmed; verify date, time and timezone "
                "before sending]\n\n")
    return ""


def build_communication_drafts(record: ScheduleRecord) -> list[CommunicationDraft]:
    name = record.candidate_name
    when = _when(record)
    prefix = _unconfirmed_prefix(record)
    platform = record.platform or "the shared meeting link"
    confirm_word = "Proposing" if record.needs_confirmation else "Confirming"
    return [
        CommunicationDraft(
            kind="join",
            subject=f"Interview Confirmation – {name}",
            body=(f"{prefix}Hi Team,\n\n{confirm_word} the interview with {name} on {when}"
                  f" ({record.duration or 'duration TBC'}). I will join on time via "
                  f"{platform}.\n\nThanks."),
        ),
        CommunicationDraft(
            kind="reschedule",
            subject=f"Reschedule Request – {name}",
            body=(f"{prefix}Hi Team,\n\nI am unavailable for the currently scheduled interview "
                  f"with {name} on {when} (via {platform}). Please reschedule with at least one "
                  "business day notice and share the updated invitation.\n\nThanks."),
        ),
        CommunicationDraft(
            kind="cancel",
            subject=f"Interview Cancellation – {name}",
            body=(f"{prefix}Hi Team,\n\nPlease cancel the interview with {name} scheduled for "
                  f"{when} (via {platform}). I will follow up if a new slot is needed.\n\n"
                  "Thanks."),
        ),
        CommunicationDraft(
            kind="no-show",
            subject=f"Interview No-Show – {name}",
            body=(f"{prefix}Hi Team,\n\n{name} did not join the interview scheduled for {when} "
                  f"(via {platform}), and I waited approximately 10 minutes without receiving "
                  "an update. Please mark this profile as not proceeding from my side.\n\n"
                  "Thanks."),
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
