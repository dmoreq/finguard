"""Chat backend configuration (validated at boundary)."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

RouterMode = Literal["keyword", "semantic", "hybrid"]


class ChatSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    router_mode: RouterMode = Field(default="hybrid", alias="ROUTER_MODE")
    semantic_router_threshold: float = Field(default=0.72, alias="SEMANTIC_ROUTER_THRESHOLD")
    llm_extract_enabled: bool = Field(default=False, alias="LLM_EXTRACT_ENABLED")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")

    @property
    def ci_no_semantic(self) -> bool:
        return os.environ.get("CI_NO_SEMANTIC", "").strip().lower() in ("1", "true", "yes")

    @property
    def llm_extract_active(self) -> bool:
        return self.llm_extract_enabled and bool(self.gemini_api_key)


@lru_cache
def get_chat_settings() -> ChatSettings:
    return ChatSettings()
