"""Backward compatible re-exports for rule extraction."""

from actions.chat.extraction.rules import (
    build_edit_fields,
    build_transaction_fields,
    infer_transaction_type,
    parse_amount,
    parse_category,
)

extract_edit_fields = build_edit_fields
extract_transaction_fields = build_transaction_fields

__all__ = [
    "extract_edit_fields",
    "extract_transaction_fields",
    "infer_transaction_type",
    "parse_amount",
    "parse_category",
]
