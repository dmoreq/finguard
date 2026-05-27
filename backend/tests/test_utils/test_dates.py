"""Tests for relative date and period parsing."""

from __future__ import annotations

import pendulum
import pytest

from actions.utils.dates import parse_relative_date, period_to_date_range


@pytest.fixture
def frozen_now(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fix 'now' to 2026-05-27 noon UTC for deterministic tests."""
    fixed = pendulum.datetime(2026, 5, 27, 12, 0, 0, tz="UTC")
    monkeypatch.setattr(
        "actions.utils.dates.pendulum.now",
        lambda tz=None: fixed if tz is None else fixed.in_timezone(tz),
    )


def test_parse_relative_date_defaults_to_today(frozen_now: None) -> None:
    result = parse_relative_date(None, timezone="UTC")
    assert result.to_date_string() == "2026-05-27"


def test_parse_relative_date_yesterday(frozen_now: None) -> None:
    result = parse_relative_date("yesterday", timezone="UTC")
    assert result.to_date_string() == "2026-05-26"


def test_parse_relative_date_iso_string(frozen_now: None) -> None:
    result = parse_relative_date("2026-05-20", timezone="UTC")
    assert result.to_date_string() == "2026-05-20"


def test_parse_relative_date_invalid_falls_back_to_today(frozen_now: None) -> None:
    result = parse_relative_date("not-a-real-date", timezone="UTC")
    assert result.to_date_string() == "2026-05-27"


def test_period_to_date_range_this_month(frozen_now: None) -> None:
    start, end = period_to_date_range("this_month", timezone="UTC")
    assert start == "2026-05-01"
    assert end == "2026-05-27"


def test_period_to_date_range_last_month(frozen_now: None) -> None:
    start, end = period_to_date_range("last_month", timezone="UTC")
    assert start == "2026-04-01"
    assert end == "2026-04-30"


def test_period_to_date_range_unknown_defaults_to_month(frozen_now: None) -> None:
    start, end = period_to_date_range("unknown_period", timezone="UTC")
    assert start == "2026-05-01"
    assert end == "2026-05-27"
