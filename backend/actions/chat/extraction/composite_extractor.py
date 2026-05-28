"""Rules-first extraction with optional LLM fallback."""

from __future__ import annotations

from typing import Any

from actions.chat.extraction.gemini import GeminiFieldExtractor
from actions.chat.extraction.rules import build_transaction_fields
from actions.chat.extraction.rules_extractor import RulesFieldExtractor
from actions.chat.extraction.schemas import ExtractResult
from actions.chat.settings import ChatSettings, get_chat_settings


class CompositeFieldExtractor:
    """Applies rules first; calls LLM only when required slots stay empty."""

    def __init__(
        self,
        settings: ChatSettings | None = None,
        rules: RulesFieldExtractor | None = None,
        llm: GeminiFieldExtractor | None = None,
    ) -> None:
        self._settings = settings or get_chat_settings()
        self._rules = rules or RulesFieldExtractor()
        self._llm = llm

    def _llm_client(self) -> GeminiFieldExtractor | None:
        if not self._settings.llm_extract_active:
            return None
        if self._llm is not None:
            return self._llm
        key = self._settings.gemini_api_key
        if not key:
            return None
        return GeminiFieldExtractor(api_key=key, model=self._settings.gemini_model)

    async def extract(self, text: str) -> ExtractResult:
        rule_fields = self._rules.extract_transaction(text)
        if rule_fields.get("amount") and rule_fields.get("category"):
            return ExtractResult(status="success", fields=rule_fields, source="rules")

        llm = self._llm_client()
        if llm is None:
            return ExtractResult(status="partial", fields=rule_fields, source="rules")

        llm_result = await llm.extract_transaction(text)
        if llm_result.status != "success":
            return llm_result

        merged = {**rule_fields, **llm_result.fields}
        if merged.get("amount") and merged.get("category"):
            return ExtractResult(status="success", fields=merged, source="llm")
        return ExtractResult(status="partial", fields=merged, source="llm")

    def extract_transaction(self, text: str) -> dict[str, Any]:
        """Sync shim for protocol callers — rules only."""
        return build_transaction_fields(text)
