#!/usr/bin/env python3
"""Generate a source-level public benchmark scorecard."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def read_json(path: Path) -> dict:
    return json.loads(read_text(path)) if path.exists() else {}


def has_all(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def is_primary_status(value: str) -> bool:
    lowered = value.lower()
    return "official" in lowered or "primary" in lowered


def score_dimension(root: Path, dimension_id: str, weight: int) -> dict:
    skill = read_text(root / "SKILL.md")
    router = read_text(root / "references/tool-router.md")
    safety = read_text(root / "references/safety-policy.md")
    workflows = read_text(root / "references/workflows.md")
    source_ledger = read_text(root / "references/source-ledger.md")
    gotchas = read_text(root / "references/gotchas.md")
    benchmark = read_text(root / "BENCHMARK.md")
    workflow_ci = read_text(root / ".github/workflows/ci.yml")
    routing_cases = (read_json(root / "evals/routing-evals.json").get("cases") or [])
    codex_eval_file = read_json(root / "evals/codex-evals.json")
    codex_cases = (codex_eval_file.get("cases") or codex_eval_file.get("evals") or [])
    adversarial_cases = (read_json(root / "evals/adversarial-evals.json").get("cases") or [])
    live_cases = (read_json(root / "evals/live-behavior-evals.json").get("cases") or [])
    comparison = read_json(root / "benchmarks/public-comparison-2026-06-28.json")
    candidates = comparison.get("candidates") or []
    official_sources = [item for item in candidates if is_primary_status(str(item.get("source_status", "")))]

    checks: list[tuple[str, bool]] = []
    if dimension_id == "routing_precision":
        checks = [
            ("description_load_and_do_not_load", "Load when" in skill and "Do not load" in skill),
            ("routing_cases_min_8", len(routing_cases) >= 8),
            ("negative_cases_present", any(case.get("should_load") is False for case in routing_cases)),
            ("one_skill_merge_logic", "Do not create separate user-facing skills for every vendor" in router),
        ]
    elif dimension_id == "source_discipline":
        checks = [
            ("source_ledger_exists", bool(source_ledger)),
            ("official_or_primary_sources_min_20", len(official_sources) >= 20),
            ("evidence_labels_required", has_all(skill, ["timestamp", "venue", "delay"]) or has_all(skill, ["source", "timestamp", "venue"])),
            ("dune_semantics_gotcha", "table semantics" in gotchas and "pump.fun" in gotchas),
            ("public_source_audit_script", (root / "scripts/audit_public_sources.py").exists()),
        ]
    elif dimension_id == "safety_boundary":
        checks = [
            ("risk_tiers", "Risk Tiers" in safety),
            ("tier_4_confirmation", "Tier 4" in safety and "Explicit confirmation required" in safety),
            ("full_execution_checklist", has_all(safety, ["venue", "account", "instrument", "quantity", "slippage", "max loss", "kill switch"])),
            (
                "adversarial_safety_cases",
                {"live_execution", "secret_request", "prompt_injection"}.issubset({case.get("category") for case in adversarial_cases}),
            ),
        ]
    elif dimension_id == "workflow_coverage":
        checks = [
            (
                "workflow_sections",
                has_all(workflows, ["Market Snapshot", "Token Due Diligence", "Smart-Money", "Options", "Strategy Backtest", "Execution Prep", "MM", "Local Skill Delegation"]),
            ),
            (
                "live_behavior_categories",
                {"routing_source_discipline", "execution_safety", "data_semantics", "strategy_validation", "public_claims"}.issubset({case.get("category") for case in live_cases}),
            ),
        ]
    elif dimension_id == "portability":
        packager = read_text(root / "scripts/package_skill.py")
        exporter = read_text(root / "scripts/export_github_repo.py")
        checks = [
            ("deterministic_packager", "FIXED_ZIP_TIMESTAMP" in packager),
            ("install_smoke", (root / "scripts/install_package_smoke.py").exists()),
            ("quality_suite", (root / "scripts/run_quality_suite.py").exists()),
            ("github_export_subdir_validation", "github_actions_subdir_workflow" in exporter),
            ("ci_quality_suite_subdir", "working-directory: stark-finance-trading" in workflow_ci and "scripts/run_quality_suite.py" in workflow_ci),
        ]
    elif dimension_id == "eval_coverage":
        checks = [
            ("routing_evals", len(routing_cases) >= 8),
            ("codex_evals", len(codex_cases) >= 8),
            ("adversarial_evals", len(adversarial_cases) >= 10),
            ("live_behavior_evals", len(live_cases) >= 6),
            ("live_signoff_script", (root / "scripts/generate_live_eval_signoff.py").exists()),
        ]
    elif dimension_id == "public_readiness":
        required = ["README.md", "LICENSE.txt", "CHANGELOG.md", "SECURITY.md", "CONTRIBUTING.md", "VALIDATION.md", "BENCHMARK.md"]
        checks = [
            ("public_docs", all((root / item).exists() for item in required)),
            (
                "release_evidence_scripts",
                all(
                    (root / item).exists()
                    for item in [
                        "scripts/export_github_repo.py",
                        "scripts/package_skill.py",
                        "scripts/generate_release_manifest.py",
                        "scripts/generate_release_notes.py",
                    ]
                ),
            ),
            ("github_actions_workflow_validator", (root / "scripts/validate_github_actions_workflow.py").exists() and "GitHub Actions Workflow Gate" in benchmark),
            ("public_comparison_report", (root / "benchmarks/PUBLIC_COMPARISON_2026-06-28.md").exists()),
            ("public_source_audit", (root / "scripts/audit_public_sources.py").exists()),
            ("local_skill_inventory", (root / "scripts/discover_local_skill_inventory.py").exists() and (root / "references/local-skill-router.md").exists()),
            ("competitive_task_benchmark", (root / "scripts/generate_competitive_task_benchmark.py").exists() and (root / "benchmarks/competitive-task-cases.json").exists()),
            ("no_superiority_claim_status", comparison.get("claim_status") == "benchmark_defined_no_superiority_claim" and "Avoid public superiority claims" in benchmark),
        ]
    else:
        checks = [("unknown_dimension", False)]

    passed = sum(1 for _, ok in checks if ok)
    score = round(weight * passed / len(checks), 2) if checks else 0
    return {
        "id": dimension_id,
        "weight": weight,
        "score": score,
        "passed_checks": passed,
        "total_checks": len(checks),
        "checks": [{"id": name, "passed": ok} for name, ok in checks],
    }


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# stark-finance-trading Public Benchmark",
        "",
        f"- Status: {report['status']}",
        f"- Score: {report['score']}/{report['max_score']}",
        f"- Claim status: `{report['claim_status']}`",
        f"- Public candidates: {report['candidate_count']}",
        f"- Official or primary sources: {report['official_or_primary_sources']}",
        "",
        "## Scorecard",
        "",
        "| Dimension | Score | Checks |",
        "|---|---:|---:|",
    ]
    for item in report["dimensions"]:
        lines.append(f"| `{item['id']}` | {item['score']}/{item['weight']} | {item['passed_checks']}/{item['total_checks']} |")
    lines.extend([
        "",
        "## Evidence Boundary",
        "",
        report["evidence_boundary"],
        "",
        "## Pending Proof",
        "",
        "- Live behavior eval against an approved model-service runner.",
        "- Reviewed public competitor task runs.",
        "- Remote GitHub Actions completion after publishing.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--cases", default="benchmarks/public-benchmark-cases.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    cases = read_json(root / args.cases)
    comparison = read_json(root / "benchmarks/public-comparison-2026-06-28.json")
    candidates = comparison.get("candidates") or []
    dimensions = [
        score_dimension(root, item["id"], int(item["weight"]))
        for item in cases.get("dimensions", [])
    ]
    score = round(sum(item["score"] for item in dimensions), 2)
    max_score = sum(item["weight"] for item in dimensions)
    minimum = int(cases.get("minimum_pass_score", 90))
    report = {
        "schema_version": "1.0",
        "status": "PASS" if score >= minimum and all(item["passed_checks"] == item["total_checks"] for item in dimensions) else "FAIL",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": "stark-finance-trading",
        "benchmark_type": cases.get("benchmark_type"),
        "claim_status": "source_level_benchmark_pass_live_comparison_pending",
        "score": score,
        "max_score": max_score,
        "minimum_pass_score": minimum,
        "candidate_count": len(candidates),
        "official_or_primary_sources": sum(1 for item in candidates if is_primary_status(str(item.get("source_status", "")))),
        "dimensions": dimensions,
        "evidence_boundary": "Source-level benchmark over the current skill tree. This does not prove live model behavior, remote GitHub CI, or public superiority over competing projects.",
    }
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
        print(f"public benchmark: {report['status']} {score}/{max_score}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
