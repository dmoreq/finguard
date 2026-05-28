"""HTTP contract tests for scripts/mock-rasa.py."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[2]
MOCK_SCRIPT = ROOT / "scripts" / "mock-rasa.py"


@pytest.fixture(scope="module")
def mock_rasa_url() -> str:
    port = 18765
    env = {**os.environ, "MOCK_RASA_PORT": str(port)}
    proc = subprocess.Popen(
        [sys.executable, str(MOCK_SCRIPT)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(30):
        try:
            httpx.get(f"{url}/status", timeout=0.5)
            break
        except httpx.HTTPError:
            time.sleep(0.1)
    else:
        proc.kill()
        pytest.fail("mock Rasa did not start")

    yield url
    proc.terminate()
    proc.wait(timeout=5)


def test_mock_rasa_status(mock_rasa_url: str) -> None:
    response = httpx.get(f"{mock_rasa_url}/status", timeout=2.0)
    assert response.status_code == 200
    assert response.json()["version"] == "mock"


def test_mock_rasa_expense_webhook(mock_rasa_url: str) -> None:
    response = httpx.post(
        f"{mock_rasa_url}/webhooks/rest/webhook",
        json={"sender": "local-user", "message": "spent 12 on lunch"},
        timeout=2.0,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["custom"]["type"] == "transaction_pending"
    assert payload[0]["custom"]["transaction"]["amount"] == 12.0


def test_mock_rasa_balance_report(mock_rasa_url: str) -> None:
    response = httpx.post(
        f"{mock_rasa_url}/webhooks/rest/webhook",
        json={"sender": "local-user", "message": "show my balance report"},
        timeout=2.0,
    )
    body = response.json()
    assert body[0]["custom"]["type"] == "balance"
