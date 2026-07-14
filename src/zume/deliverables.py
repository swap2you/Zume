"""Consolidated candidate deliverables (Phase 3).

Generates at most seven user-facing DOCX documents. Each function returns the
document bytes so the orchestrator can write them atomically (no ``__vN``).

Interviewer-only vs candidate-shareable separation is strict: only
:func:`candidate_exercise_sheet` is safe to share with a candidate.
"""

from __future__ import annotations

from typing import Any

from zume import feedback as fb
from zume.documents import ZumeDocument
from zume.models import (
    CommunicationDraft,
    Decision,
    FeedbackResult,
    InterviewKit,
    ScheduleRecord,
    ScreeningResult,
)
from zume.screening import COMPETENCY_DISCLAIMER, recruiter_feedback_text

# Canonical deliverable filenames (numbered so Explorer sort matches workflow).
SCREENING_SUMMARY = "01_Screening_Summary.docx"
INTERVIEW_GUIDE = "02_Three_Hour_Interview_Guide.docx"
SCORECARD = "03_Interview_Scorecard.docx"
CANDIDATE_SHEET = "04_Candidate_Exercise_Sheet.docx"
SCHEDULE_COMMS = "05_Schedule_and_Communications.docx"
FINAL_EVALUATION = "06_Final_Interview_Evaluation.docx"
POST_INTERVIEW_COMMS = "07_Post_Interview_Communications.docx"

ALL_DELIVERABLES = [
    SCREENING_SUMMARY, INTERVIEW_GUIDE, SCORECARD, CANDIDATE_SHEET,
    SCHEDULE_COMMS, FINAL_EVALUATION, POST_INTERVIEW_COMMS,
]


def _decision_kind(decision: Decision) -> str:
    return {
        Decision.PROCEED: "success",
        Decision.CONDITIONAL: "warning",
        Decision.DO_NOT_PROCEED: "danger",
    }[decision]


def _guide_title(duration_minutes: int) -> str:
    hours = duration_minutes / 60
    if duration_minutes == 180:
        return "Three-Hour Interview Guide"
    return f"{duration_minutes}-Minute ({hours:g}h) Interview Guide"


# ---------------------------------------------------------------------------
# 01 — Screening summary (merges resume, ATS, recruiter feedback, focus sheet)


def screening_summary(theme: dict[str, Any], result: ScreeningResult,
                      resume_summary: str, source_name: str) -> bytes:
    doc = ZumeDocument(theme, "Screening Summary", f"Candidate: {result.candidate_name}")
    doc.banner(f"Screening decision: {result.decision.value}",
               kind=_decision_kind(result.decision), label="DECISION")
    doc.banner(COMPETENCY_DISCLAIMER, kind="info", label="SCORE MEANING")
    doc.key_values([
        ("Candidate", result.candidate_name),
        ("Source file", source_name or "pasted text"),
        ("Resume evidence coverage", f"{result.score_percent:g}%"),
        ("Experience gate", result.experience_state.value),
        ("Experience detail", result.experience_detail or "—"),
    ])
    if result.manual_review_required:
        doc.banner("Experience could not be confirmed from the resume; manual review "
                   "required before a final decision.", kind="warning", label="MANUAL REVIEW")

    doc.heading("Resume summary", 1)
    doc.paragraph(resume_summary)

    doc.heading("Mandatory-skill evidence", 1)
    doc.paragraph("Compact evidence per mandatory skill (quantified > project > "
                  "responsibility > skills-list). This is evidence strength, not competency.")
    rows = []
    for item in result.evidence:
        if not item.mandatory:
            continue
        quote = (item.quotes[0][:90] + "…") if item.quotes and len(item.quotes[0]) > 90 \
            else (item.quotes[0] if item.quotes else "—")
        rows.append([item.label, item.evidence_type.value.replace("_", " "),
                     f"{int(item.credit * 100)}%", item.source_hint or "—", quote])
    doc.table(["Skill", "Evidence", "Credit", "Source", "Excerpt"], rows)

    doc.heading("Risks, inconsistencies and missing evidence", 1)
    doc.bullets(result.risks or ["No screening risks identified."])
    if result.reject_signals:
        doc.banner("Automatic reject signals detected.", kind="danger", label="REJECT SIGNAL")
        doc.bullets(result.reject_signals)

    doc.heading("Candidate-specific knockout questions", 1)
    doc.bullets(result.validation_questions or ["Use the standard validation set."])

    doc.heading("Recruiter screening message (copy-ready)", 1)
    doc.code_block(recruiter_feedback_text(result))
    return doc.to_bytes()


