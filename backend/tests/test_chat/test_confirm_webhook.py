"""Webhook: record → confirm flow."""

from __future__ import annotations

import pytest

from actions.chat.session import clear_sessions
from actions.chat.webhook import handle_webhook
from actions.db.client import get_db
from actions.db.queries import get_transaction


@pytest.fixture(autouse=True)
async def _clear():
    await clear_sessions()
    yield
    await clear_sessions()


@pytest.mark.asyncio
async def test_record_then_confirm(db_path) -> None:
    sender = "user-confirm-flow"
    first = await handle_webhook(
        {
            "sender": sender,
            "message": "spent $30 on groceries",
            "metadata": {"user_id": "user-a"},
        }
    )
    assert first[0].get("custom", {}).get("type") == "transaction_pending"
    tx_id = first[0]["custom"]["transaction"]["id"]

    second = await handle_webhook(
        {
            "sender": sender,
            "message": "confirm",
            "metadata": {"user_id": "user-a"},
        }
    )
    assert "Saved" in second[0].get("text", "")

    async with get_db() as conn:
        row = await get_transaction(conn, "user-a", tx_id)
    assert row is not None
    assert row.status == "confirmed"
