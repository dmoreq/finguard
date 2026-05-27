"""Typed Supabase query functions for financial data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from supabase import AsyncClient

from actions.models.transaction import (
    BalanceSummary,
    SpendingByCategory,
    TransactionInsert,
    TransactionRow,
)
from actions.utils.dates import period_to_date_range


async def insert_transaction(
    client: AsyncClient,
    tx: TransactionInsert,
) -> TransactionRow:
    """Insert a pending transaction. Returns the created row."""
    logger.debug(
        "insert_transaction_start",
        user_id=tx.user_id,
        amount=tx.amount,
        category=tx.category,
    )

    response = await client.table("transactions").insert(tx.model_dump()).execute()

    if not response.data:
        raise ValueError("Transaction insert returned no data")

    result = TransactionRow.model_validate(response.data[0])

    logger.info(
        "transaction_inserted",
        tx_id=result.id,
        amount=tx.amount,
        category=tx.category,
        user_id=tx.user_id,
    )

    return result


async def get_spending_by_category(
    client: AsyncClient,
    user_id: str,
    period: str,
    timezone: str = "UTC",
    category: str | None = None,
) -> list[SpendingByCategory]:
    """
    Return spending totals grouped by category for a given period.
    Filters by status='confirmed' only (pending transactions excluded).
    """
    start, end = period_to_date_range(period, timezone)

    query = (
        client.table("transactions")
        .select("category, amount")
        .eq("user_id", user_id)
        .eq("type", "expense")
        .eq("status", "confirmed")
        .gte("transaction_date", start)
        .lte("transaction_date", end)
    )

    if category:
        query = query.eq("category", category)

    response = await query.execute()

    logger.debug(
        "spending_query",
        user_id=user_id,
        period=period,
        rows=len(response.data),
    )

    # Group by category
    by_category: dict[str, tuple[float, int]] = {}
    for row in response.data:
        cat = row.get("category", "uncategorized")
        amount = float(row.get("amount", 0))
        current_total, count = by_category.get(cat, (0.0, 0))
        by_category[cat] = (current_total + amount, count + 1)

    return [
        SpendingByCategory(category=cat, total=total, count=count)
        for cat, (total, count) in sorted(by_category.items())
    ]


async def get_balance_summary(
    client: AsyncClient,
    user_id: str,
    period: str,
    timezone: str = "UTC",
) -> BalanceSummary:
    """Return total income, expenses, and net for the period."""
    start, end = period_to_date_range(period, timezone)

    logger.debug("balance_query_start", user_id=user_id, period=period, start=start, end=end)

    try:
        response = await client.rpc(
            "get_balance_summary",
            {
                "p_user_id": user_id,
                "p_start": start,
                "p_end": end,
            },
        ).execute()

        if response.data:
            data = response.data[0]
            result = BalanceSummary(
                income=float(data.get("income", 0)),
                expenses=float(data.get("expenses", 0)),
                net=float(data.get("net", 0)),
                period=period,
            )
        else:
            result = BalanceSummary(period=period)

        logger.info(
            "balance_computed",
            user_id=user_id,
            income=result.income,
            expenses=result.expenses,
            net=result.net,
        )
        return result

    except Exception as e:
        logger.warning("balance_rpc_failed_using_fallback", error=str(e))
        # Fallback if RPC doesn't exist — query tables directly
        return await _get_balance_summary_fallback(client, user_id, start, end)


async def _get_balance_summary_fallback(
    client: AsyncClient,
    user_id: str,
    start: str,
    end: str,
) -> BalanceSummary:
    """Fallback balance query without RPC."""
    response = (
        await client.table("transactions")
        .select("type, amount")
        .eq("user_id", user_id)
        .eq("status", "confirmed")
        .gte("transaction_date", start)
        .lte("transaction_date", end)
        .execute()
    )

    income_total = 0.0
    expense_total = 0.0

    for row in response.data:
        tx_type = row.get("type")
        amount = float(row.get("amount", 0))

        if tx_type == "income":
            income_total += amount
        elif tx_type == "expense":
            expense_total += amount

    return BalanceSummary(
        income=income_total,
        expenses=expense_total,
        net=income_total - expense_total,
    )


async def list_transactions(
    client: AsyncClient,
    user_id: str,
    limit: int = 10,
    period: str | None = None,
    category: str | None = None,
    timezone: str = "UTC",
) -> list[TransactionRow]:
    """List recent transactions with optional filtering."""
    query = (
        client.table("transactions")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "confirmed")
        .order("transaction_date", desc=True)
        .limit(limit)
    )

    if period:
        start, end = period_to_date_range(period, timezone)
        query = query.gte("transaction_date", start).lte("transaction_date", end)

    if category:
        query = query.eq("category", category)

    response = await query.execute()

    logger.debug(
        "transactions_listed",
        user_id=user_id,
        count=len(response.data),
        limit=limit,
    )

    return [TransactionRow.model_validate(row) for row in response.data]


async def delete_transaction(
    client: AsyncClient,
    user_id: str,
    transaction_id: str,
) -> bool:
    """Delete a transaction (soft delete via status change)."""
    logger.info(
        "delete_transaction",
        user_id=user_id,
        tx_id=transaction_id,
    )

    response = (
        await client.table("transactions")
        .update({"status": "discarded"})
        .eq("id", transaction_id)
        .eq("user_id", user_id)
        .execute()
    )

    return bool(response.data)


async def update_transaction(
    client: AsyncClient,
    user_id: str,
    transaction_id: str,
    updates: dict,
) -> TransactionRow | None:
    """Update a transaction."""
    logger.info(
        "update_transaction",
        user_id=user_id,
        tx_id=transaction_id,
        fields=list(updates.keys()),
    )

    response = (
        await client.table("transactions")
        .update(updates)
        .eq("id", transaction_id)
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:
        return TransactionRow.model_validate(response.data[0])

    return None
