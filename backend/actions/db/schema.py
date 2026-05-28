"""SQLite schema for local development."""

from __future__ import annotations

import contextlib

import aiosqlite

from actions.db.local_user import LOCAL_USER_ID

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS profiles (
  id TEXT PRIMARY KEY,
  display_name TEXT,
  currency TEXT NOT NULL DEFAULT 'VND',
  timezone TEXT NOT NULL DEFAULT 'Asia/Ho_Chi_Minh',
  locale TEXT NOT NULL DEFAULT 'vi',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS transactions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('income', 'expense', 'pending')),
  amount REAL NOT NULL CHECK (amount >= 0),
  currency TEXT NOT NULL DEFAULT 'USD',
  category TEXT NOT NULL,
  description TEXT,
  transaction_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending_confirmation',
  source TEXT NOT NULL DEFAULT 'manual_chat',
  ai_confidence REAL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS transactions_user_date_idx
  ON transactions (user_id, transaction_date DESC);

CREATE TABLE IF NOT EXISTS chat_sessions (
  sender_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  state_json TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


async def ensure_schema(conn: aiosqlite.Connection) -> None:
    await conn.executescript(SCHEMA_SQL)
    with contextlib.suppress(aiosqlite.OperationalError):
        await conn.execute("ALTER TABLE profiles ADD COLUMN locale TEXT NOT NULL DEFAULT 'vi'")
    await conn.execute(
        """
        INSERT INTO profiles (id, display_name, currency, timezone, locale)
        VALUES (?, ?, 'VND', 'Asia/Ho_Chi_Minh', 'vi')
        ON CONFLICT (id) DO NOTHING
        """,
        (LOCAL_USER_ID, "Local user"),
    )
    await conn.commit()
