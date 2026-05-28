"""Intent routing (backward compatible re-exports)."""

from __future__ import annotations

from actions.chat.domain.intents import Intent, IntentResult
from actions.chat.factory import build_composite_router
from actions.chat.routing.composite import CompositeIntentRouter

_router: CompositeIntentRouter | None = None


def reset_router_cache() -> None:
    global _router
    _router = None


def _router_instance() -> CompositeIntentRouter:
    global _router
    if _router is None:
        _router = build_composite_router()
    return _router


def classify_intent(text: str, *, confirmation_pending: bool = False) -> IntentResult:
    """Classify user text; delegates to the composite router."""
    return _router_instance().classify(text, confirmation_pending=confirmation_pending)


__all__ = ["Intent", "IntentResult", "classify_intent", "CompositeIntentRouter"]
