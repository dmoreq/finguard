"""Keyword and regex intent classifier (no LLM, no embeddings)."""

from __future__ import annotations

import re
import unicodedata

from actions.chat.domain.intents import Intent, IntentResult

_VI_EXPENSE = ("chi tiêu", "chi tieu", "tiêu", "tieu", "mua", "trả", "tra")
_VI_INCOME = (
    "lương",
    "luong",
    "nhận lương",
    "nhan luong",
    "thưởng",
    "thuong",
    "thu nhập",
    "thu nhap",
)
_VI_BALANCE = ("số dư", "so du", "thu chi", "còn bao nhiêu", "con bao nhieu")
_VI_SPENDING = ("chi bao nhiêu", "chi bao nhieu", "chi tiêu theo", "tổng chi", "tong chi")
_VI_LIST = ("giao dịch", "giao dich", "lịch sử", "lich su", "danh sách giao dịch")

_INCOME_ONLY = ("got paid", "salary", "bonus", "freelance", "received", "income") + _VI_INCOME
_EXPENSE_STRONG = ("spent", "spend", "bought", "purchase") + _VI_EXPENSE

_INTENT_KEYWORDS: list[tuple[Intent, tuple[str, ...]]] = [
    (Intent.LOG_INCOME, _INCOME_ONLY),
    (Intent.LOG_EXPENSE, _EXPENSE_STRONG + ("paid", "groceries", "coffee", "lunch")),
    (Intent.CHECK_BALANCE, ("balance", "net", "income vs", "earn", "earned") + _VI_BALANCE),
    (
        Intent.ANALYZE_SPENDING,
        ("spending", "spent last", "expenses", "breakdown", "by category", "how much did i spend")
        + _VI_SPENDING,
    ),
    (
        Intent.LIST_TRANSACTIONS,
        ("recent transaction", "transaction history", "what did i record", "list transaction")
        + _VI_LIST,
    ),
    (Intent.CHITCHAT, ("hello", "hi", "hey", "thanks", "thank you", "help", "xin chào", "cảm ơn")),
]


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


class KeywordIntentClassifier:
    """Open-domain intent classification via keywords and patterns."""

    def classify(self, text: str, *, confirmation_pending: bool = False) -> IntentResult:
        del confirmation_pending
        normalized = text.strip()
        if not normalized:
            return IntentResult(Intent.UNKNOWN, 0.0)

        lower = normalized.lower()
        folded = _fold(lower)

        analyze = (
            r"how much did i spend|spending breakdown|show my .* spending|"
            r"expenses?\s+last|biggest expenses|chi bao nhi[eê]u|chi tieu theo"
        )
        if re.search(analyze, lower) or re.search(analyze, folded):
            return IntentResult(Intent.ANALYZE_SPENDING)
        if re.search(r"\bbalance\b|income vs|how much did i earn", lower):
            return IntentResult(Intent.CHECK_BALANCE)
        if any(k in lower or _fold(k) in folded for k in _VI_BALANCE):
            return IntentResult(Intent.CHECK_BALANCE)
        if re.search(r"recent transaction|transaction history|what did i record", lower):
            return IntentResult(Intent.LIST_TRANSACTIONS)
        if any(k in lower or _fold(k) in folded for k in _VI_LIST):
            return IntentResult(Intent.LIST_TRANSACTIONS)

        if any(k in lower or _fold(k) in folded for k in _INCOME_ONLY):
            return IntentResult(Intent.LOG_INCOME)
        if any(k in lower or _fold(k) in folded for k in _EXPENSE_STRONG):
            return IntentResult(Intent.LOG_EXPENSE)
        if "paid" in lower and not any(k in lower for k in _INCOME_ONLY):
            return IntentResult(Intent.LOG_EXPENSE)

        best: Intent | None = None
        best_score = 0
        for intent, keywords in _INTENT_KEYWORDS:
            score = sum(1 for kw in keywords if kw in lower or _fold(kw) in folded)
            if score > best_score:
                best_score = score
                best = intent

        if best and best_score > 0:
            return IntentResult(best, min(1.0, best_score / 3))

        amount_hints = (
            "spent",
            "paid",
            "bought",
            "$",
            "k",
            "k ",
            "triệu",
            "trieu",
            "nghìn",
            "ngàn",
        )
        if re.search(r"\d", lower) and any(w in lower or _fold(w) in folded for w in amount_hints):
            return IntentResult(Intent.LOG_EXPENSE, 0.6)

        return IntentResult(Intent.UNKNOWN, 0.0)
