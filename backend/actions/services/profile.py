"""User profile helpers for chat."""

from __future__ import annotations

from pydantic import BaseModel

from actions.db.client import get_db
from actions.db.queries import get_profile


class UserProfile(BaseModel):
    user_id: str
    currency: str = "USD"
    timezone: str = "UTC"


async def load_user_profile(user_id: str) -> UserProfile:
    async with get_db() as conn:
        row = await get_profile(conn, user_id)
    return UserProfile(
        user_id=user_id,
        currency=row.get("currency") or "USD",
        timezone=row.get("timezone") or "UTC",
    )
