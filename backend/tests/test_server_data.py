"""REST /data/* endpoints on the action server."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from actions.db.queries import insert_transaction
from actions.models.transaction import TransactionInsert
from actions.server import app


@pytest.fixture
def client(db_path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("FINGUARD_DB_PATH", str(db_path))
    with TestClient(app) as test_client:
        yield test_client


def test_data_transactions_empty(client: TestClient) -> None:
    response = client.get("/data/transactions")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_data_transactions_after_insert(client: TestClient, db_conn) -> None:
    await insert_transaction(
        db_conn,
        TransactionInsert(
            user_id="local-user",
            type="expense",
            amount=5.0,
            category="coffee",
            description=None,
            transaction_date="2026-05-15",
            status="confirmed",
        ),
    )
    response = client.get("/data/transactions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == 5.0


@pytest.mark.asyncio
async def test_data_clear_transactions(client: TestClient, db_conn) -> None:
    await insert_transaction(
        db_conn,
        TransactionInsert(
            user_id="local-user",
            type="expense",
            amount=1.0,
            category="misc",
            description=None,
            transaction_date="2026-05-15",
            status="confirmed",
        ),
    )
    assert client.delete("/data/transactions").status_code == 200
    assert client.get("/data/transactions").json() == []


def test_data_profile_get_and_patch(client: TestClient) -> None:
    get_resp = client.get("/data/profile")
    assert get_resp.status_code == 200
    assert get_resp.json()["currency"] == "USD"

    patch_resp = client.patch(
        "/data/profile",
        json={"display_name": "QA User", "currency": "GBP", "timezone": "UTC"},
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["display_name"] == "QA User"
    assert body["currency"] == "GBP"


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "action-server"
