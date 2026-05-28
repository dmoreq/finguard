"""Integration tests for SQLite query functions."""

from __future__ import annotations

from actions.db.queries import (
    clear_user_transactions,
    delete_transaction,
    get_balance_summary,
    get_latest_pending_transaction,
    get_profile,
    get_spending_by_category,
    get_transaction,
    insert_transaction,
    list_user_transactions,
    update_profile,
    update_transaction,
)
from actions.models.transaction import TransactionInsert


async def test_insert_transaction_round_trip(db_conn, tx_insert) -> None:
    row = await insert_transaction(db_conn, tx_insert)
    assert row.id
    assert row.amount == 25.5
    assert row.currency == "USD"
    assert row.category == "groceries"

    fetched = await get_transaction(db_conn, "user-a", row.id)
    assert fetched is not None
    assert fetched.status == "confirmed"


async def test_get_latest_pending_transaction(db_conn) -> None:
    pending = TransactionInsert(
        user_id="user-a",
        type="expense",
        amount=12.0,
        category="dining",
        description=None,
        transaction_date="2026-05-15",
        status="pending_confirmation",
    )
    inserted = await insert_transaction(db_conn, pending)
    latest = await get_latest_pending_transaction(db_conn, "user-a")
    assert latest is not None
    assert latest.id == inserted.id

    none_for_other = await get_latest_pending_transaction(db_conn, "user-b")
    assert none_for_other is None


async def test_update_transaction_confirms_pending(db_conn) -> None:
    row = await insert_transaction(
        db_conn,
        TransactionInsert(
            user_id="user-a",
            type="expense",
            amount=9.0,
            category="coffee",
            description=None,
            transaction_date="2026-05-15",
            status="pending_confirmation",
        ),
    )
    updated = await update_transaction(db_conn, "user-a", row.id, {"status": "confirmed"})
    assert updated is not None
    assert updated.status == "confirmed"


async def test_delete_transaction_scoped_to_user(db_conn, tx_insert) -> None:
    row = await insert_transaction(db_conn, tx_insert)
    ok = await delete_transaction(db_conn, "user-a", row.id)
    assert ok is True
    still = await get_transaction(db_conn, "user-a", row.id)
    assert still is not None
    assert still.status == "discarded"

    ok_other = await delete_transaction(db_conn, "user-b", row.id)
    assert ok_other is False


async def test_get_spending_by_category_filters(db_conn) -> None:
    await insert_transaction(
        db_conn,
        TransactionInsert(
            user_id="user-a",
            type="expense",
            amount=30.0,
            category="food",
            description=None,
            transaction_date="2026-05-10",
            status="confirmed",
        ),
    )
    await insert_transaction(
        db_conn,
        TransactionInsert(
            user_id="user-a",
            type="expense",
            amount=20.0,
            category="transport",
            description=None,
            transaction_date="2026-05-12",
            status="confirmed",
        ),
    )
    rows = await get_spending_by_category(db_conn, "user-a", "this_month", "UTC", "food")
    assert len(rows) == 1
    assert rows[0].category == "food"
    assert rows[0].total == 30.0


async def test_get_balance_summary(db_conn) -> None:
    await insert_transaction(
        db_conn,
        TransactionInsert(
            user_id="user-a",
            type="income",
            amount=1000.0,
            category="salary",
            description=None,
            transaction_date="2026-05-05",
            status="confirmed",
        ),
    )
    await insert_transaction(
        db_conn,
        TransactionInsert(
            user_id="user-a",
            type="expense",
            amount=200.0,
            category="food",
            description=None,
            transaction_date="2026-05-08",
            status="confirmed",
        ),
    )
    summary = await get_balance_summary(db_conn, "user-a", "this_month", "UTC")
    assert summary.income == 1000.0
    assert summary.expenses == 200.0
    assert summary.net == 800.0


async def test_list_user_transactions_order_and_limit(db_conn) -> None:
    for day in ("2026-05-01", "2026-05-20", "2026-05-10"):
        await insert_transaction(
            db_conn,
            TransactionInsert(
                user_id="user-a",
                type="expense",
                amount=1.0,
                category="misc",
                description=None,
                transaction_date=day,
                status="confirmed",
            ),
        )
    rows = await list_user_transactions(db_conn, "user-a", limit=2)
    assert len(rows) == 2
    assert rows[0].transaction_date >= rows[1].transaction_date


async def test_clear_user_transactions_only_target_user(db_conn, tx_insert) -> None:
    await insert_transaction(db_conn, tx_insert)
    other = tx_insert.model_copy(update={"user_id": "user-b", "transaction_date": "2026-05-16"})
    await insert_transaction(db_conn, other)

    await clear_user_transactions(db_conn, "user-a")
    assert await list_user_transactions(db_conn, "user-a") == []
    assert len(await list_user_transactions(db_conn, "user-b")) == 1


async def test_profile_defaults_and_update(db_conn) -> None:
    profile = await get_profile(db_conn, "local-user")
    assert profile["currency"] == "VND"

    updated = await update_profile(db_conn, "local-user", display_name="Test User", currency="EUR")
    assert updated["display_name"] == "Test User"
    assert updated["currency"] == "EUR"
    assert (await get_profile(db_conn, "local-user"))["currency"] == "EUR"


async def test_query_functions_include_user_id_in_sql() -> None:
    """Meta-test: DB functions that accept user_id must reference it in SQL."""
    import inspect

    import actions.db.queries as queries

    skip = {"_now_iso", "_row_to_transaction"}
    for name, func in inspect.getmembers(queries, inspect.isfunction):
        if name.startswith("_") or name in skip:
            continue
        if "user_id" not in inspect.signature(func).parameters:
            continue
        source = inspect.getsource(func)
        assert "user_id" in source, f"{name} must scope by user_id"
