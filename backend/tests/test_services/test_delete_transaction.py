"""Discard pending transaction service."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from actions.db.client import get_db
from actions.db.queries import insert_transaction
from actions.models.transaction import TransactionInsert
from actions.services.delete_transaction import DeleteInput, delete_transaction


@pytest.mark.asyncio
async def test_delete_transaction_marks_discarded_and_clears_session(db_path) -> None:
    async with get_db() as conn:
        row = await insert_transaction(
            conn,
            TransactionInsert(
                user_id="user-discard",
                type="expense",
                amount=30.0,
                category="groceries",
                transaction_date="2026-05-20",
                status="pending_confirmation",
            ),
        )

    result = await delete_transaction(
        DeleteInput(user_id="user-discard", transaction_id=row.id, user_locale="en")
    )

    assert result.session is not None
    assert result.session.confirmation_pending is False
    assert result.session.last_transaction_id is None
    assert result.session.dialogue_phase == "idle"
    assert "discarded" in result.messages[0]["text"].lower()

    async with get_db() as conn:
        from actions.db.queries import get_transaction

        updated = await get_transaction(conn, "user-discard", row.id)
    assert updated is not None
    assert updated.status == "discarded"


@pytest.mark.asyncio
async def test_delete_transaction_not_found_returns_message(db_path) -> None:
    result = await delete_transaction(
        DeleteInput(user_id="user-missing", transaction_id="tx-missing", user_locale="en")
    )
    assert result.session is None
    assert "couldn't find" in result.messages[0]["text"].lower()


@pytest.mark.asyncio
async def test_delete_transaction_db_error_returns_discard_error(db_path) -> None:
    with patch("actions.services.delete_transaction.get_db") as mock_get_db:
        mock_get_db.side_effect = RuntimeError("db down")
        result = await delete_transaction(
            DeleteInput(user_id="user-x", transaction_id="tx-x", user_locale="vi")
        )
    assert result.session is None
    assert "Sorry" in result.messages[0]["text"] or "Xin lỗi" in result.messages[0]["text"]
