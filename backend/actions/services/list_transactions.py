"""List recent transactions."""

from __future__ import annotations

import pendulum
from pydantic import BaseModel

from actions.chat.respond.payloads import custom_message, text_message
from actions.db.client import get_db
from actions.db.queries import list_transactions as db_list
from actions.services.types import ServiceResult
from actions.utils.categories import display_label
from actions.utils.formatting import format_currency, format_date_relative
from actions.utils.i18n import period_label, t


class ListInput(BaseModel):
    user_id: str
    query_period: str | None = None
    query_category: str | None = None
    user_timezone: str = "UTC"
    user_locale: str = "vi"


async def list_transactions(input: ListInput) -> ServiceResult:
    locale = input.user_locale
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
        return ServiceResult(messages=[text_message(t("list_error", locale))])

    if not transactions:
        if input.query_category:
            msg = t("list_empty_category", locale, category=input.query_category)
        elif input.query_period:
            msg = t("list_empty_period", locale, period=period_label(input.query_period, locale))
        else:
            msg = t("list_empty", locale)
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
        label = display_label(tx.category, locale)
        lines.append(f"  {icon} {amount_fmt} — {label} ({date_fmt})")

    if locale == "vi":
        message = (
            f"**Giao dịch gần đây:**\n"
            f"{chr(10).join(lines)}\n\n"
            f"Hiển thị {len(transactions)} giao dịch mới nhất."
        )
    else:
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
