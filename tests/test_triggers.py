from zume.cli import match_trigger


def test_exact_triggers_map_to_workflows(repo_root):
    assert match_trigger(repo_root, "Filter Resume – Automation Hiring") == "filter_resume"
    assert match_trigger(repo_root, "Interview Prep – Automation Hiring") == "interview_prep"
    assert match_trigger(repo_root, "Schedule Interview – Automation Hiring") == "schedule_interview"
    assert match_trigger(repo_root, "Interview Feedback – Automation Hiring") == "interview_feedback"


def test_trigger_tolerates_dash_and_case_variants(repo_root):
    assert match_trigger(repo_root, "filter resume - automation hiring") == "filter_resume"
    assert match_trigger(repo_root, "  Interview   Prep – Automation Hiring ") == "interview_prep"


def test_unknown_trigger_returns_none(repo_root):
    assert match_trigger(repo_root, "Make Coffee – Automation Hiring") is None
    assert match_trigger(repo_root, "Filter Resume") is None
