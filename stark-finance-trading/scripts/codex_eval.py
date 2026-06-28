#!/usr/bin/env python3
"""Prepare or guard live behavior evals for stark-finance-trading.

This script intentionally does not call a model service by default. It creates
dry-run review artifacts and refuses live execution unless an approved signoff
packet is provided.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cases(eval_set: Path, max_cases: int | None) -> list[dict]:
    data = json.loads(eval_set.read_text(encoding="utf-8"))
    cases = data.get("cases") or data.get("evals") or []
    if max_cases is not None:
        cases = cases[:max_cases]
    return cases


def listify(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def required_items(case: dict) -> list[object]:
    items: list[object] = []
    for field in ("required_checks", "required_terms", "required_safety_terms", "must_do", "must_not_do"):
        items.extend(listify(case.get(field)))
    return items


def read_signoff(path: Path | None) -> dict | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_review_markdown(path: Path, report: dict) -> None:
    lines = [
        "# Live Behavior Eval Review",
        "",
        f"- Status: {report['status']}",
        f"- Mode: {report['mode']}",
        f"- Cases: {report['case_count']}",
        f"- Approval status: {report.get('approval_status', 'N/A')}",
        "",
        "## Cases",
        "",
        "| Case | Category | Prompt SHA256 | Required Checks |",
        "|---|---|---|---:|",
    ]
    for case in report["cases"]:
        lines.append(
            f"| `{case['id']}` | `{case['category']}` | `{case['prompt_sha256']}` | {case['required_check_count']} |"
        )
    lines.extend([
        "",
        "## Evidence Boundary",
        "",
        report["evidence_boundary"],
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-path", default=".")
    parser.add_argument("--eval-set", default="evals/live-behavior-evals.json")
    parser.add_argument("--out-dir", default="evals/artifacts/live-behavior")
    parser.add_argument("--sandbox", default="read-only")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--model", default="")
    parser.add_argument("--signoff")
    parser.add_argument("--require-approved-signoff", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    eval_set = Path(args.eval_set)
    cases = load_cases(eval_set, args.max_cases)
    signoff = read_signoff(Path(args.signoff)) if args.signoff else None
    approval_status = (signoff or {}).get("approval_status", "MISSING")

    live_allowed = (
        args.require_approved_signoff
        and signoff is not None
        and signoff.get("status") == "PASS"
        and approval_status == "APPROVED"
    )
    if args.require_approved_signoff and not live_allowed:
        status = "BLOCKED"
        mode = "approval_required"
    else:
        status = "PASS"
        mode = "dry_run"

    case_rows = [
        {
            "id": case.get("id", f"case-{index + 1}"),
            "category": case.get("category", ""),
            "prompt_sha256": sha256_text(case.get("prompt", "")),
            "required_check_count": len(required_items(case)),
        }
        for index, case in enumerate(cases)
    ]
    report = {
        "schema_version": "1.0",
        "status": status,
        "mode": mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "skill_path": str(Path(args.skill_path)),
        "eval_set": str(eval_set),
        "case_count": len(cases),
        "cases": case_rows,
        "sandbox": args.sandbox,
        "timeout": args.timeout,
        "model": args.model,
        "approval_status": approval_status,
        "evidence_boundary": "Dry-run artifacts and approval checks do not prove live model behavior. Live eval execution requires explicit approved signoff and a separate model-service runner.",
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "review.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_review_markdown(out_dir / "review.md", report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"codex eval {status}: {out_dir}")
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
