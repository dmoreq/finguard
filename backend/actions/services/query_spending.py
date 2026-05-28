"""Spending report service."""

from __future__ import annotations

from pydantic import BaseModel

from actions.chat.respond.payloads import custom_message, text_message
from actions.db.client import get_db
from actions.db.queries import get_spending_by_category
from actions.services.types import ServiceResult
from actions.utils.formatting import format_currency


class SpendingInput(BaseModel):
    user_id: str
    query_period: str = "this_month"
    query_category: str | None = None
    user_currency: str = "USD"
    user_timezone: str = "UTC"


async def query_spending(input: SpendingInput) -> ServiceResult:
    try:
        async with get_db() as conn:
            spending = await get_spending_by_category(
                conn,
                input.user_id,
                input.query_period,
                input.user_timezone,
                input.query_category,
            )
    except Exception:
        return ServiceResult(
            messages=[text_message("Sorry, I couldn't fetch your spending data. Please try again.")]
        )

    if not spending:
        msg = (
            f"No expenses found for {input.query_period}."
            if not input.query_category
            else f"No expenses found for {input.query_category} in {input.query_period}."
        )
        return ServiceResult(messages=[text_message(msg)])

    total_spent = sum(s.total for s in spending)
    lines = []
    for item in sorted(spending, key=lambda x: x.total, reverse=True):
        pct = (item.total / total_spent * 100) if total_spent > 0 else 0
        formatted = format_currency(item.total, input.user_currency)
        lines.append(f"  • {item.category.title()}: {formatted} ({pct:.0f}%)")

    breakdown = "\n".join(lines)
    total_fmt = format_currency(total_spent, input.user_currency)
    message = (
        f"**Spending for {input.query_period.replace('_', ' ')}:**\n"
        f"{breakdown}\n\n"
        f"**Total: {total_fmt}**"
    )

    return ServiceResult(
        messages=[
            custom_message(
                {
                    "type": "spending_report",
                    "data": {
                        "period": input.query_period,
                        "total": total_spent,
                        "currency": input.user_currency,
                        "by_category": [
                            {"category": s.category, "total": s.total, "count": s.count}
                            for s in spending
                        ],
                    },
                    "text": message,
                }
            )
        ]
    )
