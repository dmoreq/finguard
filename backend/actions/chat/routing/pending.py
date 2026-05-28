"""Regex router for pending confirmation replies (always runs first)."""

from __future__ import annotations

import re
import unicodedata

from actions.chat.domain.intents import Intent, IntentResult

_CONFIRM_RE = re.compile(
    r"^(yes|yeah|yep|confirm|ok|okay|save|looks good|that'?s correct|approve|"
    r"xác nhận|xac nhan|đúng rồi|dung roi|lưu|luu|đồng ý|dong y)\b",
    re.I,
)
_DISCARD_RE = re.compile(
    r"^(no|nope|discard|cancel|delete|never mind|nevermind|reject|"
    r"hủy|huy|bỏ|bo|không|khong|không lưu|khong luu|xóa|xoa)\b",
    re.I,
)
_EDIT_RE = re.compile(
    r"\b(change|edit|update|fix|set|sửa|sua|đổi|doi|chỉnh|chinh)\b",
    re.I,
)


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower().strip())
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


class PendingIntentClassifier:
    """Maps short replies to manage_* intents while a transaction is pending."""

    def classify(self, text: str, *, confirmation_pending: bool = False) -> IntentResult:
        normalized = text.strip()
        if not confirmation_pending or not normalized:
            return IntentResult(Intent.UNKNOWN, 0.0)

        folded = _fold(normalized)
        if _CONFIRM_RE.search(normalized) or _CONFIRM_RE.search(folded):
            return IntentResult(Intent.MANAGE_CONFIRM)
        if _DISCARD_RE.search(normalized) or _DISCARD_RE.search(folded):
            return IntentResult(Intent.MANAGE_DISCARD)
        if (
            _EDIT_RE.search(normalized)
            or _EDIT_RE.search(folded)
            or re.search(r"\b(amount|số tiền|so tien|danh mục|danh muc)\b", normalized, re.I)
        ):
            return IntentResult(Intent.MANAGE_EDIT)
        if re.search(r"\d", normalized):
            return IntentResult(Intent.MANAGE_EDIT, 0.7)
        return IntentResult(Intent.MANAGE_EDIT, 0.5)
