#!/usr/bin/env python3
"""Evaluate intent router against utterances.jsonl (keyword or hybrid)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from actions.chat.factory import reset_dialogue_engine  # noqa: E402
from actions.chat.router import classify_intent  # noqa: E402

DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "utterances.jsonl"
VI_FIXTURE = ROOT / "tests" / "fixtures" / "utterances-vi.jsonl"


def main() -> int:
    fixture_name = os.environ.get("ROUTER_FIXTURE", "en").lower()
    fixture = VI_FIXTURE if fixture_name in ("vi", "vietnamese") else DEFAULT_FIXTURE

    if not fixture.exists():
        print(f"Missing {fixture}")
        return 1

    mode = os.environ.get("ROUTER_MODE", "keyword").lower()
    minimum_pct = 95.0 if mode == "hybrid" else 85.0
    reset_dialogue_engine()

    total = 0
    correct = 0
    failures: list[str] = []
    for line in fixture.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        expected = row["intent"]
        pending = bool(row.get("confirmation_pending")) or expected.startswith("manage_")
        result = classify_intent(row["text"], confirmation_pending=pending)
        total += 1
        ok = result.intent == expected
        correct += int(ok)
        if not ok:
            failures.append(
                f"FAIL expected={expected} got={result.intent} text={row['text']!r}",
            )

    pct = 100.0 * correct / total if total else 0.0
    print(f"FIXTURE={fixture.name} ROUTER_MODE={mode} accuracy: {correct}/{total} ({pct:.1f}%)")
    print(f"Minimum required: {minimum_pct:.0f}%")
    for line in failures:
        print(line)

    return 0 if pct >= minimum_pct else 1


if __name__ == "__main__":
    raise SystemExit(main())
