"""Structured transaction extraction via Gemini JSON (P2)."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from actions.chat.extraction.schemas import ExtractResult


class TransactionExtractSchema(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1)
    description: str | None = None
    transaction_type: str | None = None


def _parse_json_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


class GeminiFieldExtractor:
    """LLM extraction using Gemini structured JSON (implements LlmFieldExtractor)."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._model = model

    async def extract_transaction(self, text: str) -> ExtractResult:
        try:
            import google.generativeai as genai  # type: ignore[import-untyped]

            genai.configure(api_key=self._api_key)  # type: ignore[attr-defined]
            model = genai.GenerativeModel(self._model)  # type: ignore[attr-defined]
            prompt = (
                "Extract expense or income transaction fields from the user message. "
                "Return JSON only with keys: amount (positive number), category (string), "
                "description (optional string or null), transaction_type (expense or income). "
                f"Message: {text}"
            )
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(  # type: ignore[attr-defined]
                    response_mime_type="application/json",
                ),
            )
            raw = response.text or ""
            payload = _parse_json_response(raw)
            parsed = TransactionExtractSchema.model_validate(payload)
            fields: dict[str, Any] = {
                "amount": parsed.amount,
                "category": parsed.category.lower().strip(),
            }
            if parsed.description:
                fields["description"] = parsed.description
            if parsed.transaction_type in ("expense", "income"):
                fields["transaction_type"] = parsed.transaction_type
            return ExtractResult(status="success", fields=fields, source="llm")
        except ValidationError as exc:
            return ExtractResult(
                status="validation_error",
                source="llm",
                error_message=str(exc),
            )
        except Exception as exc:
            return ExtractResult(
                status="api_error",
                source="llm",
                error_message=f"LLM provider unavailable: {exc}",
            )
