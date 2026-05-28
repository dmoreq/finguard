"""Manual transaction CRUD and backup API tests."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from actions.server import app


@pytest.mark.asyncio
async def test_create_and_patch_transaction(db_path) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post(
            "/data/transactions",
            json={
                "type": "expense",
                "amount": 120000,
                "category": "dining",
                "transaction_date": "2026-05-20",
            },
        )
        assert create.status_code == 200
        tx_id = create.json()["id"]

        patch = await client.patch(
            f"/data/transactions/{tx_id}",
            json={"amount": 90000},
        )
        assert patch.status_code == 200
        assert patch.json()["amount"] == 90000


@pytest.mark.asyncio
async def test_backup_and_restore(db_path) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/data/transactions",
            json={
                "type": "income",
                "amount": 5000000,
                "category": "salary",
                "transaction_date": "2026-05-01",
            },
        )
        backup = await client.get("/data/backup")
        assert backup.status_code == 200
        payload = backup.json()
        assert "transactions" in payload
        assert len(payload["transactions"]) >= 1

        await client.delete("/data/transactions")
        restore = await client.post("/data/restore", json=payload)
        assert restore.status_code == 200

        listed = await client.get("/data/transactions")
        assert len(listed.json()) >= 1
