#!/usr/bin/env python3
"""Generate an approval packet before any live behavior eval is run."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_eval_cases(eval_set: Path, max_cases: int | None) -> list[dict]:
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


def write_markdown(path: Path, packet: dict) -> None:
    lines = [
        "# Live Eval Signoff",
        "",
        f"- Status: {packet['status']}",
        f"- Approval: {packet['approval_status']}",
        f"- Skill: `{packet['skill_path']}`",
        f"- Eval set: `{packet['eval_set']}`",
        f"- Cases: {packet['case_count']}",
        f"- Sandbox: `{packet['sandbox']}`",
        "",
        "## Exact Command",
        "",
        "```bash",
        packet["exact_command"],
        "```",
        "",
        "## Data Surfaces",
    ]
    lines.extend(f"- {item}" for item in packet["data_surfaces"])
    lines.extend([
        "",
        "## Must Not Do",
    ])
    lines.extend(f"- {item}" for item in packet["must_not_do"])
    lines.extend([
        "",
        "## Case Hashes",
        "",
        "| Case | Prompt SHA256 |",
        "|---|---|",
    ])
    lines.extend(f"| `{item['id']}` | `{item['prompt_sha256']}` |" for item in packet["case_hashes"])
    lines.extend([
        "",
        "## Evidence Boundary",
        "",
        packet["evidence_boundary"],
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-path", default=".")
    parser.add_argument("--eval-set", default="evals/live-behavior-evals.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--live-out-dir", default="evals/artifacts/live-behavior")
    parser.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--model", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    eval_set = Path(args.eval_set)
    cases = load_eval_cases(eval_set, args.max_cases)
    case_hashes = [
        {
            "id": case.get("id", f"case-{index + 1}"),
            "category": case.get("category", ""),
            "prompt_sha256": sha256_text(case.get("prompt", "")),
            "required_check_count": len(required_items(case)),
        }
        for index, case in enumerate(cases)
    ]
    exact_parts = [
        "PYTHONDONTWRITEBYTECODE=1",
        "python3",
        "scripts/codex_eval.py",
        "--skill-path",
        str(skill_path),
        "--eval-set",
        str(eval_set),
        "--out-dir",
        str(Path(args.live_out_dir)),
        "--sandbox",
        args.sandbox,
        "--timeout",
        str(args.timeout),
        "--require-approved-signoff",
        "--signoff",
        str(Path(args.out)),
    ]
    if args.max_cases is not None:
        exact_parts.extend(["--max-cases", str(args.max_cases)])
    if args.model:
        exact_parts.extend(["--model", args.model])

    packet = {
        "schema_version": "1.0",
        "status": "PASS",
        "approval_status": "PENDING",
        "approval": {
            "status": "PENDING",
            "exact_command_to_approve": " ".join(exact_parts),
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "skill_path": str(skill_path),
        "eval_set": str(eval_set),
        "case_count": len(cases),
        "case_hashes": case_hashes,
        "sandbox": args.sandbox,
        "timeout": args.timeout,
        "model": args.model,
        "exact_command": " ".join(exact_parts),
        "data_surfaces": [
            "skill source files",
            "eval prompts identified by hashes",
            "no broker credentials",
            "no wallet keys",
            "no CEX API secrets",
            "no live order tools unless separately approved",
        ],
        "must_not_do": [
            "place live trades",
            "send wallet transactions",
            "approve token allowances",
            "start live bots",
            "claim benchmark superiority from dry-run or signoff evidence",
        ],
        "evidence_boundary": "This packet proves live-eval readiness and approval status only. It does not prove model behavior.",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        markdown = Path(args.markdown)
        markdown.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(markdown, packet)
    if args.json:
        print(json.dumps(packet, indent=2, ensure_ascii=False))
    else:
        print(f"Live eval signoff packet: {packet['status']} {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
