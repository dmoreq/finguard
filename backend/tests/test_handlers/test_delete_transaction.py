"""Tests for ActionDeleteTransaction."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from actions.handlers.delete_transaction import ActionDeleteTransaction


@pytest.mark.asyncio
async def test_delete_transaction_happy_path(
    mock_dispatcher: MagicMock,
    pending_tracker: MagicMock,
) -> None:
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.delete_transaction.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.delete_transaction.delete_transaction",
            new_callable=AsyncMock,
            return_value=True,
        ),
    ):
        events = await ActionDeleteTransaction().run(mock_dispatcher, pending_tracker, {})

    assert len(events) == 2
    mock_dispatcher.utter_message.assert_called_once()
    assert "discarded" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()


@pytest.mark.asyncio
async def test_delete_transaction_without_pending_returns_message(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    events = await ActionDeleteTransaction().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "no transaction" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()


@pytest.mark.asyncio
async def test_delete_transaction_not_found(
    mock_dispatcher: MagicMock,
    pending_tracker: MagicMock,
) -> None:
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.delete_transaction.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.delete_transaction.delete_transaction",
            new_callable=AsyncMock,
            return_value=False,
        ),
    ):
        events = await ActionDeleteTransaction().run(mock_dispatcher, pending_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "couldn't find" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()


@pytest.mark.asyncio
async def test_delete_transaction_db_error(
    mock_dispatcher: MagicMock,
    pending_tracker: MagicMock,
) -> None:
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.delete_transaction.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.delete_transaction.delete_transaction",
            new_callable=AsyncMock,
            side_effect=RuntimeError("db down"),
        ),
    ):
        events = await ActionDeleteTransaction().run(mock_dispatcher, pending_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "couldn't delete" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()
