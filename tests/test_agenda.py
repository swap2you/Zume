"""Phase 4 — 180-minute agenda and 20-minute knockout invariants."""

from zume import agenda as agenda_lib
from zume import config as cfg
from zume import questions as q_lib


def test_agenda_totals_exactly_180_minutes():
    segments = agenda_lib.build_agenda()
    assert sum(s.minutes for s in segments) == 180


def test_knockout_is_first_and_20_minutes():
    segments = agenda_lib.build_agenda()
    assert segments[0].minutes == 20
    assert "knockout" in segments[0].title.lower()


def test_final_close_is_fixed_five_minutes():
    segments = agenda_lib.build_agenda()
    assert segments[-1].minutes == 5


def test_agenda_validation_passes():
    segments = agenda_lib.build_agenda()
    assert agenda_lib.validate_agenda(segments, agenda_lib.KNOCKOUT_MINUTES) == []


def test_knockout_items_all_have_recommended_answers(repo_root):
    areas = q_lib.load_library(cfg.load_question_library(repo_root))
    knockout = agenda_lib.build_knockout(areas)
    assert len(knockout) >= 5
    for item in knockout:
        assert item.question
        assert item.recommended_answer
