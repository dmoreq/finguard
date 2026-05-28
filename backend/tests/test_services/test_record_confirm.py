"""Integration: record → confirm via services."""

from __future__ import annotations

import pytest

from actions.db.client import get_db
from actions.db.queries import get_transaction, list_user_transactions
from actions.services.record_transaction import RecordInput, record_transaction
from actions.services.update_transaction import UpdateInput, update_transaction


@pytest.mark.asyncio
async def test_record_then_confirm_persists(db_path) -> None:
    record = await record_transaction(
        RecordInput(
            user_id="user-a",
            amount=42.0,
            category="groceries",
            transaction_date="2026-05-15",
            transaction_type="expense",
        )
    )
    assert record.session is not None
    tx_id = record.session.last_transaction_id
    assert tx_id

    async with get_db() as conn:
        pending = await get_transaction(conn, "user-a", tx_id)
    assert pending is not None
    assert pending.status == "pending_confirmation"

    confirm = await update_transaction(
        UpdateInput(
            user_id="user-a",
            transaction_id=tx_id,
            confirm=True,
        )
    )
    assert confirm.session is not None
    assert confirm.session.confirmation_pending is False

    async with get_db() as conn:
        confirmed = await get_transaction(conn, "user-a", tx_id)
        rows = await list_user_transactions(conn, "user-a")

    assert confirmed is not None
    assert confirmed.status == "confirmed"
    assert any(r.id == tx_id and r.status == "confirmed" for r in rows)
