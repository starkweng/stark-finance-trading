#!/usr/bin/env python3
"""Run the portable quality suite for stark-finance-trading."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def sanitize_output(text: str, cwd: Path) -> str:
    replacements = [
        (str(cwd), "."),
        (str(cwd.parent), ".."),
    ]
    sanitized = text
    for old, new in replacements:
        sanitized = sanitized.replace(old, new)
    return sanitized


def run_step(name: str, cmd: list[str], cwd: Path, allow_failure: bool = False) -> dict:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    stdout = sanitize_output(proc.stdout, cwd)
    stderr = sanitize_output(proc.stderr, cwd)
    return {
        "name": name,
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "status": "PASS" if proc.returncode == 0 or allow_failure else "FAIL",
        "stdout_tail": stdout[-3000:],
        "stderr_tail": stderr[-3000:],
        "allowed_failure": allow_failure,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--dist", default="dist")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    dist = (root / args.dist).resolve()
    dist_for_cmd = Path(args.dist)
    dist.mkdir(parents=True, exist_ok=True)
    py = sys.executable or "python3"

    steps = [
        ("quick_validate", [py, "scripts/quick_validate.py", "."]),
        ("skill_validator", [py, "scripts/validate_stark_finance_trading.py", "."]),
        ("public_readiness", [py, "scripts/validate_public_readiness.py", "."]),
        ("codex_evals_json", [py, "-m", "json.tool", "evals/codex-evals.json"]),
        ("routing_evals_json", [py, "-m", "json.tool", "evals/routing-evals.json"]),
        ("adversarial_evals_json", [py, "-m", "json.tool", "evals/adversarial-evals.json"]),
        ("live_behavior_evals_json", [py, "-m", "json.tool", "evals/live-behavior-evals.json"]),
        ("public_comparison_json", [py, "-m", "json.tool", "benchmarks/public-comparison-2026-06-28.json"]),
        ("public_benchmark_cases_json", [py, "-m", "json.tool", "benchmarks/public-benchmark-cases.json"]),
        ("competitive_task_cases_json", [py, "-m", "json.tool", "benchmarks/competitive-task-cases.json"]),
        (
            "eval_review_bundle_script_syntax",
            [
                py,
                "-c",
                "from pathlib import Path\nfor p in ['scripts/generate_eval_review_bundle.py', 'scripts/score_eval_review_bundle.py', 'scripts/generate_release_manifest.py', 'scripts/generate_release_notes.py', 'scripts/validate_github_actions_workflow.py', 'scripts/smoke_github_export.py', 'scripts/validate_release_readiness.py']:\n    compile(Path(p).read_text(encoding='utf-8'), p, 'exec')",
            ],
        ),
        (
            "github_actions_workflow",
            [
                py,
                "scripts/validate_github_actions_workflow.py",
                "--root",
                ".",
                "--out",
                str(dist_for_cmd / "stark-finance-trading.github-actions-workflow.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.github-actions-workflow.md"),
                "--json",
            ],
        ),
        (
            "public_source_audit_offline",
            [
                py,
                "scripts/audit_public_sources.py",
                "--root",
                ".",
                "--out",
                str(dist_for_cmd / "stark-finance-trading.public-source-audit.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.public-source-audit.md"),
                "--json",
            ],
        ),
        (
            "public_benchmark",
            [
                py,
                "scripts/generate_public_benchmark.py",
                "--root",
                ".",
                "--out",
                str(dist_for_cmd / "stark-finance-trading.public-benchmark.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.public-benchmark.md"),
                "--json",
            ],
        ),
        (
            "competitive_task_benchmark",
            [
                py,
                "scripts/generate_competitive_task_benchmark.py",
                "--root",
                ".",
                "--out",
                str(dist_for_cmd / "stark-finance-trading.competitive-task-benchmark.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.competitive-task-benchmark.md"),
                "--json",
            ],
        ),
        ("package", [py, "scripts/package_skill.py", ".", str(dist_for_cmd)]),
        ("install_smoke", [py, "scripts/install_package_smoke.py", str(dist_for_cmd / "stark-finance-trading.skill"), "--json"]),
        (
            "release_manifest",
            [
                py,
                "scripts/generate_release_manifest.py",
                str(dist_for_cmd / "stark-finance-trading.skill"),
                "--skill-root",
                ".",
                "--out",
                str(dist_for_cmd / "stark-finance-trading.release-manifest.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.release-manifest.md"),
                "--json",
            ],
        ),
        (
            "live_eval_signoff",
            [
                py,
                "scripts/generate_live_eval_signoff.py",
                "--skill-path",
                ".",
                "--eval-set",
                "evals/live-behavior-evals.json",
                "--live-out-dir",
                str(dist_for_cmd / "live-eval"),
                "--out",
                str(dist_for_cmd / "stark-finance-trading.live-eval-signoff.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.live-eval-signoff.md"),
                "--sandbox",
                "read-only",
                "--max-cases",
                "6",
            ],
        ),
        (
            "release_notes",
            [
                py,
                "scripts/generate_release_notes.py",
                "--skill-root",
                ".",
                "--release-manifest",
                str(dist_for_cmd / "stark-finance-trading.release-manifest.json"),
                "--live-signoff",
                str(dist_for_cmd / "stark-finance-trading.live-eval-signoff.json"),
                "--out",
                str(dist_for_cmd / "stark-finance-trading.release-notes.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.release-notes.md"),
                "--json",
            ],
        ),
        (
            "codex_eval_dry_run",
            [
                py,
                "scripts/codex_eval.py",
                "--skill-path",
                ".",
                "--eval-set",
                "evals/live-behavior-evals.json",
                "--out-dir",
                str(dist_for_cmd / "live-eval-dry-run"),
                "--max-cases",
                "6",
                "--json",
            ],
        ),
        (
            "live_eval_review_bundle",
            [
                py,
                "scripts/generate_eval_review_bundle.py",
                str(dist_for_cmd / "live-eval-dry-run"),
                "--eval-set",
                "evals/live-behavior-evals.json",
                "--out-dir",
                str(dist_for_cmd / "stark-finance-trading.live-eval-review"),
                "--title",
                "stark-finance-trading Live Behavior Eval Review",
                "--json",
            ],
        ),
        (
            "live_eval_review_scorecard",
            [
                py,
                "scripts/score_eval_review_bundle.py",
                str(dist_for_cmd / "stark-finance-trading.live-eval-review"),
                "--out",
                str(dist_for_cmd / "stark-finance-trading.live-eval-scorecard.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.live-eval-scorecard.md"),
                "--json",
            ],
        ),
        (
            "competitive_eval_signoff",
            [
                py,
                "scripts/generate_live_eval_signoff.py",
                "--skill-path",
                ".",
                "--eval-set",
                "benchmarks/competitive-task-cases.json",
                "--live-out-dir",
                str(dist_for_cmd / "competitive-eval"),
                "--out",
                str(dist_for_cmd / "stark-finance-trading.competitive-eval-signoff.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.competitive-eval-signoff.md"),
                "--sandbox",
                "read-only",
                "--max-cases",
                "8",
            ],
        ),
        (
            "competitive_codex_eval_dry_run",
            [
                py,
                "scripts/codex_eval.py",
                "--skill-path",
                ".",
                "--eval-set",
                "benchmarks/competitive-task-cases.json",
                "--out-dir",
                str(dist_for_cmd / "competitive-eval-dry-run"),
                "--max-cases",
                "8",
                "--json",
            ],
        ),
        (
            "competitive_eval_review_bundle",
            [
                py,
                "scripts/generate_eval_review_bundle.py",
                str(dist_for_cmd / "competitive-eval-dry-run"),
                "--eval-set",
                "benchmarks/competitive-task-cases.json",
                "--out-dir",
                str(dist_for_cmd / "stark-finance-trading.competitive-eval-review"),
                "--title",
                "stark-finance-trading Competitive Task Eval Review",
                "--json",
            ],
        ),
        (
            "competitive_eval_review_scorecard",
            [
                py,
                "scripts/score_eval_review_bundle.py",
                str(dist_for_cmd / "stark-finance-trading.competitive-eval-review"),
                "--out",
                str(dist_for_cmd / "stark-finance-trading.competitive-eval-scorecard.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.competitive-eval-scorecard.md"),
                "--json",
            ],
        ),
        (
            "github_export",
            [
                py,
                "scripts/export_github_repo.py",
                "--skill-root",
                ".",
                "--out-dir",
                str(dist_for_cmd / "github-export" / "stark-finance-trading"),
                "--release-artifacts-dir",
                str(dist_for_cmd),
                "--zip",
                str(dist_for_cmd / "stark-finance-trading-github-repo.zip"),
                "--report",
                str(dist_for_cmd / "stark-finance-trading.github-export-report.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.github-export-report.md"),
                "--json",
            ],
        ),
        (
            "github_export_smoke",
            [
                py,
                "scripts/smoke_github_export.py",
                "--zip",
                str(dist_for_cmd / "stark-finance-trading-github-repo.zip"),
                "--out",
                str(dist_for_cmd / "stark-finance-trading.github-export-smoke.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.github-export-smoke.md"),
                "--json",
            ],
        ),
        (
            "release_readiness",
            [
                py,
                "scripts/validate_release_readiness.py",
                "--skill-root",
                ".",
                "--dist",
                str(dist_for_cmd),
                "--out",
                str(dist_for_cmd / "stark-finance-trading.release-readiness.json"),
                "--markdown",
                str(dist_for_cmd / "stark-finance-trading.release-readiness.md"),
                "--json",
            ],
        ),
    ]
    results = [run_step(name, cmd, root) for name, cmd in steps]
    status = "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL"
    report = {
        "schema_version": "1.0",
        "status": status,
        "root": str(Path(args.root)),
        "dist": str(dist_for_cmd),
        "steps": results,
        "evidence_boundary": "Portable local quality suite; does not prove remote GitHub Actions or live model behavior.",
    }
    (dist / "stark-finance-trading.quality-suite.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"quality suite: {status}")
        for item in results:
            print(f"- {item['name']}: {item['status']}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
