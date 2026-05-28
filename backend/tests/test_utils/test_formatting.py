"""Tests for formatting helpers."""

from decimal import Decimal

import pendulum

from actions.utils.formatting import (
    format_currency,
    format_date_relative,
    format_spending_report,
    format_transaction_summary,
)


def test_format_currency_usd() -> None:
    assert format_currency(45.5, "USD") == "$45.50"


def test_format_currency_unknown_uses_code() -> None:
    assert format_currency(10, "VND") == "VND10.00"


def test_format_date_relative_today() -> None:
    now = pendulum.datetime(2026, 5, 15, tz="UTC")
    dt = pendulum.datetime(2026, 5, 15, 10, 0, 0, tz="UTC")
    assert format_date_relative(dt, now) == "today"


def test_format_transaction_summary() -> None:
    text = format_transaction_summary(12.5, "coffee", "2026-05-15", "USD", "UTC")
    assert "$12.50" in text
    assert "Coffee" in text


def test_format_spending_report() -> None:
    text = format_spending_report(1000, 250, "USD")
    assert "Income: $1,000.00" in text
    assert "Expenses: $250.00" in text
    assert "Net: $750.00" in text


def test_format_currency_accepts_decimal() -> None:
    assert format_currency(Decimal("9.9"), "EUR") == "€9.90"
