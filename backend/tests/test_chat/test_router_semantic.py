"""Semantic router tests (mocked backend, no model download)."""

from __future__ import annotations

from actions.chat.domain.intents import Intent
from actions.chat.routing.routes_loader import RouteDefinition
from actions.chat.routing.semantic import SemanticIntentClassifier, StubSemanticRouterBackend


def test_semantic_maps_route_to_intent() -> None:
    backend = StubSemanticRouterBackend({"spent fifty on food": ("log_expense", 0.9)})
    classifier = SemanticIntentClassifier(
        threshold=0.7,
        routes=[RouteDefinition("log_expense", ("spent fifty on food",))],
        backend=backend,
    )
    result = classifier.classify("spent fifty on food")
    assert result.intent == Intent.LOG_EXPENSE


def test_semantic_below_threshold_is_unknown() -> None:
    backend = StubSemanticRouterBackend({"hello": ("chitchat", 0.5)})
    classifier = SemanticIntentClassifier(
        threshold=0.72,
        routes=[RouteDefinition("chitchat", ("hello",))],
        backend=backend,
    )
    result = classifier.classify("hello")
    assert result.intent == Intent.UNKNOWN
