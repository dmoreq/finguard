"""Rule-based parsing primitives (no LLM)."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from actions.utils.categories import category_after_for, map_vietnamese_hint, normalize_category

_AMOUNT_PATTERNS = [
    re.compile(r"\b([\d]{1,3}(?:\.\d{3})+)\s*(?:đ|vnd|dong|đồng)?\b", re.I),
    re.compile(r"\b([\d,]+(?:\.\d+)?)\s*(?:triệu|trieu|tr)\b", re.I),
    re.compile(r"\b([\d,]+(?:\.\d+)?)\s*(?:nghìn|nghin|ngàn|ngan)\b", re.I),
    re.compile(r"\$\s*([\d,]+(?:\.\d+)?)\s*k?\b", re.I),
    re.compile(r"\b([\d,]+(?:\.\d+)?)\s*k\b", re.I),
    re.compile(r"\b([\d,]+(?:\.\d+)?)\s*(?:usd|dollars?)\b", re.I),
    re.compile(r"(?:spent|paid|bought|for|chi|tiêu|tieu|mua|trả|tra)\s+([\d,]+(?:\.\d+)?)", re.I),
]

_EDIT_AMOUNT = re.compile(
    r"\b(?:amount|change\s+amount|set\s+amount|fix\s+amount|"
    r"số\s*tiền|so\s*tien|sửa\s*thành|sua\s*thanh|đổi\s*thành|doi\s*thanh)\s*"
    r"(?:to|is|=|thành|thanh)?\s*([\d,.]+(?:\.\d+)?)\s*(?:k|nghìn|nghin|ngàn|ngan|triệu|trieu|tr|đ|vnd)?",
    re.I,
)
_EDIT_CATEGORY = re.compile(
    r"\b(?:category|danh\s*mục|danh\s*muc)\s*(?:to|is|=|thành|thanh)?\s*"
    r"([a-zà-ỹ\s]{2,24}?)(?:\s+hôm nay|\s+hom nay|$|\.)",
    re.I,
)

_EXPENSE_HINTS = frozenset(
    {
        "spent",
        "spend",
        "bought",
        "paid",
        "purchase",
        "chi tiêu",
        "chi tieu",
        "tiêu",
        "tieu",
        "mua",
        "trả",
        "tra",
    }
)
_INCOME_HINTS = frozenset(
    {
        "paid",
        "salary",
        "bonus",
        "freelance",
        "income",
        "received",
        "lương",
        "luong",
        "thưởng",
        "thuong",
        "nhận",
        "nhan",
        "thu nhập",
        "thu nhap",
    }
)


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def _scale_amount(raw: str, matched: re.Match[str], full_text: str) -> float:
    value = (
        float(raw.replace(",", "").replace(".", ""))
        if re.fullmatch(r"[\d.]+", raw.replace(",", "")) and raw.count(".") > 1
        else float(raw.replace(",", ""))
    )
    span = full_text[matched.start() : matched.end()].lower()
    folded_span = _fold(span)
    if "triệu" in folded_span or "trieu" in folded_span or re.search(r"\btr\b", folded_span):
        value *= 1_000_000
    elif (
        any(x in folded_span for x in ("nghìn", "nghin", "ngàn", "ngan"))
        or "k" in span
        and value < 1000
    ):
        value *= 1_000
    return round(value, 2)


def parse_amount(text: str) -> float | None:
    for pattern in _AMOUNT_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        raw = match.group(1)
        if re.match(r"[\d]{1,3}(?:\.\d{3})+", raw):
            value = float(raw.replace(".", ""))
        else:
            value = _scale_amount(raw, match, text)
        if value > 0:
            return round(value, 2)
    return None


def parse_category(text: str) -> str | None:
    return category_after_for(text)


def infer_transaction_type(text: str) -> str:
    lower = text.lower()
    folded = _fold(lower)
    if any(h in lower or _fold(h) in folded for h in _INCOME_HINTS) and not any(
        h in lower or _fold(h) in folded for h in ("chi tiêu", "chi tieu", "spent")
    ):
        if "nhận lương" in lower or "nhan luong" in folded or "lương" in lower or "luong" in folded:
            return "income"
        if any(x in lower for x in ("bonus", "thưởng", "thuong", "freelance", "paycheck")):
            return "income"
        if "received" in lower or "nhận" in lower:
            return "income"
    if any(h in lower or _fold(h) in folded for h in _EXPENSE_HINTS):
        return "expense"
    return "expense"


def build_transaction_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    amount = parse_amount(text)
    if amount is not None:
        fields["amount"] = amount
    category = parse_category(text)
    if category:
        fields["category"] = normalize_category(category)
    fields["transaction_type"] = infer_transaction_type(text)
    return fields


def build_edit_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    amount = parse_amount(text)
    if amount is None:
        edit_amount = _EDIT_AMOUNT.search(text)
        if edit_amount:
            fragment = edit_amount.group(0)
            amount = parse_amount(fragment) or round(
                float(edit_amount.group(1).replace(",", "")), 2
            )
    if amount is not None:
        fields["amount"] = amount

    category = parse_category(text)
    if category is None:
        edit_category = _EDIT_CATEGORY.search(text)
        if edit_category:
            raw = edit_category.group(1).strip()
            category = map_vietnamese_hint(raw) or normalize_category(raw)
    if category:
        fields["category"] = normalize_category(category)

    if re.search(r"\b(description|note|memo|mô tả|mo ta|ghi chú|ghi chu)\b", text, re.I):
        rest = re.sub(
            r".*\b(?:description|note|memo|mô tả|mo ta|ghi chú|ghi chu)"
            r"\s*(?:to|is|thành|thanh)?\s*",
            "",
            text,
            flags=re.I,
        )
        if rest.strip():
            fields["description"] = rest.strip()[:200]
    return fields
