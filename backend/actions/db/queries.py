"""SQLite queries for local development."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import aiosqlite
from loguru import logger

from actions.models.transaction import (
    BalanceSummary,
    SpendingByCategory,
    TransactionInsert,
    TransactionRow,
)
from actions.utils.dates import period_to_date_range


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _row_to_transaction(row: aiosqlite.Row) -> TransactionRow:
    return TransactionRow.model_validate(dict(row))


async def insert_transaction(conn: aiosqlite.Connection, tx: TransactionInsert) -> TransactionRow:
    tx_id = str(uuid.uuid4())
    now = _now_iso()
    data = tx.model_dump()
    data["id"] = tx_id
    data["created_at"] = now
    data["updated_at"] = now

    await conn.execute(
        """
        INSERT INTO transactions (
          id, user_id, type, amount, currency, category, description,
          transaction_date, status, source, ai_confidence, created_at, updated_at
        ) VALUES (
          :id, :user_id, :type, :amount, :currency, :category, :description,
          :transaction_date, :status, :source, :ai_confidence, :created_at, :updated_at
        )
        """,
        data,
    )
    await conn.commit()

    cursor = await conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    row = await cursor.fetchone()
    if not row:
        raise ValueError("Transaction insert returned no data")

    result = _row_to_transaction(row)
    logger.info("transaction_inserted", tx_id=result.id, user_id=tx.user_id)
    return result


async def get_spending_by_category(
    conn: aiosqlite.Connection,
    user_id: str,
    period: str,
    timezone: str = "UTC",
    category: str | None = None,
) -> list[SpendingByCategory]:
    start, end = period_to_date_range(period, timezone)
    sql = """
        SELECT category, amount FROM transactions
        WHERE user_id = ? AND type = 'expense' AND status = 'confirmed'
          AND transaction_date >= ? AND transaction_date <= ?
    """
    params: list[Any] = [user_id, start, end]
    if category:
        sql += " AND category = ?"
        params.append(category)

    cursor = await conn.execute(sql, params)
    rows = await cursor.fetchall()

    by_category: dict[str, tuple[float, int]] = {}
    for row in rows:
        cat = row["category"] or "uncategorized"
        amount = float(row["amount"] or 0)
        total, count = by_category.get(cat, (0.0, 0))
        by_category[cat] = (total + amount, count + 1)

    return [
        SpendingByCategory(category=cat, total=total, count=count)
        for cat, (total, count) in sorted(by_category.items())
    ]


async def get_balance_summary(
    conn: aiosqlite.Connection,
    user_id: str,
    period: str,
    timezone: str = "UTC",
) -> BalanceSummary:
    start, end = period_to_date_range(period, timezone)
    cursor = await conn.execute(
        """
        SELECT type, amount FROM transactions
        WHERE user_id = ? AND status = 'confirmed'
          AND transaction_date >= ? AND transaction_date <= ?
        """,
        (user_id, start, end),
    )
    rows = await cursor.fetchall()

    income_total = 0.0
    expense_total = 0.0
    for row in rows:
        amount = float(row["amount"] or 0)
        if row["type"] == "income":
            income_total += amount
        elif row["type"] == "expense":
            expense_total += amount

    return BalanceSummary(
        income=income_total,
        expenses=expense_total,
        net=income_total - expense_total,
        period=period,
    )


async def list_transactions(
    conn: aiosqlite.Connection,
    user_id: str,
    limit: int = 10,
    period: str | None = None,
    category: str | None = None,
    timezone: str = "UTC",
) -> list[TransactionRow]:
    sql = """
        SELECT * FROM transactions
        WHERE user_id = ? AND status = 'confirmed'
    """
    params: list[Any] = [user_id]

    if period:
        start, end = period_to_date_range(period, timezone)
        sql += " AND transaction_date >= ? AND transaction_date <= ?"
        params.extend([start, end])
    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY transaction_date DESC LIMIT ?"
    params.append(limit)

    cursor = await conn.execute(sql, params)
    rows = await cursor.fetchall()
    return [_row_to_transaction(row) for row in rows]


async def list_user_transactions(
    conn: aiosqlite.Connection,
    user_id: str,
    limit: int = 200,
) -> list[TransactionRow]:
    """All non-discarded transactions for the UI."""
    cursor = await conn.execute(
        """
        SELECT * FROM transactions
        WHERE user_id = ? AND status != 'discarded'
        ORDER BY transaction_date DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = await cursor.fetchall()
    return [_row_to_transaction(row) for row in rows]


