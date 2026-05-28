#!/usr/bin/env python3
"""Evaluate keyword intent router against utterances.jsonl (Phase 0 spike)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from actions.chat.router import classify_intent  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "utterances.jsonl"


def main() -> int:
    if not FIXTURE.exists():
        print(f"Missing {FIXTURE}")
        return 1

    total = 0
    correct = 0
    for line in FIXTURE.read_text().splitlines():
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
            print(f"FAIL expected={expected} got={result.intent} text={row['text']!r}")

    pct = 100.0 * correct / total if total else 0
    print(f"Accuracy: {correct}/{total} ({pct:.1f}%)")
    return 0 if pct >= 85 else 1


if __name__ == "__main__":
    raise SystemExit(main())
