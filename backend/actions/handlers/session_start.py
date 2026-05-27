"""Action: initialize session with user context."""

from typing import Any

from loguru import logger
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.db.client import get_supabase


class ActionSessionStart(Action):
    """Initialize a new conversation session with user profile data."""

    def name(self) -> str:
        return "action_session_start"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict]:
        """Execute the action: load user profile and inject into slots."""
        metadata: dict = {}
        if tracker.latest_message and isinstance(tracker.latest_message, dict):
            metadata = tracker.latest_message.get("metadata") or {}

        # Prefer explicit metadata from the Next.js proxy; fall back to sender_id
        user_id = metadata.get("user_id") or tracker.sender_id

        if not user_id:
            logger.warning("session_start_no_user_id", sender=tracker.sender_id)
            return [SlotSet("user_id", "unknown")]

        logger.info("session_start", user_id=user_id)

        try:
            async with get_supabase() as client:
                response = (
                    await client.table("profiles")
                    .select("display_name, currency, timezone")
                    .eq("id", user_id)
                    .single()
                    .execute()
                )

                profile = response.data if response.data else {}
        except Exception as e:
            logger.warning(
                "session_start_profile_fetch_failed",
                user_id=user_id,
                error=str(e),
            )
            profile = {}

        # Extract profile fields with defaults
        currency = profile.get("currency", "USD")
        timezone = profile.get("timezone", "UTC")
        display_name = profile.get("display_name", user_id[:8])

        logger.info(
            "session_initialized",
            user_id=user_id,
            currency=currency,
            timezone=timezone,
            display_name=display_name,
        )

        return [
            SlotSet("user_id", user_id),
            SlotSet("user_currency", currency),
            SlotSet("user_timezone", timezone),
            SlotSet("user_display_name", display_name),
            SlotSet("confirmation_pending", False),
        ]