async def get_latest_pending_transaction(
    conn: aiosqlite.Connection,
    user_id: str,
) -> TransactionRow | None:
    cursor = await conn.execute(
        """
        SELECT * FROM transactions
        WHERE user_id = ? AND status = 'pending_confirmation'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (user_id,),
    )
    row = await cursor.fetchone()
    return _row_to_transaction(row) if row else None


async def get_transaction(
    conn: aiosqlite.Connection,
    user_id: str,
    transaction_id: str,
) -> TransactionRow | None:
    cursor = await conn.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id),
    )
    row = await cursor.fetchone()
    return _row_to_transaction(row) if row else None


async def delete_transaction(
    conn: aiosqlite.Connection,
    user_id: str,
    transaction_id: str,
) -> bool:
    cursor = await conn.execute(
        """
        UPDATE transactions SET status = 'discarded', updated_at = ?
        WHERE id = ? AND user_id = ?
        """,
        (_now_iso(), transaction_id, user_id),
    )
    await conn.commit()
    return cursor.rowcount > 0


async def update_transaction(
    conn: aiosqlite.Connection,
    user_id: str,
    transaction_id: str,
    updates: dict,
) -> TransactionRow | None:
    if not updates:
        return await get_transaction(conn, user_id, transaction_id)

    updates = {**updates, "updated_at": _now_iso()}
    columns = ", ".join(f"{key} = ?" for key in updates)
    values = [*updates.values(), transaction_id, user_id]

    await conn.execute(
        f"UPDATE transactions SET {columns} WHERE id = ? AND user_id = ?",  # nosec B608
        values,
    )
    await conn.commit()
    return await get_transaction(conn, user_id, transaction_id)


async def get_profile(conn: aiosqlite.Connection, user_id: str) -> dict[str, str]:
    cursor = await conn.execute(
        "SELECT display_name, currency, timezone, locale FROM profiles WHERE id = ?",
        (user_id,),
    )
    row = await cursor.fetchone()
    if not row:
        return {
            "display_name": user_id[:8],
            "currency": "VND",
            "timezone": "Asia/Ho_Chi_Minh",
            "locale": "vi",
        }
    keys = row.keys() if hasattr(row, "keys") else []
    locale = row["locale"] if "locale" in keys else "vi"
    return {
        "display_name": row["display_name"] or user_id[:8],
        "currency": row["currency"] or "VND",
        "timezone": row["timezone"] or "Asia/Ho_Chi_Minh",
        "locale": locale or "vi",
    }


async def update_profile(
    conn: aiosqlite.Connection,
    user_id: str,
    *,
    display_name: str | None = None,
    currency: str | None = None,
    timezone: str | None = None,
    locale: str | None = None,
) -> dict[str, str]:
    current = await get_profile(conn, user_id)
    merged = {
        "display_name": display_name if display_name is not None else current["display_name"],
        "currency": currency if currency is not None else current["currency"],
        "timezone": timezone if timezone is not None else current["timezone"],
        "locale": locale if locale is not None else current.get("locale", "vi"),
    }
    await conn.execute(
        """
        INSERT INTO profiles (id, display_name, currency, timezone, locale, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET
          display_name = excluded.display_name,
          currency = excluded.currency,
          timezone = excluded.timezone,
          locale = excluded.locale,
          updated_at = excluded.updated_at
        """,
        (
            user_id,
            merged["display_name"],
            merged["currency"],
            merged["timezone"],
            merged["locale"],
            _now_iso(),
        ),
    )
    await conn.commit()
    return merged


async def get_expense_total(
    conn: aiosqlite.Connection,
    user_id: str,
    period: str,
    timezone: str = "UTC",
    category: str | None = None,
) -> float:
    spending = await get_spending_by_category(conn, user_id, period, timezone, category)
    return sum(item.total for item in spending)


async def clear_user_transactions(conn: aiosqlite.Connection, user_id: str) -> None:
    await conn.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    await conn.commit()


async def get_chat_session_row(conn: aiosqlite.Connection, sender_id: str) -> dict[str, Any] | None:
    cursor = await conn.execute(
        "SELECT sender_id, user_id, state_json FROM chat_sessions WHERE sender_id = ?",
        (sender_id,),
    )
    row = await cursor.fetchone()
    if row is None:
        return None
    return dict(row)


async def upsert_chat_session(
    conn: aiosqlite.Connection,
    sender_id: str,
    user_id: str,
    state_json: str,
) -> None:
    await conn.execute(
        """
        INSERT INTO chat_sessions (sender_id, user_id, state_json, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (sender_id) DO UPDATE SET
          user_id = excluded.user_id,
          state_json = excluded.state_json,
          updated_at = excluded.updated_at
        """,
        (sender_id, user_id, state_json, _now_iso()),
    )
    await conn.commit()


async def clear_chat_sessions(conn: aiosqlite.Connection) -> None:
    await conn.execute("DELETE FROM chat_sessions")
    await conn.commit()
