"""Resume screening: evidence matrix, scoring gates and decision rules."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from zume.candidate import atomic_write_text
from zume.documents import ZumeDocument
from zume.ingest import ResumeProfile
from zume.models import Decision, EvidenceItem, EvidenceLevel, ScreeningResult
from zume.providers import get_provider

SKILL_LABELS = {
    "java": "Java",
    "selenium": "Selenium",
    "testng_cucumber": "TestNG + Cucumber",
    "rest_assured": "REST Assured",
    "sql_oracle": "SQL + Oracle",
    "framework": "Framework ownership",
    "cicd": "CI/CD",
    "ownership": "Independent ownership",
}

# Explicit keyword patterns per mandatory skill.
_EXPLICIT_PATTERNS: dict[str, list[str]] = {
    "java": [r"\bjava\b(?!\s*script)"],
    "selenium": [r"\bselenium\b"],
    "testng_cucumber": [r"\btestng\b", r"\bcucumber\b"],
    "rest_assured": [r"rest[\s-]?assured"],
    "sql_oracle": [r"\boracle\b"],
    "framework": [r"framework"],
    "cicd": [r"\bjenkins\b", r"\bgitlab\b", r"ci/?cd", r"\bpipeline"],
    "ownership": [r"\bmentor", r"\bowned\b", r"\bownership\b", r"\bled\b",
                  r"independent", r"maintained", r"\bbuilt\b", r"\bdesigned\b"],
}

# Weaker signals that justify only an "inferred" rating.
_INFERRED_PATTERNS: dict[str, list[str]] = {
    "sql_oracle": [r"\bsql\b", r"\bdatabase\b"],
    "cicd": [r"\bmaven\b", r"\bgit\b"],
    "rest_assured": [r"\bapi\b.{0,40}automat", r"automat.{0,40}\bapi\b"],
    "testng_cucumber": [r"\bjunit\b", r"\bbdd\b"],
}

GOOD_TO_HAVE_PATTERNS: dict[str, list[str]] = {
    "Appium": [r"\bappium\b"],
    "BrowserStack": [r"browser\s?stack"],
    "Android and iOS": [r"\bandroid\b", r"\bios\b"],
    "JMeter": [r"\bjmeter\b"],
    "BlazeMeter": [r"blaze\s?meter"],
    "SQL Server": [r"sql\s+server"],
    "Ant": [r"\bant\b"],
    "Selenium Grid": [r"selenium\s+grid"],
}

CORE_SKILLS = ("java", "selenium", "rest_assured", "sql_oracle")


def _find_quotes(text: str, patterns: list[str], limit: int = 2) -> list[str]:
    quotes: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for pattern in patterns:
            if re.search(pattern, stripped, re.IGNORECASE):
                snippet = stripped if len(stripped) <= 160 else stripped[:157] + "..."
                if snippet not in quotes:
                    quotes.append(snippet)
                break
        if len(quotes) >= limit:
            break
    return quotes


def build_evidence(profile: ResumeProfile, standard: dict[str, Any]) -> list[EvidenceItem]:
    text = profile.text
    items: list[EvidenceItem] = []
    for skill, spec in standard["mandatory"].items():
        weight = int(spec.get("weight", 0)) if isinstance(spec, dict) else 0
        explicit_quotes = _find_quotes(text, _EXPLICIT_PATTERNS.get(skill, []))
        if explicit_quotes:
            level, note = EvidenceLevel.EXPLICIT, "Stated directly in the resume."
            quotes = explicit_quotes
        else:
            inferred_quotes = _find_quotes(text, _INFERRED_PATTERNS.get(skill, []))
            if inferred_quotes:
                level, note = EvidenceLevel.INFERRED, "Related evidence only; must be validated live."
                quotes = inferred_quotes
            else:
                level, note = EvidenceLevel.MISSING, "No supporting evidence found in the resume."
                quotes = []
        items.append(EvidenceItem(
            skill=skill, label=SKILL_LABELS.get(skill, skill), level=level,
            weight=weight, mandatory=True, quotes=quotes, note=note,
        ))
    for name, patterns in GOOD_TO_HAVE_PATTERNS.items():
        quotes = _find_quotes(text, patterns, limit=1)
        items.append(EvidenceItem(
            skill=name.lower().replace(" ", "_"), label=name,
            level=EvidenceLevel.EXPLICIT if quotes else EvidenceLevel.MISSING,
            weight=0, mandatory=False, quotes=quotes,
            note="Good-to-have skill." if quotes else "Not mentioned.",
        ))
    return items


def detect_reject_signals(profile: ResumeProfile, standard: dict[str, Any],
                          evidence: list[EvidenceItem]) -> list[str]:
    signals: list[str] = []
    minimum = float(standard["role"]["minimum_overall_experience_years"])
    if profile.experience_years is not None and profile.experience_years < minimum:
        signals.append(
            f"Overall experience {profile.experience_years:g} years is below the "
            f"{minimum:g}-year minimum."
        )
    text = profile.text.lower()
    if re.search(r"basic\s+(?:knowledge\s+of\s+)?java|java\s*[:(-]?\s*basic", text):
        signals.append("Java is explicitly described as basic.")
    mandatory = {item.skill: item for item in evidence if item.mandatory}
    if "postman" in text and mandatory["rest_assured"].level == EvidenceLevel.MISSING:
        signals.append("API experience appears limited to Postman without programmatic automation.")
    if mandatory["ownership"].level == EvidenceLevel.MISSING and \
            mandatory["framework"].level == EvidenceLevel.MISSING:
        signals.append("No independent coding or framework ownership evidence.")
    return signals


def compute_score(evidence: list[EvidenceItem]) -> float:
    total = sum(item.weight for item in evidence if item.mandatory)
    if total == 0:
        return 0.0
    earned = 0.0
    for item in evidence:
        if not item.mandatory:
            continue
        if item.level == EvidenceLevel.EXPLICIT:
            earned += item.weight
        elif item.level == EvidenceLevel.INFERRED:
            earned += item.weight * 0.5
    return round(earned / total * 100, 1)


def decide(gate_passed: bool, reject_signals: list[str], score_percent: float,
           evidence: list[EvidenceItem]) -> Decision:
    if not gate_passed or reject_signals:
        return Decision.DO_NOT_PROCEED
    mandatory = {item.skill: item for item in evidence if item.mandatory}
    core_missing = [s for s in CORE_SKILLS if mandatory[s].level == EvidenceLevel.MISSING]
    core_explicit = all(mandatory[s].level == EvidenceLevel.EXPLICIT for s in CORE_SKILLS)
    if core_explicit and score_percent >= 75:
        return Decision.PROCEED
    if score_percent >= 50 and len(core_missing) <= 1:
        return Decision.CONDITIONAL
    return Decision.DO_NOT_PROCEED


def build_risks_and_questions(evidence: list[EvidenceItem]) -> tuple[list[str], list[str]]:
    risks: list[str] = []
    questions: list[str] = []
    for item in evidence:
        if not item.mandatory:
            continue
        if item.level == EvidenceLevel.MISSING:
            risks.append(f"{item.label}: no resume evidence; treat as unverified.")
            questions.append(
                f"Ask the candidate to demonstrate {item.label} hands-on; the resume "
                "provides no supporting evidence."
            )
        elif item.level == EvidenceLevel.INFERRED:
            risks.append(f"{item.label}: only indirect evidence; verify depth live.")
            questions.append(
                f"Probe {item.label} depth with a live exercise; resume evidence is indirect."
            )
    return risks, questions


def screen_resume(profile: ResumeProfile, standard: dict[str, Any]) -> ScreeningResult:
    evidence = build_evidence(profile, standard)
    minimum = float(standard["role"]["minimum_overall_experience_years"])
    gate_passed = profile.experience_years is not None and profile.experience_years >= minimum
    reject_signals = detect_reject_signals(profile, standard, evidence)
    if profile.experience_years is None:
        reject_signals = list(reject_signals)
        # Unknown experience is a risk, not an automatic reject; gate stays failed
        # unless evidence is added, so decision degrades to Do Not Proceed only
        # when combined with other rules below.
        gate_passed = False
    score = compute_score(evidence)
    decision = decide(gate_passed, reject_signals, score, evidence)
    risks, questions = build_risks_and_questions(evidence)
    if profile.experience_years is None:
        risks.insert(0, "Overall experience could not be read from the resume; confirm before scheduling.")
    return ScreeningResult(
        candidate_name=profile.name,
        experience_years=profile.experience_years,
        experience_gate_passed=gate_passed,
        evidence=evidence,
        reject_signals=reject_signals,
        score_percent=score,
        decision=decision,
        risks=risks,
        validation_questions=questions,
    )


# --------------------------------------------------------------------------
# Document generation


def _decision_banner(doc: ZumeDocument, decision: Decision) -> None:
    if decision == Decision.PROCEED:
        doc.banner("Proceed with technical screening.", kind="success", label="DECISION")
    elif decision == Decision.CONDITIONAL:
        doc.banner("Conditional technical screen required.", kind="warning", label="DECISION")
    else:
        doc.banner("Do not proceed for the current Senior SDET role.", kind="danger", label="DECISION")


def _evidence_rows(result: ScreeningResult, mandatory: bool) -> list[list[str]]:
    rows = []
    for item in result.evidence:
        if item.mandatory != mandatory:
            continue
        quote = item.quotes[0] if item.quotes else "—"
        weight = str(item.weight) if item.mandatory else "—"
        rows.append([item.label, item.level.value.title(), weight, quote, item.note])
    return rows


def generate_standardized_resume(theme: dict[str, Any], profile: ResumeProfile,
                                 result: ScreeningResult, out_path: Path) -> None:
    provider = get_provider()
    doc = ZumeDocument(theme, "Standardized Resume Record", f"Candidate: {profile.name}")
    doc.heading("Profile summary", 1)
    doc.paragraph(provider.summarize_resume(profile.text))
    doc.heading("Key facts", 1)
    exp = f"{profile.experience_years:g} years" if profile.experience_years else "Not stated"
    doc.key_values([
        ("Candidate", profile.name),
        ("Overall experience", exp),
        ("Screening score", f"{result.score_percent:g}%"),
    ])
    doc.heading("Resume content (verbatim extract)", 1)
    for chunk in [c.strip() for c in profile.text.split("\n") if c.strip()][:80]:
        doc.paragraph(chunk)
    doc.save(out_path)


def generate_ats_screening(theme: dict[str, Any], result: ScreeningResult, out_path: Path) -> None:
    doc = ZumeDocument(theme, "ATS Screening Report", f"Candidate: {result.candidate_name}")
    _decision_banner(doc, result.decision)
    doc.heading("Decision", 1)
    exp = f"{result.experience_years:g} years" if result.experience_years else "Not stated"
    doc.key_values([
        ("Decision", result.decision.value),
        ("Weighted evidence score", f"{result.score_percent:g}%"),
        ("Experience gate (8+ years)", "Passed" if result.experience_gate_passed else "Not passed"),
        ("Overall experience", exp),
    ])
    doc.heading("Evidence matrix — mandatory skills", 1)
    doc.table(
        ["Skill", "Evidence", "Weight", "Resume quote", "Note"],
        _evidence_rows(result, mandatory=True),
    )
    doc.heading("Evidence matrix — good-to-have skills", 1)
    doc.table(
        ["Skill", "Evidence", "Weight", "Resume quote", "Note"],
        _evidence_rows(result, mandatory=False),
    )
    doc.heading("Risks and inconsistencies", 1)
    if result.risks:
        doc.banner(f"{len(result.risks)} risk item(s) require live validation.", kind="warning")
        doc.bullets(result.risks)
    else:
        doc.paragraph("No screening risks identified.")
    if result.reject_signals:
        doc.heading("Automatic reject signals", 1)
        doc.banner("Automatic reject signals were detected.", kind="danger")
        doc.bullets(result.reject_signals)
    doc.heading("Candidate-specific validation questions", 1)
    if result.validation_questions:
        doc.bullets(result.validation_questions)
    else:
        doc.paragraph("Standard validation set applies; no extra questions generated.")
    doc.save(out_path)


PROCEED_TEMPLATE = """Subject: Profile Screening Feedback – [Candidate]

