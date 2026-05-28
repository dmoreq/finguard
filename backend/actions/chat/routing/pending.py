"""Regex router for pending confirmation replies (always runs first)."""

from __future__ import annotations

import re

from actions.chat.domain.intents import Intent, IntentResult

_CONFIRM_RE = re.compile(
    r"^(yes|yeah|yep|confirm|ok|okay|save|looks good|that'?s correct|approve)\b",
    re.I,
)
_DISCARD_RE = re.compile(
    r"^(no|nope|discard|cancel|delete|never mind|nevermind|reject)\b",
    re.I,
)
_EDIT_RE = re.compile(r"\b(change|edit|update|fix|set)\b", re.I)


class PendingIntentClassifier:
    """Maps short replies to manage_* intents while a transaction is pending."""

    def classify(self, text: str, *, confirmation_pending: bool = False) -> IntentResult:
        normalized = text.strip()
        if not confirmation_pending or not normalized:
            return IntentResult(Intent.UNKNOWN, 0.0)

        if _CONFIRM_RE.search(normalized):
            return IntentResult(Intent.MANAGE_CONFIRM)
        if _DISCARD_RE.search(normalized):
            return IntentResult(Intent.MANAGE_DISCARD)
        if _EDIT_RE.search(normalized) or re.search(r"\bamount\b", normalized, re.I):
            return IntentResult(Intent.MANAGE_EDIT)
        return IntentResult(Intent.MANAGE_EDIT, 0.5)
