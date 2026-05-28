"""
FastAPI backend: chat webhook + data API for the Next.js app.
"""

import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from actions.chat.webhook import handle_webhook
from actions.db.client import get_db
from actions.db.local_user import LOCAL_USER_ID
from actions.db.queries import (
    clear_user_transactions,
    delete_transaction,
    get_profile,
    get_transaction,
    insert_transaction,
    list_user_transactions,
    update_profile,
)
from actions.models.transaction import TransactionInsert
from actions.services.create_transaction import (
    CreateTransactionInput,
    PatchTransactionInput,
    create_confirmed_transaction,
    patch_confirmed_transaction,
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
    version="0.3.0",
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


@app.post("/data/transactions")
async def data_create_transaction(request: Request, user_id: str = LOCAL_USER_ID) -> dict:
    body = await request.json()
    profile = await data_get_profile(user_id)
    try:
        input_data = CreateTransactionInput(
            user_id=user_id,
            type=body["type"],
            amount=float(body["amount"]),
            category=body["category"],
            description=body.get("description"),
            transaction_date=body.get("transaction_date"),
            currency=profile.get("currency", "VND"),
            timezone=profile.get("timezone", "Asia/Ho_Chi_Minh"),
        )
        row = await create_confirmed_transaction(input_data)
    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return row.model_dump(mode="json")


@app.patch("/data/transactions/{transaction_id}")
async def data_patch_transaction(
    transaction_id: str,
    request: Request,
    user_id: str = LOCAL_USER_ID,
) -> dict:
    body = await request.json()
    try:
        row = await patch_confirmed_transaction(
            PatchTransactionInput(
                user_id=user_id,
                transaction_id=transaction_id,
                type=body.get("type"),
                amount=float(body["amount"]) if body.get("amount") is not None else None,
                category=body.get("category"),
                description=body.get("description"),
                transaction_date=body.get("transaction_date"),
            )
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return row.model_dump(mode="json")


@app.delete("/data/transactions/{transaction_id}")
async def data_delete_transaction(transaction_id: str, user_id: str = LOCAL_USER_ID) -> dict:
    async with get_db() as conn:
        existing = await get_transaction(conn, user_id, transaction_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Transaction not found")
        await delete_transaction(conn, user_id, transaction_id)
    return {"ok": True}


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
            locale=body.get("locale"),
        )


@app.get("/data/backup")
async def data_backup(user_id: str = LOCAL_USER_ID) -> dict[str, Any]:
    async with get_db() as conn:
        profile = await get_profile(conn, user_id)
        rows = await list_user_transactions(conn, user_id)
    return {
        "version": 1,
        "exported_at": datetime.now(UTC).isoformat(),
        "profile": profile,
        "transactions": [row.model_dump(mode="json") for row in rows],
    }


@app.post("/data/restore")
async def data_restore(request: Request, user_id: str = LOCAL_USER_ID) -> dict:
    body = await request.json()
    if not isinstance(body, dict) or "transactions" not in body:
        raise HTTPException(status_code=422, detail="Invalid backup format")

    profile = body.get("profile") or {}
    async with get_db() as conn:
        await clear_user_transactions(conn, user_id)
        await update_profile(
            conn,
            user_id,
            display_name=profile.get("display_name"),
            currency=profile.get("currency"),
            timezone=profile.get("timezone"),
            locale=profile.get("locale"),
        )
        for item in body["transactions"]:
            tx = TransactionInsert(
                user_id=user_id,
                type=item["type"],
                amount=float(item["amount"]),
                currency=item.get("currency") or profile.get("currency") or "VND",
                category=item["category"],
                description=item.get("description"),
                transaction_date=item["transaction_date"],
                status=item.get("status") or "confirmed",
                source=item.get("source") or "restore",
            )
            await insert_transaction(conn, tx)
    return {"ok": True, "restored": len(body["transactions"])}


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
    uvicorn.run(app, host="0.0.0.0", port=port)  # nosec B104
