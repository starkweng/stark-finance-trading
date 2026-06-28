#!/usr/bin/env python3
"""Validate GitHub Actions workflow coverage for stark-finance-trading."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_SNIPPETS = [
    ("workflow_name", "name: stark-finance-trading-ci"),
    ("push_trigger", "push:"),
    ("pull_request_trigger", "pull_request:"),
    ("manual_trigger", "workflow_dispatch:"),
    ("ubuntu_runner", "runs-on: ubuntu-latest"),
    ("checkout", "actions/checkout@v4"),
    ("python_setup", "actions/setup-python@v5"),
    ("python_312", 'python-version: "3.12"'),
    ("subdir_working_directory", "working-directory: stark-finance-trading"),
    ("quality_suite", "python3 scripts/run_quality_suite.py --json"),
    ("package_build", "python3 scripts/package_skill.py . dist"),
    ("install_smoke", "python3 scripts/install_package_smoke.py dist/stark-finance-trading.skill --json"),
    ("artifact_upload", "actions/upload-artifact@v4"),
]


REQUIRED_ARTIFACTS = [
    "stark-finance-trading/dist/stark-finance-trading.skill",
    "stark-finance-trading/dist/stark-finance-trading.quality-suite.json",
    "stark-finance-trading/dist/stark-finance-trading.release-manifest.json",
    "stark-finance-trading/dist/stark-finance-trading.release-manifest.md",
    "stark-finance-trading/dist/stark-finance-trading.release-notes.json",
    "stark-finance-trading/dist/stark-finance-trading.release-notes.md",
    "stark-finance-trading/dist/stark-finance-trading.public-source-audit.json",
    "stark-finance-trading/dist/stark-finance-trading.public-source-audit.md",
    "stark-finance-trading/dist/stark-finance-trading.public-benchmark.json",
    "stark-finance-trading/dist/stark-finance-trading.public-benchmark.md",
    "stark-finance-trading/dist/stark-finance-trading.local-skill-inventory.json",
    "stark-finance-trading/dist/stark-finance-trading.local-skill-inventory.md",
    "stark-finance-trading/dist/stark-finance-trading.competitive-task-benchmark.json",
    "stark-finance-trading/dist/stark-finance-trading.competitive-task-benchmark.md",
    "stark-finance-trading/dist/stark-finance-trading.live-eval-signoff.json",
    "stark-finance-trading/dist/stark-finance-trading.live-eval-signoff.md",
    "stark-finance-trading/dist/stark-finance-trading.live-eval-review/**",
    "stark-finance-trading/dist/stark-finance-trading.live-eval-scorecard.json",
    "stark-finance-trading/dist/stark-finance-trading.live-eval-scorecard.md",
    "stark-finance-trading/dist/stark-finance-trading.competitive-eval-signoff.json",
    "stark-finance-trading/dist/stark-finance-trading.competitive-eval-signoff.md",
    "stark-finance-trading/dist/stark-finance-trading.competitive-eval-review/**",
    "stark-finance-trading/dist/stark-finance-trading.competitive-eval-scorecard.json",
    "stark-finance-trading/dist/stark-finance-trading.competitive-eval-scorecard.md",
    "stark-finance-trading/dist/stark-finance-trading.github-export-report.json",
    "stark-finance-trading/dist/stark-finance-trading.github-export-report.md",
    "stark-finance-trading/dist/stark-finance-trading.github-export-smoke.json",
    "stark-finance-trading/dist/stark-finance-trading.github-export-smoke.md",
    "stark-finance-trading/dist/stark-finance-trading.release-readiness.json",
    "stark-finance-trading/dist/stark-finance-trading.release-readiness.md",
    "stark-finance-trading/dist/stark-finance-trading-github-repo.zip",
    "stark-finance-trading/VALIDATION.md",
    "stark-finance-trading/BENCHMARK.md",
    "stark-finance-trading/benchmarks/PUBLIC_COMPARISON_2026-06-28.md",
]


def check_contains(text: str, check_id: str, snippet: str) -> dict[str, Any]:
    return {
        "id": check_id,
        "passed": snippet in text,
        "evidence": snippet,
    }


def validate(workflow_path: Path) -> dict[str, Any]:
    text = workflow_path.read_text(encoding="utf-8")
    checks = [check_contains(text, check_id, snippet) for check_id, snippet in REQUIRED_SNIPPETS]
    artifact_checks = [
        {
            "id": f"artifact:{artifact}",
            "passed": artifact in text,
            "evidence": artifact,
        }
        for artifact in REQUIRED_ARTIFACTS
    ]
    all_checks = checks + artifact_checks
    return {
        "schema_version": "1.0",
        "status": "PASS" if all(item["passed"] for item in all_checks) else "FAIL",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "workflow": str(workflow_path),
        "checks": all_checks,
        "required_snippet_count": len(REQUIRED_SNIPPETS),
        "required_artifact_count": len(REQUIRED_ARTIFACTS),
        "failed_checks": [item for item in all_checks if not item["passed"]],
        "evidence_boundary": "Static workflow coverage validation only. It does not prove remote GitHub Actions execution, uploaded artifact availability, or live model behavior.",
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# GitHub Actions Workflow Validation",
        "",
        f"- Status: {report['status']}",
        f"- Workflow: `{report['workflow']}`",
        f"- Required snippets: {report['required_snippet_count']}",
        f"- Required artifacts: {report['required_artifact_count']}",
        "",
        "## Checks",
        "",
        "| Check | Status | Evidence |",
        "|---|---|---|",
    ]
    for check in report["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(f"| `{check['id']}` | {status} | `{check['evidence']}` |")
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate GitHub Actions workflow coverage.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--workflow", default=".github/workflows/ci.yml")
    parser.add_argument("--out")
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    workflow_path = root / args.workflow
    if not workflow_path.exists():
        report = {
            "schema_version": "1.0",
            "status": "FAIL",
            "workflow": str(workflow_path),
            "checks": [],
            "failed_checks": [{"id": "workflow_exists", "passed": False, "evidence": str(workflow_path)}],
            "evidence_boundary": "Workflow file is missing.",
        }
    else:
        report = validate(workflow_path)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        markdown = Path(args.markdown)
        markdown.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(markdown, report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"github actions workflow: {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
