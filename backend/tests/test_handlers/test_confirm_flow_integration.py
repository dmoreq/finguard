"""Integration: record → confirm persists in SQLite."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from actions.db.queries import get_transaction, list_user_transactions
from actions.handlers.record_transaction import ActionRecordTransaction
from actions.handlers.update_transaction import ActionUpdateTransaction


@pytest.mark.asyncio
async def test_record_then_confirm_persists(db_path, mock_dispatcher: MagicMock) -> None:
    tracker = MagicMock()
    tracker.active_flow_metadata = {"transaction_type": "expense"}

    def get_slot(name: str):
        return {
            "amount": 42.0,
            "category": "groceries",
            "description": None,
            "transaction_date": "2026-05-15",
            "user_id": "user-a",
            "user_currency": "USD",
            "user_timezone": "UTC",
            "ai_confidence": None,
        }.get(name)

    tracker.get_slot.side_effect = get_slot

    record_events = await ActionRecordTransaction().run(mock_dispatcher, tracker, {})
    tx_id_slot = next(
        e
        for e in record_events
        if e.get("event") == "slot" and e.get("name") == "last_transaction_id"
    )
    tx_id = tx_id_slot["value"]

    from actions.db.client import get_db

    async with get_db() as conn:
        pending = await get_transaction(conn, "user-a", tx_id)
    assert pending is not None
    assert pending.status == "pending_confirmation"

    confirm_tracker = MagicMock()

    def confirm_slots(name: str):
        return {
            "confirmation_pending": True,
            "last_transaction_id": tx_id,
            "user_id": "user-a",
            "amount": 42.0,
            "category": "groceries",
            "description": None,
            "transaction_date": "2026-05-15",
            "user_currency": "USD",
            "user_timezone": "UTC",
        }.get(name)

    confirm_tracker.get_slot.side_effect = confirm_slots

    await ActionUpdateTransaction().run(mock_dispatcher, confirm_tracker, {})

    async with get_db() as conn:
        confirmed = await get_transaction(conn, "user-a", tx_id)
        rows = await list_user_transactions(conn, "user-a")

    assert confirmed is not None
    assert confirmed.status == "confirmed"
    assert any(r.id == tx_id and r.status == "confirmed" for r in rows)
