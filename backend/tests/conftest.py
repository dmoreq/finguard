"""Shared pytest fixtures for action handler tests."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from actions.db.client import get_db
from actions.db.queries import insert_transaction
from actions.models.transaction import TransactionInsert, TransactionRow

REPORT_USER_ID = "user-reports"
REPORT_TIMEZONE = "UTC"


@pytest.fixture(autouse=True)
def _keyword_router_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid loading embedding models in unit tests."""
    monkeypatch.setenv("ROUTER_MODE", "keyword")
    from actions.chat.factory import reset_dialogue_engine

    reset_dialogue_engine()


@pytest.fixture
def db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Isolated SQLite file per test."""
    path = tmp_path / "test.db"
    monkeypatch.setenv("FINGUARD_DB_PATH", str(path))
    return path


@pytest.fixture
async def seeded_report_transactions(db_path: Path) -> AsyncGenerator[str, None]:
    """Confirmed income and expenses in May 2026 for this_month queries."""
    rows = [
        TransactionInsert(
            user_id=REPORT_USER_ID,
            type="income",
            amount=3000.0,
            category="salary",
            transaction_date="2026-05-01",
            status="confirmed",
        ),
        TransactionInsert(
            user_id=REPORT_USER_ID,
            type="expense",
            amount=80.0,
            category="groceries",
            transaction_date="2026-05-10",
            status="confirmed",
        ),
        TransactionInsert(
            user_id=REPORT_USER_ID,
            type="expense",
            amount=20.0,
            category="dining",
            transaction_date="2026-05-15",
            status="confirmed",
        ),
        TransactionInsert(
            user_id=REPORT_USER_ID,
            type="expense",
            amount=50.0,
            category="groceries",
            transaction_date="2026-05-20",
            status="confirmed",
        ),
    ]
    async with get_db() as conn:
        for row in rows:
            await insert_transaction(conn, row)
    yield REPORT_USER_ID


@pytest.fixture
async def db_conn(db_path: Path) -> AsyncGenerator:
    async with get_db() as conn:
        yield conn


@pytest.fixture
def tx_insert() -> TransactionInsert:
    return TransactionInsert(
        user_id="user-a",
        type="expense",
        amount=25.5,
        currency="USD",
        category="groceries",
        description="milk",
        transaction_date="2026-05-15",
        status="confirmed",
    )


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
