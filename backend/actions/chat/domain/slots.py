"""Transaction slot filling helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from actions.services.profile import UserProfile
from actions.services.record_transaction import RecordInput
from actions.utils.i18n import t


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
            user_locale=profile.normalized_locale,
        )


def prompt_for_missing_field(field: str, transaction_type: str, locale: str = "vi") -> str:
    if field == "amount":
        return t("missing_amount", locale)
    if field == "category":
        kind = (
            t("income_source", locale)
            if transaction_type == "income"
            else t("category_kind", locale)
        )
        template = t("missing_category", locale)
        if "{kind}" in template:
            return template.format(kind=kind)
        return template
    return t("missing_more", locale)
