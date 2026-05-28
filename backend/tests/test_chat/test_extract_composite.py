"""Composite field extractor tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from actions.chat.extraction.composite_extractor import CompositeFieldExtractor
from actions.chat.extraction.schemas import ExtractResult
from actions.chat.settings import ChatSettings


@pytest.mark.asyncio
async def test_rules_complete_skips_llm() -> None:
    settings = ChatSettings(LLM_EXTRACT_ENABLED=True, GEMINI_API_KEY="test-key")
    llm = AsyncMock()
    extractor = CompositeFieldExtractor(settings=settings, llm=llm)
    result = await extractor.extract("spent $45 on groceries")
    assert result.source == "rules"
    assert result.status == "success"
    llm.extract_transaction.assert_not_called()


@pytest.mark.asyncio
async def test_llm_disabled_returns_partial() -> None:
    settings = ChatSettings(LLM_EXTRACT_ENABLED=False)
    extractor = CompositeFieldExtractor(settings=settings)
    result = await extractor.extract("spent on food")
    assert result.status == "partial"
    assert result.source == "rules"


@pytest.mark.asyncio
async def test_llm_fills_missing_fields() -> None:
    settings = ChatSettings(LLM_EXTRACT_ENABLED=True, GEMINI_API_KEY="k")
    llm = MagicMock()
    llm.extract_transaction = AsyncMock(
        return_value=ExtractResult(
            status="success",
            fields={"amount": 50.0, "category": "food"},
            source="llm",
        )
    )
    extractor = CompositeFieldExtractor(settings=settings, llm=llm)
    result = await extractor.extract("spent on food")
    assert result.status == "success"
    assert result.fields["amount"] == 50.0
