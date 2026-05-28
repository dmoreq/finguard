"""
FastAPI wrapper around rasa-sdk ActionExecutor.
Provides better observability, structured logging, and custom middleware
compared to running `rasa run actions` directly.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from rasa_sdk.executor import ActionExecutor

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
    """Initialize action executor on startup, cleanup on shutdown."""
    setup_logging()
    logger.info("Initializing action server...")

    executor = ActionExecutor()
    executor.register_package("actions.handlers")

    app.state.executor = executor
    logger.info("✓ Action server started — packages registered: actions.handlers")

    yield

    logger.info("Action server shutting down...")


app = FastAPI(
    title="Finguard Action Server",
    version="0.1.0",
    description="Rasa CALM custom action executor for financial transactions",
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
    """Health check endpoint for Docker Compose."""
    return {"status": "ok", "service": "action-server"}


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


@app.post("/webhook")
async def webhook(request: Request) -> JSONResponse:
    """
    Rasa CALM action webhook.
    Receives action request from Rasa, executes custom action, returns events.
    """
    payload = await request.json()
    action_name = payload.get("next_action", "unknown")
    sender_id = payload.get("sender_id", "unknown")

    logger.info("action_called", action=action_name, sender=sender_id)

    try:
        result = await app.state.executor.run(payload)
        events_count = len(result.get("events", []))
        logger.debug("action_completed", action=action_name, events=events_count, sender=sender_id)
        return JSONResponse(result)
    except Exception as e:
        logger.exception("action_failed", action=action_name, sender=sender_id, error=str(e))
        return JSONResponse(
            {"error": "Action execution failed", "action": action_name},
            status_code=500,
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "5055"))
    uvicorn.run(app, host="0.0.0.0", port=port)
