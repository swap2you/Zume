"""Phase 13 — scheduling correctness."""

from datetime import date

from zume import scheduling as sched


def _build(details: str, today=date(2026, 7, 1)):
    return sched.build_schedule("Test Person", None, details, today=today)


def test_valid_future_schedule_is_confirmed():
    record = _build(
        "Date: 2026-07-20\nTime: 10:00 AM ET\nDuration: 90 minutes\n"
        "Interviewers: Panel\nMeeting: Zoom")
    assert record.timezone == "ET"
    assert not record.needs_confirmation
    assert record.validation_issues == []
    assert record.field_sources["date"] == "text"
    assert record.field_confidence["timezone"] == "medium"


def test_missing_timezone_requires_confirmation():
    record = _build("Date: 2026-07-20\nTime: 10:00\nDuration: 60 minutes")
    assert record.timezone == ""
    assert record.needs_confirmation
    assert any("Timezone" in i for i in record.validation_issues)


def test_past_date_is_flagged():
    record = _build("Date: 2020-01-01\nTime: 10:00 ET\nDuration: 60 min")
    assert any("past" in i.lower() for i in record.validation_issues)


def test_ambiguous_date_format_is_flagged():
    record = _build("Date: 03/04/2026\nTime: 10:00 ET\nDuration: 60 min")
    assert any("ambiguous" in i.lower() for i in record.validation_issues)


def test_impossible_time_is_flagged():
    record = _build("Date: 2026-07-20\nTime: 25:00\nDuration: 60 min\nTimezone: UTC")
    assert any("valid clock time" in i for i in record.validation_issues)


def test_zero_duration_is_flagged():
    record = _build("Date: 2026-07-20\nTime: 10:00 ET\nDuration: 0 minutes")
    assert any("greater than zero" in i for i in record.validation_issues)


def test_screenshot_alone_is_untrusted():
    # No details -> everything missing -> must require confirmation.
    record = sched.build_schedule("Test Person", None, None, today=date(2026, 7, 1))
    assert record.needs_confirmation
    assert record.date == ""


def test_duration_parsing_hours_and_minutes():
    assert sched.parse_duration_minutes("1.5 hours") == 90
    assert sched.parse_duration_minutes("45 min") == 45
    assert sched.parse_duration_minutes("nonsense") is None


def test_iana_timezone_is_extracted():
    record = _build(
        "Date: 2026-07-20\nTime: 10:00\nTimezone: America/New_York\nDuration: 60 min")
    assert record.timezone == "America/New_York"
    assert record.field_confidence["timezone"] == "high"
