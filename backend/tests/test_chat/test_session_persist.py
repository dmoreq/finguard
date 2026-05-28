"""Session store integration tests."""

from __future__ import annotations

import pytest

from actions.chat.session_store import SqliteSessionStore, clear_sessions
from actions.chat.webhook import handle_webhook
from actions.db.client import get_db
from actions.db.queries import get_chat_session_row


@pytest.fixture(autouse=True)
async def _reset_sessions():
    await clear_sessions()
    yield
    await clear_sessions()


@pytest.mark.asyncio
async def test_pending_survives_new_store_instance(db_path) -> None:
    sender = "persist-user"
    first = await handle_webhook(
        {
            "sender": sender,
            "message": "spent $25 on dining",
            "metadata": {"user_id": "user-a"},
        }
    )
    assert first[0].get("custom", {}).get("type") == "transaction_pending"

    store = SqliteSessionStore()
    session = await store.get(sender, "user-a")
    assert session.confirmation_pending is True
    assert session.last_transaction_id is not None

    second = await handle_webhook(
        {
            "sender": sender,
            "message": "confirm",
            "metadata": {"user_id": "user-a"},
        }
    )
    assert "Saved" in second[0].get("text", "")


@pytest.mark.asyncio
async def test_session_row_written_to_sqlite(db_path) -> None:
    sender = "sqlite-sender"
    await handle_webhook(
        {"sender": sender, "message": "hello", "metadata": {"user_id": "user-a"}},
    )
    async with get_db() as conn:
        row = await get_chat_session_row(conn, sender)
    assert row is not None
