"""Extraction contracts."""

from __future__ import annotations

from typing import Any, Protocol


class TransactionFieldExtractor(Protocol):
    def extract_transaction(self, text: str) -> dict[str, Any]:
        """Extract amount, category, transaction_type, etc."""
        ...


class EditFieldExtractor(Protocol):
    def extract_edit(self, text: str) -> dict[str, Any]:
        """Extract fields the user wants to change on a pending transaction."""
        ...
