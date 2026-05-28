"""Embedding-based intent classifier via semantic-router."""

from __future__ import annotations

from typing import Protocol

from actions.chat.domain.intents import Intent, IntentResult
from actions.chat.routing.routes_loader import RouteDefinition, load_route_definitions

ROUTE_TO_INTENT: dict[str, Intent] = {
    "log_expense": Intent.LOG_EXPENSE,
    "log_income": Intent.LOG_INCOME,
    "check_balance": Intent.CHECK_BALANCE,
    "analyze_spending": Intent.ANALYZE_SPENDING,
    "list_transactions": Intent.LIST_TRANSACTIONS,
    "chitchat": Intent.CHITCHAT,
}


class SemanticRouterBackend(Protocol):
    def route(self, text: str) -> tuple[str | None, float]:
        """Return (route_name, similarity_score)."""
        ...


def _build_semantic_router_backend(
    routes: list[RouteDefinition],
) -> SemanticRouterBackend:
    from semantic_router import Route
    from semantic_router.encoders import FastEmbedEncoder
    from semantic_router.routers import SemanticRouter

    layer = SemanticRouter(
        encoder=FastEmbedEncoder(),
        routes=[Route(name=r.name, utterances=list(r.utterances)) for r in routes],
        auto_sync="local",
    )

    class _Backend:
        def route(self, text: str) -> tuple[str | None, float]:
            choice = layer(text)
            if choice is None:
                return None, 0.0
            name = choice.name
            score = float(getattr(choice, "similarity_score", None) or 1.0)
            return name, score

    return _Backend()


class SemanticIntentClassifier:
    """Classifies open-domain text using embedding similarity."""

    def __init__(
        self,
        threshold: float = 0.72,
        routes: list[RouteDefinition] | None = None,
        backend: SemanticRouterBackend | None = None,
    ) -> None:
        self._threshold = threshold
        self._routes = routes or load_route_definitions()
        self._backend = backend or _build_semantic_router_backend(self._routes)

    def classify(self, text: str, *, confirmation_pending: bool = False) -> IntentResult:
        del confirmation_pending
        normalized = text.strip()
        if not normalized:
            return IntentResult(Intent.UNKNOWN, 0.0)

        route_name, score = self._backend.route(normalized)
        if route_name is None or score < self._threshold:
            return IntentResult(Intent.UNKNOWN, score)

        intent = ROUTE_TO_INTENT.get(route_name)
        if intent is None:
            return IntentResult(Intent.UNKNOWN, score)
        return IntentResult(intent, score)


class StubSemanticRouterBackend:
    """Test double: maps exact utterance text to route names."""

    def __init__(self, utterance_to_route: dict[str, tuple[str, float]]) -> None:
        self._map = utterance_to_route

    def route(self, text: str) -> tuple[str | None, float]:
        return self._map.get(text.strip(), (None, 0.0))
