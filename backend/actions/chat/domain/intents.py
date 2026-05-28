"""Intent taxonomy for the chat backend."""

from __future__ import annotations

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
