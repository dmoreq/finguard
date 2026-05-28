"""Tests for ActionGetBalance."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from actions.handlers.get_balance import ActionGetBalance
from actions.models.transaction import BalanceSummary


@pytest.mark.asyncio
async def test_get_balance_happy_path(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    balance = BalanceSummary(
        income=1000.0,
        expenses=450.0,
        net=550.0,
        currency="USD",
        period="this_month",
    )

    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.get_balance.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.get_balance.get_balance_summary",
            new_callable=AsyncMock,
            return_value=balance,
        ),
    ):
        events = await ActionGetBalance().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    payload = mock_dispatcher.utter_message.call_args.kwargs["json_message"]
    assert payload["type"] == "balance"
    assert payload["data"]["income"] == 1000.0
    assert payload["data"]["expenses"] == 450.0
    assert payload["data"]["net"] == 550.0
    assert payload["data"]["sentiment"] == "positive"
    assert "✓" in payload["text"]


@pytest.mark.asyncio
async def test_get_balance_negative_net(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    balance = BalanceSummary(
        income=200.0,
        expenses=350.0,
        net=-150.0,
        currency="USD",
        period="this_month",
    )

    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.get_balance.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.get_balance.get_balance_summary",
            new_callable=AsyncMock,
            return_value=balance,
        ),
    ):
        events = await ActionGetBalance().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    payload = mock_dispatcher.utter_message.call_args.kwargs["json_message"]
    assert payload["data"]["sentiment"] == "negative"
    assert "✗" in payload["text"]


@pytest.mark.asyncio
async def test_get_balance_query_failed(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.get_balance.get_db", return_value=mock_cm),
        patch(
            "actions.handlers.get_balance.get_balance_summary",
            new_callable=AsyncMock,
            side_effect=RuntimeError("db down"),
        ),
    ):
        events = await ActionGetBalance().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "couldn't fetch" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()
