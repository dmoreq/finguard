"""Webhook integration: balance and spending intents (CP-2)."""

from __future__ import annotations

import pytest

from actions.chat.session import clear_sessions
from actions.chat.webhook import handle_webhook
from tests.conftest import REPORT_USER_ID


@pytest.fixture(autouse=True)
async def _clear():
    await clear_sessions()
    yield
    await clear_sessions()


@pytest.fixture(autouse=True)
async def _seed_reports(seeded_report_transactions: str) -> None:
    assert seeded_report_transactions == REPORT_USER_ID


@pytest.mark.asyncio
async def test_webhook_balance_intent(db_path, seeded_report_transactions: str) -> None:
    messages = await handle_webhook(
        {
            "sender": "balance-user",
            "message": "what's my balance this month?",
            "metadata": {"user_id": REPORT_USER_ID},
        }
    )
    custom = messages[0].get("custom")
    assert custom is not None
    assert custom["type"] == "balance"
    assert custom["data"]["income"] == 3000.0
    assert custom["data"]["expenses"] == 150.0


@pytest.mark.asyncio
async def test_webhook_spending_intent(db_path, seeded_report_transactions: str) -> None:
    messages = await handle_webhook(
        {
            "sender": "spend-user",
            "message": "how much did I spend this month?",
            "metadata": {"user_id": REPORT_USER_ID},
        }
    )
    custom = messages[0].get("custom")
    assert custom is not None
    assert custom["type"] == "spending_report"
    assert custom["data"]["total"] == 150.0


@pytest.mark.asyncio
async def test_webhook_list_transactions_intent(db_path, seeded_report_transactions: str) -> None:
    messages = await handle_webhook(
        {
            "sender": "list-user",
            "message": "show recent transactions",
            "metadata": {"user_id": REPORT_USER_ID},
        }
    )
    custom = messages[0].get("custom")
    assert custom is not None
    assert custom["type"] == "transaction_list"
    assert custom["data"]["count"] >= 1
