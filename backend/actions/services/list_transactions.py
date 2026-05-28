"""List recent transactions."""

from __future__ import annotations

import pendulum
from pydantic import BaseModel

from actions.chat.respond.payloads import custom_message, text_message
from actions.db.client import get_db
from actions.db.queries import list_transactions as db_list
from actions.services.types import ServiceResult
from actions.utils.formatting import format_currency, format_date_relative


class ListInput(BaseModel):
    user_id: str
    query_period: str | None = None
    query_category: str | None = None
    user_timezone: str = "UTC"


async def list_transactions(input: ListInput) -> ServiceResult:
    try:
        async with get_db() as conn:
            transactions = await db_list(
                conn,
                input.user_id,
                limit=20,
                period=input.query_period,
                category=input.query_category,
                timezone=input.user_timezone,
            )
    except Exception:
        return ServiceResult(
            messages=[text_message("Sorry, I couldn't fetch your transactions. Please try again.")]
        )

    if not transactions:
        msg = (
            f"No transactions found for {input.query_period}."
            if input.query_period
            else "No transactions found."
        )
        if input.query_category:
            msg = f"No {input.query_category} transactions found."
        return ServiceResult(messages=[text_message(msg)])

    now = pendulum.now(input.user_timezone)
    lines = []
    for tx in transactions:
        amount_fmt = format_currency(tx.amount, tx.currency)
        date_fmt = format_date_relative(
            pendulum.parse(tx.transaction_date, tz=input.user_timezone),
            now,
        )
        icon = "+" if tx.type == "income" else "−"
        status_badge = (
            " ⏳"
            if tx.status == "pending_confirmation"
            else " ✓"
            if tx.status == "confirmed"
            else " ✗"
        )
        lines.append(f"  {icon} {amount_fmt} — {tx.category.title()} on {date_fmt}{status_badge}")

    message = (
        f"**Recent transactions:**\n"
        f"{chr(10).join(lines)}\n\n"
        f"Showing {len(transactions)} most recent."
    )

    return ServiceResult(
        messages=[
            custom_message(
                {
                    "type": "transaction_list",
                    "data": {
                        "count": len(transactions),
                        "transactions": [
                            {
                                "id": tx.id,
                                "type": tx.type,
                                "amount": tx.amount,
                                "currency": tx.currency,
                                "category": tx.category,
                                "date": tx.transaction_date,
                                "status": tx.status,
                            }
                            for tx in transactions
                        ],
                    },
                    "text": message,
                }
            )
        ]
    )
