#!/usr/bin/env python3
"""Validate public benchmark and adversarial coverage for stark-finance-trading."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_BENCHMARK_FILES = [
    "BENCHMARK.md",
    "benchmarks/public-comparison-2026-06-28.json",
    "benchmarks/PUBLIC_COMPARISON_2026-06-28.md",
    "benchmarks/public-benchmark-cases.json",
    "benchmarks/competitive-task-cases.json",
    "references/local-skill-router.md",
    "references/public-tool-catalog.json",
    "evals/adversarial-evals.json",
    "evals/live-behavior-evals.json",
    "evals/tool-routing-cases.json",
    "scripts/codex_eval.py",
    "scripts/live_eval_runner_fixture.py",
    "scripts/run_live_eval_harness_smoke.py",
    "scripts/audit_public_sources.py",
    "scripts/discover_local_skill_inventory.py",
    "scripts/plan_tool_route.py",
    "scripts/runtime_capability_scan.py",
    "scripts/generate_integration_activation_plan.py",
    "scripts/generate_release_blocker_plan.py",
    "scripts/validate_public_tool_catalog.py",
    "scripts/generate_competitive_task_benchmark.py",
    "scripts/generate_eval_review_bundle.py",
    "scripts/generate_public_benchmark.py",
    "scripts/generate_live_eval_signoff.py",
    "scripts/generate_release_manifest.py",
    "scripts/generate_release_notes.py",
    "scripts/run_quality_suite.py",
    "scripts/enable_remote_ci.py",
    "scripts/validate_github_actions_workflow.py",
    "scripts/smoke_github_export.py",
    "scripts/score_eval_review_bundle.py",
    "scripts/validate_release_readiness.py",
    "scripts/audit_external_proofs.py",
    "scripts/audit_goal_completion.py",
    "scripts/discover_github_finance_tools.py",
    "scripts/analyze_competitive_gaps.py",
    "scripts/generate_competitive_route_backlog.py",
    "workflow-templates/stark-finance-trading-ci.yml",
]

REQUIRED_ADVERSARIAL_CATEGORIES = {
    "prompt_injection",
    "secret_request",
    "live_execution",
    "overclaim",
    "stale_data",
    "negative_routing",
    "token_identity",
    "legal_boundary",
    "untrusted_tool_output",
    "data_semantics",
}

FORBIDDEN_PUBLIC_CLAIMS = [
    re.compile(r"best on GitHub", re.I),
    re.compile(r"最牛"),
    re.compile(r"最强"),
    re.compile(r"打败所有竞品"),
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False, indent=2))
    return 1


def validate(root: Path) -> int:
    if root.is_file():
        root = root.parent

    missing = [rel for rel in REQUIRED_BENCHMARK_FILES if not (root / rel).exists()]
    if missing:
        return fail(f"missing public readiness files: {', '.join(missing)}")

    comparison = load_json(root / "benchmarks/public-comparison-2026-06-28.json")
    candidates = comparison.get("candidates", [])
    if comparison.get("claim_status") != "benchmark_defined_no_superiority_claim":
        return fail("public comparison must avoid superiority claims")
    if len(candidates) < 20:
        return fail("public comparison must include at least 20 candidates")
    official_count = sum(1 for item in candidates if "official" in item.get("source_status", "") or "primary" in item.get("source_status", ""))
    if official_count < 18:
        return fail("public comparison must prioritize official or primary sources")
    for item in candidates:
        for field in ["name", "category", "source_url", "source_status", "route_role", "what_stark_must_do_better"]:
            if not item.get(field):
                return fail(f"candidate missing {field}: {item.get('name', '<unknown>')}")
        if not str(item["source_url"]).startswith("https://"):
            return fail(f"candidate source_url must be https: {item['name']}")
    public_tool_catalog = load_json(root / "references/public-tool-catalog.json")
    public_tools = public_tool_catalog.get("catalog", [])
    if len(public_tools) < 30:
        return fail("public tool catalog must include at least 30 tools")
    if sum(1 for item in public_tools if "official" in str(item.get("source_status", ""))) < 30:
        return fail("public tool catalog must be official-source-led")
    if sum(1 for item in public_tools if item.get("default_action_tier") == 4) < 5:
        return fail("public tool catalog must identify high-risk execution surfaces")
    public_tool_ids = {item.get("id") for item in public_tools}
    for required_id in ["dune-mcp", "alchemy-mcp", "etherscan-mcp", "alpaca-mcp", "ibkr-tws-api", "hummingbot", "freqtrade"]:
        if required_id not in public_tool_ids:
            return fail(f"public tool catalog missing required id: {required_id}")
    benchmark_cases = load_json(root / "benchmarks/public-benchmark-cases.json")
    dimensions = benchmark_cases.get("dimensions", [])
    if len(dimensions) < 7:
        return fail("public benchmark cases must include at least 7 dimensions")
    if sum(int(item.get("weight", 0)) for item in dimensions) != 100:
        return fail("public benchmark weights must sum to 100")
    competitive = load_json(root / "benchmarks/competitive-task-cases.json")
    competitive_cases = competitive.get("cases", [])
    if len(competitive_cases) < 8:
        return fail("competitive task benchmark must include at least 8 cases")
    for case in competitive_cases:
        if not case.get("required_terms") or not case.get("required_safety_terms"):
            return fail(f"competitive task case needs coverage and safety terms: {case.get('id')}")

    adversarial = load_json(root / "evals/adversarial-evals.json")
    cases = adversarial.get("cases", [])
    if len(cases) < 10:
        return fail("adversarial evals must include at least 10 cases")
    categories = {case.get("category") for case in cases}
    missing_categories = sorted(REQUIRED_ADVERSARIAL_CATEGORIES - categories)
    if missing_categories:
        return fail(f"adversarial evals missing categories: {', '.join(missing_categories)}")
    for case in cases:
        if not case.get("must_do") or not case.get("must_not_do"):
            return fail(f"adversarial case needs must_do and must_not_do: {case.get('id')}")

    live_behavior = load_json(root / "evals/live-behavior-evals.json")
    live_cases = live_behavior.get("cases", [])
    live_categories = {case.get("category") for case in live_cases}
    for category in ["routing_source_discipline", "execution_safety", "public_claims"]:
        if category not in live_categories:
            return fail(f"live behavior evals missing category: {category}")
    tool_routing = load_json(root / "evals/tool-routing-cases.json")
    tool_routing_cases = tool_routing.get("cases", [])
    if len(tool_routing_cases) < 10:
        return fail("tool routing cases must include at least 10 cases")
    if not any(case.get("should_load") is False for case in tool_routing_cases):
        return fail("tool routing cases must include negative handoff cases")
    if not any("ibkr-tws-api" in case.get("expected_tool_ids", []) for case in tool_routing_cases):
        return fail("tool routing cases must cover IBKR wrapper boundary")

    benchmark_md = (root / "BENCHMARK.md").read_text(encoding="utf-8")
    if (
        "Public Comparison Candidates" not in benchmark_md
        or "Adversarial Coverage" not in benchmark_md
        or "Public Benchmark Gate" not in benchmark_md
        or "Public source audit" not in benchmark_md
        or "Competitive Task Benchmark" not in benchmark_md
        or "Eval Review Bundle" not in benchmark_md
        or "Eval Review Scorecard Gate" not in benchmark_md
        or "Live Eval Harness Smoke" not in benchmark_md
        or "GitHub Actions Workflow Gate" not in benchmark_md
        or "Remote CI Proof Gate" not in benchmark_md
        or "External Proof Audit Gate" not in benchmark_md
        or "Goal Completion Audit Gate" not in benchmark_md
        or "GitHub Discovery Gate" not in benchmark_md
        or "GitHub Export Smoke Gate" not in benchmark_md
        or "Release Readiness Gate" not in benchmark_md
        or "Competitive Gap Analysis Gate" not in benchmark_md
        or "Competitive Route Backlog Gate" not in benchmark_md
        or "Integration Activation Plan Gate" not in benchmark_md
        or "Release Blocker Plan Gate" not in benchmark_md
    ):
        return fail("BENCHMARK.md must mention public comparison, public source audit, competitive task benchmark, eval review bundle, Eval Review Scorecard Gate, Live Eval Harness Smoke, GitHub Actions Workflow Gate, Remote CI Proof Gate, External Proof Audit Gate, Goal Completion Audit Gate, GitHub Discovery Gate, Competitive Gap Analysis Gate, Competitive Route Backlog Gate, Integration Activation Plan Gate, Release Blocker Plan Gate, GitHub Export Smoke Gate, Release Readiness Gate, adversarial coverage, and public benchmark gate")

    scanned_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [
            root / "README.md",
            root / "BENCHMARK.md",
            root / "benchmarks/PUBLIC_COMPARISON_2026-06-28.md",
        ]
    )
    # Allow anti-claim examples only when framed as rejected language.
    sanitized = scanned_text.replace("Avoid public superiority claims", "")
    for pattern in FORBIDDEN_PUBLIC_CLAIMS:
        if pattern.search(sanitized):
            return fail(f"unverified public superiority claim matched: {pattern.pattern}")

    print(json.dumps({
        "ok": True,
        "skill": "stark-finance-trading",
        "candidates": len(candidates),
        "official_or_primary_sources": official_count,
        "adversarial_cases": len(cases),
        "live_behavior_cases": len(live_cases),
        "public_benchmark_dimensions": len(dimensions),
        "competitive_task_cases": len(competitive_cases),
        "public_tool_catalog_tools": len(public_tools),
        "tool_routing_cases": len(tool_routing_cases),
        "adversarial_categories": sorted(categories),
        "live_behavior_categories": sorted(live_categories),
        "evidence_boundary": comparison.get("evidence_boundary"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    raise SystemExit(validate(target))
