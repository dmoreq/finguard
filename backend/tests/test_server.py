"""Smoke tests for the FastAPI action server."""

from fastapi.testclient import TestClient

from actions.server import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "action-server"}
