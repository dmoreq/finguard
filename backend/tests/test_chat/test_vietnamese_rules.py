"""Vietnamese rule extraction and pending reply tests."""

from __future__ import annotations

import pytest

from actions.chat.extraction.rules import build_edit_fields, build_transaction_fields, parse_amount
from actions.chat.routing.pending import PendingIntentClassifier


def test_vnd_triệu() -> None:
    assert parse_amount("chi tiêu 1 triệu tiền nhà") == 1_000_000.0


def test_vnd_nghìn() -> None:
    assert parse_amount("tiêu 100 nghìn đi chợ") == 100_000.0


def test_vnd_dotted() -> None:
    assert parse_amount("trả 500.000đ xăng") == 500_000.0


def test_vnd_ngàn() -> None:
    assert parse_amount("chi 80 ngàn cà phê") == 80_000.0


def test_vietnamese_expense_fields() -> None:
    fields = build_transaction_fields("Chi tiêu 80k cà phê sáng nay")
    assert fields["amount"] == 80_000.0
    assert fields["category"] == "dining"
    assert fields["transaction_type"] == "expense"


def test_vietnamese_income_fields() -> None:
    fields = build_transaction_fields("Nhận lương 15 triệu")
    assert fields["amount"] == 15_000_000.0
    assert fields["transaction_type"] == "income"


def test_vietnamese_edit_amount() -> None:
    fields = build_edit_fields("Sửa thành 60k")
    assert fields["amount"] == 60_000.0


def test_vietnamese_edit_category() -> None:
    fields = build_edit_fields("Đổi danh mục thành ăn uống")
    assert fields["category"] == "dining"


@pytest.mark.parametrize(
    "text,intent",
    [
        ("Xác nhận", "manage_confirm"),
        ("Hủy", "manage_discard"),
        ("Sửa thành 60k", "manage_edit"),
    ],
)
def test_vietnamese_pending_replies(text: str, intent: str) -> None:
    from actions.chat.domain.intents import Intent

    result = PendingIntentClassifier().classify(text, confirmation_pending=True)
    assert result.intent == Intent(intent)
