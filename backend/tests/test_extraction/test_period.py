"""Rule-based period and report hint extraction."""

from __future__ import annotations

from actions.chat.extraction.period import (
    parse_category_hint,
    parse_period_from_text,
    prior_period,
    wants_trend_comparison,
)


def test_parse_period_english_this_month() -> None:
    assert parse_period_from_text("what is my balance this month?") == "this_month"


def test_parse_period_vietnamese_last_month() -> None:
    assert parse_period_from_text("số dư tháng trước") == "last_month"


def test_parse_period_defaults_when_no_match() -> None:
    assert parse_period_from_text("hello") == "this_month"
    assert parse_period_from_text("hello", default="last_7d") == "last_7d"


def test_parse_period_ytd() -> None:
    assert parse_period_from_text("spending from từ đầu năm") == "ytd"


def test_parse_category_hint_vietnamese_dining() -> None:
    assert parse_category_hint("chi tiêu ăn uống tháng này") == "dining"


def test_parse_category_hint_english_groceries() -> None:
    assert parse_category_hint("groceries spending") == "groceries"


def test_wants_trend_comparison() -> None:
    assert wants_trend_comparison("spending trend this month") is True
    assert wants_trend_comparison("so với tháng trước") is True
    assert wants_trend_comparison("balance this month") is False


def test_prior_period_maps_this_month_to_last_month() -> None:
    assert prior_period("this_month") == "last_month"
    assert prior_period("last_7d") == "last_7d"