Hi Team,

Reviewed [Candidate]'s profile.

Recommendation: Proceed with technical screening.

The profile is aligned with [key skills]. The interview should specifically validate [top risks] through live exercises.

Please provide at least one business day notice before scheduling.

Thanks."""

DO_NOT_PROCEED_TEMPLATE = """Subject: Profile Screening Feedback – [Candidate]

Hi Team,

Reviewed [Candidate]'s profile.

Recommendation: Do not proceed for the current Senior SDET role.

The profile does not meet the required hands-on depth in [gaps].

Thanks."""

CONDITIONAL_TEMPLATE = """Subject: Profile Screening Feedback – [Candidate]

Hi Team,

Reviewed [Candidate]'s profile.

Recommendation: Conditional technical screen.

The profile shows relevant indicators, but the evidence for [gaps] is not conclusive. A strict live technical screen should validate [top risks] before proceeding further.

Please provide at least one business day notice before scheduling.

Thanks."""


def recruiter_feedback_text(result: ScreeningResult) -> str:
    provider = get_provider()
    explicit = [i.label for i in result.evidence if i.mandatory and i.level == EvidenceLevel.EXPLICIT]
    gaps = [i.label for i in result.evidence
            if i.mandatory and i.level != EvidenceLevel.EXPLICIT]
    top_risks = "; ".join(result.risks[:3]) if result.risks else "core mandatory skills"
    replacements = {
        "Candidate": result.candidate_name,
        "key skills": ", ".join(explicit) if explicit else "the stated stack",
        "top risks": top_risks,
        "gaps": ", ".join(gaps) if gaps else "the mandatory skill areas",
    }
    if result.decision == Decision.PROCEED:
        template = PROCEED_TEMPLATE
    elif result.decision == Decision.CONDITIONAL:
        template = CONDITIONAL_TEMPLATE
    else:
        template = DO_NOT_PROCEED_TEMPLATE
    return provider.draft_communication(template, replacements)


def generate_recruiter_feedback(theme: dict[str, Any], result: ScreeningResult,
                                docx_path: Path, md_path: Path) -> None:
    body = recruiter_feedback_text(result)
    doc = ZumeDocument(theme, "Recruiter Feedback", f"Candidate: {result.candidate_name}")
    _decision_banner(doc, result.decision)
    doc.heading("Copy-ready draft", 1)
    for para in body.split("\n\n"):
        doc.paragraph(para)
    doc.heading("Actions", 1)
    if result.decision == Decision.DO_NOT_PROCEED:
        doc.bullets(["Send the draft to the recruiting team.", "Archive the candidate record."])
    else:
        doc.bullets([
            "Send the draft to the recruiting team.",
            "Request scheduling with at least one business day notice.",
            "Prepare the interview kit before the confirmed slot.",
        ])
    doc.save(docx_path)
    atomic_write_text(md_path, f"# Recruiter Feedback — {result.candidate_name}\n\n```text\n{body}\n```\n")
