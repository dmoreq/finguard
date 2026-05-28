"""Intent routing (backward compatible re-exports)."""

from __future__ import annotations

from actions.chat.domain.intents import Intent, IntentResult
from actions.chat.routing.composite import CompositeIntentRouter

_default_router = CompositeIntentRouter()


def classify_intent(text: str, *, confirmation_pending: bool = False) -> IntentResult:
    """Classify user text; delegates to the composite router."""
    return _default_router.classify(text, confirmation_pending=confirmation_pending)


__all__ = ["Intent", "IntentResult", "classify_intent", "CompositeIntentRouter"]
