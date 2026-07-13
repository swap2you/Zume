"""Interview preparation: focus sheet, 3-hour guide, scorecard, exercise pack."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from zume.documents import ZumeDocument
from zume.models import (
    Decision,
    EvidenceLevel,
    ExerciseSelection,
    InterviewKit,
    ScreeningResult,
)

CORE_AREAS = ["java", "selenium", "rest_assured", "sql_oracle", "framework_ci"]

THREE_HOUR_PLAN = [
    ("0:00–0:15", "Introductions and role/framework walkthrough", "Framework ownership, communication"),
    ("0:15–0:45", "Java live coding", "Collections, OOP, independent implementation"),
    ("0:45–1:20", "Selenium live coding", "Locators, waits, Page Object, debugging"),
    ("1:20–1:50", "REST Assured live coding", "Chaining, assertions, specifications"),
    ("1:50–2:15", "SQL / Oracle exercises", "Joins, aggregation, latest-record queries"),
    ("2:15–2:40", "Framework and CI/CD deep dive", "Design, Jenkins/Git, diagnosis"),
    ("2:40–2:55", "Resume validation and scenario questions", "Candidate-specific risks"),
    ("2:55–3:00", "Candidate questions and wrap-up", "Close and next steps"),
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


def select_exercises(library: dict[str, Any], result: ScreeningResult) -> list[ExerciseSelection]:
    selections: list[ExerciseSelection] = []
    areas = list(CORE_AREAS)
    if _supports_optional_area(result, ["Appium", "BrowserStack", "Android and iOS"]):
        areas.insert(4, "appium")
    mandatory = {item.skill: item for item in result.evidence if item.mandatory}
    for area in areas:
        spec = library["areas"].get(area)
        if not spec:
            continue
        exercises = spec["exercises"]
        # Weak/missing evidence warrants two exercises in that area.
        related = {
            "java": "java", "selenium": "selenium", "rest_assured": "rest_assured",
            "sql_oracle": "sql_oracle", "framework_ci": "framework",
        }.get(area)
        count = 1
        if related and mandatory.get(related) and \
                mandatory[related].level != EvidenceLevel.EXPLICIT:
            count = 2
        for exercise in exercises[:max(count, 1)]:
            selections.append(ExerciseSelection(
                area=area,
                area_label=spec["label"],
                exercise_id=exercise["id"],
                title=exercise["title"],
                task=exercise["task"].strip(),
                expected_answer=exercise["expected_answer"].strip(),
                reference_solution=exercise["reference_solution"].strip(),
                follow_up=exercise["follow_up"].strip(),
                red_flags=list(exercise.get("red_flags", [])),
            ))
    return selections


def build_kit(library: dict[str, Any], result: ScreeningResult) -> InterviewKit:
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
        exercises=select_exercises(library, result),
    )


def generate_focus_sheet(theme: dict[str, Any], kit: InterviewKit,
                         result: ScreeningResult, out_path: Path) -> None:
    doc = ZumeDocument(theme, "Candidate Focus Sheet", f"Candidate: {kit.candidate_name}")
    if result.decision == Decision.PROCEED:
        doc.banner("Screening decision: Proceed. Validate depth live.", kind="success", label="CONTEXT")
    else:
        doc.banner(f"Screening decision: {result.decision.value}. Apply a strict bar.",
                   kind="warning", label="CONTEXT")
    doc.heading("Focus areas", 1)
    doc.bullets(kit.focus_areas)
    doc.heading("Candidate-specific validation questions", 1)
    if kit.validation_questions:
        doc.bullets(kit.validation_questions)
    else:
        doc.paragraph("No candidate-specific questions; run the standard validation set.")
    doc.heading("Selected exercises at a glance", 1)
    doc.table(
        ["Area", "Exercise", "Follow-up"],
        [[e.area_label, e.title, e.follow_up] for e in kit.exercises],
    )
    doc.save(out_path)


def generate_interview_guide(theme: dict[str, Any], kit: InterviewKit,
                             library: dict[str, Any], out_path: Path) -> None:
    doc = ZumeDocument(theme, "Full Interview Guide (3 Hours)", f"Candidate: {kit.candidate_name}")
    doc.banner("Score reasoning, modification and debugging separately from the final code.",
               kind="info", label="CALIBRATION")
    doc.heading("Session plan", 1)
    doc.table(["Time", "Segment", "What to assess"],
              [[t, s, a] for t, s, a in THREE_HOUR_PLAN])
    doc.heading("Exercises with expected answers", 1)
    for exercise in kit.exercises:
        doc.heading(f"{exercise.area_label}: {exercise.title}", 2)
        doc.key_values([("Task", exercise.task)])
        doc.paragraph("Expected answer:", bold=True)
        doc.paragraph(exercise.expected_answer)
        doc.paragraph("Reference solution:", bold=True)
        for line in exercise.reference_solution.splitlines():
            doc.paragraph(line or " ", size_pt=9)
        doc.key_values([("Follow-up modification", exercise.follow_up)])
        if exercise.red_flags:
            doc.paragraph("Red flags:", bold=True)
            doc.bullets(exercise.red_flags)
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
        ["Area", "Weight", "Score (0–10)", "Evidence / notes"],
        [[label, str(weight), "", ""] for label, weight in SCORECARD_AREAS],
    )
    doc.heading("Recommendation bands", 1)
    doc.table(["Score", "Recommendation"], [
        ["85–100", "Strong Senior SDET"],
        ["75–84", "Proceed"],
        ["68–74", "Borderline / second focused round"],
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
    doc = ZumeDocument(theme, "Selected Exercise Pack", f"Candidate: {kit.candidate_name}")
    doc.banner("Interviewer copy — contains expected answers and reference solutions.",
               kind="warning", label="CONFIDENTIAL")
    for exercise in kit.exercises:
        doc.heading(f"{exercise.area_label}: {exercise.title}", 1)
        doc.key_values([
            ("Exercise ID", exercise.exercise_id),
            ("Task", exercise.task),
            ("Follow-up", exercise.follow_up),
        ])
        doc.paragraph("Reference solution:", bold=True)
        for line in exercise.reference_solution.splitlines():
            doc.paragraph(line or " ", size_pt=9)
        if exercise.red_flags:
            doc.paragraph("Red flags:", bold=True)
            doc.bullets(exercise.red_flags)
    doc.save(out_path)
