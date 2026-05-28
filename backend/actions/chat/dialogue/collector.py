"""Multi-turn transaction slot collection."""

from __future__ import annotations

from actions.chat.domain.session import ChatSession
from actions.chat.domain.slots import TransactionDraft, prompt_for_missing_field
from actions.chat.extraction.protocol import TransactionFieldExtractor
from actions.chat.respond.payloads import text_message
from actions.services.profile import UserProfile
from actions.services.record_transaction import record_transaction
from actions.services.types import ServiceResult


class TransactionCollector:
    """Merges extracted fields and records or prompts for missing slots."""

    def __init__(self, extractor: TransactionFieldExtractor) -> None:
        self._extractor = extractor

    async def collect(
        self,
        session: ChatSession,
        profile: UserProfile,
        text: str,
        *,
        default_transaction_type: str | None = None,
    ) -> ServiceResult:
        fields = self._extractor.extract_transaction(text)
        if default_transaction_type and "transaction_type" not in fields:
            fields["transaction_type"] = default_transaction_type

        draft = TransactionDraft.merge(session.partial_transaction, fields)
        session.partial_transaction = draft.fields

        missing = draft.missing_required()
        if missing:
            session.dialogue_phase = "collecting"
            prompt = prompt_for_missing_field(missing[0], draft.transaction_type)
            return ServiceResult(messages=[text_message(prompt)])

        return await record_transaction(draft.to_record_input(profile))
