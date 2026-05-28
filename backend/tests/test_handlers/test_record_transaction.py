"""Tests for ActionRecordTransaction."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from actions.handlers.record_transaction import ActionRecordTransaction
from actions.models.transaction import TransactionRow


@pytest.mark.asyncio
async def test_record_transaction_happy_path(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    row = TransactionRow(
        id="tx-new",
        user_id="user-1",
        type="expense",
        amount=45.0,
        currency="USD",
        category="groceries",
        description=None,
        transaction_date="2026-05-27",
        status="pending_confirmation",
        source="manual_chat",
        ai_confidence=None,
        created_at=datetime(2026, 5, 27, 12, 0, 0),
        updated_at=datetime(2026, 5, 27, 12, 0, 0),
    )

    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.record_transaction.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.record_transaction.insert_transaction",
            new_callable=AsyncMock,
            return_value=row,
        ),
        patch(
            "actions.handlers.record_transaction.parse_relative_date",
            return_value=MagicMock(to_date_string=lambda: "2026-05-27"),
        ),
    ):
        events = await ActionRecordTransaction().run(mock_dispatcher, mock_tracker, {})

    assert len(events) == 2
    mock_dispatcher.utter_message.assert_called_once()
    payload = mock_dispatcher.utter_message.call_args.kwargs["json_message"]
    assert payload["type"] == "transaction_pending"
    assert payload["transaction"]["id"] == "tx-new"


@pytest.mark.asyncio
async def test_record_transaction_rejects_invalid_amount(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_tracker.get_slot.side_effect = lambda name: {
        "amount": -5.0,
        "category": "groceries",
        "user_id": "user-1",
        "user_currency": "USD",
        "user_timezone": "UTC",
    }.get(name)

    events = await ActionRecordTransaction().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "couldn't process" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()
