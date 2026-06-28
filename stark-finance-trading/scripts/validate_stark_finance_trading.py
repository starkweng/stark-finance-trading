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
    "references/safety-policy.md",
    "references/workflows.md",
    "references/source-ledger.md",
    "references/gotchas.md",
    "evals/routing-evals.json",
    "evals/adversarial-evals.json",
    "evals/live-behavior-evals.json",
    "benchmarks/public-comparison-2026-06-28.json",
    "benchmarks/PUBLIC_COMPARISON_2026-06-28.md",
    "benchmarks/public-benchmark-cases.json",
    "benchmarks/competitive-task-cases.json",
    "scripts/codex_eval.py",
    "scripts/audit_public_sources.py",
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

    safety = read(root / "references/safety-policy.md")
    for phrase in ["Risk Tiers", "Tier 4", "Live Confirmation Checklist", "Never execute"]:
        if phrase not in safety:
            return fail(f"safety-policy missing phrase: {phrase}")

    workflows = read(root / "references/workflows.md")
    for phrase in ["Market Snapshot", "Token Due Diligence", "Strategy Backtest", "Execution Prep"]:
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
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    raise SystemExit(validate(target))
