"""Tests for ActionListTransactions."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from actions.handlers.list_transactions import ActionListTransactions
from actions.models.transaction import TransactionRow


@pytest.mark.asyncio
async def test_list_transactions_happy_path(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    transactions = [
        TransactionRow(
            id="tx-1",
            user_id="user-1",
            type="expense",
            amount=45.0,
            currency="USD",
            category="groceries",
            description=None,
            transaction_date="2026-05-27",
            status="confirmed",
            source="manual_chat",
            ai_confidence=None,
            created_at=datetime(2026, 5, 27, 12, 0, 0),
            updated_at=datetime(2026, 5, 27, 12, 0, 0),
        ),
        TransactionRow(
            id="tx-2",
            user_id="user-1",
            type="income",
            amount=1000.0,
            currency="USD",
            category="salary",
            description=None,
            transaction_date="2026-05-26",
            status="pending_confirmation",
            source="manual_chat",
            ai_confidence=None,
            created_at=datetime(2026, 5, 26, 12, 0, 0),
            updated_at=datetime(2026, 5, 26, 12, 0, 0),
        ),
    ]

    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.list_transactions.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.list_transactions.list_transactions",
            new_callable=AsyncMock,
            return_value=transactions,
        ),
    ):
        events = await ActionListTransactions().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    payload = mock_dispatcher.utter_message.call_args.kwargs["json_message"]
    assert payload["type"] == "transaction_list"
    assert payload["data"]["count"] == 2
    assert payload["data"]["transactions"][0]["id"] == "tx-1"
    assert payload["data"]["transactions"][1]["type"] == "income"
    assert "Recent transactions" in payload["text"]
    assert "✓" in payload["text"]
    assert "⏳" in payload["text"]


@pytest.mark.asyncio
async def test_list_transactions_empty(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.list_transactions.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.list_transactions.list_transactions",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        events = await ActionListTransactions().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "no transactions found" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()


@pytest.mark.asyncio
async def test_list_transactions_empty_with_category_filter(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_tracker.get_slot.side_effect = lambda name: {
        "user_id": "user-1",
        "user_timezone": "UTC",
        "query_period": "this_month",
        "query_category": "dining",
    }.get(name)

    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.list_transactions.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.list_transactions.list_transactions",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        events = await ActionListTransactions().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert (
        "no dining transactions found"
        in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()
    )


@pytest.mark.asyncio
async def test_list_transactions_query_failed(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.list_transactions.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.list_transactions.list_transactions",
            new_callable=AsyncMock,
            side_effect=RuntimeError("db down"),
        ),
    ):
        events = await ActionListTransactions().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "couldn't fetch" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()
