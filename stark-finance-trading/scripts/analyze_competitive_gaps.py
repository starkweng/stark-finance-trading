#!/usr/bin/env python3
"""Analyze public finance/trading tool discovery against Stark router coverage."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"

TAG_TO_CATEGORY = {
    "backtest": "backtest",
    "bot_framework": "bot_framework",
    "broker_execution": "broker_execution",
    "finance_or_trading_candidate": "general_finance_candidate",
    "market_data": "market_data",
    "mcp": "mcp",
    "onchain": "onchain",
    "options_flow": "options_flow",
    "research": "research",
}

CATEGORY_TOOL_IDS = {
    "backtest": [
        "quantconnect-mcp",
        "lean",
        "nautilus-trader",
        "freqtrade",
        "hummingbot",
        "ccxt",
    ],
    "bot_framework": [
        "hummingbot",
        "freqtrade",
        "nautilus-trader",
        "ccxt",
    ],
    "broker_execution": [
        "alpaca-mcp",
        "tradier-mcp",
        "ibkr-tws-api",
        "ctrader-ai-agent-connect",
        "coinbase-cdp-agentkit",
    ],
    "general_finance_candidate": [
        "openbb",
        "alpaca-mcp",
        "binance-skills-hub",
    ],
    "market_data": [
        "alpaca-mcp",
        "openbb",
        "alpha-vantage-mcp",
        "fmp-mcp",
        "factset-mcp",
        "twelve-data-mcp",
        "massive-polygon-mcp",
        "databento-api",
        "coingecko-mcp",
        "coinmarketcap-mcp",
    ],
    "mcp": [
        "dune-mcp",
        "alchemy-mcp",
        "etherscan-mcp",
        "alpaca-mcp",
        "quicknode-mcp",
        "coingecko-mcp",
        "coinmarketcap-mcp",
    ],
    "onchain": [
        "dune-mcp",
        "alchemy-mcp",
        "etherscan-mcp",
        "binance-skills-hub",
        "coinbase-cdp-agentkit",
        "quicknode-mcp",
        "coingecko-mcp",
        "coinmarketcap-mcp",
        "token-terminal-mcp",
        "defillama-api",
        "helius-mcp",
        "jupiter-apis",
        "dexscreener-api",
    ],
    "options_flow": [
        "unusual-whales-mcp",
        "alpaca-mcp",
        "tradier-mcp",
        "ibkr-tws-api",
        "massive-polygon-mcp",
    ],
    "research": [
        "openbb",
        "fmp-mcp",
        "factset-mcp",
        "token-terminal-mcp",
        "defillama-api",
    ],
}

CATEGORY_PROFILES = {
    "backtest": {
        "coverage_status": "COVERED_SOURCE_LEVEL",
        "stark_response": "Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution.",
        "default_backlog_action": "add_route_eval",
    },
    "bot_framework": {
        "coverage_status": "COVERED_WITH_LIVE_GATING_REQUIRED",
        "stark_response": "Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review.",
        "default_backlog_action": "add_route_eval",
    },
    "broker_execution": {
        "coverage_status": "PARTIAL_RUNTIME",
        "stark_response": "Keep broker/order surfaces in Tier 4 with account, venue, order, margin, and kill-switch preview before confirmation.",
        "default_backlog_action": "requires_secret_or_auth",
    },
    "general_finance_candidate": {
        "coverage_status": "WATCHLIST",
        "stark_response": "Keep on watchlist until it maps to a concrete data, research, broker, onchain, or strategy workflow.",
        "default_backlog_action": "maintain_watch",
    },
    "market_data": {
        "coverage_status": "COVERED_SOURCE_LEVEL",
        "stark_response": "Route by dataset, venue, entitlement, delay status, and timestamp before using market data in decisions.",
        "default_backlog_action": "runtime_install_candidate",
    },
    "mcp": {
        "coverage_status": "COVERED_GENERIC_MCP",
        "stark_response": "Use MCP as a substrate, but only promote concrete finance routes with source, auth, and safety metadata.",
        "default_backlog_action": "maintain_watch",
    },
    "onchain": {
        "coverage_status": "PARTIAL_RUNTIME",
        "stark_response": "Use Dune/Alchemy/Binance where configured; keep Etherscan and endpoint-specific surfaces gated by env/auth checks.",
        "default_backlog_action": "requires_secret_or_auth",
    },
    "options_flow": {
        "coverage_status": "PARTIAL_RUNTIME",
        "stark_response": "Treat flow/greeks/dark-pool data as signal evidence, not execution advice; live credentials and redistribution rules remain external.",
        "default_backlog_action": "requires_secret_or_auth",
    },
    "research": {
        "coverage_status": "COVERED_SOURCE_LEVEL",
        "stark_response": "Route to research/fundamentals tools with metric definitions, source provenance, and no public superiority claim.",
        "default_backlog_action": "maintain_watch",
    },
}

STATUS_PRIORITY = {
    "GAP": 70,
    "PARTIAL_RUNTIME": 55,
    "COVERED_WITH_LIVE_GATING_REQUIRED": 42,
    "COVERED_GENERIC_MCP": 24,
    "COVERED_SOURCE_LEVEL": 16,
    "WATCHLIST": 12,
}

ALIAS_TO_TOOL_ID = {
    "alchemy": "alchemy-mcp",
    "alpaca": "alpaca-mcp",
    "alpha vantage": "alpha-vantage-mcp",
    "binance": "binance-skills-hub",
    "ccxt": "ccxt",
    "coingecko": "coingecko-mcp",
    "coinmarketcap": "coinmarketcap-mcp",
    "dune": "dune-mcp",
    "etherscan": "etherscan-mcp",
    "freqtrade": "freqtrade",
    "hummingbot": "hummingbot",
    "ibkr": "ibkr-tws-api",
    "interactive brokers": "ibkr-tws-api",
    "lean": "lean",
    "massive": "massive-polygon-mcp",
    "nautilus": "nautilus-trader",
    "openbb": "openbb",
    "polygon": "massive-polygon-mcp",
    "quantconnect": "quantconnect-mcp",
    "quicknode": "quicknode-mcp",
    "tradier": "tradier-mcp",
    "twelve data": "twelve-data-mcp",
    "unusual whales": "unusual-whales-mcp",
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def artifact_path(dist: Path, suffix: str) -> Path:
    return dist / f"{SKILL_NAME}.{suffix}"


def runtime_lookup(runtime: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("id")): item for item in runtime.get("tools") or []}


def catalog_lookup(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("id")): item for item in catalog.get("catalog") or []}


def normalize_categories(tags: list[str]) -> tuple[list[str], list[str]]:
    categories: list[str] = []
    unclassified: list[str] = []
    for tag in tags:
        category = TAG_TO_CATEGORY.get(str(tag))
        if category:
            categories.append(category)
        else:
            unclassified.append(str(tag))
    return sorted(set(categories or ["general_finance_candidate"])), sorted(set(unclassified))


def merge_status(statuses: list[str]) -> str:
    if not statuses:
        return "GAP"
    for status in ["GAP", "PARTIAL_RUNTIME", "COVERED_WITH_LIVE_GATING_REQUIRED", "COVERED_GENERIC_MCP"]:
        if status in statuses:
            return status
    if "WATCHLIST" in statuses and len(set(statuses)) == 1:
        return "WATCHLIST"
    return "COVERED_SOURCE_LEVEL"


def tool_runtime_status(tool_id: str, runtime_by_id: dict[str, dict[str, Any]], catalog_by_id: dict[str, dict[str, Any]]) -> str:
    if tool_id in runtime_by_id:
        return str(runtime_by_id[tool_id].get("runtime_status") or "observed_unknown")
    if tool_id in catalog_by_id:
        return str(catalog_by_id[tool_id].get("installed_status") or "catalog_only")
    return "not_in_catalog"


def category_summary(
    category: str,
    runtime_by_id: dict[str, dict[str, Any]],
    catalog_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    profile = CATEGORY_PROFILES[category]
    tool_ids = [tool_id for tool_id in CATEGORY_TOOL_IDS.get(category, []) if tool_id in catalog_by_id]
    runtime_statuses = {tool_id: tool_runtime_status(tool_id, runtime_by_id, catalog_by_id) for tool_id in tool_ids}
    env_missing = [
        tool_id
        for tool_id in tool_ids
        if tool_id in runtime_by_id and runtime_by_id[tool_id].get("required_env_present")
        and not all(bool(value) for value in (runtime_by_id[tool_id].get("required_env_present") or {}).values())
    ]
    configured_count = sum(
        1
        for status in runtime_statuses.values()
        if status in {"configured_mcp", "enabled_plugin", "local_skill_backed", "deferred_tool_source"}
    )
    return {
        "category": category,
        "coverage_status": profile["coverage_status"],
        "default_backlog_action": profile["default_backlog_action"],
        "catalog_tool_ids": tool_ids,
        "runtime_statuses": runtime_statuses,
        "configured_or_deferred_count": configured_count,
        "env_missing_tool_ids": env_missing,
        "stark_response": profile["stark_response"],
    }


def match_catalog_tools(candidate: dict[str, Any], catalog_by_id: dict[str, dict[str, Any]]) -> list[str]:
    text = " ".join(
        str(candidate.get(key) or "")
        for key in ["id", "name", "full_name", "description", "html_url"]
    ).lower()
    matched = []
    for alias, tool_id in ALIAS_TO_TOOL_ID.items():
        if alias in text and tool_id in catalog_by_id:
            matched.append(tool_id)
    return sorted(set(matched))


def backlog_action_for(
    candidate: dict[str, Any],
    categories: list[str],
    coverage_status: str,
    matched_tool_ids: list[str],
) -> str:
    stars = int(candidate.get("stars") or 0)
    tier = int(candidate.get("default_action_tier") or 0)
    if coverage_status == "GAP":
        return "runtime_install_candidate"
    if coverage_status == "PARTIAL_RUNTIME":
        return "requires_secret_or_auth"
    if "bot_framework" in categories and tier >= 3:
        return "add_route_eval"
    if "backtest" in categories and stars >= 3000:
        return "add_route_eval"
    if not matched_tool_ids and ("market_data" in categories or "mcp" in categories) and stars >= 1000:
        return "runtime_install_candidate"
    if coverage_status == "COVERED_GENERIC_MCP" and not matched_tool_ids:
        return "maintain_watch"
    return "maintain_watch"


def priority_score(candidate: dict[str, Any], coverage_status: str, backlog_action: str) -> float:
    stars = int(candidate.get("stars") or 0)
    tier = int(candidate.get("default_action_tier") or 0)
    score = STATUS_PRIORITY.get(coverage_status, 20) + tier * 10 + math.log10(max(stars, 1)) * 7
    if backlog_action in {"requires_secret_or_auth", "runtime_install_candidate"}:
        score += 16
    if backlog_action == "add_route_eval":
        score += 10
    return round(score, 2)


def classify_candidate(
    candidate: dict[str, Any],
    category_summaries: dict[str, dict[str, Any]],
    runtime_by_id: dict[str, dict[str, Any]],
    catalog_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    tags = [str(tag) for tag in candidate.get("route_tags") or []]
    categories, unclassified = normalize_categories(tags)
    statuses = [category_summaries[category]["coverage_status"] for category in categories if category in category_summaries]
    coverage_status = merge_status(statuses)
    matched_tool_ids = match_catalog_tools(candidate, catalog_by_id)
    matched_runtime_statuses = {
        tool_id: tool_runtime_status(tool_id, runtime_by_id, catalog_by_id)
        for tool_id in matched_tool_ids
    }
    action = backlog_action_for(candidate, categories, coverage_status, matched_tool_ids)
    response_parts = [
        category_summaries[category]["stark_response"]
        for category in categories
        if category in category_summaries
    ]
    return {
        "id": candidate.get("id") or candidate.get("full_name") or candidate.get("name"),
        "name": candidate.get("full_name") or candidate.get("name"),
        "url": candidate.get("html_url") or "",
        "description": candidate.get("description") or "",
        "stars": candidate.get("stars"),
        "language": candidate.get("language") or "",
        "route_tags": tags,
        "coverage_categories": categories,
        "unclassified_tags": unclassified,
        "default_action_tier": candidate.get("default_action_tier"),
        "coverage_status": coverage_status,
        "stark_response": " ".join(dict.fromkeys(response_parts)),
        "backlog_action": action,
        "priority_score": priority_score(candidate, coverage_status, action),
        "matched_catalog_tool_ids": matched_tool_ids,
        "matched_runtime_statuses": matched_runtime_statuses,
    }


def category_rollup(candidates: list[dict[str, Any]], summaries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for category, summary in sorted(summaries.items()):
        related = [item for item in candidates if category in item["coverage_categories"]]
        rows.append(
            {
                **summary,
                "candidate_count": len(related),
                "total_stars": sum(int(item.get("stars") or 0) for item in related),
                "top_candidate": related[0]["name"] if related else "",
            }
        )
    return sorted(rows, key=lambda item: (-item["candidate_count"], -item["total_stars"], item["category"]))


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    dist = Path(args.dist).resolve()
    github = read_json(artifact_path(dist, "github-tool-discovery.json"))
    runtime = read_json(artifact_path(dist, "runtime-capabilities.json"))
    route_plan = read_json(artifact_path(dist, "tool-route-plan.json"))
    public_benchmark = read_json(artifact_path(dist, "public-benchmark.json"))
    catalog = read_json(root / "references" / "public-tool-catalog.json")

    runtime_by_id = runtime_lookup(runtime)
    catalog_by_id = catalog_lookup(catalog)
    categories = sorted(CATEGORY_PROFILES)
    summaries = {
        category: category_summary(category, runtime_by_id, catalog_by_id)
        for category in categories
    }
    candidates = [
        classify_candidate(item, summaries, runtime_by_id, catalog_by_id)
        for item in github.get("candidates") or []
    ]
    candidates = sorted(candidates, key=lambda item: (-item["priority_score"], -(int(item.get("stars") or 0)), item["name"] or ""))
    unclassified_tags = sorted({tag for item in candidates for tag in item.get("unclassified_tags") or []})
    top_backlog = [
        item
        for item in candidates
        if item["backlog_action"] in {"requires_secret_or_auth", "runtime_install_candidate", "add_route_eval"}
    ][:20]
    high_priority_backlog = [
        item for item in top_backlog if item["priority_score"] >= 78 or int(item.get("stars") or 0) >= 5000
    ]
    status_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    for item in candidates:
        status_counts[item["coverage_status"]] = status_counts.get(item["coverage_status"], 0) + 1
        action_counts[item["backlog_action"]] = action_counts.get(item["backlog_action"], 0) + 1

    input_statuses = {
        "github_tool_discovery": github.get("status") or "MISSING",
        "runtime_capabilities": runtime.get("status") or "MISSING",
        "tool_route_plan": route_plan.get("status") or "MISSING",
        "public_benchmark": public_benchmark.get("status") or "MISSING",
        "public_tool_catalog": "PASS" if catalog.get("catalog") else "MISSING",
    }
    input_ok = all(status in {"PASS", "WARN"} for status in input_statuses.values())
    competitive_gap_status = "WARN" if unclassified_tags else "PASS"
    if not input_ok or not candidates:
        competitive_gap_status = "FAIL"
    return {
        "schema_version": "1.0",
        "status": competitive_gap_status,
        "competitive_gap_status": competitive_gap_status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "input_statuses": input_statuses,
        "discovery_mode": github.get("mode") or "",
        "candidate_count": len(candidates),
        "covered_count": sum(
            count
            for status, count in status_counts.items()
            if status in {"COVERED_SOURCE_LEVEL", "COVERED_GENERIC_MCP", "COVERED_WITH_LIVE_GATING_REQUIRED"}
        ),
        "partial_count": status_counts.get("PARTIAL_RUNTIME", 0),
        "gap_count": status_counts.get("GAP", 0),
        "watchlist_count": status_counts.get("WATCHLIST", 0),
        "high_priority_backlog_count": len(high_priority_backlog),
        "coverage_status_counts": dict(sorted(status_counts.items())),
        "backlog_action_counts": dict(sorted(action_counts.items())),
        "unclassified_tags": unclassified_tags,
        "category_rollup": category_rollup(candidates, summaries),
        "top_backlog": top_backlog,
        "candidates": candidates,
        "next_actions": [
            "Set or confirm secrets only where needed, especially ETHERSCAN_API_KEY for explorer-backed live calls.",
            "Promote high-star backtest/bot frameworks into route evals before adding runtime adapters.",
            "Keep broker and bot paths under Tier 4 live_gating_required controls until account, margin, and kill-switch previews are reviewable.",
            "Use runtime_install_candidate only for gaps that add a real route, not for generic MCP lists.",
        ],
        "evidence_boundary": (
            "Competitive gap analysis combines GitHub discovery, local runtime metadata, route regression, public benchmark, "
            "and the curated public tool catalog. It is a planning and backlog artifact, not proof of installability, "
            "official status, API entitlement, live model behavior, market-data correctness, trading performance, "
            "remote CI completion, or public superiority."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Competitive Gap Analysis",
        "",
        f"- Status: {report['status']}",
        f"- Discovery mode: `{report['discovery_mode']}`",
        f"- Candidates: {report['candidate_count']}",
        f"- Covered: {report['covered_count']}",
        f"- Partial runtime: {report['partial_count']}",
        f"- Gaps: {report['gap_count']}",
        f"- High-priority backlog: {report['high_priority_backlog_count']}",
        "",
        "## Category Rollup",
        "",
        "| Category | Coverage | Candidates | Runtime/Deferred | Env Missing | Top Candidate |",
        "|---|---|---:|---:|---|---|",
    ]
    for item in report["category_rollup"]:
        lines.append(
            "| {category} | {coverage_status} | {candidate_count} | {configured_or_deferred_count} | {env_missing} | {top_candidate} |".format(
                category=item["category"],
                coverage_status=item["coverage_status"],
                candidate_count=item["candidate_count"],
                configured_or_deferred_count=item["configured_or_deferred_count"],
                env_missing=", ".join(item["env_missing_tool_ids"]) or "-",
                top_candidate=item["top_candidate"] or "-",
            )
        )
    lines.extend(
        [
            "",
            "## Top Backlog",
            "",
            "| Candidate | Stars | Tags | Coverage | Action | Priority | URL |",
            "|---|---:|---|---|---|---:|---|",
        ]
    )
    for item in report["top_backlog"][:25]:
        stars = "" if item.get("stars") is None else str(item.get("stars"))
        lines.append(
            f"| {item['name']} | {stars} | {', '.join(item['route_tags'])} | {item['coverage_status']} | {item['backlog_action']} | {item['priority_score']} | {item['url']} |"
        )
    lines.extend(
        [
            "",
            "## Candidate Coverage",
            "",
            "| Candidate | Stars | Categories | Coverage | Stark Response |",
            "|---|---:|---|---|---|",
        ]
    )
    for item in report["candidates"][:30]:
        stars = "" if item.get("stars") is None else str(item.get("stars"))
        response = item["stark_response"].replace("|", "/")
        lines.append(
            f"| {item['name']} | {stars} | {', '.join(item['coverage_categories'])} | {item['coverage_status']} | {response} |"
        )
    if report.get("unclassified_tags"):
        lines.extend(["", "## Unclassified Tags", ""])
        lines.extend(f"- `{tag}`" for tag in report["unclassified_tags"])
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze public finance/trading tool gaps and backlog.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--dist", default="dist")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
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
        print(f"competitive gap analysis: {report['status']} candidates={report['candidate_count']}")
    return 0 if report["status"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
