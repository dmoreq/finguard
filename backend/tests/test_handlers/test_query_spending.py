"""Tests for ActionQuerySpending."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from actions.handlers.query_spending import ActionQuerySpending
from actions.models.transaction import SpendingByCategory


@pytest.mark.asyncio
async def test_query_spending_happy_path(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    spending = [
        SpendingByCategory(category="groceries", total=300.0, count=5),
        SpendingByCategory(category="dining", total=200.0, count=3),
    ]

    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.query_spending.get_supabase", return_value=mock_cm),
        patch(
            "actions.handlers.query_spending.get_spending_by_category",
            new_callable=AsyncMock,
            return_value=spending,
        ),
    ):
        events = await ActionQuerySpending().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    payload = mock_dispatcher.utter_message.call_args.kwargs["json_message"]
    assert payload["type"] == "spending_report"
    assert payload["data"]["total"] == 500.0
    assert payload["data"]["currency"] == "USD"
    assert payload["data"]["period"] == "this_month"
    assert len(payload["data"]["by_category"]) == 2
    assert "Groceries" in payload["text"]
    assert "Total:" in payload["text"]


@pytest.mark.asyncio
async def test_query_spending_empty(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.query_spending.get_supabase", return_value=mock_cm),
        patch(
            "actions.handlers.query_spending.get_spending_by_category",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        events = await ActionQuerySpending().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "no expenses found" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()


@pytest.mark.asyncio
async def test_query_spending_empty_with_category_filter(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_tracker.get_slot.side_effect = lambda name: {
        "user_id": "user-1",
        "user_currency": "USD",
        "user_timezone": "UTC",
        "query_period": "this_month",
        "query_category": "dining",
    }.get(name)

    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.query_spending.get_supabase", return_value=mock_cm),
        patch(
            "actions.handlers.query_spending.get_spending_by_category",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        events = await ActionQuerySpending().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    text = mock_dispatcher.utter_message.call_args.kwargs["text"].lower()
    assert "no expenses found" in text
    assert "dining" in text


@pytest.mark.asyncio
async def test_query_spending_query_failed(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    with (
        patch("actions.handlers.query_spending.get_supabase", return_value=mock_cm),
        patch(
            "actions.handlers.query_spending.get_spending_by_category",
            new_callable=AsyncMock,
            side_effect=RuntimeError("db down"),
        ),
    ):
        events = await ActionQuerySpending().run(mock_dispatcher, mock_tracker, {})

    assert events == []
    mock_dispatcher.utter_message.assert_called_once()
    assert "couldn't fetch" in mock_dispatcher.utter_message.call_args.kwargs["text"].lower()
