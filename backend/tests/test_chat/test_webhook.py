"""Chat webhook tests."""

from __future__ import annotations

import pytest

from actions.chat.session import clear_sessions
from actions.chat.webhook import handle_webhook


@pytest.fixture(autouse=True)
async def _clear():
    await clear_sessions()
    yield
    await clear_sessions()


@pytest.mark.asyncio
async def test_webhook_record_expense(db_path) -> None:
    messages = await handle_webhook(
        {
            "sender": "user-a",
            "message": "spent $18 on dining for lunch",
            "metadata": {"user_id": "user-a"},
        }
    )
    assert len(messages) >= 1
    custom = messages[0].get("custom")
    assert custom is not None
    assert custom.get("type") == "transaction_pending"
    tx = custom.get("transaction")
    assert tx is not None
    assert tx.get("amount") == 18


@pytest.mark.asyncio
async def test_webhook_chitchat() -> None:
    messages = await handle_webhook(
        {"sender": "u1", "message": "hello", "metadata": {"user_id": "u1"}}
    )
    assert messages[0].get("text")
