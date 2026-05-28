"""Routing contracts."""

from __future__ import annotations

from typing import Protocol

from actions.chat.domain.intents import IntentResult


class IntentClassifier(Protocol):
    """Classifies user text into a financial chat intent."""

    def classify(self, text: str, *, confirmation_pending: bool = False) -> IntentResult:
        """Return intent and confidence for the utterance."""
        ...
