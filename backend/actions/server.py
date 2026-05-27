"""
FastAPI wrapper around rasa-sdk ActionExecutor.
Provides better observability, structured logging, and custom middleware
compared to running `rasa run actions` directly.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from rasa_sdk.executor import ActionExecutor

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


@app.get("/health")
async def health() -> dict:
    """Health check endpoint for Docker Compose."""
    return {"status": "ok", "service": "action-server"}


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
