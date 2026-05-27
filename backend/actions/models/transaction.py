"""Pydantic models for financial transactions."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TransactionInsert(BaseModel):
    """Schema for creating a new transaction."""

    user_id: str
    type: Literal["income", "expense", "pending"]
    amount: float = Field(gt=0, description="Amount must be positive")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    transaction_date: str = Field(description="ISO date string: YYYY-MM-DD")
    status: Literal["pending_confirmation", "confirmed", "discarded"] = "pending_confirmation"
    source: Literal["manual_chat", "manual_form", "import", "integration"] = "manual_chat"
    ai_confidence: float | None = Field(default=None, ge=0, le=1)

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        """Round amount to 2 decimal places."""
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        """Normalize category to lowercase."""
        return v.strip().lower()


class TransactionRow(BaseModel):
    """Schema for a transaction row from the database."""

    id: str
    user_id: str
    type: Literal["income", "expense", "pending"]
    amount: float
    currency: str
    category: str
    description: str | None
    transaction_date: str
    status: Literal["pending_confirmation", "confirmed", "discarded"]
    source: Literal["manual_chat", "manual_form", "import", "integration"]
    ai_confidence: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""

    amount: float | None = None
    category: str | None = None
    description: str | None = None
    transaction_date: str | None = None
    status: Literal["pending_confirmation", "confirmed", "discarded"] | None = None

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float | None) -> float | None:
        if v is None:
            return None
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return v.strip().lower()


class SpendingByCategory(BaseModel):
    """Spending totals grouped by category."""

    category: str
    total: float
    count: int = 0


class BalanceSummary(BaseModel):
    """Summary of income, expenses, and net balance."""

    income: float = 0.0
    expenses: float = 0.0
    net: float = 0.0
    currency: str = "USD"
    period: str = "this_month"
