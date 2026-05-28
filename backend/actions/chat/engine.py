"""Dialogue engine entry point (backward compatible)."""

from __future__ import annotations

from actions.chat.domain.session import ChatSession
from actions.chat.factory import get_dialogue_engine
from actions.services.types import ServiceResult


async def handle_turn(session: ChatSession, text: str) -> ServiceResult:
    return await get_dialogue_engine().handle_turn(session, text)
