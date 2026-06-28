#!/usr/bin/env python3
"""Discover public GitHub finance/trading/Web3 tool candidates."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_QUERIES = [
    {"id": "finance_mcp", "query": "finance mcp server in:name,description,readme"},
    {"id": "trading_mcp", "query": "trading mcp server in:name,description,readme"},
    {"id": "market_data_mcp", "query": "market data mcp server in:name,description,readme"},
    {"id": "broker_mcp", "query": "broker trading mcp in:name,description,readme"},
    {"id": "crypto_mcp", "query": "crypto mcp server in:name,description,readme"},
    {"id": "web3_mcp", "query": "web3 onchain mcp server in:name,description,readme"},
    {"id": "backtest_framework", "query": "backtesting trading framework stars:>500"},
    {"id": "trading_bot_framework", "query": "trading bot cryptocurrency stars:>500"},
    {"id": "quant_framework", "query": "quant trading framework stars:>500"},
    {"id": "openbb_finance", "query": "OpenBB finance in:name,description,readme"},
    {"id": "alpaca_trading", "query": "alpaca trading mcp OR alpaca trading api in:name,description,readme"},
    {"id": "dune_alchemy_etherscan", "query": "dune alchemy etherscan mcp in:name,description,readme"},
]

ROUTE_KEYWORDS = {
    "mcp": ["mcp", "model context protocol"],
    "market_data": ["market data", "quote", "ohlcv", "bars", "polygon", "alpaca", "fmp", "alpha vantage"],
    "broker_execution": ["broker", "order", "paper trading", "live trading", "ibkr", "alpaca", "tradier", "robinhood"],
    "options_flow": ["options", "greeks", "flow", "dark pool"],
    "onchain": ["web3", "onchain", "ethereum", "solana", "dune", "alchemy", "etherscan", "defi"],
    "backtest": ["backtest", "backtesting", "lean", "quantconnect", "strategy"],
    "bot_framework": ["bot", "hummingbot", "freqtrade", "ccxt"],
    "research": ["research", "openbb", "fundamental", "financial statement", "macro"],
}
RELEVANCE_TERMS = [
    "finance",
    "financial",
    "trading",
    "trade",
    "market data",
    "stock",
    "options",
    "broker",
    "crypto",
    "web3",
    "onchain",
    "defi",
    "backtest",
    "quant",
    "mcp",
    "alpaca",
    "openbb",
    "dune",
    "alchemy",
    "etherscan",
    "hummingbot",
    "freqtrade",
    "ccxt",
]
STRONG_RELEVANCE_TERMS = [term for term in RELEVANCE_TERMS if term not in {"mcp"}]
STRONG_ROUTE_TAGS = {
    "market_data",
    "broker_execution",
    "options_flow",
    "onchain",
    "backtest",
    "bot_framework",
}
GENERIC_REPO_PATTERNS = [
    re.compile(r"^awesome-(python|go|rust|selfhosted)$", re.I),
    re.compile(r"^public-apis$", re.I),
    re.compile(r"^free-for-dev$", re.I),
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def run_gh_search(query: str, per_query: int, timeout: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cmd = [
        "gh",
        "api",
        "-X",
        "GET",
        "search/repositories",
        "-f",
        f"q={query}",
        "-f",
        "sort=stars",
        "-f",
        "order=desc",
        "-F",
        f"per_page={per_query}",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    meta = {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stderr_tail": proc.stderr[-1000:],
        "stdout_tail": proc.stdout[-1000:] if proc.returncode != 0 else "",
    }
    if proc.returncode != 0:
        return [], meta
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        meta["returncode"] = 1
        meta["stderr_tail"] = f"invalid JSON: {exc}"
        return [], meta
    return list(payload.get("items") or []), meta


def route_tags_for(text: str) -> list[str]:
    lowered = text.lower()
    tags = []
    for tag, terms in ROUTE_KEYWORDS.items():
        if any(term in lowered for term in terms):
            tags.append(tag)
    return tags or ["finance_or_trading_candidate"]


def action_tier_for(tags: list[str], text: str) -> int:
    lowered = text.lower()
    if "broker_execution" in tags or any(term in lowered for term in ["live trading", "place order", "wallet", "swap"]):
        return 4
    if "bot_framework" in tags or "backtest" in tags:
        return 3
    if "mcp" in tags:
        return 2
    return 1


def normalize_repo(item: dict[str, Any], query_id: str) -> dict[str, Any]:
    description = item.get("description") or ""
    topics = item.get("topics") or []
    text = " ".join(
        str(value)
        for value in [
            item.get("name") or "",
            item.get("full_name") or "",
            description,
            " ".join(topics),
        ]
    )
    tags = route_tags_for(text)
    return {
        "id": item.get("full_name"),
        "name": item.get("name"),
        "full_name": item.get("full_name"),
        "html_url": item.get("html_url"),
        "description": description,
        "query_ids": [query_id],
        "route_tags": tags,
        "default_action_tier": action_tier_for(tags, text),
        "language": item.get("language") or "",
        "topics": topics,
        "stars": int(item.get("stargazers_count") or 0),
        "forks": int(item.get("forks_count") or 0),
        "open_issues": int(item.get("open_issues_count") or 0),
        "pushed_at": item.get("pushed_at") or "",
        "license": ((item.get("license") or {}).get("spdx_id") or ""),
        "source_status": "github_live_search",
        "stark_relevance": "candidate_for_public_comparison_or_router_source",
    }


def is_relevant_repo(item: dict[str, Any]) -> bool:
    name = str(item.get("name") or "")
    full_name = str(item.get("full_name") or "")
    if any(pattern.search(name) for pattern in GENERIC_REPO_PATTERNS):
        return False
    text = " ".join(
        [
            full_name,
            name,
            str(item.get("description") or ""),
            " ".join(item.get("topics") or []),
        ]
    ).lower()
    tags = set(item.get("route_tags") or [])
    if tags & STRONG_ROUTE_TAGS:
        return True
    return any(term in text for term in STRONG_RELEVANCE_TERMS)


def fallback_from_curated(root: Path, limit: int) -> list[dict[str, Any]]:
    comparison = read_json(root / "benchmarks" / "public-comparison-2026-06-28.json")
    repos: list[dict[str, Any]] = []
    for item in (comparison.get("candidates") or [])[:limit]:
        source_url = str(item.get("source_url") or "")
        text = " ".join([str(item.get("name") or ""), str(item.get("category") or ""), source_url])
        repos.append(
            {
                "id": item.get("name"),
                "name": item.get("name"),
                "full_name": item.get("name"),
                "html_url": source_url,
                "description": item.get("route_role") or "",
                "query_ids": ["curated_fallback"],
                "route_tags": route_tags_for(text),
                "default_action_tier": int(item.get("default_risk_tier") or 0),
                "language": "",
                "topics": [],
                "stars": None,
                "forks": None,
                "open_issues": None,
                "pushed_at": "",
                "license": "",
                "source_status": "curated_fallback_not_live_github_search",
                "stark_relevance": item.get("what_stark_must_do_better") or "",
            }
        )
    return repos


def dedupe_repos(repos: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for item in repos:
        repo_id = str(item.get("id") or item.get("html_url") or item.get("name"))
        if repo_id in by_id:
            existing = by_id[repo_id]
            existing["query_ids"] = sorted(set(existing.get("query_ids", []) + item.get("query_ids", [])))
            existing["route_tags"] = sorted(set(existing.get("route_tags", []) + item.get("route_tags", [])))
            continue
        by_id[repo_id] = item
    relevant = [item for item in by_id.values() if is_relevant_repo(item)]
    return sorted(relevant, key=lambda item: int(item.get("stars") or 0), reverse=True)[:limit]


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# GitHub Finance/Trading Tool Discovery",
        "",
        f"- Status: {report['status']}",
        f"- Mode: `{report['mode']}`",
        f"- Query count: {report['query_count']}",
        f"- Candidate count: {report['candidate_count']}",
        f"- MCP candidates: {report['tag_counts'].get('mcp', 0)}",
        f"- Execution-tier candidates: {report['execution_tier_candidate_count']}",
        "",
        "## Top Candidates",
        "",
        "| Repo | Stars | Tags | Tier | URL |",
        "|---|---:|---|---:|---|",
    ]
    for item in report["candidates"][:30]:
        stars = item.get("stars")
        star_text = "" if stars is None else str(stars)
        lines.append(
            f"| {item.get('full_name') or item.get('name')} | {star_text} | {', '.join(item.get('route_tags') or [])} | {item.get('default_action_tier')} | {item.get('html_url')} |"
        )
    if report.get("failed_queries"):
        lines.extend(["", "## Failed Queries", ""])
        lines.extend(f"- `{item['id']}`: {item['stderr_tail']}" for item in report["failed_queries"])
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    queries = DEFAULT_QUERIES
    repos: list[dict[str, Any]] = []
    query_reports: list[dict[str, Any]] = []
    failed_queries: list[dict[str, Any]] = []
    live_attempted = args.live or args.auto_live
    live_ok = False
    if live_attempted and shutil.which("gh"):
        for query in queries:
            items, meta = run_gh_search(query["query"], args.per_query, args.timeout)
            meta["id"] = query["id"]
            meta["query"] = query["query"]
            meta["result_count"] = len(items)
            query_reports.append(meta)
            if meta["returncode"] != 0:
                failed_queries.append(meta)
                continue
            live_ok = True
            repos.extend(normalize_repo(item, query["id"]) for item in items)

    mode = "live_github_search" if live_ok else "curated_fallback"
    if not live_ok:
        if args.live and not args.allow_fallback:
            repos = []
        else:
            repos = fallback_from_curated(root, args.limit)
    candidates = dedupe_repos(repos, args.limit)
    tag_counts: dict[str, int] = {}
    for item in candidates:
        for tag in item.get("route_tags") or []:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    status = "PASS" if candidates and (live_ok or args.allow_fallback or not args.live) else "FAIL"
    if live_ok and failed_queries:
        status = "WARN"
    return {
        "schema_version": "1.0",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": "stark-finance-trading",
        "mode": mode,
        "query_count": len(queries),
        "candidate_count": len(candidates),
        "tag_counts": dict(sorted(tag_counts.items())),
        "mcp_candidate_count": tag_counts.get("mcp", 0),
        "execution_tier_candidate_count": sum(1 for item in candidates if int(item.get("default_action_tier") or 0) >= 3),
        "failed_query_count": len(failed_queries),
        "queries": query_reports,
        "failed_queries": failed_queries,
        "candidates": candidates,
        "evidence_boundary": (
            "GitHub discovery is a public repository search snapshot. It helps maintain the comparison set and "
            "router backlog, but it does not prove installability, official status, API entitlement, live model behavior, "
            "market-data correctness, trading performance, remote CI completion, or public superiority."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover public GitHub finance/trading/Web3 tool candidates.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--live", action="store_true", help="Use GitHub API through gh CLI.")
    parser.add_argument("--auto-live", action="store_true", help="Try live discovery when gh exists, otherwise fallback.")
    parser.add_argument("--allow-fallback", action="store_true")
    parser.add_argument("--per-query", type=int, default=8)
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--timeout", type=int, default=30)
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
        print(f"github discovery: {report['status']} {report['mode']} {report['candidate_count']} candidates")
    return 0 if report["status"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
