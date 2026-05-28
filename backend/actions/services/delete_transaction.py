"""Discard a pending transaction."""

from __future__ import annotations

from pydantic import BaseModel

from actions.chat.respond.payloads import text_message
from actions.db.client import get_db
from actions.db.queries import delete_transaction as db_delete
from actions.services.types import ServiceResult, SessionUpdates
from actions.utils.i18n import t


class DeleteInput(BaseModel):
    user_id: str
    transaction_id: str
    user_locale: str = "vi"


async def delete_transaction(input: DeleteInput) -> ServiceResult:
    try:
        async with get_db() as conn:
            success = await db_delete(conn, input.user_id, input.transaction_id)
    except Exception:
        return ServiceResult(messages=[text_message(t("discard_error", input.user_locale))])

    if success:
        return ServiceResult(
            messages=[text_message(t("discard_ok", input.user_locale))],
            session=SessionUpdates(
                confirmation_pending=False,
                last_transaction_id=None,
                dialogue_phase="idle",
                clear_partial=True,
            ),
        )
    return ServiceResult(messages=[text_message(t("not_found", input.user_locale))])
