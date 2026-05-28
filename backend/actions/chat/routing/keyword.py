"""Keyword and regex intent classifier (no LLM, no embeddings)."""

from __future__ import annotations

import re

from actions.chat.domain.intents import Intent, IntentResult

_INCOME_ONLY = ("got paid", "salary", "bonus", "freelance", "received", "income")
_EXPENSE_STRONG = ("spent", "spend", "bought", "purchase")

_INTENT_KEYWORDS: list[tuple[Intent, tuple[str, ...]]] = [
    (Intent.LOG_INCOME, _INCOME_ONLY),
    (
        Intent.LOG_EXPENSE,
        _EXPENSE_STRONG + ("paid", "groceries", "coffee", "lunch"),
    ),
    (Intent.CHECK_BALANCE, ("balance", "net", "income vs", "earn", "earned")),
    (
        Intent.ANALYZE_SPENDING,
        ("spending", "spent last", "expenses", "breakdown", "by category", "how much did i spend"),
    ),
    (
        Intent.LIST_TRANSACTIONS,
        ("recent transaction", "transaction history", "what did i record", "list transaction"),
    ),
    (Intent.CHITCHAT, ("hello", "hi", "hey", "thanks", "thank you", "help")),
]


class KeywordIntentClassifier:
    """Open-domain intent classification via keywords and patterns."""

    def classify(self, text: str, *, confirmation_pending: bool = False) -> IntentResult:
        del confirmation_pending  # pending handled by CompositeIntentRouter
        normalized = text.strip()
        if not normalized:
            return IntentResult(Intent.UNKNOWN, 0.0)

        lower = normalized.lower()

        analyze = (
            r"how much did i spend|spending breakdown|show my .* spending|"
            r"expenses?\s+last|biggest expenses"
        )
        if re.search(analyze, lower):
            return IntentResult(Intent.ANALYZE_SPENDING)
        if re.search(r"\bbalance\b|income vs|how much did i earn", lower):
            return IntentResult(Intent.CHECK_BALANCE)
        if re.search(r"recent transaction|transaction history|what did i record", lower):
            return IntentResult(Intent.LIST_TRANSACTIONS)

        if any(k in lower for k in _INCOME_ONLY):
            return IntentResult(Intent.LOG_INCOME)
        if any(k in lower for k in _EXPENSE_STRONG):
            return IntentResult(Intent.LOG_EXPENSE)
        if "paid" in lower and not any(k in lower for k in _INCOME_ONLY):
            return IntentResult(Intent.LOG_EXPENSE)

        best: Intent | None = None
        best_score = 0
        for intent, keywords in _INTENT_KEYWORDS:
            score = sum(1 for kw in keywords if kw in lower)
            if score > best_score:
                best_score = score
                best = intent

        if best and best_score > 0:
            return IntentResult(best, min(1.0, best_score / 3))

        amount_hints = ("spent", "paid", "bought", "$", "k")
        if re.search(r"\d", lower) and any(w in lower for w in amount_hints):
            return IntentResult(Intent.LOG_EXPENSE, 0.6)

        return IntentResult(Intent.UNKNOWN, 0.0)
