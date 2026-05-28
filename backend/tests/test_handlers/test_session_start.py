"""Tests for ActionSessionStart."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from rasa_sdk.events import SlotSet

from actions.handlers.session_start import ActionSessionStart


def _mock_db_cm() -> AsyncMock:
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = MagicMock()
    mock_cm.__aexit__.return_value = None
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

    with (
        patch("actions.handlers.session_start.get_db", return_value=_mock_db_cm()),
        patch(
            "actions.handlers.session_start.get_profile",
            new=AsyncMock(return_value=profile),
        ),
        patch(
            "actions.handlers.session_start.get_latest_pending_transaction",
            new=AsyncMock(return_value=None),
        ),
    ):
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

    with (
        patch("actions.handlers.session_start.get_db", return_value=_mock_db_cm()),
        patch(
            "actions.handlers.session_start.get_profile",
            new=AsyncMock(
                return_value={"display_name": "Bob", "currency": "USD", "timezone": "UTC"},
            ),
        ),
        patch(
            "actions.handlers.session_start.get_latest_pending_transaction",
            new=AsyncMock(return_value=None),
        ),
    ):
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

    with (
        patch("actions.handlers.session_start.get_db", return_value=_mock_db_cm()),
        patch(
            "actions.handlers.session_start.get_profile",
            new=AsyncMock(side_effect=RuntimeError("db down")),
        ),
    ):
        events = await ActionSessionStart().run(mock_dispatcher, mock_tracker, {})

    assert events == [
        SlotSet("user_id", "user-99"),
        SlotSet("user_currency", "USD"),
        SlotSet("user_timezone", "UTC"),
        SlotSet("user_display_name", "user-99"),
        SlotSet("confirmation_pending", False),
    ]


@pytest.mark.asyncio
async def test_session_start_syncs_pending_transaction(
    mock_dispatcher: MagicMock,
    mock_tracker: MagicMock,
) -> None:
    from actions.models.transaction import TransactionRow

    mock_tracker.latest_message = {"metadata": {"user_id": "user-pending"}}
    profile = {"display_name": "Alice", "currency": "USD", "timezone": "UTC"}
    pending = TransactionRow(
        id="tx-pending-1",
        user_id="user-pending",
        type="expense",
        amount=10.0,
        currency="USD",
        category="food",
        description=None,
        transaction_date="2026-05-27",
        status="pending_confirmation",
        source="manual_chat",
        ai_confidence=None,
        created_at=datetime(2026, 5, 27, 12, 0, 0),
        updated_at=datetime(2026, 5, 27, 12, 0, 0),
    )

    with (
        patch("actions.handlers.session_start.get_db", return_value=_mock_db_cm()),
        patch(
            "actions.handlers.session_start.get_profile",
            new=AsyncMock(return_value=profile),
        ),
        patch(
            "actions.handlers.session_start.get_latest_pending_transaction",
            new=AsyncMock(return_value=pending),
        ),
    ):
        events = await ActionSessionStart().run(mock_dispatcher, mock_tracker, {})

    assert SlotSet("confirmation_pending", True) in events
    assert SlotSet("last_transaction_id", "tx-pending-1") in events
