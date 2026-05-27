"""Tests for ActionSessionStart."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rasa_sdk.events import SlotSet

from actions.handlers.session_start import ActionSessionStart


def _mock_profile_client(
    profile_data: dict | None,
    *,
    execute_side_effect: Exception | None = None,
) -> AsyncMock:
    mock_client = MagicMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client
    mock_cm.__aexit__.return_value = None

    mock_execute = AsyncMock(
        return_value=MagicMock(data=profile_data),
        side_effect=execute_side_effect,
    )
    chain = mock_client.table.return_value.select.return_value.eq.return_value.single
    chain.return_value.execute = mock_execute

    return mock_cm


@pytest.mark.asyncio
async def test_session_start_loads_profile_from_metadata(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_tracker.latest_message = {
        "metadata": {"user_id": "user-from-meta"},
    }
    profile = {
        "display_name": "Alice",
        "currency": "EUR",
        "timezone": "Europe/Berlin",
    }
    mock_cm = _mock_profile_client(profile)

    with patch("actions.handlers.session_start.get_supabase", return_value=mock_cm):
        events = await ActionSessionStart().run(mock_dispatcher, mock_tracker, {})

    assert events == [
        SlotSet("user_id", "user-from-meta"),
        SlotSet("user_currency", "EUR"),
        SlotSet("user_timezone", "Europe/Berlin"),
        SlotSet("user_display_name", "Alice"),
        SlotSet("confirmation_pending", False),
    ]


@pytest.mark.asyncio
async def test_session_start_falls_back_to_sender_id(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_tracker.latest_message = {}
    mock_tracker.sender_id = "sender-123"
    mock_cm = _mock_profile_client({"display_name": "Bob", "currency": "USD", "timezone": "UTC"})

    with patch("actions.handlers.session_start.get_supabase", return_value=mock_cm):
        events = await ActionSessionStart().run(mock_dispatcher, mock_tracker, {})

    assert events[0] == SlotSet("user_id", "sender-123")
    assert events[1] == SlotSet("user_currency", "USD")


@pytest.mark.asyncio
async def test_session_start_no_user_id(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_tracker.latest_message = {}
    mock_tracker.sender_id = None

    events = await ActionSessionStart().run(mock_dispatcher, mock_tracker, {})

    assert events == [SlotSet("user_id", "unknown")]


@pytest.mark.asyncio
async def test_session_start_profile_fetch_failure_uses_defaults(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    mock_tracker.latest_message = {"metadata": {"user_id": "user-99"}}
    mock_cm = _mock_profile_client(None, execute_side_effect=RuntimeError("db down"))

    with patch("actions.handlers.session_start.get_supabase", return_value=mock_cm):
        events = await ActionSessionStart().run(mock_dispatcher, mock_tracker, {})

    assert events == [
        SlotSet("user_id", "user-99"),
        SlotSet("user_currency", "USD"),
        SlotSet("user_timezone", "UTC"),
        SlotSet("user_display_name", "user-99"),
        SlotSet("confirmation_pending", False),
    ]
