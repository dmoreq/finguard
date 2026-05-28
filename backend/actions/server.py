"""
FastAPI backend: chat webhook + data API for the Next.js app.
"""

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from actions.chat.webhook import handle_webhook
from actions.db.client import get_db
from actions.db.local_user import LOCAL_USER_ID
from actions.db.queries import (
    clear_user_transactions,
    get_profile,
    list_user_transactions,
    update_profile,
)
from actions.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Finguard backend started (chat + data API)")
    yield
    logger.info("Finguard backend shutting down...")


app = FastAPI(
    title="Finguard Backend",
    version="0.2.0",
    description="Chat assistant and SQLite data API for FinGuard",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "finguard-backend"}


@app.get("/status")
async def status() -> dict:
    """Rasa-compatible status probe for health scripts."""
    return {"status": "ok"}


@app.get("/data/transactions")
async def data_transactions(user_id: str = LOCAL_USER_ID) -> list[dict]:
    async with get_db() as conn:
        rows = await list_user_transactions(conn, user_id)
    return [row.model_dump(mode="json") for row in rows]


@app.delete("/data/transactions")
async def data_clear_transactions(user_id: str = LOCAL_USER_ID) -> dict:
    async with get_db() as conn:
        await clear_user_transactions(conn, user_id)
    return {"ok": True}


@app.get("/data/profile")
async def data_get_profile(user_id: str = LOCAL_USER_ID) -> dict:
    async with get_db() as conn:
        return await get_profile(conn, user_id)


@app.patch("/data/profile")
async def data_update_profile(request: Request, user_id: str = LOCAL_USER_ID) -> dict:
    body = await request.json()
    async with get_db() as conn:
        return await update_profile(
            conn,
            user_id,
            display_name=body.get("display_name"),
            currency=body.get("currency"),
            timezone=body.get("timezone"),
        )


@app.post("/webhooks/rest/webhook")
async def rest_webhook(request: Request) -> list[dict[str, Any]]:
    """Rasa REST-compatible chat endpoint used by Next.js /api/chat."""
    payload = await request.json()
    sender = payload.get("sender", "unknown")
    logger.info("chat_message", sender=sender)
    try:
        return await handle_webhook(payload)
    except Exception as exc:
        logger.exception("chat_webhook_failed", sender=sender)
        raise HTTPException(status_code=500, detail="Chat processing failed") from exc


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "5055"))
    uvicorn.run(app, host="0.0.0.0", port=port)
