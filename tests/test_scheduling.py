"""Scheduling correctness (Phase 13) and 180-minute duration control (Phase 9)."""

from datetime import date

from zume import scheduling as sched


def _build(details: str, today=date(2026, 7, 1)):
    return sched.build_schedule("Test Person", None, details, today=today)


def test_valid_future_180_minute_schedule_is_confirmed():
    record = _build(
        "Date: 2026-07-20\nTime: 10:00 AM\nTimezone: America/New_York\n"
        "Duration: 180 minutes\nInterviewers: Panel\nMeeting: Zoom")
    assert record.timezone == "America/New_York"
    assert record.duration_minutes == 180
    assert record.duration_status == "confirmed"
    assert not record.needs_confirmation
    assert record.validation_issues == []
    assert record.field_sources["date"] == "text"


def test_missing_timezone_requires_confirmation():
    record = _build("Date: 2026-07-20\nTime: 10:00\nDuration: 180 minutes")
    assert record.timezone == ""
    assert record.needs_confirmation
    assert any("Timezone" in i for i in record.validation_issues)


def test_ambiguous_et_timezone_requires_resolution():
    record = _build(
        "Date: 2026-07-20\nTime: 10:00 AM ET\nDuration: 180 minutes")
    assert record.timezone == "ET"
    assert record.needs_confirmation
    assert any("ambiguous" in i.lower() for i in record.validation_issues)


def test_past_date_is_flagged():
    record = _build("Date: 2020-01-01\nTime: 10:00\nTimezone: UTC\nDuration: 180 min")
    assert any("past" in i.lower() for i in record.validation_issues)


def test_ambiguous_date_format_is_flagged():
    record = _build("Date: 03/04/2026\nTime: 10:00\nTimezone: UTC\nDuration: 180 min")
    assert any("ambiguous" in i.lower() for i in record.validation_issues)


def test_impossible_time_is_flagged():
    record = _build("Date: 2026-07-20\nTime: 25:00\nDuration: 180 min\nTimezone: UTC")
    assert any("valid clock time" in i for i in record.validation_issues)


def test_zero_duration_is_flagged():
    record = _build("Date: 2026-07-20\nTime: 10:00\nTimezone: UTC\nDuration: 0 minutes")
    assert any("greater than zero" in i for i in record.validation_issues)


def test_screenshot_alone_is_untrusted():
    record = sched.build_schedule("Test Person", None, None, today=date(2026, 7, 1))
    assert record.needs_confirmation
    assert record.date == ""


def test_duration_parsing_hours_and_minutes():
    assert sched.parse_duration_minutes("1.5 hours") == 90
    assert sched.parse_duration_minutes("45 min") == 45
    assert sched.parse_duration_minutes("nonsense") is None


def test_iana_timezone_is_extracted():
    record = _build(
        "Date: 2026-07-20\nTime: 10:00\nTimezone: America/New_York\nDuration: 180 min")
    assert record.timezone == "America/New_York"
    assert record.field_confidence["timezone"] == "high"


def test_missing_duration_requires_confirmation():
    record = _build("Date: 2026-07-20\nTime: 10:00\nTimezone: UTC")
    assert record.duration_status == "missing"
    assert any("Duration is missing" in i for i in record.validation_issues)


def test_90_minute_schedule_blocks_as_mismatch():
    record = _build("Date: 2026-07-20\nTime: 10:00\nTimezone: UTC\nDuration: 90 minutes")
    assert record.duration_minutes == 90
    assert record.duration_status == "mismatch"
    assert any("standard interview is 180" in i for i in record.validation_issues)


def test_120_minute_schedule_blocks_as_mismatch():
    record = _build("Date: 2026-07-20\nTime: 10:00\nTimezone: UTC\nDuration: 120 minutes")
    assert record.duration_status == "mismatch"
    assert record.needs_confirmation


def test_180_minute_schedule_is_accepted():
    record = _build("Date: 2026-07-20\nTime: 10:00\nTimezone: UTC\nDuration: 180 minutes")
    assert record.duration_status == "confirmed"
    assert record.validation_issues == []


def test_240_minute_schedule_blocks_as_mismatch():
    record = _build("Date: 2026-07-20\nTime: 10:00\nTimezone: UTC\nDuration: 240 minutes")
    assert record.duration_minutes == 240
    assert record.duration_status == "mismatch"
    assert any("standard interview is 180" in i for i in record.validation_issues)
