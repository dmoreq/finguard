"""Action: record a new transaction after CALM collects all slots."""

from typing import Any, Literal, cast

from loguru import logger
from pydantic import BaseModel, field_validator
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.db.client import get_supabase
from actions.db.queries import insert_transaction
from actions.models.transaction import TransactionInsert
from actions.utils.categories import normalize_category
from actions.utils.dates import parse_relative_date
from actions.utils.formatting import format_transaction_summary


class RecordTransactionSlots(BaseModel):
    """Validates slots extracted by CALM before DB write."""

    amount: float
    category: str
    description: str | None = None
    transaction_date: str | None = None
    transaction_type: str = "expense"
    user_id: str
    user_currency: str = "USD"
    user_timezone: str = "UTC"

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def normalize_category_field(cls, v: str) -> str:
        return normalize_category(v)


class ActionRecordTransaction(Action):
    """Record a new transaction (income or expense) to the database."""

    def name(self) -> str:
        return "action_record_transaction"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict]:
        """Execute the action: validate slots, parse date, insert to Supabase."""
        transaction_type = tracker.active_flow_metadata.get("transaction_type", "expense")

        try:
            slots = RecordTransactionSlots(
                amount=tracker.get_slot("amount"),
                category=tracker.get_slot("category"),
                description=tracker.get_slot("description"),
                transaction_date=tracker.get_slot("transaction_date"),
                transaction_type=transaction_type,
                user_id=tracker.get_slot("user_id"),
                user_currency=tracker.get_slot("user_currency") or "USD",
                user_timezone=tracker.get_slot("user_timezone") or "UTC",
            )
        except ValueError as e:
            logger.warning(
                "slot_validation_failed",
                error=str(e),
                sender=tracker.sender_id,
                flow=tracker.active_flow_name,
            )
            dispatcher.utter_message(text=f"I couldn't process that: {e}. Could you try again?")
            return []

        # Resolve relative date using pendulum
        resolved_date = parse_relative_date(
            raw=slots.transaction_date,
            timezone=slots.user_timezone,
        )

        tx_type = cast(Literal["income", "expense", "pending"], slots.transaction_type)
        tx = TransactionInsert(
            user_id=slots.user_id,
            type=tx_type,
            amount=slots.amount,
            currency=slots.user_currency,
            category=slots.category,
            description=slots.description,
            transaction_date=resolved_date.to_date_string(),
            status="pending_confirmation",
            source="manual_chat",
            ai_confidence=tracker.get_slot("ai_confidence"),
        )

        # Insert to Supabase
        try:
            async with get_supabase() as client:
                result = await insert_transaction(client, tx)
        except Exception as e:
            logger.exception(
                "transaction_insert_failed",
                user_id=slots.user_id,
                error=str(e),
            )
            dispatcher.utter_message(
                text="Sorry, I couldn't save that transaction. Please try again."
            )
            return []

        # Format confirmation message
        amount_fmt = format_transaction_summary(
            slots.amount,
            slots.category,
            resolved_date.to_date_string(),
            slots.user_currency,
            slots.user_timezone,
        )

        logger.info(
            "transaction_created",
            tx_id=result.id,
            amount=slots.amount,
            category=slots.category,
            date=resolved_date.to_date_string(),
            sender=tracker.sender_id,
        )

        # Send transaction card as JSON message
        dispatcher.utter_message(
            json_message={
                "type": "transaction_pending",
                "transaction": {
                    "id": result.id,
                    "type": slots.transaction_type,
                    "amount": slots.amount,
                    "currency": slots.user_currency,
                    "category": slots.category,
                    "description": slots.description,
                    "date": resolved_date.to_date_string(),
                },
                "text": f"Got it — {amount_fmt}. Confirm or edit?",
            }
        )

        return [
            SlotSet("last_transaction_id", result.id),
            SlotSet("confirmation_pending", True),
        ]
