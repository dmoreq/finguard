"""Handle confirm / discard / edit while a transaction is pending."""

from __future__ import annotations

from actions.chat.domain.intents import Intent
from actions.chat.domain.session import ChatSession
from actions.chat.extraction.protocol import EditFieldExtractor
from actions.chat.respond.payloads import text_message
from actions.chat.routing.composite import CompositeIntentRouter
from actions.services.delete_transaction import DeleteInput, delete_transaction
from actions.services.profile import UserProfile
from actions.services.types import ServiceResult
from actions.services.update_transaction import UpdateInput, update_transaction
from actions.utils.i18n import t


class PendingConfirmationHandler:
    """Processes manage_* intents when confirmation_pending is set."""

    def __init__(
        self,
        router: CompositeIntentRouter,
        edit_extractor: EditFieldExtractor,
    ) -> None:
        self._router = router
        self._edit_extractor = edit_extractor

    def applies(self, session: ChatSession) -> bool:
        return bool(session.confirmation_pending and session.last_transaction_id)

    async def handle(
        self,
        session: ChatSession,
        profile: UserProfile,
        text: str,
    ) -> ServiceResult | None:
        if not self.applies(session):
            return None

        routed = self._router.classify(text, confirmation_pending=True)
        intent = routed.intent

        if intent == Intent.MANAGE_CONFIRM:
            return await update_transaction(
                UpdateInput(
                    user_id=profile.user_id,
                    transaction_id=session.last_transaction_id or "",
                    user_currency=profile.currency,
                    user_timezone=profile.timezone,
                    user_locale=profile.normalized_locale,
                    confirm=True,
                )
            )

        if intent == Intent.MANAGE_DISCARD:
            return await delete_transaction(
                DeleteInput(
                    user_id=profile.user_id,
                    transaction_id=session.last_transaction_id or "",
                    user_locale=profile.normalized_locale,
                )
            )

        if intent == Intent.MANAGE_EDIT:
            edits = self._edit_extractor.extract_edit(text)
            if not edits:
                return ServiceResult(
                    messages=[text_message(t("edit_prompt", profile.normalized_locale))]
                )
            return await update_transaction(
                UpdateInput(
                    user_id=profile.user_id,
                    transaction_id=session.last_transaction_id or "",
                    user_currency=profile.currency,
                    user_timezone=profile.timezone,
                    user_locale=profile.normalized_locale,
                    confirm=False,
                    amount=edits.get("amount"),
                    category=edits.get("category"),
                    description=edits.get("description"),
                    transaction_date=edits.get("transaction_date"),
                )
            )

        return None
