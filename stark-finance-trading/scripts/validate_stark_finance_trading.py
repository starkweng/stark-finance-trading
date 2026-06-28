#!/usr/bin/env python3
"""Deterministic validator for the stark-finance-trading skill."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "VERSION",
    "CHANGELOG.md",
    "references/tool-router.md",
    "references/local-skill-router.md",
    "references/safety-policy.md",
    "references/workflows.md",
    "references/source-ledger.md",
    "references/public-tool-catalog.json",
    "references/gotchas.md",
    "evals/routing-evals.json",
    "evals/adversarial-evals.json",
    "evals/live-behavior-evals.json",
    "evals/tool-routing-cases.json",
    "benchmarks/public-comparison-2026-06-28.json",
    "benchmarks/PUBLIC_COMPARISON_2026-06-28.md",
    "benchmarks/public-benchmark-cases.json",
    "benchmarks/competitive-task-cases.json",
    "scripts/codex_eval.py",
    "scripts/live_eval_runner_fixture.py",
    "scripts/run_live_eval_harness_smoke.py",
    "scripts/audit_public_sources.py",
    "scripts/discover_local_skill_inventory.py",
    "scripts/plan_tool_route.py",
    "scripts/runtime_capability_scan.py",
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
    "workflow-templates/stark-finance-trading-ci.yml",
]

REQUIRED_TOOL_TERMS = [
    "Dune",
    "Alchemy",
    "Etherscan",
    "Binance",
    "GMGN",
    "Alpaca",
    "OpenBB",
    "QuantConnect",
    "Alpha Vantage",
    "Financial Modeling Prep",
    "FactSet",
    "Twelve Data",
    "Unusual Whales",
    "Massive",
    "Tradier",
    "cTrader",
    "Coinbase",
    "QuickNode",
    "CoinGecko",
    "CoinMarketCap",
    "Token Terminal",
    "DeFiLlama",
    "Helius",
    "Jupiter",
    "DexScreener",
    "Databento",
    "Stripe",
    "Plaid",
    "IBKR",
    "NautilusTrader",
    "CCXT",
]

REQUIRED_LOCAL_SKILL_TERMS = [
    "earnings-preview",
    "equity-research",
    "dcf-model",
    "comps-analysis",
    "bond-futures-basis",
    "option-vol-analysis",
    "portfolio-rebalance",
    "gmgn-token",
    "gmgn-swap",
    "binance",
    "derivatives-trading-coin-futures",
    "stark-liquidity-strategy",
    "stark-tokenomics-planner",
    "stark-market-ops",
]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk_[A-Za-z0-9_-]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*=\s*['\"][^'\"]{12,}['\"]"),
]


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> int:
    if root.is_file():
        root = root.parent

    missing = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing:
        return fail(f"missing required files: {', '.join(missing)}")

    skill = read(root / "SKILL.md")
    if "name: stark-finance-trading" not in skill:
        return fail("SKILL.md name must be stark-finance-trading")
    if "Load when" not in skill or "Do not load" not in skill:
        return fail("description must include Load when and Do not load")
    if "read-only evidence -> simulation/backtest -> paper/demo -> explicit live confirmation" not in skill.lower():
        return fail("SKILL.md must encode the execution escalation ladder")
    if len(skill) > 14000:
        return fail("SKILL.md is too large; keep it as a router")

    router = read(root / "references/tool-router.md")
    missing_terms = [term for term in REQUIRED_TOOL_TERMS if term not in router]
    if missing_terms:
        return fail(f"tool-router missing terms: {', '.join(missing_terms)}")
    if "Do not create separate user-facing skills for every vendor" not in router:
        return fail("tool-router must preserve one-skill merge logic")
    if "references/local-skill-router.md" not in router:
        return fail("tool-router must route local finance skills through local-skill-router.md")

    local_router = read(root / "references/local-skill-router.md")
    missing_local_terms = [term for term in REQUIRED_LOCAL_SKILL_TERMS if term not in local_router]
    if missing_local_terms:
        return fail(f"local-skill-router missing terms: {', '.join(missing_local_terms)}")
    if "User-facing entry: stark-finance-trading" not in local_router:
        return fail("local-skill-router must keep stark-finance-trading as the user-facing entry")

    local_inventory_script = read(root / "scripts/discover_local_skill_inventory.py")
    for phrase in ["DEFAULT_RECOMMENDED_SKILLS", "Local SKILL.md inventory", "stark-finance-trading"]:
        if phrase not in local_inventory_script:
            return fail(f"discover_local_skill_inventory missing phrase: {phrase}")

    public_tool_catalog = json.loads(read(root / "references/public-tool-catalog.json"))
    public_tools = public_tool_catalog.get("catalog", [])
    public_tool_ids = {item.get("id") for item in public_tools}
    for required_id in ["dune-mcp", "alchemy-mcp", "etherscan-mcp", "alpaca-mcp", "openbb", "ibkr-tws-api", "hummingbot", "freqtrade"]:
        if required_id not in public_tool_ids:
            return fail(f"public-tool-catalog missing required id: {required_id}")
    if len(public_tools) < 30:
        return fail("public-tool-catalog must include at least 30 tools")
    if sum(1 for item in public_tools if "official" in str(item.get("source_status", ""))) < 30:
        return fail("public-tool-catalog must prioritize official source-backed tools")
    if sum(1 for item in public_tools if item.get("default_action_tier") == 4) < 5:
        return fail("public-tool-catalog must identify execution/high-risk surfaces")
    public_tool_script = read(root / "scripts/validate_public_tool_catalog.py")
    for phrase in ["REQUIRED_TOOL_IDS", "REQUIRED_ROUTE_TAGS", "public tool catalog"]:
        if phrase not in public_tool_script:
            return fail(f"validate_public_tool_catalog missing phrase: {phrase}")

    safety = read(root / "references/safety-policy.md")
    for phrase in ["Risk Tiers", "Tier 4", "Live Confirmation Checklist", "Never execute"]:
        if phrase not in safety:
            return fail(f"safety-policy missing phrase: {phrase}")

    workflows = read(root / "references/workflows.md")
    for phrase in ["Market Snapshot", "Token Due Diligence", "Strategy Backtest", "Execution Prep", "Local Skill Delegation"]:
        if phrase not in workflows:
            return fail(f"workflows missing phrase: {phrase}")

    evals = json.loads(read(root / "evals/routing-evals.json"))
    cases = evals.get("cases", [])
    if len(cases) < 8:
        return fail("routing evals must include at least 8 cases")
    if not any(case.get("should_load") is False for case in cases):
        return fail("routing evals need at least one negative case")
    if not any(case.get("risk_tier") == 4 for case in cases):
        return fail("routing evals need a live execution gated case")

    adversarial = json.loads(read(root / "evals/adversarial-evals.json"))
    adversarial_cases = adversarial.get("cases", [])
    if len(adversarial_cases) < 10:
        return fail("adversarial evals must include at least 10 cases")
    if not any(case.get("category") == "prompt_injection" for case in adversarial_cases):
        return fail("adversarial evals need a prompt_injection case")
    if not any(case.get("category") == "live_execution" for case in adversarial_cases):
        return fail("adversarial evals need a live_execution case")

    live_behavior = json.loads(read(root / "evals/live-behavior-evals.json"))
    live_cases = live_behavior.get("cases", [])
    if len(live_cases) < 6:
        return fail("live behavior evals must include at least 6 cases")
    if not any(case.get("category") == "execution_safety" for case in live_cases):
        return fail("live behavior evals need an execution_safety case")

    tool_routing = json.loads(read(root / "evals/tool-routing-cases.json"))
    tool_routing_cases = tool_routing.get("cases", [])
    if len(tool_routing_cases) < 10:
        return fail("tool routing cases must include at least 10 cases")
    if not any(case.get("should_load") is False for case in tool_routing_cases):
        return fail("tool routing cases need at least one negative case")
    if not any("binance-skills-hub" in case.get("expected_tool_ids", []) and case.get("min_risk_tier") == 4 for case in tool_routing_cases):
        return fail("tool routing cases need a Binance live execution gated case")
    plan_tool_route_script = read(root / "scripts/plan_tool_route.py")
    for phrase in ["ROUTE_RULES", "NEGATIVE_RULES", "plan_route", "runtime_report", "tool-routing-cases.json"]:
        if phrase not in plan_tool_route_script:
            return fail(f"plan_tool_route missing phrase: {phrase}")
    runtime_script = read(root / "scripts/runtime_capability_scan.py")
    for phrase in ["RUNTIME_HINTS", "configured_mcp", "enabled_plugin", "Local runtime capability scan"]:
        if phrase not in runtime_script:
            return fail(f"runtime_capability_scan missing phrase: {phrase}")
    codex_eval_script = read(root / "scripts/codex_eval.py")
    for phrase in ["runner_command", "runner_kind", "fixture_run", "approval_required", "runner_required"]:
        if phrase not in codex_eval_script:
            return fail(f"codex_eval missing live runner harness phrase: {phrase}")
    external_proof_script = read(root / "scripts/audit_external_proofs.py")
    for phrase in ["external_proof_status", "remote_github_actions_run", "approved_live_model_eval", "HARNESS_ONLY_NOT_MODEL_PROOF"]:
        if phrase not in external_proof_script:
            return fail(f"audit_external_proofs missing phrase: {phrase}")
    goal_completion_script = read(root / "scripts/audit_goal_completion.py")
    for phrase in ["goal_completion_status", "NOT_COMPLETE_REQUIREMENTS_PENDING", "stark_named_single_front_door", "remote_github_actions_proven"]:
        if phrase not in goal_completion_script:
            return fail(f"audit_goal_completion missing phrase: {phrase}")

    comparison = json.loads(read(root / "benchmarks/public-comparison-2026-06-28.json"))
    candidates = comparison.get("candidates", [])
    if comparison.get("claim_status") != "benchmark_defined_no_superiority_claim":
        return fail("public comparison must preserve no-superiority-claim status")
    if len(candidates) < 20:
        return fail("public comparison needs at least 20 candidates")
    benchmark_cases = json.loads(read(root / "benchmarks/public-benchmark-cases.json"))
    dimensions = benchmark_cases.get("dimensions", [])
    if len(dimensions) < 7:
        return fail("public benchmark needs at least 7 dimensions")
    if sum(int(item.get("weight", 0)) for item in dimensions) != 100:
        return fail("public benchmark dimension weights must sum to 100")
    competitive_cases = json.loads(read(root / "benchmarks/competitive-task-cases.json")).get("cases", [])
    if len(competitive_cases) < 8:
        return fail("competitive task benchmark needs at least 8 cases")

    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ""}:
            text = read(path)
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    return fail(f"possible secret pattern in {path.relative_to(root)}")

    print(json.dumps({
        "ok": True,
        "skill": "stark-finance-trading",
        "required_files": len(REQUIRED_FILES),
        "routing_cases": len(cases),
        "adversarial_cases": len(adversarial_cases),
        "live_behavior_cases": len(live_cases),
        "public_comparison_candidates": len(candidates),
        "public_benchmark_dimensions": len(dimensions),
        "competitive_task_cases": len(competitive_cases),
        "router_terms": len(REQUIRED_TOOL_TERMS),
        "local_skill_terms": len(REQUIRED_LOCAL_SKILL_TERMS),
        "public_tool_catalog_tools": len(public_tools),
        "tool_routing_cases": len(tool_routing_cases),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    raise SystemExit(validate(target))
