"""Build Rasa-compatible webhook payload dicts."""

from __future__ import annotations

from typing import Any


def text_message(content: str) -> dict[str, Any]:
    return {"text": content}


def custom_message(payload: dict[str, Any]) -> dict[str, Any]:
    return {"custom": payload}
