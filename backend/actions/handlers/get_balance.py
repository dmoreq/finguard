"""Action: get balance summary (income vs expenses)."""

from typing import Any

from loguru import logger
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.db.client import get_db
from actions.db.queries import get_balance_summary
from actions.utils.formatting import format_currency


class ActionGetBalance(Action):
    """Retrieve balance summary (income, expenses, net) for a period."""

    def name(self) -> str:
        return "action_get_balance"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict]:
        """Execute the action: fetch balance data and format report."""
        user_id = tracker.get_slot("user_id")
        user_currency = tracker.get_slot("user_currency") or "USD"
        user_timezone = tracker.get_slot("user_timezone") or "UTC"

        query_period = tracker.get_slot("query_period") or "this_month"

        logger.info(
            "balance_query_requested",
            user_id=user_id,
            period=query_period,
            sender=tracker.sender_id,
        )

        try:
            async with get_db() as conn:
                balance = await get_balance_summary(
                    conn,
                    user_id,
                    query_period,
                    user_timezone,
                )
        except Exception as e:
            logger.exception("balance_query_failed", user_id=user_id, error=str(e))
            dispatcher.utter_message(text="Sorry, I couldn't fetch your balance. Please try again.")
            return []

        # Format response
        income_fmt = format_currency(balance.income, user_currency)
        expenses_fmt = format_currency(balance.expenses, user_currency)
        net_fmt = format_currency(balance.net, user_currency)

        # Determine net sentiment (for tone)
        if balance.net > 0:
            sentiment = "positive"
            net_text = f"✓ {net_fmt} in net income"
        elif balance.net < 0:
            sentiment = "negative"
            net_text = f"✗ {net_fmt} in net expenses"
        else:
            sentiment = "neutral"
            net_text = "Balanced — no net change"

        message = (
            f"**{query_period.replace('_', ' ').title()}:**\n"
            f"Income: {income_fmt}\n"
            f"Expenses: {expenses_fmt}\n"
            f"Net: {net_text}"
        )

        logger.info(
            "balance_report_generated",
            user_id=user_id,
            period=query_period,
            income=balance.income,
            expenses=balance.expenses,
            net=balance.net,
        )

        dispatcher.utter_message(
            json_message={
                "type": "balance",
                "data": {
                    "period": query_period,
                    "income": balance.income,
                    "expenses": balance.expenses,
                    "net": balance.net,
                    "currency": user_currency,
                    "sentiment": sentiment,
                },
                "text": message,
            }
        )

        return []
