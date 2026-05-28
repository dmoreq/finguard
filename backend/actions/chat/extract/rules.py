"""Rule-based slot extraction (no LLM)."""

from __future__ import annotations

import re
from typing import Any

_AMOUNT_PATTERNS = [
    re.compile(r"\$\s*([\d,]+(?:\.\d+)?)\s*k?\b", re.I),
    re.compile(r"\b([\d,]+(?:\.\d+)?)\s*k\b", re.I),
    re.compile(r"\b([\d,]+(?:\.\d+)?)\s*(?:usd|dollars?)\b", re.I),
    re.compile(r"(?:spent|paid|bought|for)\s+([\d,]+(?:\.\d+)?)", re.I),
]

_CATEGORY_AFTER_FOR = re.compile(
    r"\b(?:on|for)\s+([a-z][a-z\s]{1,24}?)(?:\s+yesterday|\s+today|$|\.)",
    re.I,
)

_INCOME_HINTS = frozenset({"paid", "salary", "bonus", "freelance", "income", "received"})


def parse_amount(text: str) -> float | None:
    for pattern in _AMOUNT_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        raw = match.group(1).replace(",", "")
        value = float(raw)
        if "k" in text[match.start() : match.end()].lower() and value < 1000:
            value *= 1000
        if value > 0:
            return round(value, 2)
    return None


def parse_category(text: str) -> str | None:
    match = _CATEGORY_AFTER_FOR.search(text)
    if match:
        return match.group(1).strip().lower()
    lower = text.lower()
    for cat in (
        "coffee",
        "groceries",
        "grocery",
        "dining",
        "lunch",
        "dinner",
        "transport",
        "uber",
        "rent",
        "utilities",
    ):
        if cat in lower:
            return "groceries" if cat == "grocery" else cat
    return None


def infer_transaction_type(text: str) -> str:
    lower = text.lower()
    if any(h in lower for h in _INCOME_HINTS) and "spent" not in lower:
        return "income"
    return "expense"


def extract_transaction_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    amount = parse_amount(text)
    if amount is not None:
        fields["amount"] = amount
    category = parse_category(text)
    if category:
        fields["category"] = category
    fields["transaction_type"] = infer_transaction_type(text)
    return fields


def extract_edit_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    amount = parse_amount(text)
    if amount is not None:
        fields["amount"] = amount
    category = parse_category(text)
    if category:
        fields["category"] = category
    if re.search(r"\b(description|note|memo)\b", text, re.I):
        rest = re.sub(r".*\b(?:description|note|memo)\s*(?:to|is)?\s*", "", text, flags=re.I)
        if rest.strip():
            fields["description"] = rest.strip()[:200]
    return fields
