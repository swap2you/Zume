from zume import screening as scr
from zume.config import load_hiring_standard
from zume.ingest import parse_resume
from zume.models import Decision, EvidenceLevel, EvidenceType, ExperienceState

# Rich resume: every core skill has project-level evidence, so it proceeds.
STRONG_RESUME = """Aarav Mehta
Senior Automation Engineer with 9.2 years of experience.
Skills: Java, Selenium 4, TestNG, Cucumber, REST Assured, Oracle SQL, Maven, Git, Jenkins.
Built and maintained a Java Selenium Page Object framework, implemented API chaining with REST Assured, validated payments in Oracle SQL, and integrated suites with Jenkins. Mentored two engineers.
"""

# Thin resume: core skills appear ONLY in a skills list (no project evidence).
SKILLS_ONLY_RESUME = """Ravi Kumar
Senior SDET with 9 years of experience.
Skills: Java, Selenium, TestNG, Cucumber, REST Assured, Oracle SQL, Jenkins, Maven.
Maintained the automation framework and owned overall test delivery.
"""

JUNIOR_RESUME = """Rohan N
QA Engineer with 4 years experience.
Skills: Java, Selenium, TestNG, REST Assured, Oracle SQL, Jenkins.
Maintained the regression framework independently.
"""

POSTMAN_RESUME = """Vikas Sharma
Test Engineer with 9 years of experience.
Skills: Java, Selenium, TestNG, Oracle SQL, Jenkins.
API testing with Postman collections. Maintained the framework independently.
"""

MANUAL_RESUME = """Priya Singh
Manual tester with 10 years experience in banking projects.
Skills: test case design, UAT coordination, defect triage.
"""


def _screen(text, root):
    return scr.screen_resume(parse_resume(text), load_hiring_standard(root))


def test_strong_resume_proceeds(repo_root):
    result = _screen(STRONG_RESUME, repo_root)
    assert result.experience_state == ExperienceState.PASSED
    assert result.experience_gate_passed
    assert result.decision == Decision.PROCEED
    assert result.score_percent >= 75
    assert not result.reject_signals


def test_experience_gate_blocks_junior(repo_root):
    result = _screen(JUNIOR_RESUME, repo_root)
    assert result.experience_state == ExperienceState.FAILED
    assert not result.experience_gate_passed
    assert result.decision == Decision.DO_NOT_PROCEED
    assert any("below" in s for s in result.reject_signals)


def test_postman_only_api_is_reject_signal(repo_root):
    result = _screen(POSTMAN_RESUME, repo_root)
    assert any("Postman" in s for s in result.reject_signals)
    assert result.decision == Decision.DO_NOT_PROCEED


def test_manual_resume_does_not_proceed(repo_root):
    result = _screen(MANUAL_RESUME, repo_root)
    assert result.decision == Decision.DO_NOT_PROCEED


def test_evidence_levels_are_labeled(repo_root):
    result = _screen(STRONG_RESUME, repo_root)
    mandatory = {e.skill: e for e in result.evidence if e.mandatory}
    assert mandatory["java"].level == EvidenceLevel.EXPLICIT
    assert mandatory["java"].quotes  # grounded in a resume quote
    assert mandatory["java"].evidence_type in {EvidenceType.PROJECT, EvidenceType.QUANTIFIED}
    assert set(mandatory) == {"java", "selenium", "testng_cucumber", "rest_assured",
                              "sql_oracle", "framework", "cicd", "ownership"}


def test_missing_evidence_generates_risks_and_questions(repo_root):
    result = _screen(POSTMAN_RESUME, repo_root)
    assert any("REST Assured" in r for r in result.risks)
    assert result.validation_questions


def test_skills_list_only_scores_lower_than_project_evidence(repo_root):
    """Phase 4: a bare skills-list mention must not earn full credit."""
    rich = _screen(STRONG_RESUME, repo_root)
    thin = _screen(SKILLS_ONLY_RESUME, repo_root)
    thin_mandatory = {e.skill: e for e in thin.evidence if e.mandatory}
    # core skills present only in the skills list are typed as skills_list
    assert thin_mandatory["rest_assured"].evidence_type == EvidenceType.SKILLS_LIST
    assert thin_mandatory["sql_oracle"].evidence_type == EvidenceType.SKILLS_LIST
    # skills-list credit is strictly less than project credit
    assert thin_mandatory["rest_assured"].credit < 0.5
    # thin evidence scores materially lower and does not proceed
    assert thin.score_percent < rich.score_percent
    assert thin.decision != Decision.PROCEED


def test_coverage_is_not_a_perfect_score(repo_root):
    """Evidence coverage reflects evidence strength, not competency."""
    result = _screen(STRONG_RESUME, repo_root)
    assert 75 <= result.score_percent < 100
    project = next(e for e in result.evidence if e.skill == "java")
    listed = next(e for e in result.evidence if e.skill == "testng_cucumber")
    assert project.credit > listed.credit
