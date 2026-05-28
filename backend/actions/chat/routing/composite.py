"""Facade: pending guard first, then primary classifier."""

from __future__ import annotations

from actions.chat.domain.intents import Intent, IntentResult
from actions.chat.routing.pending import PendingIntentClassifier
from actions.chat.routing.protocol import IntentClassifier


class CompositeIntentRouter:
    """Single entry point for intent classification (Open/Closed for new backends)."""

    def __init__(
        self,
        primary: IntentClassifier,
        pending: PendingIntentClassifier | None = None,
    ) -> None:
        self._primary = primary
        self._pending = pending or PendingIntentClassifier()

    def classify(self, text: str, *, confirmation_pending: bool = False) -> IntentResult:
        if confirmation_pending:
            pending_result = self._pending.classify(text, confirmation_pending=True)
            if pending_result.intent != Intent.UNKNOWN:
                return pending_result
        return self._primary.classify(text, confirmation_pending=False)
