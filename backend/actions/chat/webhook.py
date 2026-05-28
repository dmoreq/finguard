"""REST webhook handler (Rasa-compatible)."""

from __future__ import annotations

from typing import Any

from actions.chat.factory import get_dialogue_engine
from actions.chat.session_store import get_session, save_session


async def handle_webhook(payload: dict[str, Any]) -> list[dict[str, Any]]:
    sender = str(payload.get("sender") or "local-user")
    message = str(payload.get("message") or "").strip()
    metadata = payload.get("metadata") or {}
    user_id = str(metadata.get("user_id") or sender)

    if not message:
        return [{"text": "Please send a message."}]

    session = await get_session(sender, user_id)
    result = await get_dialogue_engine().handle_turn(session, message)
    await save_session(sender, session)
    return result.messages
