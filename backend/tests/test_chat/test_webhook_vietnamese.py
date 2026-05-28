"""Webhook integration: Vietnamese pending actions."""

from __future__ import annotations

import pytest

from actions.chat.session import clear_sessions
from actions.chat.webhook import handle_webhook
from actions.db.client import get_db
from actions.db.queries import get_transaction, update_profile


@pytest.fixture(autouse=True)
async def _clear():
    await clear_sessions()
    yield
    await clear_sessions()


async def _seed_vi_profile(user_id: str) -> None:
    async with get_db() as conn:
        await update_profile(
            conn,
            user_id,
            currency="VND",
            timezone="Asia/Ho_Chi_Minh",
            locale="vi",
        )


async def _record_pending_vi(sender: str, user_id: str) -> str:
    await _seed_vi_profile(user_id)
    messages = await handle_webhook(
        {
            "sender": sender,
            "message": "Chi tiêu 80k cà phê",
            "metadata": {"user_id": user_id},
        }
    )
    custom = messages[0].get("custom")
    assert custom is not None
    assert custom["type"] == "transaction_pending"
    return custom["transaction"]["id"]


@pytest.mark.asyncio
async def test_vietnamese_golden_flow(db_path) -> None:
    sender = "vi-golden"
    user_id = "user-vi-golden"
    tx_id = await _record_pending_vi(sender, user_id)

    edit = await handle_webhook(
        {"sender": sender, "message": "Sửa thành 60k", "metadata": {"user_id": user_id}}
    )
    custom = edit[0].get("custom")
    assert custom is not None
    assert custom["transaction"]["amount"] == 60_000.0

    confirm = await handle_webhook(
        {"sender": sender, "message": "Xác nhận", "metadata": {"user_id": user_id}}
    )
    assert "lưu" in confirm[0].get("text", "").lower() or "đã" in confirm[0].get("text", "").lower()

    async with get_db() as conn:
        row = await get_transaction(conn, user_id, tx_id)
    assert row is not None
    assert row.status == "confirmed"
    assert float(row.amount) == 60_000.0

    balance = await handle_webhook(
        {"sender": sender, "message": "Số dư tháng nay", "metadata": {"user_id": user_id}}
    )
    assert balance[0].get("custom") is not None or "thu" in balance[0].get("text", "").lower()

    spending = await handle_webhook(
        {"sender": sender, "message": "Tháng nay chi bao nhiêu", "metadata": {"user_id": user_id}}
    )
    spending_custom = spending[0].get("custom")
    spending_text = spending[0].get("text", "").lower()
    assert spending_custom is not None or "chi" in spending_text or "tổng" in spending_text
