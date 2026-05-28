"""Hybrid router tests."""

from __future__ import annotations

from actions.chat.domain.intents import Intent
from actions.chat.routing.hybrid import HybridIntentClassifier
from actions.chat.routing.keyword import KeywordIntentClassifier
from actions.chat.routing.routes_loader import RouteDefinition
from actions.chat.routing.semantic import SemanticIntentClassifier, StubSemanticRouterBackend


def test_hybrid_falls_back_to_keyword() -> None:
    semantic = SemanticIntentClassifier(
        threshold=0.9,
        routes=[RouteDefinition("log_expense", ("only this phrase",))],
        backend=StubSemanticRouterBackend({}),
    )
    hybrid = HybridIntentClassifier(semantic=semantic, keyword=KeywordIntentClassifier())
    result = hybrid.classify("what's my balance?")
    assert result.intent == Intent.CHECK_BALANCE


def test_hybrid_uses_semantic_when_confident() -> None:
    semantic = SemanticIntentClassifier(
        threshold=0.7,
        routes=[RouteDefinition("log_expense", ("spent fifty on food",))],
        backend=StubSemanticRouterBackend({"spent fifty on food": ("log_expense", 0.95)}),
    )
    hybrid = HybridIntentClassifier(semantic=semantic)
    result = hybrid.classify("spent fifty on food")
    assert result.intent == Intent.LOG_EXPENSE
