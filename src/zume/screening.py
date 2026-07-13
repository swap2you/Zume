"""Resume screening: evidence matrix, scoring gates and decision rules.

Important: the percentage produced here is *resume evidence coverage*, not a
measure of technical competency. Competency must be verified live. This module
never invents evidence, duration, proficiency or recency.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from zume.candidate import atomic_write_text
from zume.documents import ZumeDocument
from zume.ingest import ResumeProfile, analyze_experience
from zume.models import (
    Confidence,
    Decision,
    EvidenceItem,
    EvidenceLevel,
    EvidenceType,
    ExperienceState,
    ScreeningResult,
)
from zume.providers import get_provider

COMPETENCY_DISCLAIMER = (
    "This score measures evidence found in the resume. It does not establish "
    "technical competency. Competency must be verified through live assessment."
)

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

# Verbs that indicate hands-on project delivery / ownership.
_OWNERSHIP_VERBS = re.compile(
    r"\b(built|build|designed|architected|owned|led|created|established|drove|"
    r"reduced|improved|increased|mentored|spearheaded|delivered)\b", re.IGNORECASE)
_PROJECT_VERBS = re.compile(
    r"\b(implemented|developed|automated|integrated|maintained|validated|"
    r"engineered|refactored|migrated|optimi[sz]ed|configured)\b", re.IGNORECASE)
_QUANTIFIER = re.compile(
    r"(\d+\s*%|\bby\s+\d+|\d+\s*\+?\s*(?:tests?|engineers?|suites?|pipelines?|"
    r"apis?|services?|members?|projects?|years?))", re.IGNORECASE)
_YEAR_TOKEN = re.compile(r"\b(19|20)\d{2}\b")
_PRESENT_TOKEN = re.compile(r"\b(present|current|to date|now)\b", re.IGNORECASE)
_DURATION_TOKEN = re.compile(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", re.IGNORECASE)
_SKILLS_LINE = re.compile(
    r"^\s*(skills?|technical skills?|technologies|tech stack|core competencies|"
    r"tools?|expertise)\b", re.IGNORECASE)


def _is_skills_line(line: str) -> bool:
    if _SKILLS_LINE.search(line):
        return True
    # Prose (has action/ownership verbs) is never a bare skills enumeration.
    if _OWNERSHIP_VERBS.search(line) or _PROJECT_VERBS.search(line):
        return False
    # A skills enumeration is several short comma-separated tokens.
    segments = [s.strip() for s in line.split(",") if s.strip()]
    if len(segments) >= 4:
        short = sum(1 for s in segments if len(s.split()) <= 3)
        if short / len(segments) >= 0.7:
            return True
    return False


def _matched_lines(text: str, patterns: list[str]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if any(re.search(p, line, re.IGNORECASE) for p in patterns):
            out.append((idx, line))
    return out


def _snippet(line: str) -> str:
    return line if len(line) <= 160 else line[:157] + "..."


def _classify_skill(text: str, skill: str) -> dict[str, Any]:
    """Return a deterministic evidence classification for a single skill."""
    explicit = _matched_lines(text, _EXPLICIT_PATTERNS.get(skill, []))
    if explicit:
        non_skills = [(n, ln) for n, ln in explicit if not _is_skills_line(ln)]
        skills_only = not non_skills
        ownership = any(_OWNERSHIP_VERBS.search(ln) for _, ln in explicit)
        quantified = any(
            _OWNERSHIP_VERBS.search(ln) and _QUANTIFIER.search(ln)
            for _, ln in non_skills
        )
        project = any(
            _OWNERSHIP_VERBS.search(ln) or _PROJECT_VERBS.search(ln)
            for _, ln in non_skills
        )
        if quantified:
            etype = EvidenceType.QUANTIFIED
        elif project:
            etype = EvidenceType.PROJECT
        elif non_skills:
            etype = EvidenceType.RESPONSIBILITY
        else:
            etype = EvidenceType.SKILLS_LIST
        quotes = [_snippet(ln) for _, ln in explicit[:2]]
        years = [m.group(0) for _, ln in explicit for m in _YEAR_TOKEN.finditer(ln)]
        recency = ""
        if any(_PRESENT_TOKEN.search(ln) for _, ln in explicit):
            recency = "current"
        elif years:
            recency = max(years)
        duration = ""
        for _, ln in explicit:
            dm = _DURATION_TOKEN.search(ln)
            if dm:
                duration = f"{dm.group(1)} years"
                break
        first = explicit[0][0]
        source = "skills section" if skills_only else f"line {first}"
        return {
            "level": EvidenceLevel.EXPLICIT,
            "evidence_type": etype,
            "quotes": quotes,
            "recency": recency,
            "duration": duration,
            "ownership_present": ownership,
            "summary_or_skills_only": skills_only,
            "source_hint": source,
        }
    inferred = _matched_lines(text, _INFERRED_PATTERNS.get(skill, []))
    if inferred:
        return {
            "level": EvidenceLevel.INFERRED,
            "evidence_type": EvidenceType.INFERRED,
            "quotes": [_snippet(ln) for _, ln in inferred[:2]],
            "recency": "",
            "duration": "",
            "ownership_present": False,
            "summary_or_skills_only": False,
            "source_hint": f"line {inferred[0][0]}",
        }
    return {
        "level": EvidenceLevel.MISSING,
        "evidence_type": EvidenceType.MISSING,
        "quotes": [],
        "recency": "",
        "duration": "",
        "ownership_present": False,
        "summary_or_skills_only": False,
        "source_hint": "",
    }


_TYPE_NOTES = {
    EvidenceType.QUANTIFIED: "Quantified ownership/impact evidence.",
    EvidenceType.PROJECT: "Project-specific implementation evidence.",
    EvidenceType.RESPONSIBILITY: "Responsibility statement; verify depth live.",
    EvidenceType.SKILLS_LIST: "Skills-list mention only; not proof of depth.",
    EvidenceType.INFERRED: "Indirect evidence only; must be validated live.",
    EvidenceType.MISSING: "No supporting evidence found in the resume.",
}


def _evidence_scoring(standard: dict[str, Any]) -> dict[str, Any]:
    return standard.get("evidence_scoring", {})


def build_evidence(profile: ResumeProfile, standard: dict[str, Any]) -> list[EvidenceItem]:
    text = profile.text
    scoring = _evidence_scoring(standard)
    credit_map = scoring.get("credit", {})
    confidence_map = scoring.get("confidence_by_type", {})
    items: list[EvidenceItem] = []
    for skill, spec in standard["mandatory"].items():
        weight = int(spec.get("weight", 0)) if isinstance(spec, dict) else 0
        info = _classify_skill(text, skill)
        etype: EvidenceType = info["evidence_type"]
        credit = float(credit_map.get(etype.value, 0.0))
        confidence = Confidence(confidence_map.get(etype.value, "none"))
        items.append(EvidenceItem(
            skill=skill, label=SKILL_LABELS.get(skill, skill), level=info["level"],
            weight=weight, mandatory=True, quotes=info["quotes"],
            note=_TYPE_NOTES[etype], evidence_type=etype, confidence=confidence,
            credit=round(credit, 2), recency=info["recency"], duration=info["duration"],
            ownership_present=info["ownership_present"],
            summary_or_skills_only=info["summary_or_skills_only"],
            source_hint=info["source_hint"],
        ))
    for name, patterns in GOOD_TO_HAVE_PATTERNS.items():
        matches = _matched_lines(text, patterns)
        present = bool(matches)
        items.append(EvidenceItem(
            skill=name.lower().replace(" ", "_"), label=name,
            level=EvidenceLevel.EXPLICIT if present else EvidenceLevel.MISSING,
            weight=0, mandatory=False,
            quotes=[_snippet(matches[0][1])] if present else [],
            note="Good-to-have skill." if present else "Not mentioned.",
            evidence_type=EvidenceType.RESPONSIBILITY if present else EvidenceType.MISSING,
            confidence=Confidence.MEDIUM if present else Confidence.NONE,
            credit=0.0,
            source_hint=f"line {matches[0][0]}" if present else "",
        ))
    return items


def resolve_experience_state(profile: ResumeProfile,
                             standard: dict[str, Any]) -> tuple[ExperienceState, str, list[float]]:
    minimum = float(standard["role"]["minimum_overall_experience_years"])
    analysis = profile.experience or analyze_experience(profile.text)
    if analysis.state == "known" and analysis.years is not None:
        if analysis.years >= minimum:
            return (ExperienceState.PASSED,
                    f"{analysis.years:g} years meets the {minimum:g}-year minimum.",
                    analysis.claims)
        return (ExperienceState.FAILED,
                f"{analysis.years:g} years is below the {minimum:g}-year minimum.",
                analysis.claims)
    return ExperienceState.UNKNOWN, analysis.detail, analysis.claims


def detect_reject_signals(profile: ResumeProfile, evidence: list[EvidenceItem]) -> list[str]:
    """Non-experience automatic-reject signals only."""
    signals: list[str] = []
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


def compute_coverage(evidence: list[EvidenceItem]) -> float:
    """Resume evidence coverage as a weighted percentage of mandatory skills."""
    total = sum(item.weight for item in evidence if item.mandatory)
    if total == 0:
        return 0.0
    earned = sum(item.weight * item.credit for item in evidence if item.mandatory)
    return round(earned / total * 100, 1)


# Backward-compatible alias.
def compute_score(evidence: list[EvidenceItem]) -> float:
    return compute_coverage(evidence)


def decide(experience_state: ExperienceState, reject_signals: list[str],
           coverage: float, evidence: list[EvidenceItem],
           standard: dict[str, Any]) -> Decision:
    scoring = _evidence_scoring(standard)
    proceed_min = float(scoring.get("proceed_min_coverage", 75))
    conditional_min = float(scoring.get("conditional_min_coverage", 50))
    if experience_state == ExperienceState.FAILED:
        return Decision.DO_NOT_PROCEED
    if reject_signals:
        return Decision.DO_NOT_PROCEED
    if experience_state == ExperienceState.UNKNOWN:
        # Missing / conflicting / ambiguous experience -> manual technical screen.
        return Decision.CONDITIONAL
    mandatory = {item.skill: item for item in evidence if item.mandatory}
    core_missing = [s for s in CORE_SKILLS if mandatory[s].level == EvidenceLevel.MISSING]
    core_explicit = all(mandatory[s].level == EvidenceLevel.EXPLICIT for s in CORE_SKILLS)
    if core_explicit and coverage >= proceed_min:
        return Decision.PROCEED
    if coverage >= conditional_min and len(core_missing) <= 1:
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
        elif item.evidence_type == EvidenceType.SKILLS_LIST:
            risks.append(f"{item.label}: only a skills-list mention; depth unproven.")
            questions.append(
                f"{item.label} appears only in a skills list. Require a live exercise "
                "to confirm hands-on depth."
            )
        elif item.level == EvidenceLevel.INFERRED:
            risks.append(f"{item.label}: only indirect evidence; verify depth live.")
            questions.append(
                f"Probe {item.label} depth with a live exercise; resume evidence is indirect."
            )
    return risks, questions


def screen_resume(profile: ResumeProfile, standard: dict[str, Any]) -> ScreeningResult:
    evidence = build_evidence(profile, standard)
    experience_state, experience_detail, claims = resolve_experience_state(profile, standard)
    reject_signals = detect_reject_signals(profile, evidence)
    coverage = compute_coverage(evidence)
    decision = decide(experience_state, reject_signals, coverage, evidence, standard)
    risks, questions = build_risks_and_questions(evidence)

    display_reject_signals = list(reject_signals)
    if experience_state == ExperienceState.FAILED:
        display_reject_signals.insert(0, f"Overall experience below minimum: {experience_detail}")
    if experience_state == ExperienceState.UNKNOWN:
        risks.insert(0, f"Experience could not be confirmed: {experience_detail}")

    return ScreeningResult(
        candidate_name=profile.name,
        experience_years=profile.experience_years,
        experience_state=experience_state,
        experience_detail=experience_detail,
        experience_claims=claims,
        experience_gate_passed=(experience_state == ExperienceState.PASSED),
        evidence=evidence,
        reject_signals=display_reject_signals,
        score_percent=coverage,
        decision=decision,
        manual_review_required=(experience_state == ExperienceState.UNKNOWN),
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


def _experience_label(result: ScreeningResult) -> str:
    return {
        ExperienceState.PASSED: "Passed",
        ExperienceState.FAILED: "Failed",
        ExperienceState.UNKNOWN: "Unknown (manual review)",
    }[result.experience_state]


def _evidence_rows(result: ScreeningResult, mandatory: bool) -> list[list[str]]:
    rows = []
    for item in result.evidence:
        if item.mandatory != mandatory:
            continue
        quote = item.quotes[0] if item.quotes else "—"
        weight = str(item.weight) if item.mandatory else "—"
        rows.append([
            item.label,
            item.evidence_type.value.replace("_", " "),
            item.confidence.value,
            weight,
            f"{int(item.credit * 100)}%" if item.mandatory else "—",
            quote,
        ])
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
        ("Experience gate", _experience_label(result)),
        ("Resume evidence coverage", f"{result.score_percent:g}%"),
    ])
    doc.banner(COMPETENCY_DISCLAIMER, kind="info", label="NOTE")
    doc.heading("Resume content (verbatim extract)", 1)
    for chunk in [c.strip() for c in profile.text.split("\n") if c.strip()][:80]:
        doc.paragraph(chunk)
    doc.save(out_path)


def generate_ats_screening(theme: dict[str, Any], result: ScreeningResult, out_path: Path) -> None:
    doc = ZumeDocument(theme, "ATS Screening Report", f"Candidate: {result.candidate_name}")
    _decision_banner(doc, result.decision)
    doc.banner(COMPETENCY_DISCLAIMER, kind="info", label="SCORE MEANING")
    doc.heading("Decision", 1)
    exp = f"{result.experience_years:g} years" if result.experience_years else "Not stated"
    doc.key_values([
        ("Decision", result.decision.value),
        ("Resume evidence coverage", f"{result.score_percent:g}%"),
        ("Experience gate", _experience_label(result)),
        ("Experience detail", result.experience_detail or "—"),
        ("Overall experience", exp),
    ])
    if result.manual_review_required:
        doc.banner("Experience could not be confirmed from the resume. This candidate "
                   "requires manual experience review before a final decision.",
                   kind="warning", label="MANUAL REVIEW")
    doc.heading("Resume evidence coverage — mandatory skills", 1)
    doc.paragraph(
        "Coverage reflects the strength of resume evidence per skill (quantified > "
        "project > responsibility > skills-list). It is not a competency score.",
    )
    doc.table(
        ["Skill", "Evidence type", "Confidence", "Weight", "Credit", "Resume quote"],
        _evidence_rows(result, mandatory=True),
    )
    doc.heading("Evidence matrix — good-to-have skills", 1)
    doc.table(
        ["Skill", "Evidence type", "Confidence", "Weight", "Credit", "Resume quote"],
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

The profile is aligned with [key skills]. Resume evidence coverage is [coverage] (evidence only; not a competency score). The interview should specifically validate [top risks] through live exercises.

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

[conditional_reason] Resume evidence coverage is [coverage] (evidence only; not a competency score). A strict live technical screen should validate [top risks] before proceeding further.

Please provide at least one business day notice before scheduling.

Thanks."""


def recruiter_feedback_text(result: ScreeningResult) -> str:
    provider = get_provider()
    explicit = [i.label for i in result.evidence if i.mandatory and i.level == EvidenceLevel.EXPLICIT]
    gaps = [i.label for i in result.evidence
            if i.mandatory and i.level != EvidenceLevel.EXPLICIT]
    top_risks = "; ".join(result.risks[:3]) if result.risks else "core mandatory skills"
    if result.manual_review_required:
        conditional_reason = ("Overall experience could not be confirmed from the resume, "
                              "so this is routed to a manual technical screen.")
    else:
        conditional_reason = "The profile shows relevant indicators, but the evidence is not conclusive."
    replacements = {
        "Candidate": result.candidate_name,
        "key skills": ", ".join(explicit) if explicit else "the stated stack",
        "top risks": top_risks,
        "gaps": ", ".join(gaps) if gaps else "the mandatory skill areas",
        "coverage": f"{result.score_percent:g}%",
        "conditional_reason": conditional_reason,
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
    atomic_write_text(
        md_path,
        f"# Recruiter Feedback — {result.candidate_name}\n\n"
        f"> {COMPETENCY_DISCLAIMER}\n\n```text\n{body}\n```\n",
    )
