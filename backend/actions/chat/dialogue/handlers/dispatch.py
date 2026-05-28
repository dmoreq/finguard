"""Route classified intents to reporting and chitchat services."""

from __future__ import annotations

from actions.chat.domain.intents import Intent, IntentResult
from actions.chat.domain.session import ChatSession
from actions.chat.extraction.period import (
    parse_category_hint,
    parse_period_from_text,
    wants_trend_comparison,
)
from actions.chat.respond.payloads import text_message
from actions.chat.routing.composite import CompositeIntentRouter
from actions.services.get_balance import BalanceInput, get_balance
from actions.services.list_transactions import ListInput, list_transactions
from actions.services.profile import UserProfile
from actions.services.query_spending import SpendingInput, query_spending
from actions.services.types import ServiceResult
from actions.utils.i18n import t


class IntentDispatchHandler:
    """Handles non-collecting intents (reports, chitchat, unknown)."""

    def __init__(self, router: CompositeIntentRouter) -> None:
        self._router = router

    def classify_open(self, text: str) -> IntentResult:
        return self._router.classify(text, confirmation_pending=False)

    async def dispatch(
        self,
        session: ChatSession,
        profile: UserProfile,
        text: str,
        routed: IntentResult,
    ) -> ServiceResult:
        del session
        intent = routed.intent
        locale = profile.normalized_locale

        if intent == Intent.CHECK_BALANCE:
            period = parse_period_from_text(text)
            return await get_balance(
                BalanceInput(
                    user_id=profile.user_id,
                    query_period=period,
                    user_currency=profile.currency,
                    user_timezone=profile.timezone,
                    user_locale=locale,
                )
            )

        if intent == Intent.ANALYZE_SPENDING:
            period = parse_period_from_text(text)
            category = parse_category_hint(text)
            return await query_spending(
                SpendingInput(
                    user_id=profile.user_id,
                    query_period=period,
                    query_category=category,
                    user_currency=profile.currency,
                    user_timezone=profile.timezone,
                    user_locale=locale,
                    include_trend=wants_trend_comparison(text),
                )
            )

        if intent == Intent.LIST_TRANSACTIONS:
            period = parse_period_from_text(text, default="last_30d")
            category = parse_category_hint(text)
            return await list_transactions(
                ListInput(
                    user_id=profile.user_id,
                    query_period=period,
                    query_category=category,
                    user_timezone=profile.timezone,
                    user_locale=locale,
                )
            )

        if intent == Intent.CHITCHAT:
            return ServiceResult(messages=[text_message(t("chitchat", locale))])

        return ServiceResult(messages=[text_message(t("unknown", locale))])
