#!/usr/bin/env python3
"""Smoke-test the approved live-eval runner path with a local fixture runner."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# Live Eval Harness Smoke",
        "",
        f"- Status: {report['status']}",
        f"- Mode: `{report['mode']}`",
        f"- Cases: {report['case_count']}",
        f"- Runner kind: `{report['runner_kind']}`",
        "",
        "## Checks",
        "",
        "| Check | Status |",
        "|---|---|",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['id']}` | {'PASS' if check['passed'] else 'FAIL'} |")
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test fixture-backed live eval harness.")
    parser.add_argument("--skill-root", default=".")
    parser.add_argument("--eval-set", default="evals/live-behavior-evals.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.skill_root).resolve()
    with tempfile.TemporaryDirectory(prefix="stark-finance-live-harness-") as tmp:
        tmpdir = Path(tmp)
        signoff = tmpdir / "approved-fixture-signoff.json"
        out_dir = tmpdir / "fixture-run"
        signoff.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "status": "PASS",
                    "approval_status": "APPROVED",
                    "purpose": "Fixture-only live eval harness smoke. Not a live model-service approval.",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        cmd = [
            sys.executable,
            "scripts/codex_eval.py",
            "--skill-path",
            ".",
            "--eval-set",
            args.eval_set,
            "--out-dir",
            str(out_dir),
            "--max-cases",
            "1",
            "--require-approved-signoff",
            "--signoff",
            str(signoff),
            "--runner-command",
            f"{sys.executable} scripts/live_eval_runner_fixture.py",
            "--runner-kind",
            "fixture",
            "--json",
        ]
        proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
        review_path = out_dir / "review.json"
        review = json.loads(review_path.read_text(encoding="utf-8")) if review_path.exists() else {}

    cases = review.get("cases") or []
    checks = [
        {"id": "codex_eval_returncode", "passed": proc.returncode == 0},
        {"id": "review_status_pass", "passed": review.get("status") == "PASS"},
        {"id": "fixture_mode_labeled", "passed": review.get("mode") == "fixture_run"},
        {"id": "case_count_one", "passed": len(cases) == 1},
        {"id": "runner_returncode_zero", "passed": bool(cases and cases[0].get("runner_returncode") == 0)},
        {"id": "final_output_present", "passed": bool(cases and cases[0].get("final"))},
    ]
    status = "PASS" if all(check["passed"] for check in checks) else "FAIL"
    report = {
        "schema_version": "1.0",
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": review.get("mode", ""),
        "case_count": len(cases),
        "runner_kind": review.get("runner_kind", ""),
        "checks": checks,
        "stdout_tail": proc.stdout[-3000:],
        "stderr_tail": proc.stderr[-3000:],
        "evidence_boundary": (
            "This smoke test proves the approved runner path can execute a local fixture. "
            "It does not prove live model behavior, market-data correctness, trading performance, or public superiority."
        ),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(Path(args.markdown), report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"live eval harness smoke: {status}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
