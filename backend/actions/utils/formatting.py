"""Formatting utilities for currency, numbers, and dates."""

from decimal import Decimal

import pendulum


def format_currency(amount: float | Decimal, currency: str = "USD") -> str:
    """
    Format amount as currency string.

    Examples:
      format_currency(45.5, "USD")    → "$45.50"
      format_currency(1234.1, "EUR")  → "€1,234.10"
      format_currency(999, "GBP")     → "£999.00"
    """
    amount_decimal = Decimal(str(amount))

    # Common currency symbols
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "INR": "₹",
        "AUD": "A$",
        "CAD": "C$",
    }

    symbol = symbols.get(currency.upper(), currency.upper())

    # Format with thousand separators and 2 decimals
    formatted = f"{amount_decimal:,.2f}"

    return f"{symbol}{formatted}"


def format_date_relative(dt: pendulum.DateTime, now: pendulum.DateTime | None = None) -> str:
    """
    Format date as human-readable relative or absolute string.

    Examples:
      Today → "today"
      Yesterday → "yesterday"
      2 days ago → "2 days ago"
      2026-03-15 → "March 15"
    """
    if now is None:
        now = pendulum.now(str(dt.timezone.name) if dt.timezone else "UTC")

    # Normalize to dates (ignore time)
    date_only = dt.date()
    now_only = now.date()

    diff = (now_only - date_only).days

    match diff:
        case 0:
            return "today"
        case 1:
            return "yesterday"
        case 2:
            return "2 days ago"
        case n if n > 0 and n <= 7:
            return f"{n} days ago"
        case _:
            # Absolute date format
            return dt.format("MMMM D")


def format_transaction_summary(
    amount: float,
    category: str,
    date_str: str,
    currency: str = "USD",
    timezone: str = "UTC",
) -> str:
    """
    Format a transaction for display.

    Example:
      format_transaction_summary(45.50, "groceries", "2026-05-27", "USD")
      → "$45.50 for Groceries on May 27"
    """
    amount_fmt = format_currency(amount, currency)
    category_fmt = category.strip().title()

    dt = pendulum.parse(date_str, tz=timezone)
    if not isinstance(dt, pendulum.DateTime):
        dt = pendulum.DateTime.instance(dt)
    now = pendulum.now(timezone)
    date_fmt = format_date_relative(dt, now)

    return f"{amount_fmt} for {category_fmt} on {date_fmt.title()}"


def format_spending_report(
    total_income: float,
    total_expenses: float,
    currency: str = "USD",
) -> str:
    """
    Format spending summary for display.

    Example:
      format_spending_report(2000, 500, "USD")
      → "Income: $2,000.00 | Expenses: $500.00 | Net: $1,500.00"
    """
    net = total_income - total_expenses
    return (
        f"Income: {format_currency(total_income, currency)} | "
        f"Expenses: {format_currency(total_expenses, currency)} | "
        f"Net: {format_currency(net, currency)}"
    )
