"""Action: delete (discard) a transaction."""

from typing import Any

from loguru import logger
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from actions.db.client import get_supabase
from actions.db.queries import delete_transaction
from actions.utils.pending import clear_pending_slots, get_pending_transaction_ids


class ActionDeleteTransaction(Action):
    """Delete (soft delete via status change) a transaction."""

    def name(self) -> str:
        return "action_delete_transaction"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict]:
        """Execute the action: mark transaction as discarded."""
        pending = get_pending_transaction_ids(tracker)
        if not pending:
            dispatcher.utter_message(text="There's no transaction waiting to discard.")
            return []

        user_id, transaction_id = pending

        logger.info(
            "delete_transaction_requested",
            user_id=user_id,
            tx_id=transaction_id,
            sender=tracker.sender_id,
        )

        try:
            async with get_supabase() as client:
                success = await delete_transaction(client, user_id, transaction_id)
        except Exception as e:
            logger.exception(
                "delete_transaction_failed",
                user_id=user_id,
                tx_id=transaction_id,
                error=str(e),
            )
            dispatcher.utter_message(
                text="Sorry, I couldn't delete that transaction. Please try again."
            )
            return []

        if success:
            logger.info(
                "transaction_deleted",
                user_id=user_id,
                tx_id=transaction_id,
            )
            dispatcher.utter_message(text="Transaction discarded. ✓")
            return clear_pending_slots()
        else:
            logger.warning(
                "delete_transaction_no_rows",
                user_id=user_id,
                tx_id=transaction_id,
            )
            dispatcher.utter_message(text="Couldn't find that transaction.")
            return []
