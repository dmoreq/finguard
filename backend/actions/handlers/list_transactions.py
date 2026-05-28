"""Action: list recent transactions with optional filtering."""

from typing import Any

import pendulum
from loguru import logger
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.db.client import get_db
from actions.db.queries import list_transactions
from actions.utils.formatting import format_currency, format_date_relative


class ActionListTransactions(Action):
    """List recent transactions, optionally filtered by category or period."""

    def name(self) -> str:
        return "action_list_transactions"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict]:
        """Execute the action: fetch and format transaction list."""
        user_id = tracker.get_slot("user_id")
        user_timezone = tracker.get_slot("user_timezone") or "UTC"

        query_period = tracker.get_slot("query_period")
        query_category = tracker.get_slot("query_category")

        logger.info(
            "list_transactions_requested",
            user_id=user_id,
            period=query_period,
            category=query_category,
            sender=tracker.sender_id,
        )

        try:
            async with get_db() as conn:
                transactions = await list_transactions(
                    conn,
                    user_id,
                    limit=20,
                    period=query_period,
                    category=query_category,
                    timezone=user_timezone,
                )
        except Exception as e:
            logger.exception("list_transactions_failed", user_id=user_id, error=str(e))
            dispatcher.utter_message(
                text="Sorry, I couldn't fetch your transactions. Please try again."
            )
            return []

        # Format response
        if not transactions:
            msg = (
                f"No transactions found for {query_period}."
                if query_period
                else "No transactions found."
            )
            if query_category:
                msg = f"No {query_category} transactions found."

            dispatcher.utter_message(text=msg)
            return []

        # Build transaction list
        now = pendulum.now(user_timezone)
        lines = []

        for tx in transactions:
            amount_fmt = format_currency(tx.amount, tx.currency)
            date_fmt = format_date_relative(
                pendulum.parse(tx.transaction_date, tz=user_timezone),
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

            lines.append(
                f"  {icon} {amount_fmt} — {tx.category.title()} on {date_fmt}{status_badge}"
            )

        transaction_list = "\n".join(lines)

        message = (
            f"**Recent transactions:**\n"
            f"{transaction_list}\n\n"
            f"Showing {len(transactions)} most recent."
        )

        logger.info(
            "transaction_list_generated",
            user_id=user_id,
            count=len(transactions),
        )

        dispatcher.utter_message(
            json_message={
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

        return []
