"""Apply service-layer session mutations to chat session."""

from __future__ import annotations

from actions.chat.domain.session import ChatSession
from actions.services.types import SessionUpdates


def apply_session_updates(session: ChatSession, updates: SessionUpdates | None) -> None:
    if not updates:
        return
    if updates.dialogue_phase is not None:
        session.dialogue_phase = updates.dialogue_phase
    if updates.confirmation_pending is not None:
        session.confirmation_pending = updates.confirmation_pending
    if updates.last_transaction_id is not None:
        session.last_transaction_id = updates.last_transaction_id
    if updates.clear_partial:
        session.partial_transaction = {}
    elif updates.partial_transaction is not None:
        session.partial_transaction = updates.partial_transaction
