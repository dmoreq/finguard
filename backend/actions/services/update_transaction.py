"""Confirm or edit a pending transaction."""

from __future__ import annotations

from pydantic import BaseModel

from actions.chat.respond.payloads import custom_message, text_message
from actions.db.client import get_db
from actions.db.queries import get_transaction
from actions.db.queries import update_transaction as db_update
from actions.services.types import ServiceResult, SessionUpdates
from actions.utils.formatting import format_transaction_summary
from actions.utils.i18n import t


class UpdateInput(BaseModel):
    user_id: str
    transaction_id: str
    user_currency: str = "VND"
    user_timezone: str = "UTC"
    user_locale: str = "vi"
    confirm: bool = True
    amount: float | None = None
    category: str | None = None
    description: str | None = None
    transaction_date: str | None = None


async def update_transaction(input: UpdateInput) -> ServiceResult:
    locale = input.user_locale
    updates: dict[str, object] = {}
    if input.confirm:
        updates["status"] = "confirmed"
    if input.amount is not None:
        updates["amount"] = input.amount
    if input.category is not None:
        updates["category"] = str(input.category).strip().lower()
    if input.description is not None:
        updates["description"] = input.description
    if input.transaction_date is not None:
        updates["transaction_date"] = input.transaction_date

    if not updates:
        return ServiceResult(messages=[text_message(t("nothing_to_update", locale))])

    try:
        async with get_db() as conn:
            existing = await get_transaction(conn, input.user_id, input.transaction_id)
            if not existing:
                return ServiceResult(messages=[text_message(t("not_found", locale))])

            if updates.get("status") == "confirmed":
                if existing.status == "confirmed":
                    row = existing
                elif existing.status != "pending_confirmation":
                    return ServiceResult(
                        messages=[text_message(t("no_longer_pending", locale))],
                        session=SessionUpdates(
                            confirmation_pending=False,
                            last_transaction_id=None,
                            dialogue_phase="idle",
                        ),
                    )
                else:
                    row = await db_update(conn, input.user_id, input.transaction_id, updates)
            else:
                row = await db_update(conn, input.user_id, input.transaction_id, updates)
    except Exception:
        return ServiceResult(messages=[text_message(t("update_error", locale))])

    if not row:
        return ServiceResult(messages=[text_message(t("not_found", locale))])

    if input.confirm:
        summary = format_transaction_summary(
            float(row.amount),
            row.category,
            row.transaction_date,
            row.currency or input.user_currency,
            input.user_timezone,
        )
        return ServiceResult(
            messages=[text_message(t("confirm_saved", locale, summary=summary))],
            session=SessionUpdates(
                confirmation_pending=False,
                last_transaction_id=None,
                dialogue_phase="idle",
                clear_partial=True,
            ),
        )

    amount_fmt = format_transaction_summary(
        float(row.amount),
        row.category,
        row.transaction_date,
        row.currency or input.user_currency,
        input.user_timezone,
    )
    payload = {
        "type": "transaction_pending",
        "transaction": {
            "id": row.id,
            "type": row.type,
            "amount": float(row.amount),
            "currency": row.currency,
            "category": row.category,
            "description": row.description,
            "date": row.transaction_date,
        },
        "text": t("update_pending", locale, summary=amount_fmt),
    }

    return ServiceResult(
        messages=[custom_message(payload)],
        session=SessionUpdates(dialogue_phase="awaiting_confirmation"),
    )
