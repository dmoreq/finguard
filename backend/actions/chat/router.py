"""Keyword-based intent router (no LLM, no embedding model download)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class Intent(StrEnum):
    LOG_EXPENSE = "log_expense"
    LOG_INCOME = "log_income"
    CHECK_BALANCE = "check_balance"
    ANALYZE_SPENDING = "analyze_spending"
    LIST_TRANSACTIONS = "list_transactions"
    MANAGE_CONFIRM = "manage_confirm"
    MANAGE_DISCARD = "manage_discard"
    MANAGE_EDIT = "manage_edit"
    CHITCHAT = "chitchat"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class IntentResult:
    intent: Intent
    confidence: float = 1.0


_CONFIRM_RE = re.compile(
    r"^(yes|yeah|yep|confirm|ok|okay|save|looks good|that'?s correct|approve)\b",
    re.I,
)
_DISCARD_RE = re.compile(
    r"^(no|nope|discard|cancel|delete|never mind|nevermind|reject)\b",
    re.I,
)
_EDIT_RE = re.compile(r"\b(change|edit|update|fix|set)\b", re.I)

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


def classify_intent(text: str, *, confirmation_pending: bool = False) -> IntentResult:
    normalized = text.strip()
    if not normalized:
        return IntentResult(Intent.UNKNOWN, 0.0)

    if confirmation_pending:
        if _CONFIRM_RE.search(normalized):
            return IntentResult(Intent.MANAGE_CONFIRM)
        if _DISCARD_RE.search(normalized):
            return IntentResult(Intent.MANAGE_DISCARD)
        if _EDIT_RE.search(normalized) or re.search(r"\bamount\b", normalized, re.I):
            return IntentResult(Intent.MANAGE_EDIT)
        return IntentResult(Intent.MANAGE_EDIT, 0.5)

    lower = normalized.lower()

    _analyze = (
        r"how much did i spend|spending breakdown|show my .* spending|"
        r"expenses?\s+last|biggest expenses"
    )
    if re.search(_analyze, lower):
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

    if re.search(r"\d", lower) and any(w in lower for w in ("spent", "paid", "bought", "$", "k")):
        return IntentResult(Intent.LOG_EXPENSE, 0.6)

    return IntentResult(Intent.UNKNOWN, 0.0)
