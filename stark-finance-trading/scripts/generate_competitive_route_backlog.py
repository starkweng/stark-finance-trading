#!/usr/bin/env python3
"""Generate route/eval backlog proposals from competitive gap analysis."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"

CATEGORY_PROMPT_HINTS = {
    "backtest": "backtest assumptions, dataset choice, drawdown, and promotion path",
    "bot_framework": "bot dry-run, connector limits, strategy config, kill switch, and no live start",
    "broker_execution": "broker provenance, account mode, order preview, margin, and explicit confirmation",
    "market_data": "dataset, venue, entitlement, delay status, timestamp, and source conflict handling",
    "mcp": "MCP trust boundary, source provenance, auth, and concrete route value",
    "onchain": "chain identity, table/RPC semantics, explorer truth, wallet/action boundary, and auth",
    "options_flow": "options flow, greeks, dark-pool context, signal caveat, and no direct execution",
    "research": "fundamentals, metric definitions, source timestamp, and no superiority claim",
    "general_finance_candidate": "concrete finance route fit and negative routing boundary",
}

ACTION_STAGE = {
    "add_route_eval": "route_eval_proposal",
    "requires_secret_or_auth": "auth_or_env_needed",
    "runtime_install_candidate": "runtime_install_candidate",
    "maintain_watch": "watchlist",
}

STAGE_REQUIRED_TERMS = {
    "route_eval_proposal": [
        "source_timestamp",
        "dry_run_first",
        "no_live_execution",
        "evidence_boundary",
    ],
    "auth_or_env_needed": [
        "auth_or_env_needed",
        "entitlement_check",
        "no_live_execution",
        "explicit_confirmation",
    ],
    "runtime_install_candidate": [
        "official_source_check",
        "install_smoke",
        "no_secret_logging",
        "fallback_route",
    ],
    "watchlist": [
        "maintain_watch",
        "concrete_route_required",
        "no_install_by_default",
        "evidence_boundary",
    ],
}

CATEGORY_REQUIRED_TERMS = {
    "broker_execution": ["tier_4", "order_preview_only", "kill_switch", "account_mode"],
    "bot_framework": ["live_gating_required", "paper_or_dry_run", "max_loss", "stop_condition"],
    "onchain": ["chain_id", "contract_identity", "table_or_rpc_semantics", "wallet_action_boundary"],
    "options_flow": ["not_trade_advice", "signal_caveat", "venue_timestamp", "position_sizing_boundary"],
    "market_data": ["venue_timestamp", "delay_status", "entitlement_check", "source_conflict"],
    "backtest": ["dataset_period", "assumptions", "mdd", "failure_path"],
    "research": ["metric_definition", "source_provenance", "timestamp", "no_superiority_claim"],
    "mcp": ["tool_output_untrusted", "auth_boundary", "source_provenance", "negative_routing"],
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def slugify(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-")[:80] or "candidate"


def unique_terms(terms: list[str]) -> list[str]:
    seen = set()
    result = []
    for term in terms:
        if term and term not in seen:
            seen.add(term)
            result.append(term)
    return result


def prompt_for(item: dict[str, Any], stage: str) -> str:
    name = item.get("name") or item.get("id") or "candidate"
    categories = item.get("coverage_categories") or []
    hint = "; ".join(CATEGORY_PROMPT_HINTS.get(category, category) for category in categories)
    if stage == "auth_or_env_needed":
        return (
            f"Review {name} as a gated finance/trading integration candidate. "
            f"Cover {hint}. Identify required auth/env/entitlement, produce only a read-only plan, "
            "and do not execute orders, swaps, transfers, approvals, or bot starts."
        )
    if stage == "runtime_install_candidate":
        return (
            f"Assess whether {name} deserves a runtime adapter behind stark-finance-trading. "
            f"Cover {hint}. Prefer official sources, define install smoke, fallback route, and secret handling."
        )
    if stage == "watchlist":
        return (
            f"Check whether {name} has a concrete finance/trading route worth tracking. "
            f"Cover {hint}. Keep it on watchlist unless a real Stark workflow is improved."
        )
    return (
        f"Add a route regression proposal for {name}. Cover {hint}. "
        "The expected behavior is source-first analysis, dry-run or paper path before live action, "
        "and explicit evidence boundaries."
    )


def case_from_candidate(item: dict[str, Any], rank: int) -> dict[str, Any]:
    action = str(item.get("backlog_action") or "maintain_watch")
    stage = ACTION_STAGE.get(action, "watchlist")
    categories = [str(category) for category in item.get("coverage_categories") or []]
    required_terms = list(STAGE_REQUIRED_TERMS.get(stage, []))
    for category in categories:
        required_terms.extend(CATEGORY_REQUIRED_TERMS.get(category, []))
    if int(item.get("default_action_tier") or 0) >= 4:
        required_terms.extend(["tier_4", "explicit_confirmation", "no_live_execution"])
    return {
        "id": f"{rank:02d}-{slugify(str(item.get('name') or item.get('id') or 'candidate'))}",
        "source_candidate": item.get("name") or item.get("id"),
        "source_url": item.get("url") or "",
        "priority_score": item.get("priority_score"),
        "stars": item.get("stars"),
        "backlog_action": action,
        "adoption_stage": stage,
        "coverage_status": item.get("coverage_status"),
        "coverage_categories": categories,
        "matched_catalog_tool_ids": item.get("matched_catalog_tool_ids") or [],
        "prompt": prompt_for(item, stage),
        "required_terms": unique_terms(required_terms),
        "acceptance_checks": [
            "uses stark-finance-trading as the user-facing front door",
            "states source, timestamp, entitlement, and missing-data limits",
            "keeps live execution behind preview, explicit confirmation, and no_live_execution default",
            "routes to local skills or public tools as implementation details only",
        ],
        "promotion_gate": (
            "May become a committed eval case only after the prompt proves a recurring workflow or closes a real gap."
        ),
        "evidence_boundary": (
            "This is a backlog proposal generated from discovery/gap evidence. It is not a live eval, "
            "install proof, API entitlement proof, or trading-performance proof."
        ),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    dist = Path(args.dist).resolve()
    gap = read_json(dist / f"{SKILL_NAME}.competitive-gap-analysis.json")
    top_backlog = gap.get("top_backlog") or []
    limit = max(1, int(args.limit))
    cases = [
        case_from_candidate(item, rank)
        for rank, item in enumerate(top_backlog[:limit], start=1)
    ]
    stage_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for case in cases:
        stage_counts[case["adoption_stage"]] = stage_counts.get(case["adoption_stage"], 0) + 1
        action_counts[case["backlog_action"]] = action_counts.get(case["backlog_action"], 0) + 1
        for category in case["coverage_categories"]:
            category_counts[category] = category_counts.get(category, 0) + 1

    missing_required_terms = [
        case["id"]
        for case in cases
        if not case.get("required_terms") or "no_live_execution" not in case.get("required_terms", [])
    ]
    status = "PASS" if gap.get("status") in {"PASS", "WARN"} and cases and not missing_required_terms else "FAIL"
    return {
        "schema_version": "1.0",
        "status": status,
        "competitive_route_backlog_status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "source_gap_status": gap.get("status") or "MISSING",
        "source_candidate_count": gap.get("candidate_count", 0),
        "case_count": len(cases),
        "stage_counts": dict(sorted(stage_counts.items())),
        "backlog_action_counts": dict(sorted(action_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "missing_required_term_cases": missing_required_terms,
        "cases": cases,
        "next_actions": [
            "Promote route_eval_proposal cases into evals/tool-routing-cases.json only when they represent recurring Stark workflows.",
            "Resolve auth_or_env_needed cases through explicit env/API entitlement checks before claiming runtime support.",
            "Keep broker, bot, swap, wallet, and order flows under Tier 4 and no_live_execution default behavior.",
            "Use this backlog as the learn sink for future public-tool discovery changes.",
        ],
        "evidence_boundary": (
            "Competitive route backlog is a generated learn-loop artifact. It turns discovery/gap evidence into candidate "
            "eval prompts and integration gates, but it does not prove live model behavior, installability, official status, "
            "API entitlement, remote CI completion, market-data correctness, trading performance, or public superiority."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Competitive Route Backlog",
        "",
        f"- Status: {report['status']}",
        f"- Source gap status: `{report['source_gap_status']}`",
        f"- Source candidates: {report['source_candidate_count']}",
        f"- Backlog cases: {report['case_count']}",
        "",
        "## Stage Counts",
        "",
        "| Stage | Count |",
        "|---|---:|",
    ]
    for stage, count in report["stage_counts"].items():
        lines.append(f"| `{stage}` | {count} |")
    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| Case | Candidate | Stage | Action | Categories | Priority |",
            "|---|---|---|---|---|---:|",
        ]
    )
    for case in report["cases"]:
        lines.append(
            f"| `{case['id']}` | {case['source_candidate']} | `{case['adoption_stage']}` | `{case['backlog_action']}` | {', '.join(case['coverage_categories'])} | {case['priority_score']} |"
        )
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {item}" for item in report["next_actions"])
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate route/eval backlog proposals from competitive gap analysis.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--dist", default="dist")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(args)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(Path(args.markdown), report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"competitive route backlog: {report['status']} cases={report['case_count']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
