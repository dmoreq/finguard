"""Intent router tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from actions.chat.router import Intent, classify_intent

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "utterances.jsonl"


@pytest.mark.parametrize(
    ("text", "pending", "expected"),
    [
        ("I spent $5 on coffee", False, Intent.LOG_EXPENSE),
        ("got paid $2000", False, Intent.LOG_INCOME),
        ("what's my balance?", False, Intent.CHECK_BALANCE),
        ("how much did I spend last month?", False, Intent.ANALYZE_SPENDING),
        ("show recent transactions", False, Intent.LIST_TRANSACTIONS),
        ("confirm", True, Intent.MANAGE_CONFIRM),
        ("discard", True, Intent.MANAGE_DISCARD),
        ("change amount to 50", True, Intent.MANAGE_EDIT),
    ],
)
def test_classify_intent_examples(text: str, pending: bool, expected: Intent) -> None:
    result = classify_intent(text, confirmation_pending=pending)
    assert result.intent == expected


def test_utterance_bank_accuracy() -> None:
    import os

    if not FIXTURE.exists():
        pytest.skip("utterances fixture missing")
    if os.environ.get("CI_NO_SEMANTIC", "").lower() in ("1", "true", "yes"):
        pytest.skip("CI_NO_SEMANTIC set")

    total = 0
    correct = 0
    for line in FIXTURE.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        expected = Intent(row["intent"])
        pending = bool(row.get("confirmation_pending")) or expected.value.startswith("manage_")
        result = classify_intent(row["text"], confirmation_pending=pending)
        total += 1
        if result.intent == expected:
            correct += 1

    assert total > 0
    # Target 0.95 with hybrid router locally; keyword-only gate stays 0.85 in CI.
    minimum = 0.95 if os.environ.get("ROUTER_MODE", "keyword") == "hybrid" else 0.85
    assert correct / total >= minimum
