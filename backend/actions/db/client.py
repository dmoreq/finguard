"""Local SQLite database for development (no Supabase)."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

from actions.db.schema import ensure_schema

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "finguard.db"


def get_db_path() -> Path:
    raw = os.environ.get("FINGUARD_DB_PATH", "").strip()
    return Path(raw) if raw else DEFAULT_DB_PATH


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async SQLite connection with schema initialized."""
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = await aiosqlite.connect(path)
    conn.row_factory = aiosqlite.Row
    await ensure_schema(conn)
    try:
        yield conn
    finally:
        await conn.close()
