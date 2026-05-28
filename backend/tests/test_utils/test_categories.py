"""Tests for category normalization."""

from actions.utils.categories import normalize_category


def test_normalize_category_lowercases_and_trims() -> None:
    assert normalize_category("  Groceries  ") == "groceries"


def test_normalize_category_preserves_slashes() -> None:
    assert normalize_category("Dining Out") == "dining out"
