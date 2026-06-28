#!/usr/bin/env python3
"""Deterministic fixture runner for the live-eval execution harness.

This runner never calls a model service. It exists so CI can prove the approved
runner path works without pretending to prove live model behavior.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone


def main() -> int:
    payload = json.loads(sys.stdin.read() or "{}")
    case_id = payload.get("case_id") or "unknown"
    required_items = payload.get("required_items") or []
    report = {
        "schema_version": "1.0",
        "status": "PASS",
        "case_id": case_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "final": (
            f"Fixture runner executed case {case_id}. "
            "This is harness evidence only and not live model behavior."
        ),
        "deterministic_checks": [
            {
                "type": "fixture_runner",
                "passed": True,
                "evidence": "local fixture runner executed",
            },
            {
                "type": "required_items_received",
                "passed": bool(required_items),
                "evidence": f"required_item_count={len(required_items)}",
            },
        ],
        "evidence_boundary": "Fixture output is not live model behavior proof.",
    }
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
