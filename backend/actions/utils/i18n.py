"""Locale-aware template strings (vi primary, en fallback)."""

from __future__ import annotations

from typing import Any

DEFAULT_LOCALE = "vi"

_STRINGS: dict[str, dict[str, str]] = {
    "record_pending": {
        "vi": "Đã ghi — {summary}. Xác nhận hoặc sửa?",
        "en": "Got it — {summary}. Confirm or edit?",
    },
    "record_error": {
        "vi": "Xin lỗi, không thể lưu giao dịch. Vui lòng thử lại.",
        "en": "Sorry, I couldn't save that transaction. Please try again.",
    },
    "confirm_saved": {
        "vi": "Đã lưu — {summary}. ✓",
        "en": "Saved — {summary}. ✓",
    },
    "update_pending": {
        "vi": "Đã cập nhật — {summary}. Xác nhận hoặc sửa?",
        "en": "Updated — {summary}. Confirm or edit?",
    },
    "discard_ok": {
        "vi": "Đã hủy giao dịch. ✓",
        "en": "Transaction discarded. ✓",
    },
    "discard_error": {
        "vi": "Xin lỗi, không thể hủy giao dịch. Vui lòng thử lại.",
        "en": "Sorry, I couldn't delete that transaction. Please try again.",
    },
    "not_found": {
        "vi": "Không tìm thấy giao dịch đó.",
        "en": "Couldn't find that transaction.",
    },
    "update_error": {
        "vi": "Xin lỗi, không thể cập nhật giao dịch.",
        "en": "Sorry, I couldn't update that transaction.",
    },
    "nothing_to_update": {
        "vi": "Không có gì để cập nhật.",
        "en": "Nothing to update.",
    },
    "no_longer_pending": {
        "vi": "Giao dịch này không còn chờ xác nhận.",
        "en": "That transaction is no longer waiting to confirm.",
    },
    "edit_prompt": {
        "vi": "Bạn muốn sửa gì? Ví dụ: 'sửa thành 60k' hoặc 'đổi danh mục thành ăn uống'.",
        "en": "What should I change? You can say e.g. 'change amount to 50' or 'category dining'.",
    },
    "missing_amount": {
        "vi": "Bao nhiêu tiền? (ví dụ: 50k hoặc 100 nghìn)",
        "en": "How much was it? (e.g. 45 or $12.50)",
    },
    "missing_category": {
        "vi": "Danh mục nào? (ví dụ: ăn uống, đi lại, lương)",
        "en": "What {kind} was that? (e.g. groceries, dining, salary)",
    },
    "missing_more": {
        "vi": "Bạn có thể nói rõ hơn không?",
        "en": "Could you tell me a bit more?",
    },
    "extract_validation": {
        "vi": "Cần số tiền dương và danh mục. Vui lòng thử lại.",
        "en": "I need a positive amount and a category. Please try again.",
    },
    "extract_api_error": {
        "vi": "Không thể phân tích tin nhắn. Vui lòng thử lại hoặc nói rõ hơn.",
        "en": "I couldn't reach the extraction service. Please try again or be more specific.",
    },
    "balance_error": {
        "vi": "Xin lỗi, không thể lấy số dư. Vui lòng thử lại.",
        "en": "Sorry, I couldn't fetch your balance. Please try again.",
    },
    "spending_error": {
        "vi": "Xin lỗi, không thể lấy báo cáo chi tiêu. Vui lòng thử lại.",
        "en": "Sorry, I couldn't fetch your spending data. Please try again.",
    },
    "spending_empty": {
        "vi": "Không có chi tiêu trong {period}.",
        "en": "No expenses found for {period}.",
    },
    "spending_empty_category": {
        "vi": "Không có chi tiêu {category} trong {period}.",
        "en": "No expenses found for {category} in {period}.",
    },
    "list_error": {
        "vi": "Xin lỗi, không thể lấy danh sách giao dịch.",
        "en": "Sorry, I couldn't fetch your transactions. Please try again.",
    },
    "list_empty": {
        "vi": "Không có giao dịch nào.",
        "en": "No transactions found.",
    },
    "list_empty_period": {
        "vi": "Không có giao dịch trong {period}.",
        "en": "No transactions found for {period}.",
    },
    "list_empty_category": {
        "vi": "Không có giao dịch {category}.",
        "en": "No {category} transactions found.",
    },
    "chitchat": {
        "vi": (
            "Xin chào! Tôi có thể ghi chi tiêu, thu nhập, xem số dư và báo cáo chi tiêu. "
            'Thử: "Chi tiêu 50k cà phê".'
        ),
        "en": (
            "Hi! I can log expenses and income, show your balance, or summarize spending. "
            'Try: "spent $12 on coffee".'
        ),
    },
    "unknown": {
        "vi": (
            'Tôi chưa hiểu. Thử ghi giao dịch (ví dụ: "Chi tiêu 80k ăn trưa") '
            'hoặc hỏi "Số dư tháng này".'
        ),
        "en": (
            "I'm not sure what you mean. Try logging a transaction "
            '(e.g. "spent $20 on groceries") or ask "what\'s my balance?".'
        ),
    },
    "empty_message": {
        "vi": "Vui lòng gửi tin nhắn.",
        "en": "Please send a message.",
    },
    "income_source": {"vi": "nguồn thu", "en": "income source"},
    "category_kind": {"vi": "danh mục", "en": "category"},
}


def normalize_locale(locale: str | None) -> str:
    if not locale:
        return DEFAULT_LOCALE
    base = locale.strip().lower().split("-")[0]
    return base if base in ("vi", "en") else DEFAULT_LOCALE


def t(key: str, locale: str | None = None, **kwargs: Any) -> str:
    loc = normalize_locale(locale)
    bucket = _STRINGS.get(key, {})
    template = bucket.get(loc) or bucket.get("en") or bucket.get("vi") or key
    if kwargs:
        return template.format(**kwargs)
    return template


def period_label(period: str, locale: str | None = None) -> str:
    loc = normalize_locale(locale)
    labels_vi = {
        "this_month": "Tháng này",
        "last_month": "Tháng trước",
        "last_7d": "7 ngày qua",
        "last_30d": "30 ngày qua",
        "last_3m": "3 tháng qua",
        "ytd": "Từ đầu năm",
    }
    labels_en = {
        "this_month": "This month",
        "last_month": "Last month",
        "last_7d": "Last 7 days",
        "last_30d": "Last 30 days",
        "last_3m": "Last 3 months",
        "ytd": "Year to date",
    }
    labels = labels_vi if loc == "vi" else labels_en
    return labels.get(period, period.replace("_", " "))
