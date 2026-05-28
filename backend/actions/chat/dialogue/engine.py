"""Dialogue engine — orchestrates handlers (deterministic FSM)."""

from __future__ import annotations

from actions.chat.dialogue.collector import TransactionCollector
from actions.chat.dialogue.handlers.dispatch import IntentDispatchHandler
from actions.chat.dialogue.handlers.pending import PendingConfirmationHandler
from actions.chat.dialogue.session_state import apply_session_updates
from actions.chat.domain.intents import Intent
from actions.chat.domain.session import ChatSession
from actions.chat.extraction.rules_extractor import RulesFieldExtractor
from actions.chat.routing.composite import CompositeIntentRouter
from actions.services.profile import load_user_profile
from actions.services.types import ServiceResult


class DialogueEngine:
    """Coordinates routing, collection, and service calls for one user turn."""

    def __init__(
        self,
        router: CompositeIntentRouter | None = None,
        collector: TransactionCollector | None = None,
        pending_handler: PendingConfirmationHandler | None = None,
        dispatch_handler: IntentDispatchHandler | None = None,
    ) -> None:
        router = router or CompositeIntentRouter()
        extractor = RulesFieldExtractor()
        self._router = router
        self._collector = collector or TransactionCollector(extractor)
        self._pending = pending_handler or PendingConfirmationHandler(router, extractor)
        self._dispatch = dispatch_handler or IntentDispatchHandler(router)

    async def handle_turn(self, session: ChatSession, text: str) -> ServiceResult:
        profile = await load_user_profile(session.user_id)
        session.append_turn("user", text)

        if pending_result := await self._pending.handle(session, profile, text):
            apply_session_updates(session, pending_result.session)
            return pending_result

        if session.dialogue_phase == "collecting":
            result = await self._collector.collect(session, profile, text)
            apply_session_updates(session, result.session)
            return result

        routed = self._dispatch.classify_open(text)
        intent = routed.intent

        if intent == Intent.LOG_EXPENSE:
            result = await self._collector.collect(
                session, profile, text, default_transaction_type="expense"
            )
        elif intent == Intent.LOG_INCOME:
            result = await self._collector.collect(
                session, profile, text, default_transaction_type="income"
            )
        else:
            result = await self._dispatch.dispatch(session, profile, text, routed)

        apply_session_updates(session, result.session)
        return result