# ---------------------------------------------------------------------------
# 02 — Three-hour interviewer guide (agenda, knockout, questions, exercises)


def _render_question_block(doc: ZumeDocument, question: Any) -> None:
    doc.heading(f"{question.level.title()} \u2014 {question.question}", 3)
    doc.paragraph("Recommended answer:", bold=True)
    doc.paragraph(question.recommended_answer)
    if question.key_points:
        doc.paragraph("Key points:", bold=True)
        doc.bullets(question.key_points)
    if question.strong_signals or question.weak_signals:
        doc.table(["Strong signals", "Weak signals"],
                  [["; ".join(question.strong_signals) or "—",
                    "; ".join(question.weak_signals) or "—"]])
    for follow in question.follow_ups:
        doc.paragraph(f"Follow-up: {follow.question}", bold=True)
        doc.paragraph(f"Recommended answer: {follow.recommended_answer}")


def three_hour_guide(theme: dict[str, Any], kit: InterviewKit,
                     scoring_dims: dict[str, Any]) -> bytes:
    doc = ZumeDocument(theme, _guide_title(kit.duration_minutes),
                       f"Candidate: {kit.candidate_name}")
    doc.banner("INTERVIEWER-ONLY. Contains recommended answers and reference solutions. "
               "Do not share with the candidate.", kind="danger", label="CONFIDENTIAL")
    if kit.override_reason:
        doc.banner(f"Generated under override. Reason: {kit.override_reason}",
                   kind="danger", label="OVERRIDE")

    doc.heading("Candidate-specific risks and validation targets", 1)
    doc.bullets(kit.focus_areas)
    if kit.unverified_mandatory:
        doc.banner("Unverified mandatory skills to validate live: "
                   + ", ".join(kit.unverified_mandatory), kind="warning", label="MUST VERIFY")

    doc.heading(f"{kit.duration_minutes}-minute agenda", 1)
    doc.table(["Time", "Segment", "Focus"],
              [[f"{s.start}-{s.end} ({s.minutes}m)", s.title, s.focus] for s in kit.agenda])

    doc.page_break()
    doc.heading(f"Knockout round ({kit.knockout_minutes} minutes)", 1)
    doc.banner("First-round decision checkpoint. Record observable evidence only.",
               kind="warning", label="KNOCKOUT")
    for item in kit.knockout:
        doc.heading(item.area_label, 3)
        doc.paragraph(f"Question: {item.question}")
        doc.paragraph("Recommended answer:", bold=True)
        doc.paragraph(item.recommended_answer)
        doc.table(["Strong indicator", "Weak indicator"],
                  [[item.strong_indicator or "—", item.weak_indicator or "—"]])
    doc.paragraph("Knockout decision rule:", bold=True)
    doc.bullets(kit.knockout_decision_rule)

    doc.page_break()
    doc.heading("Question bank by area (basic / intermediate / advanced)", 1)
    for _area, block in kit.question_sections.items():
        if not block:
            continue
        doc.heading(block[0].area_label, 2)
        for question in block:
            _render_question_block(doc, question)

    doc.page_break()
    doc.heading("Live exercises (expected reasoning and reference solutions)", 1)
    for exercise in kit.exercises:
        doc.heading(f"{exercise.area_label}: {exercise.title} ({exercise.difficulty})", 2)
        doc.key_values([("Task", exercise.task)])
        doc.paragraph("Expected reasoning:", bold=True)
        doc.paragraph(exercise.expected_reasoning)
        doc.paragraph("Reference solution:", bold=True)
        doc.code_block(exercise.reference_solution)
        doc.paragraph(f"Requirement-change follow-up: {exercise.requirement_change_follow_up}",
                      bold=True)
        doc.paragraph(f"Debugging follow-up: {exercise.debugging_follow_up}", bold=True)
        if exercise.scoring_rubric:
            doc.paragraph("Scoring rubric:", bold=True)
            doc.bullets(exercise.scoring_rubric)
        if exercise.red_flags:
            doc.paragraph("Red flags:", bold=True)
            doc.bullets(exercise.red_flags)
        if exercise.independence_questions:
            doc.paragraph("Independence-verification questions:", bold=True)
            doc.bullets(exercise.independence_questions)

    doc.page_break()
    doc.heading("Interviewer skip logic and time control", 1)
    doc.bullets([
        "If the knockout fails, stop after the knockout and record the decision.",
        "Keep each segment within its minutes; if a candidate is strong early, go deeper "
        "rather than adding segments.",
        "If an area is clearly strong, skip to the advanced question; if weak, stay basic "
        "and probe reasoning.",
        "Reserve the final five minutes for candidate questions — this is fixed.",
    ])
    if scoring_dims:
        doc.heading("Per-exercise scoring dimensions", 1)
        doc.table(["Dimension", "Points"],
                  [[k.replace("_", " ").title(), str(v)] for k, v in scoring_dims.items()])

    doc.heading("Neutral independence-observation protocol", 1)
    doc.bullets([
        "Ask for the approach before coding; require narration while coding.",
        "Change a requirement after completion and ask for the live modification.",
        "Record unexplained pauses, audible device activity and sudden quality shifts "
        "as neutral, observable facts.",
        "Never state that a candidate cheated; score explanation and modification "
        "separately from the final code.",
    ])

    if kit.reserve_questions:
        doc.page_break()
        doc.heading("Appendix: reserve questions", 1)
        for question in kit.reserve_questions:
            doc.paragraph(
                f"{question.area_label} / {question.level} \u2014 {question.question}",
                bold=True)
            doc.paragraph(f"Recommended answer: {question.recommended_answer}")
    return doc.to_bytes()


