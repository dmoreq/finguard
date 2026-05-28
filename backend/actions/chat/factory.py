"""Composition root for the chat backend."""

from __future__ import annotations

from actions.chat.dialogue.collector import TransactionCollector
from actions.chat.dialogue.engine import DialogueEngine
from actions.chat.dialogue.handlers.dispatch import IntentDispatchHandler
from actions.chat.dialogue.handlers.pending import PendingConfirmationHandler
from actions.chat.extraction.composite_extractor import CompositeFieldExtractor
from actions.chat.extraction.rules_extractor import RulesFieldExtractor
from actions.chat.routing.composite import CompositeIntentRouter
from actions.chat.routing.hybrid import build_primary_classifier
from actions.chat.settings import get_chat_settings


def build_composite_router() -> CompositeIntentRouter:
    settings = get_chat_settings()
    primary = build_primary_classifier(
        settings.router_mode,
        threshold=settings.semantic_router_threshold,
    )
    return CompositeIntentRouter(primary=primary)


def create_dialogue_engine() -> DialogueEngine:
    """Build the default production dialogue engine."""
    router = build_composite_router()
    extractor = CompositeFieldExtractor()
    collector = TransactionCollector(extractor)
    return DialogueEngine(
        router=router,
        collector=collector,
        pending_handler=PendingConfirmationHandler(router, RulesFieldExtractor()),
        dispatch_handler=IntentDispatchHandler(router),
    )


_default_engine: DialogueEngine | None = None


def get_dialogue_engine() -> DialogueEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = create_dialogue_engine()
    return _default_engine


def reset_dialogue_engine() -> None:
    """Reset singleton (tests)."""
    from actions.chat.router import reset_router_cache

    global _default_engine
    _default_engine = None
    reset_router_cache()
    get_chat_settings.cache_clear()
