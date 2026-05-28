"""TransactionDraft value object tests."""

from __future__ import annotations

from actions.chat.domain.slots import TransactionDraft, prompt_for_missing_field
from actions.services.profile import UserProfile


def test_missing_required_fields() -> None:
    draft = TransactionDraft(fields={"transaction_type": "expense"})
    assert draft.missing_required() == ["amount", "category"]


def test_to_record_input() -> None:
    draft = TransactionDraft(
        fields={"amount": 12.5, "category": "coffee", "transaction_type": "expense"}
    )
    profile = UserProfile(user_id="u1", currency="USD", timezone="UTC")
    record = draft.to_record_input(profile)
    assert record.amount == 12.5
    assert record.category == "coffee"


def test_prompt_for_category_income() -> None:
    msg = prompt_for_missing_field("category", "income", "en")
    assert "income source" in msg
