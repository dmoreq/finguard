"""Gemini field extractor error paths and composite LLM fallback (Phase 0)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from actions.chat.extraction.composite_extractor import CompositeFieldExtractor
from actions.chat.extraction.gemini import GeminiFieldExtractor, _parse_json_response
from actions.chat.extraction.schemas import ExtractResult
from actions.chat.settings import ChatSettings


def test_parse_json_response_strips_markdown_fence() -> None:
    payload = _parse_json_response(
        '```json\n{"amount": 12.5, "category": "coffee"}\n```',
    )
    assert payload["amount"] == 12.5
    assert payload["category"] == "coffee"


@pytest.mark.asyncio
async def test_gemini_validation_error_on_invalid_schema() -> None:
    mock_response = MagicMock(text='{"amount": -1, "category": "food"}')
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)

    with (
        patch("google.generativeai.configure"),
        patch("google.generativeai.GenerativeModel", return_value=mock_model),
        patch("google.generativeai.GenerationConfig"),
    ):
        extractor = GeminiFieldExtractor(api_key="test-key")
        result = await extractor.extract_transaction("spent on food")

    assert result.status == "validation_error"
    assert result.source == "llm"
    assert result.error_message


@pytest.mark.asyncio
async def test_gemini_api_error_on_provider_failure() -> None:
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(side_effect=RuntimeError("network down"))

    with (
        patch("google.generativeai.configure"),
        patch("google.generativeai.GenerativeModel", return_value=mock_model),
        patch("google.generativeai.GenerationConfig"),
    ):
        extractor = GeminiFieldExtractor(api_key="test-key")
        result = await extractor.extract_transaction("spent on food")

    assert result.status == "api_error"
    assert result.source == "llm"
    assert "unavailable" in (result.error_message or "").lower()


@pytest.mark.asyncio
async def test_gemini_api_error_on_malformed_json() -> None:
    mock_response = MagicMock(text="not json at all")
    mock_model = MagicMock()
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)

    with (
        patch("google.generativeai.configure"),
        patch("google.generativeai.GenerativeModel", return_value=mock_model),
        patch("google.generativeai.GenerationConfig"),
    ):
        extractor = GeminiFieldExtractor(api_key="test-key")
        result = await extractor.extract_transaction("spent on food")

    assert result.status == "api_error"
    assert result.source == "llm"


@pytest.mark.asyncio
async def test_composite_propagates_llm_validation_error() -> None:
    settings = ChatSettings(LLM_EXTRACT_ENABLED=True, GEMINI_API_KEY="k")
    llm = MagicMock()
    llm.extract_transaction = AsyncMock(
        return_value=ExtractResult(
            status="validation_error",
            source="llm",
            error_message="invalid amount",
        )
    )
    extractor = CompositeFieldExtractor(settings=settings, llm=llm)
    result = await extractor.extract("spent on food")

    assert result.status == "validation_error"
    assert result.source == "llm"


@pytest.mark.asyncio
async def test_composite_propagates_llm_api_error() -> None:
    settings = ChatSettings(LLM_EXTRACT_ENABLED=True, GEMINI_API_KEY="k")
    llm = MagicMock()
    llm.extract_transaction = AsyncMock(
        return_value=ExtractResult(
            status="api_error",
            source="llm",
            error_message="LLM provider unavailable: timeout",
        )
    )
    extractor = CompositeFieldExtractor(settings=settings, llm=llm)
    result = await extractor.extract("spent on food")

    assert result.status == "api_error"
    assert result.source == "llm"
