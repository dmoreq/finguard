"""Extraction result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ExtractStatus = Literal["success", "partial", "validation_error", "api_error"]
ExtractSource = Literal["rules", "llm", "none"]


@dataclass(frozen=True)
class ExtractResult:
    status: ExtractStatus
    fields: dict[str, Any] = field(default_factory=dict)
    source: ExtractSource = "none"
    error_message: str | None = None

    def is_complete(self) -> bool:
        return bool(self.fields.get("amount")) and bool(self.fields.get("category"))
