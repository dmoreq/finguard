"""Balance, spending, and transaction list services (CP-2)."""

from __future__ import annotations

import pytest

from actions.services.get_balance import BalanceInput, get_balance
from actions.services.list_transactions import ListInput, list_transactions
from actions.services.query_spending import SpendingInput, query_spending
from tests.conftest import REPORT_TIMEZONE, REPORT_USER_ID


@pytest.mark.asyncio
async def test_get_balance_summary_positive_net(seeded_report_transactions: str) -> None:
    result = await get_balance(
        BalanceInput(
            user_id=seeded_report_transactions,
            query_period="this_month",
            user_currency="USD",
            user_timezone=REPORT_TIMEZONE,
            user_locale="en",
        )
    )
    custom = result.messages[0]["custom"]
    assert custom["type"] == "balance"
    data = custom["data"]
    assert data["income"] == 3000.0
    assert data["expenses"] == 150.0
    assert data["net"] == 2850.0
    assert data["sentiment"] == "positive"
    assert (
        "balance" in custom["text"].lower()
        or "Income" in custom["text"]
        or "income" in custom["text"].lower()
    )


@pytest.mark.asyncio
async def test_get_balance_empty_period_returns_neutral_net(db_path) -> None:
    result = await get_balance(
        BalanceInput(
            user_id="user-empty",
            query_period="this_month",
            user_timezone=REPORT_TIMEZONE,
        )
    )
    custom = result.messages[0]["custom"]
    assert custom["type"] == "balance"
    assert custom["data"]["net"] == 0.0
    assert custom["data"]["sentiment"] == "neutral"


@pytest.mark.asyncio
async def test_query_spending_groups_by_category(seeded_report_transactions: str) -> None:
    result = await query_spending(
        SpendingInput(
            user_id=seeded_report_transactions,
            query_period="this_month",
            user_timezone=REPORT_TIMEZONE,
        )
    )
    custom = result.messages[0]["custom"]
    assert custom["type"] == "spending_report"
    data = custom["data"]
    assert data["total"] == 150.0
    by_cat = {item["category"]: item for item in data["by_category"]}
    assert by_cat["groceries"]["total"] == 130.0
    assert by_cat["groceries"]["count"] == 2
    assert by_cat["dining"]["total"] == 20.0


@pytest.mark.asyncio
async def test_query_spending_no_expenses_returns_text_message(db_path) -> None:
    result = await query_spending(
        SpendingInput(
            user_id="user-no-spend",
            query_period="this_month",
            user_timezone=REPORT_TIMEZONE,
            user_locale="en",
        )
    )
    assert "custom" not in result.messages[0]
    assert (
        "No expenses" in result.messages[0]["text"]
        or "Không có chi tiêu" in result.messages[0]["text"]
    )


@pytest.mark.asyncio
async def test_query_spending_filters_category(seeded_report_transactions: str) -> None:
    result = await query_spending(
        SpendingInput(
            user_id=seeded_report_transactions,
            query_period="this_month",
            query_category="dining",
            user_timezone=REPORT_TIMEZONE,
        )
    )
    custom = result.messages[0]["custom"]
    assert custom["data"]["total"] == 20.0
    assert len(custom["data"]["by_category"]) == 1
    assert custom["data"]["by_category"][0]["category"] == "dining"


@pytest.mark.asyncio
async def test_get_balance_vietnamese_locale(seeded_report_transactions: str) -> None:
    result = await get_balance(
        BalanceInput(
            user_id=seeded_report_transactions,
            query_period="this_month",
            user_currency="VND",
            user_timezone=REPORT_TIMEZONE,
            user_locale="vi",
        )
    )
    custom = result.messages[0]["custom"]
    assert custom["type"] == "balance"
    text = custom["text"]
    assert "Thu:" in text or "thu" in text.lower()
    assert custom["data"]["net"] == 2850.0


@pytest.mark.asyncio
async def test_query_spending_trend_when_requested(seeded_report_transactions: str) -> None:
    result = await query_spending(
        SpendingInput(
            user_id=seeded_report_transactions,
            query_period="this_month",
            user_timezone=REPORT_TIMEZONE,
            include_trend=True,
        )
    )
    custom = result.messages[0]["custom"]
    assert custom["type"] == "spending_report"
    assert "trend" in custom["data"] or "prior_total" in custom["data"]


@pytest.mark.asyncio
async def test_list_transactions_returns_confirmed_rows(seeded_report_transactions: str) -> None:
    result = await list_transactions(
        ListInput(
            user_id=seeded_report_transactions,
            query_period="this_month",
            user_timezone=REPORT_TIMEZONE,
        )
    )
    custom = result.messages[0]["custom"]
    assert custom["type"] == "transaction_list"
    assert custom["data"]["count"] == 4
    categories = {tx["category"] for tx in custom["data"]["transactions"]}
    assert categories == {"salary", "groceries", "dining"}


@pytest.mark.asyncio
async def test_list_transactions_empty_when_no_data(db_path) -> None:
    result = await list_transactions(
        ListInput(
            user_id=REPORT_USER_ID,
            query_period="last_month",
            user_timezone=REPORT_TIMEZONE,
            user_locale="en",
        )
    )
    assert result.messages[0].get("text")
    assert (
        "No transactions" in result.messages[0]["text"]
        or "Không có giao dịch" in result.messages[0]["text"]
    )
