"""Multi-turn transaction slot collection."""

from __future__ import annotations

from actions.chat.domain.session import ChatSession
from actions.chat.domain.slots import TransactionDraft, prompt_for_missing_field
from actions.chat.extraction.composite_extractor import CompositeFieldExtractor
from actions.chat.extraction.protocol import TransactionFieldExtractor
from actions.chat.extraction.schemas import ExtractResult
from actions.chat.respond.payloads import text_message
from actions.services.profile import UserProfile
from actions.services.record_transaction import record_transaction
from actions.services.types import ServiceResult
from actions.utils.i18n import t


class TransactionCollector:
    """Merges extracted fields and records or prompts for missing slots."""

    def __init__(self, extractor: TransactionFieldExtractor | CompositeFieldExtractor) -> None:
        self._extractor = extractor

    async def _resolve_fields(self, text: str) -> ExtractResult:
        if isinstance(self._extractor, CompositeFieldExtractor):
            return await self._extractor.extract(text)
        fields = self._extractor.extract_transaction(text)
        if fields.get("amount") and fields.get("category"):
            return ExtractResult(status="success", fields=fields, source="rules")
        return ExtractResult(status="partial", fields=fields, source="rules")

    @staticmethod
    def _message_for_extract_error(result: ExtractResult, locale: str) -> str:
        if result.status == "validation_error":
            return t("extract_validation", locale)
        return t("extract_api_error", locale)

    async def collect(
        self,
        session: ChatSession,
        profile: UserProfile,
        text: str,
        *,
        default_transaction_type: str | None = None,
    ) -> ServiceResult:
        extracted = await self._resolve_fields(text)
        if extracted.status in ("validation_error", "api_error"):
            msg = self._message_for_extract_error(extracted, profile.normalized_locale)
            return ServiceResult(messages=[text_message(msg)])

        fields = dict(extracted.fields)
        if default_transaction_type and "transaction_type" not in fields:
            fields["transaction_type"] = default_transaction_type

        draft = TransactionDraft.merge(session.partial_transaction, fields)
        session.partial_transaction = draft.fields

        missing = draft.missing_required()
        if missing:
            session.dialogue_phase = "collecting"
            prompt = prompt_for_missing_field(
                missing[0], draft.transaction_type, profile.normalized_locale
            )
            return ServiceResult(messages=[text_message(prompt)])

        return await record_transaction(draft.to_record_input(profile))
