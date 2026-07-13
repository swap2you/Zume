"""Phase 2 — explicit experience-gate states (PASSED / FAILED / UNKNOWN)."""

from zume import screening as scr
from zume.config import load_hiring_standard
from zume.ingest import analyze_experience, parse_resume
from zume.models import Decision, ExperienceState

SKILLS_BLOCK = (
    "Skills: Java, Selenium, TestNG, Cucumber, REST Assured, Oracle SQL, Jenkins.\n"
    "Built and maintained a Java Selenium framework, implemented REST Assured API "
    "chaining, validated data in Oracle SQL and integrated Jenkins. Mentored two engineers.\n"
)


def _screen(text, root):
    return scr.screen_resume(parse_resume(text), load_hiring_standard(root))


def test_seven_years_fails_gate(repo_root):
    result = _screen("Sam Lee\n7 years of experience.\n" + SKILLS_BLOCK, repo_root)
    assert result.experience_state == ExperienceState.FAILED
    assert result.decision == Decision.DO_NOT_PROCEED


def test_eight_years_passes_gate(repo_root):
    result = _screen("Sam Lee\n8 years of experience.\n" + SKILLS_BLOCK, repo_root)
    assert result.experience_state == ExperienceState.PASSED
    assert result.decision != Decision.DO_NOT_PROCEED


def test_ten_years_passes_gate(repo_root):
    result = _screen("Sam Lee\n10 years of experience.\n" + SKILLS_BLOCK, repo_root)
    assert result.experience_state == ExperienceState.PASSED


def test_no_stated_experience_is_unknown_and_conditional(repo_root):
    result = _screen("Sam Lee\nSenior Test Engineer.\n" + SKILLS_BLOCK, repo_root)
    assert result.experience_state == ExperienceState.UNKNOWN
    assert result.manual_review_required
    assert result.decision == Decision.CONDITIONAL


def test_conflicting_claims_are_unknown(repo_root):
    text = ("Sam Lee\n9 years of experience.\nLater: 13 years of overall experience.\n"
            + SKILLS_BLOCK)
    analysis = analyze_experience(text)
    assert analysis.state == "unknown"
    assert sorted(analysis.claims) == [9.0, 13.0]
    result = _screen(text, repo_root)
    assert result.experience_state == ExperienceState.UNKNOWN
    assert result.decision == Decision.CONDITIONAL


def test_date_history_without_total_is_unknown(repo_root):
    text = ("Sam Lee\nSenior Test Engineer.\n"
            "Company A: 2016 - 2020. Company B: Jan 2020 - Present.\n" + SKILLS_BLOCK)
    result = _screen(text, repo_root)
    assert result.experience_state == ExperienceState.UNKNOWN
    assert "manual" in result.experience_detail.lower()


def test_decimal_experience_is_parsed(repo_root):
    analysis = analyze_experience("Senior Automation Engineer with 9.2 years of experience.")
    assert analysis.years == 9.2
    result = _screen("Sam Lee\n9.2 years of experience.\n" + SKILLS_BLOCK, repo_root)
    assert result.experience_state == ExperienceState.PASSED
    assert result.experience_years == 9.2


def test_unrelated_numeric_years_do_not_count_as_experience(repo_root):
    # Java 8 / Selenium 4 / a graduation year must not be read as experience.
    text = ("Sam Lee\nSenior Test Engineer.\n"
            "Skills: Java 8, Selenium 4, Spring 5. Graduated 2015.\n" + SKILLS_BLOCK)
    analysis = analyze_experience(text)
    assert analysis.years is None
    assert analysis.state == "unknown"
    result = _screen(text, repo_root)
    assert result.experience_state == ExperienceState.UNKNOWN
