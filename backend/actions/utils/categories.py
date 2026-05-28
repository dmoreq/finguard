"""Category slug normalization and Vietnamese hint mapping."""

from __future__ import annotations

import re
import unicodedata

# Vietnamese hints → English slug stored in DB
_VI_HINTS: dict[str, str] = {
    "an uong": "dining",
    "ăn uống": "dining",
    "an trua": "dining",
    "ăn trưa": "dining",
    "an sang": "dining",
    "ăn sáng": "dining",
    "ca phe": "dining",
    "cà phê": "dining",
    "cafe": "dining",
    "di lai": "transport",
    "đi lại": "transport",
    "grab": "transport",
    "xang": "transport",
    "xăng": "transport",
    "taxi": "transport",
    "cho": "groceries",
    "chợ": "groceries",
    "di cho": "groceries",
    "đi chợ": "groceries",
    "luong": "salary",
    "lương": "salary",
    "tien luong": "salary",
    "tiền lương": "salary",
    "thuong": "salary",
    "thưởng": "salary",
    "tien nha": "rent",
    "tiền nhà": "rent",
    "thue nha": "rent",
    "thuê nhà": "rent",
    "dien": "utilities",
    "điện": "utilities",
    "tien dien": "utilities",
    "tiền điện": "utilities",
    "nuoc": "utilities",
    "nước": "utilities",
    "freelance": "freelance",
}

_KNOWN_EN = (
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
    "salary",
    "freelance",
    "entertainment",
    "shopping",
    "health",
    "bills",
    "travel",
)


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower().strip())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def normalize_category(value: str) -> str:
    return value.strip().lower()


def map_vietnamese_hint(text: str) -> str | None:
    folded = _fold(text)
    for hint, slug in sorted(_VI_HINTS.items(), key=lambda x: -len(x[0])):
        if _fold(hint) in folded or hint in text.lower():
            return slug
    return None


def parse_category_from_text(text: str) -> str | None:
    vi = map_vietnamese_hint(text)
    if vi:
        return vi
    lower = text.lower()
    for cat in _KNOWN_EN:
        if cat in lower:
            return "groceries" if cat == "grocery" else cat
    return None


def category_after_for(text: str) -> str | None:
    """English 'on/for X' and Vietnamese 'cho X' patterns."""
    for pattern in (
        re.compile(r"\b(?:on|for)\s+([a-z][a-z\s]{1,24}?)(?:\s+yesterday|\s+today|$|\.)", re.I),
        re.compile(r"\b(?:cho|mua|trả|tra)\s+([^\d,.]{2,24}?)(?:\s+hôm nay|\s+hom nay|$|\.)", re.I),
    ):
        match = pattern.search(text)
        if match:
            fragment = match.group(1).strip().lower()
            mapped = map_vietnamese_hint(fragment) or parse_category_from_text(fragment)
            if mapped:
                return mapped
            if fragment and re.search(r"[a-z]", fragment, re.I):
                return normalize_category(fragment)
    return parse_category_from_text(text)


def display_label(slug: str, locale: str = "vi") -> str:
    loc = locale.split("-")[0].lower() if locale else "vi"
    vi_labels = {
        "dining": "Ăn uống",
        "groceries": "Chợ / siêu thị",
        "transport": "Đi lại",
        "salary": "Lương",
        "rent": "Tiền nhà",
        "utilities": "Tiện ích",
        "freelance": "Freelance",
        "coffee": "Cà phê",
        "entertainment": "Giải trí",
        "shopping": "Mua sắm",
        "health": "Sức khỏe",
        "bills": "Hóa đơn",
        "travel": "Du lịch",
    }
    if loc == "vi" and slug in vi_labels:
        return vi_labels[slug]
    return slug.replace("-", " ").title()
