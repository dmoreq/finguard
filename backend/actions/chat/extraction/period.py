"""Rule-based query period extraction from user text."""

from __future__ import annotations

import re
import unicodedata

_VALID_PERIODS = frozenset({"this_month", "last_month", "last_7d", "last_30d", "last_3m", "ytd"})

_PERIOD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("last_month", re.compile(r"last month|tháng trước|thang truoc", re.I)),
    ("this_month", re.compile(r"this month|current month|tháng nay|thang nay", re.I)),
    (
        "last_7d",
        re.compile(r"last 7 days|past week|last week|tuần này|tuan nay|7 ngày|7 ngay", re.I),
    ),
    ("last_30d", re.compile(r"last 30 days|past month|30 ngày|30 ngay", re.I)),
    ("last_3m", re.compile(r"last 3 months|past quarter|3 tháng|3 thang", re.I)),
    ("ytd", re.compile(r"year to date|ytd|this year|từ đầu năm", re.I)),
]

_TREND_HINTS = re.compile(
    r"trend|compare|vs\.?|versus|so với|so voi|tăng|tang|giảm|giam|hơn|hon|kém|kem",
    re.I,
)

_REPORT_CATEGORY_HINTS = (
    "groceries",
    "grocery",
    "dining",
    "transport",
    "entertainment",
    "utilities",
    "shopping",
    "health",
    "bills",
    "travel",
    "salary",
    "freelance",
    "an uong",
    "ăn uống",
    "di lai",
    "đi lại",
    "cho",
    "chợ",
    "luong",
    "lương",
)


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def parse_period_from_text(text: str, default: str = "this_month") -> str:
    folded = _fold(text)
    for period, pattern in _PERIOD_PATTERNS:
        if pattern.search(text) or pattern.search(folded):
            return period
    return default if default in _VALID_PERIODS else "this_month"


def parse_category_hint(text: str) -> str | None:
    from actions.utils.categories import map_vietnamese_hint, parse_category_from_text

    mapped = map_vietnamese_hint(text)
    if mapped:
        return mapped
    lower = text.lower()
    for cat in _REPORT_CATEGORY_HINTS:
        if cat in lower or _fold(cat) in _fold(text):
            return (
                "groceries"
                if cat in ("grocery", "cho", "chợ")
                else (
                    "dining"
                    if cat in ("an uong", "ăn uống")
                    else (
                        "transport"
                        if cat in ("di lai", "đi lại")
                        else ("salary" if cat in ("luong", "lương") else cat)
                    )
                )
            )
    return parse_category_from_text(text)


def wants_trend_comparison(text: str) -> bool:
    return bool(_TREND_HINTS.search(text))


def prior_period(period: str) -> str:
    mapping = {
        "this_month": "last_month",
        "last_month": "last_month",
        "last_7d": "last_7d",
        "last_30d": "last_30d",
        "last_3m": "last_3m",
        "ytd": "ytd",
    }
    return mapping.get(period, "last_month")
