"""Interview feedback: notes -> calibrated evaluation and communications."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from zume.candidate import atomic_write_text
from zume.documents import ZumeDocument
from zume.models import (
    Decision,
    FeedbackResult,
    IndependenceObservations,
    SkillScore,
)
from zume.providers import get_provider

SKILL_SENTENCE_PATTERNS: dict[str, tuple[str, list[str]]] = {
    "java": ("Java", [r"\bjava\b", r"duplicate[- ]word", r"collections?"]),
    "selenium": ("Selenium", [r"\bselenium\b", r"locator", r"dynamic[- ]table", r"page object"]),
    "testng_cucumber": ("TestNG + Cucumber", [r"\btestng\b", r"\bcucumber\b"]),
    "rest_assured": ("REST Assured", [r"rest[\s-]?assured", r"\bapi\b", r"chaining"]),
    "sql_oracle": ("SQL + Oracle", [r"\bsql\b", r"\boracle\b", r"row_number", r"\bjoin\b",
                                    r"window function", r"\bquery\b"]),
    "framework": ("Framework ownership", [r"framework"]),
    "cicd": ("CI/CD", [r"\bjenkins\b", r"pipeline", r"ci/?cd", r"\bmaven\b"]),
    "ownership": ("Independent ownership", [r"independen", r"ownership", r"mentor"]),
}

_POSITIVE = [r"clear", r"correct", r"independen", r"strong", r"completed", r"concise",
             r"good", r"solid", r"explained", r"well", r"successfully", r"confident"]
_HINT = [r"hint", r"prompt", r"minor help", r"guidance", r"nudge", r"assisted"]
_NEGATIVE = [r"unable", r"could\s*not", r"couldn't", r"failed", r"weak", r"struggl",
             r"incorrect", r"below", r"poor", r"did not", r"didn't"]

_OBSERVATION_PATTERNS: dict[str, list[str]] = {
    "unexplained_pauses": [r"pause", r"long silence", r"went quiet"],
    "audible_device_activity": [r"device", r"typing sound", r"phone", r"keyboard.*background",
                                r"audible"],
    "sudden_quality_shift": [r"sudden", r"quality shift", r"abrupt", r"dramatic improvement"],
}


def _split_sentences(notes: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?;])\s+", notes) if s.strip()]


def _sentence_score(sentence: str) -> int:
    lowered = sentence.lower()
    if any(re.search(p, lowered) for p in _NEGATIVE):
        return 3
    if any(re.search(p, lowered) for p in _HINT):
        return 6
    if any(re.search(p, lowered) for p in _POSITIVE):
        return 9
    return 7


def score_notes(notes: str) -> list[SkillScore]:
    sentences = _split_sentences(notes)
    scores: list[SkillScore] = []
    for skill, (label, patterns) in SKILL_SENTENCE_PATTERNS.items():
        hits = [s for s in sentences
                if any(re.search(p, s, re.IGNORECASE) for p in patterns)]
        if not hits:
            continue
        value = round(sum(_sentence_score(s) for s in hits) / len(hits))
        scores.append(SkillScore(
            skill=skill, label=label, score=value,
            evidence=" ".join(hits)[:400],
        ))
    return scores


def extract_observations(notes: str) -> IndependenceObservations:
    obs = IndependenceObservations()
    sentences = _split_sentences(notes)
    for field, patterns in _OBSERVATION_PATTERNS.items():
        matched = [s for s in sentences
                   if any(re.search(p, s, re.IGNORECASE) for p in patterns)]
        if matched:
            setattr(obs, field, f"Observed — {matched[0][:200]}")
    lowered = notes.lower()
    if re.search(r"explain", lowered):
        if re.search(r"(unable|could\s*not|couldn't|cannot).{0,40}explain|explain.{0,40}(unable|could\s*not)", lowered):
            obs.can_explain_solution = "Weak — could not explain the solution."
        else:
            obs.can_explain_solution = "Strong — explained the solution when asked."
    if re.search(r"modif", lowered):
        if re.search(r"(unable|could\s*not|couldn't|cannot).{0,60}modif", lowered):
            obs.can_modify_solution = "Unable — could not modify the solution."
        else:
            obs.can_modify_solution = "Independent — modified the solution when requirements changed."
    concerns = [
        getattr(obs, f).startswith("Observed")
        for f in ("unexplained_pauses", "audible_device_activity", "sudden_quality_shift")
    ]
    weak = obs.can_explain_solution.startswith("Weak") or obs.can_modify_solution.startswith("Unable")
    if weak or sum(concerns) >= 2:
        obs.confidence_independent_execution = "Low"
    elif any(concerns):
        obs.confidence_independent_execution = "Medium"
    else:
        obs.confidence_independent_execution = "High"
    return obs


MANDATORY_CORE = ("java", "selenium", "rest_assured", "sql_oracle")


def evaluate_notes(candidate_name: str, notes: str) -> FeedbackResult:
    scores = score_notes(notes)
    observations = extract_observations(notes)
    scored = {s.skill: s for s in scores}
    if scores:
        total = round(sum(s.score for s in scores) / (len(scores) * 10) * 100, 1)
    else:
        total = 0.0
    override_failed = [scored[s].label for s in MANDATORY_CORE
                       if s in scored and scored[s].score < 5]
    if observations.confidence_independent_execution == "Low":
        recommendation, decision = (
            "Do Not Proceed — confidence in independent execution is low based on "
            "recorded observations.",
            Decision.DO_NOT_PROCEED,
        )
    elif override_failed:
        recommendation, decision = (
            "Do Not Proceed — mandatory hands-on override triggered for: "
            + ", ".join(override_failed) + ".",
            Decision.DO_NOT_PROCEED,
        )
    elif total >= 85:
        recommendation, decision = "Strong Senior SDET.", Decision.PROCEED
    elif total >= 75:
        recommendation, decision = "Proceed for Senior SDET.", Decision.PROCEED
    elif total >= 68:
        recommendation, decision = (
            "Borderline — run a second focused round.", Decision.CONDITIONAL)
    else:
        recommendation, decision = "Do Not Proceed.", Decision.DO_NOT_PROCEED
    sentences = _split_sentences(notes)
    strengths = [s for s in sentences if _sentence_score(s) >= 9][:6]
    concerns = [s for s in sentences if _sentence_score(s) <= 6][:6]
    status = {
        Decision.PROCEED: "SELECTED",
        Decision.CONDITIONAL: "SECOND_ROUND",
        Decision.DO_NOT_PROCEED: "REJECTED",
    }[decision]
    return FeedbackResult(
        candidate_name=candidate_name,
        skill_scores=scores,
        total_percent=total,
        mandatory_override_failed=override_failed,
        recommendation=recommendation,
        decision=decision,
        strengths=strengths,
        concerns=concerns,
        observations=observations,
        status=status,
    )


# --------------------------------------------------------------------------
# Documents


def _decision_banner(doc: ZumeDocument, result: FeedbackResult) -> None:
    if result.decision == Decision.PROCEED:
        doc.banner(result.recommendation, kind="success", label="DECISION")
    elif result.decision == Decision.CONDITIONAL:
        doc.banner(result.recommendation, kind="warning", label="DECISION")
    else:
        doc.banner(result.recommendation, kind="danger", label="DECISION")


def _observation_rows(result: FeedbackResult) -> list[list[str]]:
    obs = result.observations
    return [
        ["Unexplained pauses", obs.unexplained_pauses],
        ["Audible device activity", obs.audible_device_activity],
        ["Sudden quality shift", obs.sudden_quality_shift],
        ["Can explain solution", obs.can_explain_solution],
        ["Can modify solution", obs.can_modify_solution],
        ["Confidence in independent execution", obs.confidence_independent_execution],
    ]


def generate_final_evaluation(theme: dict[str, Any], result: FeedbackResult,
                              notes: str, out_path: Path) -> None:
    doc = ZumeDocument(theme, "Final Interview Evaluation", f"Candidate: {result.candidate_name}")
    _decision_banner(doc, result)
    doc.heading("Decision", 1)
    doc.key_values([
        ("Decision", result.decision.value),
        ("Score", f"{result.total_percent:g}%"),
        ("New status", result.status),
    ])
    if result.mandatory_override_failed:
        doc.banner("Mandatory hands-on override triggered: "
                   + ", ".join(result.mandatory_override_failed), kind="danger", label="OVERRIDE")
    doc.heading("Skill assessment", 1)
    doc.table(
        ["Area", "Score (0–10)", "Evidence from interviewer notes"],
        [[s.label, str(s.score), s.evidence] for s in result.skill_scores]
        or [["No skill areas were identified in the notes", "—", "—"]],
    )
    doc.heading("Strengths", 1)
    doc.bullets(result.strengths or ["None recorded."])
    doc.heading("Risks and concerns", 1)
    if result.concerns:
        doc.banner(f"{len(result.concerns)} concern(s) noted by the interviewer.", kind="warning")
        doc.bullets(result.concerns)
    else:
        doc.paragraph("No concerns recorded in the notes.")
    doc.heading("Independence observations (neutral record)", 1)
    doc.paragraph(
        "The fields below record observable behavior only. They are not an "
        "accusation of external assistance."
    )
    doc.table(["Field", "Record"], _observation_rows(result))
    doc.heading("Actions", 1)
    doc.bullets([
        f"Update candidate status to {result.status}.",
        "Send the recruiter feedback draft.",
        "Archive the interviewer notes in the candidate folder.",
    ])
    doc.heading("Interviewer notes (verbatim)", 1)
    for para in notes.splitlines():
        if para.strip():
            doc.paragraph(para.strip())
    doc.save(out_path)


def generate_completed_scorecard(theme: dict[str, Any], result: FeedbackResult,
                                 out_path: Path) -> None:
    doc = ZumeDocument(theme, "Completed Scorecard", f"Candidate: {result.candidate_name}")
    _decision_banner(doc, result)
    doc.heading("Scores", 1)
    doc.table(
        ["Area", "Score (0–10)", "Evidence"],
        [[s.label, str(s.score), s.evidence] for s in result.skill_scores]
        or [["No areas scored", "—", "—"]],
    )
    doc.heading("Independence observations", 1)
    doc.table(["Field", "Record"], _observation_rows(result))
    doc.save(out_path)


def recruiter_feedback_text(result: FeedbackResult) -> str:
    provider = get_provider()
    if result.decision == Decision.PROCEED:
        assessment = ("The candidate met the senior hands-on bar across the assessed areas. "
                      "Recommendation: proceed for the Senior SDET role.")
    elif result.decision == Decision.CONDITIONAL:
        assessment = ("The candidate is borderline. Recommendation: schedule a second, "
                      "focused round before a final decision.")
    else:
        assessment = ("Recommendation: do not proceed for the current Senior SDET role. "
                      "The demonstrated depth was below the senior expectation.")
    template = (
        "Subject: Interview Feedback – [Candidate]\n\n"
        "Hi Team,\n\n"
        "[assessment]\n\n"
        "[detail]\n\n"
        "Thanks."
    )
    details: list[str] = []
    if result.strengths:
        details.append("Strengths observed: " + " ".join(result.strengths[:2]))
    if result.concerns:
        details.append("Concerns: " + " ".join(result.concerns[:2]))
    if result.observations.confidence_independent_execution in {"Low", "Medium"}:
        details.append(
            "During live coding there were recorded observations (see the evaluation "
            "document) that reduced confidence that the exercises demonstrated "
            "independent execution."
        )
    return provider.draft_communication(template, {
        "Candidate": result.candidate_name,
        "assessment": assessment,
        "detail": "\n\n".join(details) if details else "Detailed scoring is attached.",
    })


def leadership_feedback_text(result: FeedbackResult) -> str:
    return (
        f"Hi Team,\n\nSummary for {result.candidate_name} (Senior SDET pipeline): "
        f"{result.decision.value} at {result.total_percent:g}%. "
        f"{result.recommendation} Detailed evaluation and scorecard are stored in the "
        "candidate folder.\n\nThanks."
    )


def generate_recruiter_feedback(theme: dict[str, Any], result: FeedbackResult,
                                docx_path: Path, md_path: Path) -> None:
    body = recruiter_feedback_text(result)
    doc = ZumeDocument(theme, "Recruiter Feedback (Post-Interview)",
                       f"Candidate: {result.candidate_name}")
    _decision_banner(doc, result)
    doc.heading("Copy-ready draft", 1)
    for para in body.split("\n\n"):
        doc.paragraph(para)
    doc.save(docx_path)
    atomic_write_text(md_path, f"# Recruiter Feedback — {result.candidate_name}\n\n"
                               f"```text\n{body}\n```\n")


def generate_leadership_feedback(theme: dict[str, Any], result: FeedbackResult,
                                 docx_path: Path, md_path: Path) -> None:
    body = leadership_feedback_text(result)
    doc = ZumeDocument(theme, "Leadership Feedback", f"Candidate: {result.candidate_name}")
    _decision_banner(doc, result)
    doc.heading("Copy-ready draft", 1)
    for para in body.split("\n\n"):
        doc.paragraph(para)
    doc.save(docx_path)
    atomic_write_text(md_path, f"# Leadership Feedback — {result.candidate_name}\n\n"
                               f"```text\n{body}\n```\n")
