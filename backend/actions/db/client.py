"""Async Supabase client factory with connection pooling."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from supabase import AsyncClient


@asynccontextmanager
async def get_supabase() -> AsyncGenerator[AsyncClient, None]:
    """
    Async context manager for Supabase client.
    Uses service role key (bypasses RLS) — safe because
    user_id is always explicitly included in queries.

    Example:
        async with get_supabase() as client:
            result = await client.table("transactions").select("*").execute()
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("missing_supabase_credentials")
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")

    # Lazy import: supabase/realtime needs websockets>=13; rasa-sdk pins websockets<12.
    from supabase import acreate_client

    client = await acreate_client(supabase_url=supabase_url, supabase_key=supabase_key)
    try:
        yield client
    except Exception as e:
        logger.exception("supabase_client_error", error=str(e))
        raise
    finally:
        await client.aclose()
