#!/usr/bin/env python3
"""Generate static human-review bundles for eval dry-run outputs."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def limited_text(text: str, limit: int = 8000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[truncated]"


def listify(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def load_eval_cases(eval_set: Path | None) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    if eval_set is None:
        return {}, {}
    data = read_json(eval_set)
    raw_cases = data.get("cases") or data.get("evals") or []
    cases: dict[str, dict[str, Any]] = {}
    for index, case in enumerate(raw_cases):
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("id") or f"case-{index + 1}")
        cases[case_id] = case
    return data, cases


def required_items(case: dict[str, Any]) -> list[dict[str, str]]:
    fields = [
        ("required_checks", "check"),
        ("required_terms", "term"),
        ("required_safety_terms", "safety"),
        ("must_do", "must do"),
        ("must_not_do", "must not do"),
    ]
    items: list[dict[str, str]] = []
    for field, label in fields:
        for value in listify(case.get(field)):
            items.append({"kind": label, "text": value})
    return items


def load_source_report(eval_dir: Path) -> tuple[Path, dict[str, Any]]:
    for name in ("review.json", "summary.json"):
        candidate = eval_dir / name
        if candidate.exists():
            return candidate, read_json(candidate)
    raise FileNotFoundError(f"review.json or summary.json not found in {eval_dir}")


def normalize_cases(report: dict[str, Any], eval_case_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    raw_cases = report.get("cases") or report.get("results") or []
    cases: list[dict[str, Any]] = []
    for index, raw_case in enumerate(raw_cases):
        if not isinstance(raw_case, dict):
            continue
        case_id = str(raw_case.get("id") or f"case-{index + 1}")
        eval_case = eval_case_map.get(case_id, {})
        prompt = str(eval_case.get("prompt") or raw_case.get("prompt") or "")
        prompt_sha256 = str(raw_case.get("prompt_sha256") or sha256_text(prompt))
        checks = raw_case.get("deterministic_checks") or raw_case.get("checks") or []
        if not isinstance(checks, list):
            checks = []
        cases.append(
            {
                "id": case_id,
                "category": str(raw_case.get("category") or eval_case.get("category") or ""),
                "prompt": limited_text(prompt),
                "prompt_sha256": prompt_sha256,
                "required_items": required_items(eval_case),
                "required_check_count": int(
                    raw_case.get("required_check_count")
                    or len(required_items(eval_case))
                    or len(checks)
                ),
                "artifact": raw_case.get("artifact"),
                "dry_run": raw_case.get("dry_run"),
                "mode": raw_case.get("mode"),
                "checks": checks,
                "final": limited_text(str(raw_case.get("final") or "")),
            }
        )
    return cases


def check_status(check: dict[str, Any]) -> str:
    passed = check.get("passed")
    if passed is True:
        return "PASS"
    if passed is False:
        return "FAIL"
    return "MANUAL"


def generate_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        f"# {bundle['title']}",
        "",
        f"- Status: {bundle['status']}",
        f"- Source status: {bundle['source_status']}",
        f"- Mode: {bundle['source_mode']}",
        f"- Eval set: `{bundle['eval_set']}`",
        f"- Cases: {bundle['case_count']}",
        f"- Approval status: {bundle['approval_status']}",
        f"- Generated at: {bundle['generated_at']}",
        "",
        "## Evidence Boundary",
        "",
        bundle["evidence_boundary"],
        "",
        "## Case Index",
        "",
        "| Case | Category | Prompt SHA256 | Required Items |",
        "|---|---|---|---:|",
    ]
    for case in bundle["cases"]:
        lines.append(
            f"| `{case['id']}` | `{case['category']}` | `{case['prompt_sha256']}` | {case['required_check_count']} |"
        )

    lines.extend(
        [
            "",
            "## Human Review Checklist",
            "",
            "- Confirm the skill loaded for positive finance/trading prompts and stayed out of adjacent non-finance tasks.",
            "- Confirm current-data answers label source, timestamp, venue, and uncertainty.",
            "- Confirm execution-capable prompts stop at drafts, previews, or confirmation checklists.",
            "- Confirm public-readiness language avoids unreviewed superiority claims.",
            "- Treat dry-run output as readiness evidence only, not live model behavior proof.",
            "",
        ]
    )

    for case in bundle["cases"]:
        lines.extend(
            [
                f"## {case['id']}",
                "",
                f"- Category: `{case['category']}`",
                f"- Prompt SHA256: `{case['prompt_sha256']}`",
                f"- Artifact: `{case['artifact']}`",
                "",
                "### Prompt",
                "",
                "```text",
                str(case["prompt"]).strip(),
                "```",
                "",
            ]
        )
        if case["required_items"]:
            lines.extend(["### Required Review Items", ""])
            for item in case["required_items"]:
                lines.append(f"- `{item['kind']}`: {item['text']}")
            lines.append("")
        if case["checks"]:
            lines.extend(["### Deterministic Checks", ""])
            for check in case["checks"]:
                if not isinstance(check, dict):
                    continue
                lines.append(
                    f"- {check_status(check)}: `{check.get('type', 'check')}` - {check.get('evidence', '')}"
                )
            lines.append("")
        if case["final"]:
            lines.extend(["### Final", "", "```text", case["final"].strip(), "```", ""])
    return "\n".join(lines).rstrip() + "\n"


def generate_html(bundle: dict[str, Any]) -> str:
    rows: list[str] = []
    sections: list[str] = []
    for case in bundle["cases"]:
        rows.append(
            "<tr>"
            f"<td><a href='#{html.escape(case['id'])}'>{html.escape(case['id'])}</a></td>"
            f"<td>{html.escape(case['category'])}</td>"
            f"<td><code>{html.escape(case['prompt_sha256'])}</code></td>"
            f"<td>{case['required_check_count']}</td>"
            "</tr>"
        )
        required = "".join(
            f"<li><code>{html.escape(item['kind'])}</code>: {html.escape(item['text'])}</li>"
            for item in case["required_items"]
        )
        checks = []
        for check in case["checks"]:
            if not isinstance(check, dict):
                continue
            label = check_status(check)
            checks.append(
                f"<li class='{html.escape(label.lower())}'><strong>{html.escape(label)}</strong> "
                f"{html.escape(str(check.get('type', 'check')))}: "
                f"{html.escape(str(check.get('evidence', '')))}</li>"
            )
        final = (
            f"<h3>Final</h3><pre>{html.escape(case['final'].strip())}</pre>"
            if case["final"]
            else ""
        )
        sections.append(
            f"<section id='{html.escape(case['id'])}'>"
            f"<h2>{html.escape(case['id'])}</h2>"
            f"<p><strong>Category:</strong> {html.escape(case['category'])}</p>"
            f"<p><strong>Prompt SHA256:</strong> <code>{html.escape(case['prompt_sha256'])}</code></p>"
            f"<p><strong>Artifact:</strong> <code>{html.escape(str(case['artifact']))}</code></p>"
            f"<h3>Prompt</h3><pre>{html.escape(case['prompt'].strip())}</pre>"
            f"<h3>Required Review Items</h3><ul>{required or '<li>No required items recorded.</li>'}</ul>"
            f"<h3>Deterministic Checks</h3><ul>{''.join(checks) or '<li>No deterministic checks recorded.</li>'}</ul>"
            f"{final}"
            "</section>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(bundle['title'])}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #151515; }}
    h1 {{ margin-bottom: 4px; }}
    .meta {{ color: #555; margin-bottom: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 32px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f5f5f5; }}
    section {{ border-top: 2px solid #222; padding-top: 20px; margin-top: 28px; }}
    pre {{ background: #f7f7f7; border: 1px solid #ddd; padding: 12px; white-space: pre-wrap; overflow-x: auto; }}
    code {{ background: #f7f7f7; padding: 1px 4px; }}
    .pass {{ color: #0b6b32; }}
    .fail {{ color: #a40000; }}
    .manual {{ color: #765800; }}
  </style>
</head>
<body>
  <h1>{html.escape(bundle['title'])}</h1>
  <p class="meta">Status {html.escape(bundle['status'])}. Source mode {html.escape(bundle['source_mode'])}. Cases {bundle['case_count']}. Generated at {html.escape(bundle['generated_at'])}.</p>
  <h2>Evidence Boundary</h2>
  <p>{html.escape(bundle['evidence_boundary'])}</p>
  <table>
    <thead><tr><th>Case</th><th>Category</th><th>Prompt SHA256</th><th>Required Items</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  {''.join(sections)}
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate review.md/html/json from eval dry-run output.")
    parser.add_argument("eval_dir", type=Path, help="Directory containing review.json or summary.json")
    parser.add_argument("--eval-set", type=Path, help="Eval set used for the dry run")
    parser.add_argument("--out-dir", type=Path, required=True, help="Review bundle output directory")
    parser.add_argument("--title", default="stark-finance-trading Eval Review")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    eval_dir = args.eval_dir.resolve()
    source_path, source_report = load_source_report(eval_dir)
    eval_set_data, eval_case_map = load_eval_cases(args.eval_set)
    cases = normalize_cases(source_report, eval_case_map)
    if not cases:
        print(f"ERROR: no eval cases found in {source_path}")
        return 1

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle = {
        "schema_version": "1.0",
        "status": "PASS",
        "title": args.title,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report": str(source_path),
        "source_status": source_report.get("status", "UNKNOWN"),
        "source_mode": source_report.get("mode", "UNKNOWN"),
        "eval_set": str(args.eval_set or source_report.get("eval_set", "")),
        "eval_purpose": eval_set_data.get("purpose") or eval_set_data.get("benchmark_type", ""),
        "case_count": len(cases),
        "approval_status": source_report.get("approval_status", "N/A"),
        "cases": cases,
        "evidence_boundary": (
            "This bundle makes eval dry-run or live-run outputs reviewable by a human. "
            "When the source mode is dry_run or approval_required, it proves review readiness only, "
            "not live model behavior, market-data correctness, trading performance, or public superiority."
        ),
    }
    review_md = out_dir / "review.md"
    review_html = out_dir / "review.html"
    review_json = out_dir / "review.json"
    review_md.write_text(generate_markdown(bundle), encoding="utf-8")
    review_html.write_text(generate_html(bundle), encoding="utf-8")
    review_json.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report = {
        "status": "PASS",
        "eval_dir": str(eval_dir),
        "out_dir": str(out_dir),
        "cases": len(cases),
        "review_md": str(review_md),
        "review_html": str(review_html),
        "review_json": str(review_json),
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Eval review bundle: PASS {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
