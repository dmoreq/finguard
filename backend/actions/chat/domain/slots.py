"""Transaction slot filling helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from actions.services.profile import UserProfile
from actions.services.record_transaction import RecordInput


@dataclass(frozen=True)
class TransactionDraft:
    """Merged partial transaction fields during collection."""

    fields: dict[str, Any]

    @classmethod
    def merge(cls, partial: dict[str, Any], new_fields: dict[str, Any]) -> TransactionDraft:
        return cls(fields={**partial, **new_fields})

    @property
    def transaction_type(self) -> str:
        return str(self.fields.get("transaction_type", "expense"))

    def missing_required(self) -> list[str]:
        missing: list[str] = []
        if not self.fields.get("amount"):
            missing.append("amount")
        if not self.fields.get("category"):
            missing.append("category")
        return missing

    def to_record_input(self, profile: UserProfile) -> RecordInput:
        tx_type = self.transaction_type
        return RecordInput(
            user_id=profile.user_id,
            amount=float(self.fields["amount"]),
            category=str(self.fields["category"]),
            description=self.fields.get("description"),
            transaction_date=self.fields.get("transaction_date"),
            transaction_type=tx_type,  # type: ignore[arg-type]
            user_currency=profile.currency,
            user_timezone=profile.timezone,
        )


def prompt_for_missing_field(field: str, transaction_type: str) -> str:
    if field == "amount":
        return "How much was it? (e.g. 45 or $12.50)"
    if field == "category":
        kind = "income source" if transaction_type == "income" else "category"
        return f"What {kind} was that? (e.g. groceries, dining, salary)"
    return "Could you tell me a bit more?"
