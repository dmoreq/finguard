"""Dialogue engine — deterministic FSM replacing Rasa CALM flows."""

from __future__ import annotations

from typing import Any

from actions.chat.extract.period import parse_category_hint, parse_period_from_text
from actions.chat.extract.rules import extract_edit_fields, extract_transaction_fields
from actions.chat.respond.payloads import text_message
from actions.chat.router import Intent, classify_intent
from actions.chat.session import ChatSession
from actions.services.delete_transaction import DeleteInput, delete_transaction
from actions.services.get_balance import BalanceInput, get_balance
from actions.services.list_transactions import ListInput, list_transactions
from actions.services.profile import UserProfile, load_user_profile
from actions.services.query_spending import SpendingInput, query_spending
from actions.services.record_transaction import RecordInput, record_transaction
from actions.services.types import ServiceResult, SessionUpdates
from actions.services.update_transaction import UpdateInput, update_transaction


def _apply_session_updates(session: ChatSession, updates: SessionUpdates | None) -> None:
    if not updates:
        return
    if updates.dialogue_phase is not None:
        session.dialogue_phase = updates.dialogue_phase
    if updates.confirmation_pending is not None:
        session.confirmation_pending = updates.confirmation_pending
    if updates.last_transaction_id is not None:
        session.last_transaction_id = updates.last_transaction_id
    if updates.clear_partial:
        session.partial_transaction = {}
    elif updates.partial_transaction is not None:
        session.partial_transaction = updates.partial_transaction


def _merge_partial(session: ChatSession, fields: dict[str, Any]) -> dict[str, Any]:
    merged = {**session.partial_transaction, **fields}
    session.partial_transaction = merged
    return merged


def _missing_required(merged: dict[str, Any], tx_type: str) -> list[str]:
    missing: list[str] = []
    if not merged.get("amount"):
        missing.append("amount")
    if not merged.get("category"):
        missing.append("category")
    return missing


def _prompt_for_field(field: str, tx_type: str) -> str:
    if field == "amount":
        return "How much was it? (e.g. 45 or $12.50)"
    if field == "category":
        kind = "income source" if tx_type == "income" else "category"
        return f"What {kind} was that? (e.g. groceries, dining, salary)"
    return "Could you tell me a bit more?"


async def _start_collecting(
    session: ChatSession,
    profile: UserProfile,
    text: str,
    default_type: str,
) -> ServiceResult:
    fields = extract_transaction_fields(text)
    if "transaction_type" not in fields:
        fields["transaction_type"] = default_type
    merged = _merge_partial(session, fields)
    tx_type = str(merged.get("transaction_type", default_type))
    missing = _missing_required(merged, tx_type)

    if missing:
        session.dialogue_phase = "collecting"
        return ServiceResult(messages=[text_message(_prompt_for_field(missing[0], tx_type))])

    return await record_transaction(
        RecordInput(
            user_id=profile.user_id,
            amount=float(merged["amount"]),
            category=str(merged["category"]),
            description=merged.get("description"),
            transaction_date=merged.get("transaction_date"),
            transaction_type=tx_type,  # type: ignore[arg-type]
            user_currency=profile.currency,
            user_timezone=profile.timezone,
        )
    )


async def _continue_collecting(
    session: ChatSession,
    profile: UserProfile,
    text: str,
) -> ServiceResult:
    fields = extract_transaction_fields(text)
    merged = _merge_partial(session, fields)
    tx_type = str(merged.get("transaction_type", "expense"))
    missing = _missing_required(merged, tx_type)

    if missing:
        return ServiceResult(messages=[text_message(_prompt_for_field(missing[0], tx_type))])

    return await record_transaction(
        RecordInput(
            user_id=profile.user_id,
            amount=float(merged["amount"]),
            category=str(merged["category"]),
            description=merged.get("description"),
            transaction_date=merged.get("transaction_date"),
            transaction_type=tx_type,  # type: ignore[arg-type]
            user_currency=profile.currency,
            user_timezone=profile.timezone,
        )
    )


async def handle_turn(session: ChatSession, text: str) -> ServiceResult:
    profile = await load_user_profile(session.user_id)
    session.append_turn("user", text)

    if session.confirmation_pending and session.last_transaction_id:
        routed = classify_intent(text, confirmation_pending=True)
        if routed.intent == Intent.MANAGE_CONFIRM:
            result = await update_transaction(
                UpdateInput(
                    user_id=profile.user_id,
                    transaction_id=session.last_transaction_id,
                    user_currency=profile.currency,
                    user_timezone=profile.timezone,
                    confirm=True,
                )
            )
            _apply_session_updates(session, result.session)
            return result
        if routed.intent == Intent.MANAGE_DISCARD:
            result = await delete_transaction(
                DeleteInput(
                    user_id=profile.user_id,
                    transaction_id=session.last_transaction_id,
                )
            )
            _apply_session_updates(session, result.session)
            return result
        if routed.intent in (Intent.MANAGE_EDIT,):
            edits = extract_edit_fields(text)
            if not edits:
                return ServiceResult(
                    messages=[
                        text_message(
                            "What should I change? You can say e.g. "
                            "'change amount to 50' or 'category dining'."
                        )
                    ]
                )
            result = await update_transaction(
                UpdateInput(
                    user_id=profile.user_id,
                    transaction_id=session.last_transaction_id,
                    user_currency=profile.currency,
                    user_timezone=profile.timezone,
                    confirm=False,
                    amount=edits.get("amount"),
                    category=edits.get("category"),
                    description=edits.get("description"),
                    transaction_date=edits.get("transaction_date"),
                )
            )
            _apply_session_updates(session, result.session)
            return result

    if session.dialogue_phase == "collecting":
        result = await _continue_collecting(session, profile, text)
        _apply_session_updates(session, result.session)
        return result

    routed = classify_intent(text, confirmation_pending=False)
    intent = routed.intent

    if intent == Intent.LOG_EXPENSE:
        result = await _start_collecting(session, profile, text, "expense")
    elif intent == Intent.LOG_INCOME:
        result = await _start_collecting(session, profile, text, "income")
    elif intent == Intent.CHECK_BALANCE:
        period = parse_period_from_text(text)
        result = await get_balance(
            BalanceInput(
                user_id=profile.user_id,
                query_period=period,
                user_currency=profile.currency,
                user_timezone=profile.timezone,
            )
        )
    elif intent == Intent.ANALYZE_SPENDING:
        period = parse_period_from_text(text)
        category = parse_category_hint(text)
        result = await query_spending(
            SpendingInput(
                user_id=profile.user_id,
                query_period=period,
                query_category=category,
                user_currency=profile.currency,
                user_timezone=profile.timezone,
            )
        )
    elif intent == Intent.LIST_TRANSACTIONS:
        period = parse_period_from_text(text, default="last_30d")
        category = parse_category_hint(text)
        result = await list_transactions(
            ListInput(
                user_id=profile.user_id,
                query_period=period,
                query_category=category,
                user_timezone=profile.timezone,
            )
        )
    elif intent == Intent.CHITCHAT:
        result = ServiceResult(
            messages=[
                text_message(
                    "Hi! I can log expenses and income, show your balance, "
                    'or summarize spending. Try: "spent $12 on coffee".'
                )
            ]
        )
    else:
        result = ServiceResult(
            messages=[
                text_message(
                    "I'm not sure what you mean. Try logging a transaction "
                    '(e.g. "spent $20 on groceries") or ask "what\'s my balance?".'
                )
            ]
        )

    _apply_session_updates(session, result.session)
    return result
