"""Webhook integration: discard and edit pending transactions (CP-3)."""

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


async def _record_pending(sender: str, user_id: str = "user-pending") -> str:
    messages = await handle_webhook(
        {
            "sender": sender,
            "message": "spent $30 on groceries",
            "metadata": {"user_id": user_id},
        }
    )
    custom = messages[0].get("custom")
    assert custom is not None
    assert custom["type"] == "transaction_pending"
    return custom["transaction"]["id"]


@pytest.mark.asyncio
async def test_webhook_discard_pending(db_path) -> None:
    sender = "user-discard-flow"
    user_id = "user-discard"
    tx_id = await _record_pending(sender, user_id)

    messages = await handle_webhook(
        {
            "sender": sender,
            "message": "discard",
            "metadata": {"user_id": user_id},
        }
    )
    assert (
        "discarded" in messages[0].get("text", "").lower()
        or "hủy" in messages[0].get("text", "").lower()
    )

    async with get_db() as conn:
        row = await get_transaction(conn, user_id, tx_id)
    assert row is not None
    assert row.status == "discarded"


@pytest.mark.asyncio
async def test_webhook_discard_clears_session(db_path) -> None:
    sender = "user-discard-session"
    user_id = "user-discard-session"
    tx_id = await _record_pending(sender, user_id)

    await handle_webhook(
        {
            "sender": sender,
            "message": "cancel",
            "metadata": {"user_id": user_id},
        }
    )

    async with get_db() as conn:
        row = await get_transaction(conn, user_id, tx_id)
    assert row is not None
    assert row.status == "discarded"

    follow_up = await handle_webhook(
        {
            "sender": sender,
            "message": "spent $12 on coffee",
            "metadata": {"user_id": user_id},
        }
    )
    custom = follow_up[0].get("custom")
    assert custom is not None
    assert custom["type"] == "transaction_pending"
    assert custom["transaction"]["id"] != tx_id


@pytest.mark.asyncio
async def test_webhook_edit_pending_amount(db_path) -> None:
    sender = "user-edit-amount"
    user_id = "user-edit-amount"
    tx_id = await _record_pending(sender, user_id)

    messages = await handle_webhook(
        {
            "sender": sender,
            "message": "change amount to 50",
            "metadata": {"user_id": user_id},
        }
    )
    custom = messages[0].get("custom")
    assert custom is not None
    assert custom["type"] == "transaction_pending"
    assert custom["transaction"]["amount"] == 50.0
    assert (
        "confirm" in custom.get("text", "").lower() or "xác nhận" in custom.get("text", "").lower()
    )

    async with get_db() as conn:
        row = await get_transaction(conn, user_id, tx_id)
    assert row is not None
    assert row.status == "pending_confirmation"
    assert float(row.amount) == 50.0


@pytest.mark.asyncio
async def test_webhook_edit_pending_category(db_path) -> None:
    sender = "user-edit-category"
    user_id = "user-edit-category"
    tx_id = await _record_pending(sender, user_id)

    messages = await handle_webhook(
        {
            "sender": sender,
            "message": "change category to dining",
            "metadata": {"user_id": user_id},
        }
    )
    custom = messages[0].get("custom")
    assert custom is not None
    assert custom["transaction"]["category"] == "dining"

    async with get_db() as conn:
        row = await get_transaction(conn, user_id, tx_id)
    assert row is not None
    assert row.category == "dining"
    assert row.status == "pending_confirmation"


@pytest.mark.asyncio
async def test_webhook_edit_without_fields_prompts_user(db_path) -> None:
    sender = "user-edit-vague"
    user_id = "user-edit-vague"
    await _record_pending(sender, user_id)

    messages = await handle_webhook(
        {
            "sender": sender,
            "message": "edit",
            "metadata": {"user_id": user_id},
        }
    )
    text = messages[0].get("text", "")
    assert (
        "change" in text.lower()
        or "what should" in text.lower()
        or "sửa" in text.lower()
        or "sua" in text.lower()
    )
    assert messages[0].get("custom") is None
