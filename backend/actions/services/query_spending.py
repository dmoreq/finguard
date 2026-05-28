"""Spending report service."""

from __future__ import annotations

from pydantic import BaseModel

from actions.chat.extraction.period import prior_period
from actions.chat.respond.payloads import custom_message, text_message
from actions.db.client import get_db
from actions.db.queries import get_expense_total, get_spending_by_category
from actions.services.types import ServiceResult
from actions.utils.categories import display_label
from actions.utils.formatting import format_currency
from actions.utils.i18n import period_label, t


class SpendingInput(BaseModel):
    user_id: str
    query_period: str = "this_month"
    query_category: str | None = None
    user_currency: str = "VND"
    user_timezone: str = "UTC"
    user_locale: str = "vi"
    include_trend: bool = False


def _format_trend(current: float, prior: float, locale: str) -> str:
    if prior <= 0:
        if locale == "vi":
            return "Không có dữ liệu kỳ trước để so sánh."
        return "No prior-period data to compare."
    delta = current - prior
    pct = abs(delta / prior * 100)
    if locale == "vi":
        direction = "tăng" if delta > 0 else "giảm" if delta < 0 else "không đổi"
        return f"So với kỳ trước: {direction} {pct:.0f}%"
    direction = "up" if delta > 0 else "down" if delta < 0 else "unchanged"
    return f"Vs prior period: {direction} {pct:.0f}%"


async def query_spending(input: SpendingInput) -> ServiceResult:
    locale = input.user_locale
    period_label_text = period_label(input.query_period, locale)
    try:
        async with get_db() as conn:
            spending = await get_spending_by_category(
                conn,
                input.user_id,
                input.query_period,
                input.user_timezone,
                input.query_category,
            )
            prior_total = None
            if input.include_trend:
                prior = prior_period(input.query_period)
                prior_total = await get_expense_total(
                    conn,
                    input.user_id,
                    prior,
                    input.user_timezone,
                    input.query_category,
                )
    except Exception:
        return ServiceResult(messages=[text_message(t("spending_error", locale))])

    if not spending:
        if input.query_category:
            msg = t(
                "spending_empty_category",
                locale,
                category=input.query_category,
                period=period_label_text,
            )
        else:
            msg = t("spending_empty", locale, period=period_label_text)
        return ServiceResult(messages=[text_message(msg)])

    total_spent = sum(s.total for s in spending)
    lines = []
    for item in sorted(spending, key=lambda x: x.total, reverse=True):
        pct = (item.total / total_spent * 100) if total_spent > 0 else 0
        formatted = format_currency(item.total, input.user_currency)
        label = display_label(item.category, locale)
        lines.append(f"  • {label}: {formatted} ({pct:.0f}%)")

    breakdown = "\n".join(lines)
    total_fmt = format_currency(total_spent, input.user_currency)
    if locale == "vi":
        header = f"**Chi tiêu {period_label_text.lower()}:**"
        footer = f"**Tổng: {total_fmt}**"
    else:
        header = f"**Spending for {period_label_text.lower()}:**"
        footer = f"**Total: {total_fmt}**"

    message = f"{header}\n{breakdown}\n\n{footer}"
    if input.include_trend and prior_total is not None:
        message += f"\n\n{_format_trend(total_spent, prior_total, locale)}"

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
                        "prior_total": prior_total,
                    },
                    "text": message,
                }
            )
        ]
    )
