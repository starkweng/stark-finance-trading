#!/usr/bin/env python3
"""Score eval review bundles for public, evidence-labeled reviewability."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def load_review(path: Path) -> dict[str, Any]:
    if path.is_dir():
        path = path / "review.json"
    return json.loads(path.read_text(encoding="utf-8"))


def has_boundary(text: str) -> bool:
    lowered = text.lower()
    return (
        "does not prove" in lowered
        or "not prove" in lowered
        or "not live model behavior" in lowered
        or "unproven" in lowered
    )


def case_score(case: dict[str, Any], source_mode: str) -> dict[str, Any]:
    required_items = case.get("required_items") or []
    checks = case.get("checks") or []
    prompt = str(case.get("prompt") or "")
    prompt_hash = str(case.get("prompt_sha256") or "")
    final = str(case.get("final") or "")
    artifact = case.get("artifact")

    prompt_ok = bool(prompt.strip())
    hash_ok = bool(SHA256_RE.match(prompt_hash))
    required_ok = bool(required_items) and int(case.get("required_check_count") or 0) >= len(required_items)
    response_evidence_ok = bool(final.strip() or artifact or checks)
    if source_mode == "dry_run":
        response_evidence_ok = True

    checks_map = {
        "prompt_present": prompt_ok,
        "prompt_hash": hash_ok,
        "required_items": required_ok,
        "response_evidence_or_dry_run": response_evidence_ok,
    }
    passed = sum(1 for value in checks_map.values() if value)
    return {
        "id": case.get("id"),
        "category": case.get("category"),
        "score": round(100 * passed / len(checks_map), 2),
        "checks": checks_map,
        "required_item_count": len(required_items),
    }


def weighted_score(checks: list[tuple[str, bool, int]]) -> int:
    total = sum(weight for _, _, weight in checks)
    earned = sum(weight for _, passed, weight in checks if passed)
    return round(100 * earned / total) if total else 0


def score(review: dict[str, Any], *, min_score: int, require_live: bool) -> dict[str, Any]:
    cases = review.get("cases") or []
    source_mode = str(review.get("source_mode") or "")
    approval_status = str(review.get("approval_status") or "")
    evidence_boundary = str(review.get("evidence_boundary") or "")
    case_rows = [case_score(case, source_mode) for case in cases if isinstance(case, dict)]

    live_mode = source_mode in {"live", "reviewed_live"}
    if live_mode:
        behavior_proof_status = "REVIEWABLE_LIVE_EVIDENCE"
    elif source_mode in {"fixture_run", "local_tool_run"}:
        behavior_proof_status = "HARNESS_ONLY_NOT_MODEL_PROOF"
    else:
        behavior_proof_status = "UNPROVEN_DRY_RUN_ONLY"

    checks = [
        ("bundle_status_pass", review.get("status") == "PASS", 15),
        ("source_status_pass", review.get("source_status") == "PASS", 10),
        ("cases_present", bool(case_rows), 10),
        ("case_count_matches", int(review.get("case_count") or 0) == len(case_rows), 10),
        ("all_cases_reviewable", bool(case_rows) and all(item["score"] == 100 for item in case_rows), 25),
        ("source_mode_labeled", source_mode in {"dry_run", "approval_required", "runner_required", "fixture_run", "local_tool_run", "live", "reviewed_live"}, 10),
        ("approval_status_labeled", bool(approval_status), 5),
        ("evidence_boundary_labeled", has_boundary(evidence_boundary), 10),
        ("live_required_if_requested", (not require_live) or live_mode, 5),
    ]
    score_value = weighted_score(checks)
    failed = [name for name, passed, _ in checks if not passed]
    status = "PASS" if score_value >= min_score and not failed else "FAIL"
    if require_live and not live_mode:
        status = "FAIL"

    return {
        "schema_version": "1.0",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": review.get("title"),
        "source_mode": source_mode,
        "approval_status": approval_status,
        "case_count": len(case_rows),
        "score": score_value,
        "min_score": min_score,
        "behavior_proof_status": behavior_proof_status,
        "require_live": require_live,
        "checks": [
            {"id": name, "passed": passed, "weight": weight}
            for name, passed, weight in checks
        ],
        "failed_checks": failed,
        "cases": case_rows,
        "evidence_boundary": (
            "Eval scorecard covers reviewability and evidence labeling. "
            "A PASS on a dry-run bundle does not prove live model behavior, "
            "market-data correctness, trading performance, or public superiority."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Eval Review Scorecard",
        "",
        f"- Status: {report['status']}",
        f"- Score: {report['score']}/{report['min_score']} minimum",
        f"- Source mode: `{report['source_mode']}`",
        f"- Behavior proof: `{report['behavior_proof_status']}`",
        f"- Cases: {report['case_count']}",
        "",
        "## Checks",
        "",
        "| Check | Status | Weight |",
        "|---|---|---:|",
    ]
    for check in report["checks"]:
        lines.append(
            f"| `{check['id']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['weight']} |"
        )
    lines.extend(["", "## Cases", "", "| Case | Category | Score | Required Items |", "|---|---|---:|---:|"])
    for case in report["cases"]:
        lines.append(
            f"| `{case['id']}` | `{case['category']}` | {case['score']} | {case['required_item_count']} |"
        )
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a stark-finance-trading eval review bundle.")
    parser.add_argument("review_bundle", type=Path, help="Directory containing review.json, or review.json path")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--min-score", type=int, default=90)
    parser.add_argument("--require-live", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    review = load_review(args.review_bundle)
    report = score(review, min_score=args.min_score, require_live=args.require_live)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(Path(args.markdown), report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"eval review scorecard: {report['status']} {report['score']}/{report['min_score']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
