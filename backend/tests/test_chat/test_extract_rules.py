"""Rule extraction tests."""

from actions.chat.extract.rules import extract_transaction_fields, parse_amount


def test_parse_amount_dollar() -> None:
    assert parse_amount("spent $12.50 on coffee") == 12.5


def test_parse_amount_k_suffix() -> None:
    assert parse_amount("groceries 50k") == 50000.0


def test_extract_fields() -> None:
    fields = extract_transaction_fields("spent $45 on groceries")
    assert fields["amount"] == 45.0
    assert fields["category"] == "groceries"
    assert fields["transaction_type"] == "expense"
