"""Record a pending transaction."""

from __future__ import annotations

from typing import Literal, cast

from loguru import logger
from pydantic import BaseModel, field_validator

from actions.chat.respond.payloads import custom_message
from actions.db.client import get_db
from actions.db.queries import insert_transaction
from actions.models.transaction import TransactionInsert
from actions.services.types import ServiceResult, SessionUpdates
from actions.utils.categories import normalize_category
from actions.utils.dates import parse_relative_date
from actions.utils.formatting import format_transaction_summary


class RecordInput(BaseModel):
    user_id: str
    amount: float
    category: str
    description: str | None = None
    transaction_date: str | None = None
    transaction_type: Literal["income", "expense"] = "expense"
    user_currency: str = "USD"
    user_timezone: str = "UTC"
    ai_confidence: float | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def normalize_category_field(cls, v: str) -> str:
        return normalize_category(v)


async def record_transaction(input: RecordInput) -> ServiceResult:
    resolved_date = parse_relative_date(
        raw=input.transaction_date,
        timezone=input.user_timezone,
    )

    tx_type = cast(Literal["income", "expense", "pending"], input.transaction_type)
    tx = TransactionInsert(
        user_id=input.user_id,
        type=tx_type,
        amount=input.amount,
        currency=input.user_currency,
        category=input.category,
        description=input.description,
        transaction_date=resolved_date.to_date_string(),
        status="pending_confirmation",
        source="manual_chat",
        ai_confidence=input.ai_confidence,
    )

    try:
        async with get_db() as conn:
            result = await insert_transaction(conn, tx)
    except Exception as e:
        logger.exception("transaction_insert_failed", user_id=input.user_id, error=str(e))
        return ServiceResult(
            messages=[{"text": "Sorry, I couldn't save that transaction. Please try again."}]
        )

    amount_fmt = format_transaction_summary(
        input.amount,
        input.category,
        resolved_date.to_date_string(),
        input.user_currency,
        input.user_timezone,
    )

    payload = {
        "type": "transaction_pending",
        "transaction": {
            "id": result.id,
            "type": input.transaction_type,
            "amount": input.amount,
            "currency": input.user_currency,
            "category": input.category,
            "description": input.description,
            "date": resolved_date.to_date_string(),
        },
        "text": f"Got it — {amount_fmt}. Confirm or edit?",
    }

    return ServiceResult(
        messages=[custom_message(payload)],
        session=SessionUpdates(
            confirmation_pending=True,
            last_transaction_id=result.id,
            dialogue_phase="awaiting_confirmation",
            clear_partial=True,
        ),
    )
