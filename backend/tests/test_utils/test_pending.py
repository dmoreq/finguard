"""Tests for pending transaction helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from actions.utils.pending import clear_pending_slots, get_pending_transaction_ids


def _tracker(
    *,
    confirmation_pending: bool | None,
    user_id: str | None,
    last_transaction_id: str | None,
) -> MagicMock:
    tracker = MagicMock()

    def get_slot(name: str):
        return {
            "confirmation_pending": confirmation_pending,
            "user_id": user_id,
            "last_transaction_id": last_transaction_id,
        }.get(name)

    tracker.get_slot.side_effect = get_slot
    return tracker


def test_get_pending_transaction_ids_returns_pair_when_pending() -> None:
    tracker = _tracker(
        confirmation_pending=True,
        user_id="user-1",
        last_transaction_id="tx-1",
    )
    assert get_pending_transaction_ids(tracker) == ("user-1", "tx-1")


def test_get_pending_transaction_ids_returns_none_when_not_pending() -> None:
    tracker = _tracker(
        confirmation_pending=False,
        user_id="user-1",
        last_transaction_id="tx-1",
    )
    assert get_pending_transaction_ids(tracker) is None


def test_get_pending_transaction_ids_returns_none_when_missing_id() -> None:
    tracker = _tracker(
        confirmation_pending=True,
        user_id="user-1",
        last_transaction_id=None,
    )
    assert get_pending_transaction_ids(tracker) is None


def test_clear_pending_slots_resets_state() -> None:
    events = clear_pending_slots()
    assert len(events) == 2
    assert events[0]["name"] == "confirmation_pending"
    assert events[0]["value"] is False
    assert events[1]["name"] == "last_transaction_id"
    assert events[1]["value"] is None
