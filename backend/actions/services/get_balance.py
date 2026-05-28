"""Balance report service."""

from __future__ import annotations

from pydantic import BaseModel

from actions.chat.respond.payloads import custom_message, text_message
from actions.db.client import get_db
from actions.db.queries import get_balance_summary
from actions.services.types import ServiceResult
from actions.utils.formatting import format_currency
from actions.utils.i18n import period_label, t


class BalanceInput(BaseModel):
    user_id: str
    query_period: str = "this_month"
    user_currency: str = "VND"
    user_timezone: str = "UTC"
    user_locale: str = "vi"


async def get_balance(input: BalanceInput) -> ServiceResult:
    locale = input.user_locale
    try:
        async with get_db() as conn:
            balance = await get_balance_summary(
                conn,
                input.user_id,
                input.query_period,
                input.user_timezone,
            )
    except Exception:
        return ServiceResult(messages=[text_message(t("balance_error", locale))])

    income_fmt = format_currency(balance.income, input.user_currency)
    expenses_fmt = format_currency(balance.expenses, input.user_currency)
    net_fmt = format_currency(balance.net, input.user_currency)

    if balance.net > 0:
        sentiment = "positive"
        net_text = f"✓ Thu nhập ròng {net_fmt}" if locale == "vi" else f"✓ {net_fmt} in net income"
    elif balance.net < 0:
        sentiment = "negative"
        net_text = f"✗ Chi vượt thu {net_fmt}" if locale == "vi" else f"✗ {net_fmt} in net expenses"
    else:
        sentiment = "neutral"
        net_text = "Cân bằng — không đổi" if locale == "vi" else "Balanced — no net change"

    label = period_label(input.query_period, locale)
    if locale == "vi":
        message = f"**{label}:**\nThu: {income_fmt}\nChi: {expenses_fmt}\nRòng: {net_text}"
    else:
        message = f"**{label}:**\nIncome: {income_fmt}\nExpenses: {expenses_fmt}\nNet: {net_text}"

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
