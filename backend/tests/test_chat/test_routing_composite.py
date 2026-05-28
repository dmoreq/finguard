"""Composite intent router tests."""

from __future__ import annotations

from unittest.mock import MagicMock

from actions.chat.domain.intents import Intent, IntentResult
from actions.chat.routing.composite import CompositeIntentRouter
from actions.chat.routing.keyword import KeywordIntentClassifier
from actions.chat.routing.pending import PendingIntentClassifier


def test_pending_guard_overrides_primary_chitchat() -> None:
    primary = MagicMock()
    primary.classify.return_value = IntentResult(Intent.CHITCHAT, 0.99)
    router = CompositeIntentRouter(primary=primary, pending=PendingIntentClassifier())
    result = router.classify("yes", confirmation_pending=True)
    assert result.intent == Intent.MANAGE_CONFIRM
    primary.classify.assert_not_called()


def test_open_domain_delegates_to_primary() -> None:
    router = CompositeIntentRouter(
        primary=KeywordIntentClassifier(),
        pending=PendingIntentClassifier(),
    )
    result = router.classify("what's my balance?", confirmation_pending=False)
    assert result.intent == Intent.CHECK_BALANCE
