"""User profile helpers for chat."""

from __future__ import annotations

from pydantic import BaseModel

from actions.db.client import get_db
from actions.db.queries import get_profile
from actions.utils.i18n import normalize_locale


class UserProfile(BaseModel):
    user_id: str
    currency: str = "VND"
    timezone: str = "Asia/Ho_Chi_Minh"
    locale: str = "vi"

    @property
    def normalized_locale(self) -> str:
        return normalize_locale(self.locale)


async def load_user_profile(user_id: str) -> UserProfile:
    async with get_db() as conn:
        row = await get_profile(conn, user_id)
    return UserProfile(
        user_id=user_id,
        currency=row.get("currency") or "VND",
        timezone=row.get("timezone") or "Asia/Ho_Chi_Minh",
        locale=row.get("locale") or "vi",
    )
