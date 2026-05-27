"""Tests for ActionUpdateTransaction."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from actions.handlers.update_transaction import ActionUpdateTransaction
from actions.models.transaction import TransactionRow


@pytest.mark.asyncio
async def test_update_transaction_confirms_pending(
    mock_dispatcher: MagicMock,
    pending_tracker: MagicMock,
    sample_transaction_row: TransactionRow,
) -> None:
    confirmed = sample_transaction_row.model_copy(update={"status": "confirmed"})

    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.update_transaction.get_supabase", return_value=mock_cm),
        patch(
            "actions.handlers.update_transaction.get_transaction",
            new_callable=AsyncMock,
            return_value=sample_transaction_row,
        ),
        patch(
            "actions.handlers.update_transaction.update_transaction",
            new_callable=AsyncMock,
            return_value=confirmed,
        ),
    ):
        events = await ActionUpdateTransaction().run(mock_dispatcher, pending_tracker, {})

    assert len(events) == 2
    mock_dispatcher.utter_message.assert_called_once()
    assert "Saved" in mock_dispatcher.utter_message.call_args.kwargs["text"]


@pytest.mark.asyncio
async def test_update_transaction_without_pending_returns_message(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    events = await ActionUpdateTransaction().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "no transaction" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()
