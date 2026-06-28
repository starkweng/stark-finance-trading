#!/usr/bin/env python3
"""Validate and summarize the public tool catalog for stark-finance-trading."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_TOOL_IDS = {
    "dune-mcp",
    "alchemy-mcp",
    "etherscan-mcp",
    "binance-skills-hub",
    "alpaca-mcp",
    "openbb",
    "quantconnect-mcp",
    "lean",
    "alpha-vantage-mcp",
    "fmp-mcp",
    "factset-mcp",
    "twelve-data-mcp",
    "unusual-whales-mcp",
    "massive-polygon-mcp",
    "tradier-mcp",
    "ibkr-tws-api",
    "ctrader-ai-agent-connect",
    "coinbase-cdp-agentkit",
    "quicknode-mcp",
    "coingecko-mcp",
    "coinmarketcap-mcp",
    "token-terminal-mcp",
    "defillama-api",
    "helius-mcp",
    "jupiter-apis",
    "dexscreener-api",
    "stripe-agent-toolkit",
    "plaid-api",
    "databento-api",
    "hummingbot",
    "freqtrade",
    "nautilus-trader",
    "ccxt",
}

REQUIRED_ROUTE_TAGS = {
    "onchain_sql",
    "evm",
    "solana",
    "verified_contracts",
    "cex",
    "us_equities",
    "options",
    "fundamentals",
    "market_data",
    "broker",
    "backtest",
    "market_making",
    "crypto_bot",
    "protocol_fundamentals",
    "defi",
    "payments",
    "bank_data",
    "web3_infrastructure",
}

REQUIRED_FIELDS = [
    "id",
    "name",
    "provider",
    "source_url",
    "source_status",
    "priority",
    "default_action_tier",
    "route_tags",
    "best_for",
    "auth_or_setup",
    "installed_status",
    "merge_policy",
    "safety_notes",
]

OFFICIAL_STATUS_MARKERS = ("official", "primary")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(json.dumps({"status": "FAIL", "error": message}, ensure_ascii=False, indent=2))
    return 1


def is_official_or_primary(status: str) -> bool:
    lowered = status.lower()
    return any(marker in lowered for marker in OFFICIAL_STATUS_MARKERS)


def validate_catalog(root: Path) -> dict:
    catalog_path = root / "references/public-tool-catalog.json"
    source_ledger_path = root / "references/source-ledger.md"
    tool_router_path = root / "references/tool-router.md"
    catalog_doc = read_json(catalog_path)
    items = catalog_doc.get("catalog") or []
    source_ledger = source_ledger_path.read_text(encoding="utf-8", errors="replace")
    tool_router = tool_router_path.read_text(encoding="utf-8", errors="replace")

    errors: list[str] = []
    ids = [str(item.get("id", "")) for item in items]
    id_counts = Counter(ids)
    duplicate_ids = sorted(item_id for item_id, count in id_counts.items() if count > 1)
    if duplicate_ids:
        errors.append(f"duplicate ids: {', '.join(duplicate_ids)}")

    missing_ids = sorted(REQUIRED_TOOL_IDS - set(ids))
    if missing_ids:
        errors.append(f"missing required tool ids: {', '.join(missing_ids)}")

    if len(items) < 30:
        errors.append("catalog must include at least 30 public tools")

    route_tag_counts: Counter[str] = Counter()
    priority_counts: Counter[str] = Counter()
    source_status_counts: Counter[str] = Counter()
    tier_counts: Counter[str] = Counter()
    installed_status_counts: Counter[str] = Counter()
    high_risk_items: list[str] = []
    official_count = 0
    source_urls = set()

    for item in items:
        item_id = str(item.get("id", "<missing>"))
        missing_fields = [field for field in REQUIRED_FIELDS if item.get(field) in (None, "", [])]
        if missing_fields:
            errors.append(f"{item_id} missing fields: {', '.join(missing_fields)}")
            continue
        source_url = str(item["source_url"])
        if not source_url.startswith("https://"):
            errors.append(f"{item_id} source_url must be https")
        if source_url in source_urls:
            errors.append(f"{item_id} duplicate source_url: {source_url}")
        source_urls.add(source_url)
        if source_url not in source_ledger:
            errors.append(f"{item_id} source_url missing from source-ledger.md")
        if item["name"] not in tool_router and item["provider"] not in tool_router:
            errors.append(f"{item_id} not represented in tool-router.md by name or provider")
        tier = item["default_action_tier"]
        if not isinstance(tier, int) or tier not in {1, 2, 3, 4}:
            errors.append(f"{item_id} default_action_tier must be integer 1-4")
        if tier == 4:
            high_risk_items.append(item_id)
            safety_text = f"{item.get('merge_policy', '')} {item.get('safety_notes', '')}".lower()
            if not any(term in safety_text for term in ["tier 4", "explicit", "confirmation", "paper", "demo"]):
                errors.append(f"{item_id} tier 4 item needs explicit safety boundary text")
        status = str(item["source_status"])
        if is_official_or_primary(status):
            official_count += 1
        else:
            errors.append(f"{item_id} must be official or primary source-backed")
        route_tags = [str(tag) for tag in item.get("route_tags", [])]
        route_tag_counts.update(route_tags)
        priority_counts[str(item["priority"])] += 1
        source_status_counts[status] += 1
        tier_counts[str(tier)] += 1
        installed_status_counts[str(item["installed_status"])] += 1

    missing_tags = sorted(REQUIRED_ROUTE_TAGS - set(route_tag_counts))
    if missing_tags:
        errors.append(f"missing required route tags: {', '.join(missing_tags)}")
    if official_count < 30:
        errors.append("catalog must include at least 30 official or primary source-backed tools")
    if len(high_risk_items) < 5:
        errors.append("catalog must identify at least 5 execution/high-risk surfaces")
    if priority_counts.get("core", 0) < 10:
        errors.append("catalog must include at least 10 core priority tools")
    if "Do not create separate user-facing skills for every vendor" not in tool_router:
        errors.append("tool-router must preserve merge policy")

    grouped: dict[str, list[str]] = defaultdict(list)
    for item in items:
        grouped[str(item.get("priority", "unknown"))].append(str(item.get("id", "")))

    return {
        "schema_version": "1.0",
        "status": "PASS" if not errors else "FAIL",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": "stark-finance-trading",
        "catalog_path": str(catalog_path.relative_to(root)),
        "tool_count": len(items),
        "required_tool_count": len(REQUIRED_TOOL_IDS),
        "missing_required_tool_ids": missing_ids,
        "official_or_primary_count": official_count,
        "route_tag_count": len(route_tag_counts),
        "missing_required_route_tags": missing_tags,
        "high_risk_surface_count": len(high_risk_items),
        "high_risk_surfaces": sorted(high_risk_items),
        "priority_counts": dict(sorted(priority_counts.items())),
        "source_status_counts": dict(sorted(source_status_counts.items())),
        "default_action_tier_counts": dict(sorted(tier_counts.items())),
        "installed_status_counts": dict(sorted(installed_status_counts.items())),
        "grouped_by_priority": {key: sorted(value) for key, value in sorted(grouped.items())},
        "errors": errors,
        "evidence_boundary": catalog_doc.get("evidence_boundary", ""),
    }


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# stark-finance-trading Public Tool Catalog",
        "",
        f"- Status: {report['status']}",
        f"- Tools: {report['tool_count']}",
        f"- Required tools covered: {report['required_tool_count'] - len(report['missing_required_tool_ids'])}/{report['required_tool_count']}",
        f"- Official or primary source-backed: {report['official_or_primary_count']}",
        f"- Route tags: {report['route_tag_count']}",
        f"- High-risk execution/admin/payment surfaces: {report['high_risk_surface_count']}",
        "",
        "## Priority Mix",
        "",
        "| Priority | Count |",
        "|---|---:|",
    ]
    for key, value in report["priority_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "## Default Action Tiers",
        "",
        "| Tier | Count |",
        "|---|---:|",
    ])
    for key, value in report["default_action_tier_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "## High-Risk Surfaces",
        "",
    ])
    for item_id in report["high_risk_surfaces"]:
        lines.append(f"- `{item_id}`")
    if report["errors"]:
        lines.extend(["", "## Errors", ""])
        for error in report["errors"]:
            lines.append(f"- {error}")
    lines.extend([
        "",
        "## Evidence Boundary",
        "",
        report["evidence_boundary"],
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out")
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = validate_catalog(root)
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
        print(f"public tool catalog: {report['status']} ({report['tool_count']} tools)")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
