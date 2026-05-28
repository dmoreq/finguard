"""Chat session persistence tests."""

from __future__ import annotations

import json

import pytest

from actions.chat.domain.session import ChatSession
from actions.db.client import get_db
from actions.db.queries import clear_chat_sessions, get_chat_session_row, upsert_chat_session


@pytest.mark.asyncio
async def test_upsert_chat_session_round_trip(db_path) -> None:
    session = ChatSession(
        user_id="user-a",
        dialogue_phase="collecting",
        partial_transaction={"amount": 10},
    )
    async with get_db() as conn:
        await upsert_chat_session(conn, "sender-1", "user-a", json.dumps(session.model_dump()))
        row = await get_chat_session_row(conn, "sender-1")

    assert row is not None
    loaded = ChatSession.model_validate(json.loads(row["state_json"]))
    assert loaded.dialogue_phase == "collecting"
    assert loaded.partial_transaction["amount"] == 10


@pytest.mark.asyncio
async def test_clear_chat_sessions(db_path) -> None:
    async with get_db() as conn:
        await upsert_chat_session(conn, "s1", "u1", "{}")
        await clear_chat_sessions(conn)
        row = await get_chat_session_row(conn, "s1")
    assert row is None