# ---------------------------------------------------------------------------
# 03 — Compact scorecard (one to two pages)


def interview_scorecard(theme: dict[str, Any], kit: InterviewKit) -> bytes:
    doc = ZumeDocument(theme, "Interview Scorecard", f"Candidate: {kit.candidate_name}")
    doc.heading("Knockout result", 1)
    doc.table(["Result", "Notes"], [["Pass / Conditional / Fail", ""]])
    doc.heading("Area scores", 1)
    area_rows = [[block[0].area_label, "", ""]
                 for block in kit.question_sections.values() if block]
    if not area_rows:
        area_rows = [["Java", "", ""], ["Selenium", "", ""], ["REST Assured", "", ""],
                     ["SQL / Oracle", "", ""], ["Framework design", "", ""]]
    doc.table(["Area", "Score (0-10)", "Evidence notes"], area_rows)
    doc.heading("Live-exercise scores", 1)
    doc.table(["Exercise", "Score (0-10)", "Independence"],
              [[f"{e.area_label}: {e.title}", "", ""] for e in kit.exercises]
              or [["(no exercises assigned)", "", ""]])
    doc.heading("Independence observations", 1)
    doc.table(["Field", "Record"], [
        ["Unexplained pauses", ""],
        ["Audible device activity", ""],
        ["Sudden quality shift", ""],
        ["Can explain / modify solution", ""],
        ["Confidence in independent execution", "High / Medium / Low"],
    ])
    doc.banner("Mandatory override: Java, Selenium, REST Assured or SQL/Oracle below the "
               "hands-on bar means no Senior SDET recommendation regardless of total score.",
               kind="danger", label="OVERRIDE")
    doc.heading("Final recommendation", 1)
    doc.table(["Recommendation", "Rationale"],
              [["Proceed / Second round / Do not proceed", ""]])
    return doc.to_bytes()


# ---------------------------------------------------------------------------
# 04 — Candidate-shareable exercise sheet (tasks only, no answers)


def candidate_exercise_sheet(theme: dict[str, Any], kit: InterviewKit) -> bytes:
    doc = ZumeDocument(theme, "Interview Exercises (Candidate Copy)",
                       f"Candidate: {kit.candidate_name}")
    doc.banner("Shareable with the candidate. Contains tasks only — no answers, "
               "reasoning, rubrics or solutions.", kind="success", label="CANDIDATE COPY")
    for idx, exercise in enumerate(kit.exercises, start=1):
        doc.heading(f"Exercise {idx}: {exercise.area_label}", 2)
        doc.key_values([("Task", exercise.task)])
        if exercise.requirement_change_follow_up:
            doc.paragraph("You may be asked to extend or adjust this during the session.")
    doc.heading("What to expect", 1)
    doc.bullets([
        "Talk through your approach before and while you code.",
        "You may be asked to modify your solution when a requirement changes.",
        "Focus on correctness, clarity and how you reason — not memorized answers.",
    ])
    return doc.to_bytes()


