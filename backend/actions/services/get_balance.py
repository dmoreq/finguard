"""Balance report service."""

from __future__ import annotations

from pydantic import BaseModel

from actions.chat.respond.payloads import custom_message, text_message
from actions.db.client import get_db
from actions.db.queries import get_balance_summary
from actions.services.types import ServiceResult
from actions.utils.formatting import format_currency


class BalanceInput(BaseModel):
    user_id: str
    query_period: str = "this_month"
    user_currency: str = "USD"
    user_timezone: str = "UTC"


async def get_balance(input: BalanceInput) -> ServiceResult:
    try:
        async with get_db() as conn:
            balance = await get_balance_summary(
                conn,
                input.user_id,
                input.query_period,
                input.user_timezone,
            )
    except Exception:
        return ServiceResult(
            messages=[text_message("Sorry, I couldn't fetch your balance. Please try again.")]
        )

    income_fmt = format_currency(balance.income, input.user_currency)
    expenses_fmt = format_currency(balance.expenses, input.user_currency)
    net_fmt = format_currency(balance.net, input.user_currency)

    if balance.net > 0:
        sentiment = "positive"
        net_text = f"✓ {net_fmt} in net income"
    elif balance.net < 0:
        sentiment = "negative"
        net_text = f"✗ {net_fmt} in net expenses"
    else:
        sentiment = "neutral"
        net_text = "Balanced — no net change"

    period_label = input.query_period.replace("_", " ").title()
    message = (
        f"**{period_label}:**\nIncome: {income_fmt}\nExpenses: {expenses_fmt}\nNet: {net_text}"
    )

    return ServiceResult(
        messages=[
            custom_message(
                {
                    "type": "balance",
                    "data": {
                        "period": input.query_period,
                        "income": balance.income,
                        "expenses": balance.expenses,
                        "net": balance.net,
                        "currency": input.user_currency,
                        "sentiment": sentiment,
                    },
                    "text": message,
                }
            )
        ]
    )
