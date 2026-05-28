#!/usr/bin/env python3
"""Minimal Rasa REST webhook stub for local dev without Rasa Pro license."""

from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MockRasaHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        if self.path in ("/", "/status", "/health"):
            self._json(200, {"version": "mock", "status": "ok"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/webhooks/rest/webhook":
            self._json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        message = (body.get("message") or "").lower()

        if re.search(r"spent|paid|bought|expense", message):
            amount = 10.0
            match = re.search(r"(\d+(?:\.\d+)?)", message)
            if match:
                amount = float(match.group(1))
            self._json(
                200,
                [
                    {
                        "custom": {
                            "type": "transaction_pending",
                            "text": f"Got it — ${amount:.2f} (mock mode). Confirm below.",
                            "transaction": {
                                "id": "mock-tx-1",
                                "type": "expense",
                                "amount": amount,
                                "category": "other",
                                "description": None,
                                "date": "2026-05-28",
                            },
                        }
                    }
                ],
            )
            return

        if "balance" in message or "report" in message:
            self._json(
                200,
                [
                    {
                        "custom": {
                            "type": "balance",
                            "text": "**Balance (mock):** no real data — add RASA_PRO_LICENSE for CALM.",
                            "data": {
                                "period": "this_month",
                                "income": 0,
                                "expenses": 0,
                                "net": 0,
                                "currency": "USD",
                            },
                        }
                    }
                ],
            )
            return

        self._json(
            200,
            [
                {
                    "text": (
                        "Mock Rasa is running. Set RASA_PRO_LICENSE in backend/.env "
                        "and restart `make dev` for full CALM flows."
                    )
                }
            ],
        )

    def _json(self, status: int, payload: object) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 5005), MockRasaHandler)
    print("Mock Rasa listening on http://127.0.0.1:5005", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
