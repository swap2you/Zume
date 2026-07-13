"""Interview preparation: focus sheet, 3-hour guide, scorecard, exercise packs.

Two exercise artifacts are produced:
  * an interviewer pack (reference solutions, red flags, independence questions);
  * a candidate sheet (task and follow-ups ONLY — never reference solutions).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from zume.documents import ZumeDocument
from zume.exercises import Exercise, ExerciseSelector, load_exercises
from zume.models import (
    Decision,
    EvidenceLevel,
    EvidenceType,
    ExerciseSelection,
    InterviewKit,
    ScreeningResult,
)

CORE_AREAS = ["java", "selenium", "rest_assured", "sql_oracle",
              "framework_design", "debugging"]

# Which mandatory skill's evidence strength drives a double-exercise in an area.
_AREA_TO_SKILL = {
    "java": "java",
    "selenium": "selenium",
    "rest_assured": "rest_assured",
    "sql_oracle": "sql_oracle",
    "framework_design": "framework",
}

THREE_HOUR_PLAN = [
    ("0:00-0:15", "Introductions and role/framework walkthrough", "Framework ownership, communication"),
    ("0:15-0:45", "Java live coding", "Collections, OOP, independent implementation"),
    ("0:45-1:20", "Selenium live coding", "Locators, waits, Page Object, debugging"),
    ("1:20-1:50", "REST Assured live coding", "Chaining, assertions, specifications"),
    ("1:50-2:15", "SQL / Oracle exercises", "Joins, aggregation, latest-record queries"),
    ("2:15-2:40", "Framework and debugging deep dive", "Design, diagnosis, CI"),
    ("2:40-2:55", "Resume validation and scenario questions", "Candidate-specific risks"),
    ("2:55-3:00", "Candidate questions and wrap-up", "Close and next steps"),
]

SCORECARD_AREAS = [
    ("Java", 15),
    ("Selenium", 20),
    ("TestNG + Cucumber", 10),
    ("REST Assured", 15),
    ("SQL + Oracle", 10),
    ("Framework ownership", 10),
    ("CI/CD", 10),
    ("Independent ownership", 10),
]

DIMENSION_LABELS = {
    "approach_before_coding": "Approach before coding",
    "independent_implementation": "Independent implementation",
    "explanation": "Explanation",
    "modification_debugging": "Modification / debugging",
    "code_quality_cleanup": "Code quality and cleanup",
}


def _supports_optional_area(result: ScreeningResult, labels: list[str]) -> bool:
    for item in result.evidence:
        if item.label in labels and item.level == EvidenceLevel.EXPLICIT:
            return True
    return False


def select_exercises(selector: ExerciseSelector, result: ScreeningResult) -> list[ExerciseSelection]:
    areas = list(CORE_AREAS)
    if _supports_optional_area(result, ["Appium", "BrowserStack", "Android and iOS"]):
        areas.append("appium")
    mandatory = {item.skill: item for item in result.evidence if item.mandatory}
    selections: list[ExerciseSelection] = []
    for area in areas:
        related = _AREA_TO_SKILL.get(area)
        count = 1
        if related and mandatory.get(related) and \
                mandatory[related].evidence_type in {
                    EvidenceType.SKILLS_LIST, EvidenceType.INFERRED, EvidenceType.MISSING}:
            count = 2
        picked: list[Exercise] = selector.pick(area, count)
        selections.extend(ex.to_selection() for ex in picked)
    return selections


_UNVERIFIED_TYPES = {EvidenceType.SKILLS_LIST, EvidenceType.INFERRED, EvidenceType.MISSING}


def unverified_mandatory_skills(result: ScreeningResult) -> list[str]:
    """Mandatory skills whose resume evidence does not prove hands-on depth."""
    return [item.label for item in result.evidence
            if item.mandatory and item.evidence_type in _UNVERIFIED_TYPES]


def build_kit(library: dict[str, Any], result: ScreeningResult,
              override_reason: str = "",
              selector: ExerciseSelector | None = None) -> InterviewKit:
    if selector is None:
        selector = ExerciseSelector(load_exercises(library))
    focus = []
    for item in result.evidence:
        if item.mandatory and item.level != EvidenceLevel.EXPLICIT:
            focus.append(f"{item.label} ({item.level.value} evidence — validate live)")
    if not focus:
        focus = ["All mandatory areas showed explicit resume evidence; verify depth, not presence."]
    return InterviewKit(
        candidate_name=result.candidate_name,
        focus_areas=focus,
        validation_questions=list(result.validation_questions),
        exercises=select_exercises(selector, result),
        screening_decision=result.decision.value,
        unverified_mandatory=unverified_mandatory_skills(result),
        override_reason=override_reason,
    )


def generate_focus_sheet(theme: dict[str, Any], kit: InterviewKit,
                         result: ScreeningResult, out_path: Path) -> None:
    doc = ZumeDocument(theme, "Candidate Focus Sheet", f"Candidate: {kit.candidate_name}")
    if result.decision == Decision.PROCEED:
        doc.banner("Screening decision: Proceed. Validate depth live.", kind="success", label="CONTEXT")
    elif result.decision == Decision.CONDITIONAL:
        doc.banner("Screening decision: Conditional. Unverified mandatory skills MUST be "
                   "validated before any recommendation.", kind="warning", label="CONTEXT")
    else:
        doc.banner("Screening decision: Do Not Proceed. This kit was produced under an "
                   "explicit override.", kind="danger", label="CONTEXT")
    if kit.override_reason:
        doc.banner(f"Override reason: {kit.override_reason}", kind="danger", label="OVERRIDE")
    if kit.unverified_mandatory:
        doc.heading("Unverified mandatory skills (validate before recommending)", 1)
        doc.banner("These mandatory skills are NOT proven by the resume and must be "
                   "verified live: " + ", ".join(kit.unverified_mandatory),
                   kind="warning", label="MUST VERIFY")
        doc.bullets(kit.unverified_mandatory)
    doc.heading("Focus areas", 1)
    doc.bullets(kit.focus_areas)
    doc.heading("Candidate-specific validation questions", 1)
    if kit.validation_questions:
        doc.bullets(kit.validation_questions)
    else:
        doc.paragraph("No candidate-specific questions; run the standard validation set.")
    doc.heading("Selected exercises at a glance", 1)
    doc.table(
        ["Area", "Exercise", "Difficulty", "Requirement-change follow-up"],
        [[e.area_label, e.title, e.difficulty, e.requirement_change_follow_up]
         for e in kit.exercises],
    )
    doc.save(out_path)


def generate_interview_guide(theme: dict[str, Any], kit: InterviewKit,
                             library: dict[str, Any], out_path: Path) -> None:
    doc = ZumeDocument(theme, "Full Interview Guide (3 Hours)", f"Candidate: {kit.candidate_name}")
    doc.banner("Interviewer-only. Contains reference solutions. Do not share with the candidate.",
               kind="danger", label="CONFIDENTIAL")
    doc.banner("Score reasoning, modification and debugging separately from the final code.",
               kind="info", label="CALIBRATION")
    doc.heading("Session plan", 1)
    doc.table(["Time", "Segment", "What to assess"],
              [[t, s, a] for t, s, a in THREE_HOUR_PLAN])
    doc.heading("Exercises with expected reasoning", 1)
    for exercise in kit.exercises:
        doc.heading(f"{exercise.area_label}: {exercise.title} ({exercise.difficulty})", 2)
        doc.key_values([("Task", exercise.task)])
        doc.paragraph("Expected reasoning:", bold=True)
        doc.paragraph(exercise.expected_reasoning)
        doc.paragraph("Reference solution:", bold=True)
        for line in exercise.reference_solution.splitlines():
            doc.paragraph(line or " ", size_pt=9)
        doc.key_values([
            ("Requirement-change follow-up", exercise.requirement_change_follow_up),
            ("Debugging follow-up", exercise.debugging_follow_up),
        ])
        if exercise.scoring_rubric:
            doc.paragraph("Scoring rubric:", bold=True)
            doc.bullets(exercise.scoring_rubric)
        if exercise.red_flags:
            doc.paragraph("Red flags:", bold=True)
            doc.bullets(exercise.red_flags)
        if exercise.independence_questions:
            doc.paragraph("Independence-verification questions:", bold=True)
            doc.bullets(exercise.independence_questions)
    doc.heading("Scoring per exercise", 1)
    dims = library.get("scoring_dimensions", {})
    doc.table(["Dimension", "Points"],
              [[DIMENSION_LABELS.get(k, k), str(v)] for k, v in dims.items()])
    doc.heading("Independence observation protocol", 1)
    doc.paragraph(
        "Record observations neutrally. Never state that a candidate cheated; "
        "capture observable behavior and the resulting confidence level only."
    )
    doc.bullets([
        "Ask for the approach before coding and require narration while coding.",
        "Change a requirement after completion and ask for the modification live.",
        "Record unexplained pauses, audible device activity and sudden quality shifts as neutral observations.",
        "Score explanation and modification separately from the final code.",
    ])
    doc.save(out_path)


def generate_scorecard(theme: dict[str, Any], kit: InterviewKit, out_path: Path) -> None:
    doc = ZumeDocument(theme, "Interview Scorecard", f"Candidate: {kit.candidate_name}")
    doc.heading("Skill scores", 1)
    doc.table(
        ["Area", "Weight", "Score (0-10)", "Evidence / notes"],
        [[label, str(weight), "", ""] for label, weight in SCORECARD_AREAS],
    )
    doc.heading("Recommendation bands", 1)
    doc.table(["Score", "Recommendation"], [
        ["85-100", "Strong Senior SDET"],
        ["75-84", "Proceed"],
        ["68-74", "Borderline / second focused round"],
        ["Below 68", "Do Not Proceed"],
    ])
    doc.banner("Mandatory override: Java, Selenium, REST Assured or SQL/Oracle below the "
               "hands-on bar means no Senior SDET recommendation regardless of total score.",
               kind="danger", label="OVERRIDE")
    doc.heading("Independence observations", 1)
    doc.table(["Field", "Record"], [
        ["Unexplained pauses", "Yes/No + timing"],
        ["Audible device activity", "Yes/No + neutral observation"],
        ["Sudden quality shift", "Yes/No + example"],
        ["Can explain solution", "Strong / Partial / Weak"],
        ["Can modify solution", "Independent / Prompted / Unable"],
        ["Confidence in independent execution", "High / Medium / Low"],
    ])
    doc.save(out_path)


def generate_exercise_pack(theme: dict[str, Any], kit: InterviewKit, out_path: Path) -> None:
    """Interviewer copy — includes reference solutions."""
    doc = ZumeDocument(theme, "Selected Exercise Pack (Interviewer)",
                       f"Candidate: {kit.candidate_name}")
    doc.banner("Interviewer-only. Contains expected reasoning and reference solutions. "
               "Do NOT share with the candidate.", kind="danger", label="CONFIDENTIAL")
    for exercise in kit.exercises:
        doc.heading(f"{exercise.area_label}: {exercise.title}", 1)
        doc.key_values([
            ("Exercise ID", exercise.exercise_id),
            ("Difficulty", exercise.difficulty),
            ("Task", exercise.task),
            ("Requirement-change follow-up", exercise.requirement_change_follow_up),
            ("Debugging follow-up", exercise.debugging_follow_up),
        ])
        doc.paragraph("Expected reasoning:", bold=True)
        doc.paragraph(exercise.expected_reasoning)
        doc.paragraph("Reference solution:", bold=True)
        for line in exercise.reference_solution.splitlines():
            doc.paragraph(line or " ", size_pt=9)
        if exercise.scoring_rubric:
            doc.paragraph("Scoring rubric:", bold=True)
            doc.bullets(exercise.scoring_rubric)
        if exercise.red_flags:
            doc.paragraph("Red flags:", bold=True)
            doc.bullets(exercise.red_flags)
        if exercise.independence_questions:
            doc.paragraph("Independence-verification questions:", bold=True)
            doc.bullets(exercise.independence_questions)
    doc.save(out_path)


def generate_candidate_exercise_sheet(theme: dict[str, Any], kit: InterviewKit,
                                      out_path: Path) -> None:
    """Candidate-shareable copy — tasks and follow-ups ONLY, never solutions."""
    doc = ZumeDocument(theme, "Interview Exercises (Candidate Copy)",
                       f"Candidate: {kit.candidate_name}")
    doc.banner("Shareable with the candidate. Contains no reference solutions or scoring.",
               kind="success", label="CANDIDATE COPY")
    for exercise in kit.exercises:
        doc.heading(f"{exercise.area_label}: {exercise.title}", 1)
        doc.key_values([("Task", exercise.task)])
        if exercise.requirement_change_follow_up:
            doc.key_values([("Possible follow-up", exercise.requirement_change_follow_up)])
    doc.save(out_path)
