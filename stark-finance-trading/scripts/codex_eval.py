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
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECRET_RE = re.compile(r"(gh[opsu]_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,})")
NON_MODEL_RUN_MODES = {"fixture": "fixture_run", "local_tool": "local_tool_run"}


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


def redact(text: str) -> str:
    return SECRET_RE.sub("***REDACTED***", text)


def limited(text: str, limit: int) -> str:
    text = redact(text)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[truncated]"


def run_case_with_runner(
    *,
    command: str,
    cwd: Path,
    payload: dict[str, Any],
    timeout: int,
    max_output_chars: int,
) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        proc = subprocess.run(
            shlex.split(command),
            cwd=cwd,
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        stdout = limited(proc.stdout, max_output_chars)
        stderr = limited(proc.stderr, max_output_chars)
        parsed: dict[str, Any] = {}
        try:
            parsed = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            parsed = {}
        checks = parsed.get("deterministic_checks") or parsed.get("checks") or []
        if not isinstance(checks, list):
            checks = []
        checks.append(
            {
                "type": "runner_returncode",
                "passed": proc.returncode == 0,
                "evidence": f"returncode={proc.returncode}",
            }
        )
        return {
            "returncode": proc.returncode,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "stdout_tail": stdout,
            "stderr_tail": stderr,
            "parsed": parsed,
            "final": limited(str(parsed.get("final") or stdout), max_output_chars),
            "checks": checks,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": 124,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "stdout_tail": limited(exc.stdout or "", max_output_chars) if isinstance(exc.stdout, str) else "",
            "stderr_tail": limited(exc.stderr or "", max_output_chars) if isinstance(exc.stderr, str) else "",
            "parsed": {},
            "final": "",
            "checks": [
                {
                    "type": "runner_timeout",
                    "passed": False,
                    "evidence": f"timeout={timeout}",
                }
            ],
        }


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
    parser.add_argument("--runner-command", default="")
    parser.add_argument("--runner-kind", default="model_service", choices=["model_service", "fixture", "local_tool"])
    parser.add_argument("--max-output-chars", type=int, default=12000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    eval_set = Path(args.eval_set)
    cases = load_cases(eval_set, args.max_cases)
    signoff = read_signoff(Path(args.signoff)) if args.signoff else None
    approval_status = (signoff or {}).get("approval_status", "MISSING")

    approved = (
        args.require_approved_signoff
        and signoff is not None
        and signoff.get("status") == "PASS"
        and approval_status == "APPROVED"
    )
    live_allowed = approved and bool(args.runner_command)
    if args.require_approved_signoff and not approved:
        status = "BLOCKED"
        mode = "approval_required"
    elif approved and not args.runner_command:
        status = "BLOCKED"
        mode = "runner_required"
    elif live_allowed:
        status = "PASS"
        mode = "live" if args.runner_kind == "model_service" else NON_MODEL_RUN_MODES[args.runner_kind]
    else:
        status = "PASS"
        mode = "dry_run"

    case_rows = []
    for index, case in enumerate(cases):
        case_id = case.get("id", f"case-{index + 1}")
        prompt = case.get("prompt", "")
        items = required_items(case)
        row = {
            "id": case_id,
            "category": case.get("category", ""),
            "prompt_sha256": sha256_text(prompt),
            "required_check_count": len(items),
        }
        if live_allowed:
            payload = {
                "schema_version": "1.0",
                "skill_path": str(Path(args.skill_path)),
                "eval_set": str(eval_set),
                "case": case,
                "case_id": case_id,
                "prompt": prompt,
                "prompt_sha256": row["prompt_sha256"],
                "required_items": items,
                "sandbox": args.sandbox,
                "timeout": args.timeout,
                "model": args.model,
                "runner_kind": args.runner_kind,
            }
            runner = run_case_with_runner(
                command=args.runner_command,
                cwd=Path(args.skill_path).resolve() if Path(args.skill_path).exists() else Path.cwd(),
                payload=payload,
                timeout=args.timeout,
                max_output_chars=args.max_output_chars,
            )
            row.update(
                {
                    "runner_kind": args.runner_kind,
                    "runner_returncode": runner["returncode"],
                    "artifact": None,
                    "checks": runner["checks"],
                    "final": runner["final"],
                    "stdout_tail": runner["stdout_tail"],
                    "stderr_tail": runner["stderr_tail"],
                }
            )
            if runner["returncode"] != 0:
                status = "FAIL"
        case_rows.append(row)

    if mode == "live":
        evidence_boundary = (
            "Live runner output is reviewable model-service evidence only after approved signoff. "
            "It still does not prove market-data correctness, trading performance, or public superiority."
        )
    elif mode.endswith("_run"):
        evidence_boundary = (
            "Fixture/local runner output proves the eval execution harness works. "
            "It does not prove live model behavior, market-data correctness, trading performance, or public superiority."
        )
    else:
        evidence_boundary = (
            "Dry-run artifacts and approval checks do not prove live model behavior. "
            "Live eval execution requires explicit approved signoff and a separate model-service runner."
        )
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
        "runner_kind": args.runner_kind if args.runner_command else "",
        "runner_command_present": bool(args.runner_command),
        "evidence_boundary": evidence_boundary,
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
