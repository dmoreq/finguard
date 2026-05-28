"""Action: confirm or update the last pending transaction."""

from typing import Any

from loguru import logger
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.db.client import get_db
from actions.db.queries import get_transaction, update_transaction
from actions.utils.formatting import format_transaction_summary
from actions.utils.pending import clear_pending_slots, get_pending_transaction_ids


class ActionUpdateTransaction(Action):
    """Confirm a pending transaction or apply slot edits."""

    def name(self) -> str:
        return "action_update_transaction"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict]:
        pending = get_pending_transaction_ids(tracker)
        if not pending:
            dispatcher.utter_message(
                text="There's no transaction waiting to confirm. Record one first."
            )
            return []

        user_id, transaction_id = pending
        user_currency = tracker.get_slot("user_currency") or "USD"
        user_timezone = tracker.get_slot("user_timezone") or "UTC"

        updates: dict[str, object] = {"status": "confirmed"}

        if amount := tracker.get_slot("amount"):
            updates["amount"] = amount
        if category := tracker.get_slot("category"):
            updates["category"] = str(category).strip().lower()
        if description := tracker.get_slot("description"):
            updates["description"] = description
        if tx_date := tracker.get_slot("transaction_date"):
            updates["transaction_date"] = tx_date

        try:
            async with get_db() as conn:
                existing = await get_transaction(conn, user_id, transaction_id)
                if not existing:
                    dispatcher.utter_message(text="Couldn't find that transaction.")
                    return []

                if updates.get("status") == "confirmed":
                    if existing.status == "confirmed":
                        row = existing
                    elif existing.status != "pending_confirmation":
                        dispatcher.utter_message(
                            text="That transaction is no longer waiting to confirm."
                        )
                        return clear_pending_slots()
                    else:
                        row = await update_transaction(conn, user_id, transaction_id, updates)
                else:
                    row = await update_transaction(conn, user_id, transaction_id, updates)
        except Exception as e:
            logger.exception(
                "update_transaction_failed",
                user_id=user_id,
                tx_id=transaction_id,
                error=str(e),
            )
            dispatcher.utter_message(text="Sorry, I couldn't update that transaction.")
            return []

        if not row:
            dispatcher.utter_message(text="Couldn't find that transaction.")
            return []

        summary = format_transaction_summary(
            float(row.amount),
            row.category,
            row.transaction_date,
            row.currency or user_currency,
            user_timezone,
        )
        dispatcher.utter_message(text=f"Saved — {summary}. ✓")

        return clear_pending_slots()