# ---------------------------------------------------------------------------
# 05 — Schedule and communications


def schedule_and_comms(theme: dict[str, Any], record: ScheduleRecord,
                       drafts: list[CommunicationDraft]) -> bytes:
    doc = ZumeDocument(theme, "Schedule and Communications", f"Candidate: {record.candidate_name}")
    if record.needs_confirmation:
        doc.banner("Schedule is NOT confirmed. Resolve the issues below before relying on it.",
                   kind="warning", label="CONFIRM")
    else:
        doc.banner("Schedule confirmed from user-provided details.",
                   kind="success", label="CONFIRMED")

    def _row(field: str, value: str) -> list[str]:
        return [field.replace("_", " ").title(), value or "To be confirmed",
                record.field_sources.get(field, record.extraction_source),
                record.field_confidence.get(field, "-" if value else "n/a")]

    doc.heading("Confirmed details", 1)
    doc.table(["Field", "Value", "Source", "Confidence"], [
        ["Candidate", record.candidate_name, "manual", "high"],
        _row("date", record.date),
        _row("time", record.time),
        _row("timezone", record.timezone),
        _row("duration", record.duration),
        _row("interviewers", record.interviewers),
        _row("platform", record.platform),
    ])
    if record.validation_issues:
        doc.heading("Issues to resolve", 1)
        doc.bullets(record.validation_issues)
    doc.heading("Interviewer preparation checklist", 1)
    doc.bullets([
        "Review the screening summary and interview guide.",
        "Verify the meeting link and screen-sharing policy.",
        "Open the scorecard before the session starts.",
        "Confirm date, time and timezone with the recruiter.",
    ])
    doc.heading("Copy-ready communication drafts", 1)
    for draft in drafts:
        doc.heading(draft.kind.title(), 3)
        doc.code_block(f"Subject: {draft.subject}\n\n{draft.body}")
    return doc.to_bytes()


# ---------------------------------------------------------------------------
# 06 — Final evaluation (embeds the completed scorecard)


def final_evaluation(theme: dict[str, Any], result: FeedbackResult, notes: str) -> bytes:
    doc = ZumeDocument(theme, "Final Interview Evaluation", f"Candidate: {result.candidate_name}")
    doc.banner(result.recommendation, kind=_decision_kind(result.decision), label="DECISION")
    doc.key_values([
        ("Decision", result.decision.value),
        ("Interview score", f"{result.total_percent:g}%"),
        ("New status", result.status),
    ])
    if result.mandatory_override_failed:
        doc.banner("Mandatory hands-on override triggered: "
                   + ", ".join(result.mandatory_override_failed),
                   kind="danger", label="OVERRIDE")
    doc.heading("Completed scorecard", 1)
    doc.table(["Area", "Score (0-10)", "Evidence from notes"],
              [[s.label, str(s.score), s.evidence] for s in result.skill_scores]
              or [["No areas scored", "—", "—"]])
    doc.heading("Independence observations (neutral record)", 1)
    doc.table(["Field", "Record"], fb._observation_rows(result))
    doc.heading("Strengths", 1)
    doc.bullets(result.strengths or ["None recorded."])
    doc.heading("Concerns", 1)
    doc.bullets(result.concerns or ["None recorded."])
    doc.heading("Interviewer notes (verbatim)", 1)
    for line in notes.splitlines():
        if line.strip():
            doc.paragraph(line.strip())
    return doc.to_bytes()


# ---------------------------------------------------------------------------
# 07 — Post-interview communications (recruiter + leadership in one doc)


def post_interview_comms(theme: dict[str, Any], result: FeedbackResult,
                         include_leadership: bool = True) -> bytes:
    doc = ZumeDocument(theme, "Post-Interview Communications",
                       f"Candidate: {result.candidate_name}")
    doc.banner(result.recommendation, kind=_decision_kind(result.decision), label="DECISION")
    doc.heading("Recruiter draft (copy-ready)", 1)
    doc.code_block(fb.recruiter_feedback_text(result))
    if include_leadership:
        doc.heading("Leadership draft (copy-ready)", 1)
        doc.code_block(fb.leadership_feedback_text(result))
    return doc.to_bytes()
