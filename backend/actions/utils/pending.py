"""Helpers for pending transaction confirm/discard/edit flows."""

from __future__ import annotations

from rasa_sdk import Tracker


def get_pending_transaction_ids(tracker: Tracker) -> tuple[str, str] | None:
    """
    Return (user_id, transaction_id) when a transaction awaits confirmation.

    Returns None if there is no pending transaction or required slots are missing.
    """
    if not tracker.get_slot("confirmation_pending"):
        return None

    user_id = tracker.get_slot("user_id")
    transaction_id = tracker.get_slot("last_transaction_id")

    if not user_id or not transaction_id:
        return None

    return user_id, transaction_id


def clear_pending_slots() -> list[dict]:
    """Events to clear pending transaction state after confirm or discard."""
    from rasa_sdk.events import SlotSet

    return [
        SlotSet("confirmation_pending", False),
        SlotSet("last_transaction_id", None),
    ]
