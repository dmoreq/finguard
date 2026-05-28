"""Action: query spending summary by category or time period."""

from typing import Any

from loguru import logger
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.db.client import get_db
from actions.db.queries import get_spending_by_category
from actions.utils.formatting import format_currency


class ActionQuerySpending(Action):
    """Retrieve spending totals grouped by category for a time period."""

    def name(self) -> str:
        return "action_query_spending"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict]:
        """Execute the action: fetch spending data and format report."""
        user_id = tracker.get_slot("user_id")
        user_currency = tracker.get_slot("user_currency") or "USD"
        user_timezone = tracker.get_slot("user_timezone") or "UTC"

        query_period = tracker.get_slot("query_period") or "this_month"
        query_category = tracker.get_slot("query_category")

        logger.info(
            "spending_query_requested",
            user_id=user_id,
            period=query_period,
            category=query_category,
            sender=tracker.sender_id,
        )

        try:
            async with get_db() as conn:
                spending = await get_spending_by_category(
                    conn,
                    user_id,
                    query_period,
                    user_timezone,
                    query_category,
                )
        except Exception as e:
            logger.exception("spending_query_failed", user_id=user_id, error=str(e))
            dispatcher.utter_message(
                text="Sorry, I couldn't fetch your spending data. Please try again."
            )
            return []

        # Format response
        if not spending:
            msg = (
                f"No expenses found for {query_period}."
                if not query_category
                else f"No expenses found for {query_category} in {query_period}."
            )
            dispatcher.utter_message(text=msg)
            return []

        # Build category breakdown
        total_spent = sum(s.total for s in spending)
        lines = []

        for item in sorted(spending, key=lambda x: x.total, reverse=True):
            pct = (item.total / total_spent * 100) if total_spent > 0 else 0
            formatted = format_currency(item.total, user_currency)
            lines.append(f"  • {item.category.title()}: {formatted} ({pct:.0f}%)")

        breakdown = "\n".join(lines)
        total_fmt = format_currency(total_spent, user_currency)

        message = (
            f"**Spending for {query_period.replace('_', ' ')}:**\n"
            f"{breakdown}\n\n"
            f"**Total: {total_fmt}**"
        )

        logger.info(
            "spending_report_generated",
            user_id=user_id,
            period=query_period,
            total=total_spent,
            categories=len(spending),
        )

        dispatcher.utter_message(
            json_message={
                "type": "spending_report",
                "data": {
                    "period": query_period,
                    "total": total_spent,
                    "currency": user_currency,
                    "by_category": [
                        {"category": s.category, "total": s.total, "count": s.count}
                        for s in spending
                    ],
                },
                "text": message,
            }
        )

        return []
