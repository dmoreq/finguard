"""Hybrid routing: semantic when confident, otherwise keyword."""

from __future__ import annotations

from actions.chat.domain.intents import Intent, IntentResult
from actions.chat.routing.keyword import KeywordIntentClassifier
from actions.chat.routing.protocol import IntentClassifier
from actions.chat.routing.semantic import SemanticIntentClassifier


class HybridIntentClassifier:
    """Combines semantic and keyword classifiers (Open/Closed)."""

    def __init__(
        self,
        semantic: SemanticIntentClassifier,
        keyword: KeywordIntentClassifier | None = None,
    ) -> None:
        self._semantic = semantic
        self._keyword = keyword or KeywordIntentClassifier()

    def classify(self, text: str, *, confirmation_pending: bool = False) -> IntentResult:
        del confirmation_pending
        semantic_result = self._semantic.classify(text)
        if semantic_result.intent != Intent.UNKNOWN:
            return semantic_result
        return self._keyword.classify(text)


def build_primary_classifier(
    mode: str,
    *,
    threshold: float,
    semantic_backend: SemanticIntentClassifier | None = None,
) -> IntentClassifier:
    keyword = KeywordIntentClassifier()
    if mode == "keyword":
        return keyword
    semantic = semantic_backend or SemanticIntentClassifier(threshold=threshold)
    if mode == "semantic":
        return semantic
    return HybridIntentClassifier(semantic=semantic, keyword=keyword)
