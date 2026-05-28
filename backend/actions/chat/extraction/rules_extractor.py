"""Rule-based implementation of extraction protocols."""

from __future__ import annotations

from typing import Any

from actions.chat.extraction import rules


class RulesFieldExtractor:
    """Extracts transaction and edit fields using regex and keyword rules."""

    def extract_transaction(self, text: str) -> dict[str, Any]:
        return rules.build_transaction_fields(text)

    def extract_edit(self, text: str) -> dict[str, Any]:
        return rules.build_edit_fields(text)
