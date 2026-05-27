"""Shared pytest fixtures for action handler tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from actions.models.transaction import TransactionRow


@pytest.fixture
def mock_dispatcher() -> MagicMock:
    dispatcher = MagicMock()
    dispatcher.utter_message = MagicMock()
    return dispatcher


@pytest.fixture
def mock_tracker() -> MagicMock:
    tracker = MagicMock()
    tracker.sender_id = "test-sender"
    tracker.active_flow_name = "record_expense"
    tracker.active_flow_metadata = {"transaction_type": "expense"}
    tracker.get_slot = MagicMock(
        side_effect=lambda name: {
            "amount": 45.0,
            "category": "groceries",
            "description": None,
            "transaction_date": "yesterday",
            "user_id": "user-1",
            "user_currency": "USD",
            "user_timezone": "UTC",
            "ai_confidence": None,
            "confirmation_pending": False,
            "last_transaction_id": None,
        }.get(name)
    )
    return tracker


@pytest.fixture
def pending_tracker() -> MagicMock:
    tracker = MagicMock()
    tracker.sender_id = "test-sender"

    def get_slot(name: str):
        return {
            "confirmation_pending": True,
            "last_transaction_id": "tx-abc",
            "user_id": "user-1",
            "user_currency": "USD",
            "user_timezone": "UTC",
            "amount": 50.0,
            "category": "dining",
            "description": None,
            "transaction_date": None,
        }.get(name)

    tracker.get_slot.side_effect = get_slot
    return tracker


@pytest.fixture
def sample_transaction_row() -> TransactionRow:
    from datetime import datetime

    return TransactionRow(
        id="tx-abc",
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
