"""Composition root for the chat backend."""

from __future__ import annotations

from actions.chat.dialogue.engine import DialogueEngine
from actions.chat.routing.composite import CompositeIntentRouter


def create_dialogue_engine() -> DialogueEngine:
    """Build the default production dialogue engine."""
    router = CompositeIntentRouter()
    return DialogueEngine(router=router)


_default_engine: DialogueEngine | None = None


def get_dialogue_engine() -> DialogueEngine:
    global _default_engine
    if _default_engine is None:
        _default_engine = create_dialogue_engine()
    return _default_engine


def reset_dialogue_engine() -> None:
    """Reset singleton (tests)."""
    global _default_engine
    _default_engine = None
