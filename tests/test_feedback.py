from zume import feedback as fb
from zume.models import Decision

POSITIVE_NOTES = (
    "Candidate explained recent framework ownership clearly. "
    "Completed duplicate-word Java exercise and Selenium dynamic-table exercise independently. "
    "REST Assured chaining was correct. "
    "Needed a hint for ROW_NUMBER but explained the final query. "
    "Modified Selenium code correctly after the locator requirement changed. "
    "Communication was concise."
)

CONCERN_NOTES = (
    "There were long unexplained pauses before each Java answer. "
    "Audible device activity was noticeable in the background. "
    "The Selenium solution showed a sudden quality shift after a pause. "
    "Candidate was unable to explain the REST Assured solution. "
    "Candidate could not modify the SQL query when the requirement changed."
)


def test_positive_notes_proceed():
    result = fb.evaluate_notes("Aarav Mehta", POSITIVE_NOTES)
    assert result.decision == Decision.PROCEED
    assert result.total_percent >= 75
    assert result.status == "SELECTED"
    assert result.observations.confidence_independent_execution == "High"
    assert result.observations.can_modify_solution.startswith("Independent")


def test_concern_notes_reduce_confidence_neutrally():
    result = fb.evaluate_notes("Test Person", CONCERN_NOTES)
    assert result.decision == Decision.DO_NOT_PROCEED
    assert result.status == "REJECTED"
    obs = result.observations
    assert obs.unexplained_pauses.startswith("Observed")
    assert obs.audible_device_activity.startswith("Observed")
    assert obs.sudden_quality_shift.startswith("Observed")
    assert obs.confidence_independent_execution == "Low"
    # neutral language only: the recommendation must not accuse
    assert "cheat" not in result.recommendation.lower()


def test_skill_scores_grounded_in_note_sentences():
    result = fb.evaluate_notes("Aarav Mehta", POSITIVE_NOTES)
    scored = {s.skill: s for s in result.skill_scores}
    assert "java" in scored and scored["java"].evidence
    assert "selenium" in scored
    assert scored["sql_oracle"].score < scored["java"].score  # hint lowered SQL


def test_mandatory_override():
    notes = ("Java exercise failed and the candidate was unable to complete it. "
             "Selenium was strong and completed independently. "
             "REST Assured chaining was correct. SQL query was correct.")
    result = fb.evaluate_notes("Test Person", notes)
    assert "Java" in result.mandatory_override_failed
    assert result.decision == Decision.DO_NOT_PROCEED
