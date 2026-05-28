"""Create or update confirmed transactions (manual UI CRUD)."""

from __future__ import annotations

from typing import Literal, cast

from pydantic import BaseModel, field_validator

from actions.db.client import get_db
from actions.db.queries import get_transaction, insert_transaction
from actions.db.queries import update_transaction as db_update
from actions.models.transaction import TransactionInsert, TransactionRow
from actions.utils.categories import normalize_category
from actions.utils.dates import parse_relative_date


class CreateTransactionInput(BaseModel):
    user_id: str
    type: Literal["income", "expense"]
    amount: float
    category: str
    description: str | None = None
    transaction_date: str | None = None
    currency: str = "VND"
    timezone: str = "Asia/Ho_Chi_Minh"

    @field_validator("amount")
    @classmethod
    def positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def slug(cls, v: str) -> str:
        return normalize_category(v)


class PatchTransactionInput(BaseModel):
    user_id: str
    transaction_id: str
    type: Literal["income", "expense"] | None = None
    amount: float | None = None
    category: str | None = None
    description: str | None = None
    transaction_date: str | None = None


async def create_confirmed_transaction(input: CreateTransactionInput) -> TransactionRow:
    resolved = parse_relative_date(input.transaction_date, input.timezone)
    tx = TransactionInsert(
        user_id=input.user_id,
        type=cast(Literal["income", "expense", "pending"], input.type),
        amount=input.amount,
        currency=input.currency,
        category=input.category,
        description=input.description,
        transaction_date=resolved.to_date_string(),
        status="confirmed",
        source="manual_form",
    )
    async with get_db() as conn:
        return await insert_transaction(conn, tx)


async def patch_confirmed_transaction(input: PatchTransactionInput) -> TransactionRow | None:
    updates: dict[str, object] = {}
    if input.type is not None:
        updates["type"] = input.type
    if input.amount is not None:
        updates["amount"] = input.amount
    if input.category is not None:
        updates["category"] = normalize_category(input.category)
    if input.description is not None:
        updates["description"] = input.description
    if input.transaction_date is not None:
        updates["transaction_date"] = input.transaction_date
    if not updates:
        async with get_db() as conn:
            return await get_transaction(conn, input.user_id, input.transaction_id)
    async with get_db() as conn:
        return await db_update(conn, input.user_id, input.transaction_id, updates)
