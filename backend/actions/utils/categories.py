"""Category slug normalization (lowercase in DB)."""


def normalize_category(value: str) -> str:
    return value.strip().lower()
