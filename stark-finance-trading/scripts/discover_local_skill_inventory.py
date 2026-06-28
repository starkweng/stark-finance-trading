#!/usr/bin/env python3
"""Discover local finance/trading-adjacent skills for routing evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"

DEFAULT_RECOMMENDED_SKILLS = [
    "stark-finance-trading",
    "dune",
    "alchemy",
    "binance",
    "binance-agentic-wallet",
    "crypto-market-rank",
    "query-token-info",
    "query-token-audit",
    "query-address-info",
    "trading-signal",
    "meme-rush",
    "gmgn-market",
    "gmgn-token",
    "gmgn-portfolio",
    "gmgn-track",
    "gmgn-swap",
    "earnings-preview",
    "earnings-analysis",
    "equity-research",
    "dcf-model",
    "comps-analysis",
    "bond-futures-basis",
    "bond-relative-value",
    "fixed-income-portfolio",
    "fx-carry-trade",
    "swap-curve-strategy",
    "option-vol-analysis",
    "portfolio-monitoring",
    "portfolio-rebalance",
    "deal-screening",
    "deal-sourcing",
    "deal-tracker",
    "dd-checklist",
    "ic-memo",
    "cim-builder",
    "audit-xls",
    "gl-recon",
    "break-trace",
    "roll-forward",
    "stark-liquidity-strategy",
    "stark-tokenomics-planner",
    "stark-market-ops",
    "stark-mkt-ops",
    "stark-capital-strategy",
    "stark-data-analytics",
]

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    (
        "core_router",
        ["stark-finance-trading"],
    ),
    (
        "web3_market_onchain",
        [
            "dune",
            "alchemy",
            "etherscan",
            "token",
            "crypto",
            "meme",
            "gmgn",
            "wallet",
            "smart money",
            "holder",
            "liquidity",
            "onchain",
        ],
    ),
    (
        "execution_capable",
        [
            "buy",
            "sell",
            "swap",
            "order draft",
            "order preview",
            "order placement",
            "futures",
            "derivatives",
            "agentic-wallet",
            "launch",
            "pump.fun",
            "binance",
        ],
    ),
    (
        "equity_research",
        [
            "equity",
            "earnings",
            "stock",
            "company",
            "sector",
            "catalyst",
            "thesis",
            "tear sheet",
            "morning note",
        ],
    ),
    (
        "valuation_modeling",
        [
            "dcf",
            "comps",
            "valuation",
            "3-statement",
            "lbo",
            "merger",
            "model-update",
            "returns",
        ],
    ),
    (
        "fixed_income_fx_derivatives",
        [
            "bond",
            "fixed income",
            "futures basis",
            "fx",
            "carry",
            "swap curve",
            "option vol",
            "volatility",
            "rates",
        ],
    ),
    (
        "portfolio_risk",
        [
            "portfolio",
            "rebalance",
            "allocation",
            "risk",
            "performance",
            "client report",
            "client review",
        ],
    ),
    (
        "private_markets_deal",
        [
            "deal",
            "dd",
            "due diligence",
            "ic memo",
            "cim",
            "m&a",
            "investment committee",
            "sourcing",
        ],
    ),
    (
        "finance_ops_accounting",
        [
            "audit",
            "accrual",
            "recon",
            "roll-forward",
            "kyc",
            "aml",
            "ledger",
            "month-end",
        ],
    ),
    (
        "stark_boundary_or_adjacent",
        [
            "stark-liquidity",
            "stark-tokenomics",
            "stark-market",
            "stark-mkt",
            "stark-capital",
            "stark-data",
        ],
    ),
]

RECOMMENDED_SET = set(DEFAULT_RECOMMENDED_SKILLS)

EXCLUDED_SKILL_PREFIXES = (
    "ckm:",
    "design-",
    "figma-",
    "imagegen-",
    "redesign-",
)

EXCLUDED_SKILL_NAMES = {
    "awesome-design-md",
    "binance-sports-ai-analyzer",
    "darwin-skill",
    "excalidraw-diagram",
    "imagegen-frontend-web",
    "open-design",
    "stark-designer",
    "stark-motion-site-builder",
    "ui-ux-pro-max",
}

FINANCE_RELATED_PATTERNS = [
    "financial",
    "finance",
    "trading",
    "trade idea",
    "trade recommendation",
    "market data",
    "capital markets",
    "market-making",
    "market making",
    "orderbook",
    "order book",
    "broker",
    "portfolio",
    "rebalance",
    "equity",
    "earnings",
    "stock",
    "ticker",
    "valuation",
    "dcf",
    "comps",
    "3-statement",
    "lbo",
    "merger",
    "bond",
    "fixed income",
    "rates",
    "swap curve",
    "fx",
    "xau",
    "option",
    "volatility",
    "futures",
    "derivatives",
    "crypto",
    "token",
    "web3",
    "onchain",
    "wallet",
    "liquidity",
    "holder",
    "smart money",
    "meme coin",
    "pump.fun",
    "binance",
    "gmgn",
    "dune",
    "alchemy",
    "etherscan",
    "deal",
    "due diligence",
    "investment committee",
    "cim",
    "m&a",
    "accounting",
    "audit",
    "accrual",
    "ledger",
    "recon",
    "roll-forward",
    "kyc",
    "aml",
]


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip("\"'")
    return meta


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def display_path(path: Path) -> str:
    try:
        home = Path.home().resolve()
        resolved = path.resolve()
        if home in [resolved, *resolved.parents]:
            return "~/" + resolved.relative_to(home).as_posix()
    except OSError:
        pass
    return path.as_posix()


def default_scan_roots(skill_root: Path) -> list[Path]:
    roots = [
        skill_root,
        skill_root.parent,
        Path.home() / ".agents" / "skills",
        Path.home() / ".codex" / "skills",
        Path.home() / "Documents" / "AI Space" / "Projects" / "Skill&Plugin repo" / ".agents" / "skills",
        Path.home() / "Documents" / "AI Space" / "Projects" / "Skill&Plugin repo" / ".codex" / "skills",
    ]
    env = os.environ.get("STARK_FINANCE_SKILL_ROOTS", "")
    for raw in env.split(os.pathsep):
        if raw.strip():
            roots.append(Path(raw.strip()).expanduser())
    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        try:
            key = str(root.expanduser().resolve())
        except OSError:
            key = str(root.expanduser())
        if key not in seen:
            seen.add(key)
            unique.append(root.expanduser())
    return unique


def skill_files_for_root(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if root.is_file() and root.name == "SKILL.md":
        return [root]
    if (root / "SKILL.md").exists():
        return [root / "SKILL.md"]
    return sorted(root.glob("*/SKILL.md"))


def classify(name: str, description: str) -> list[str]:
    haystack = f"{name} {description}".lower()
    categories = [
        category
        for category, terms in CATEGORY_RULES
        if any(term.lower() in haystack for term in terms)
    ]
    return categories or ["other_finance_candidate"]


def is_finance_related(name: str, description: str) -> bool:
    if name in RECOMMENDED_SET:
        return True
    if name in EXCLUDED_SKILL_NAMES or any(name.startswith(prefix) for prefix in EXCLUDED_SKILL_PREFIXES):
        return False
    haystack = f"{name} {description}".lower()
    if "design token" in haystack and not any(term in haystack for term in ["crypto", "web3", "tokenomics"]):
        return False
    return any(term.lower() in haystack for term in FINANCE_RELATED_PATTERNS)


def discover(skill_root: Path, scan_roots: list[Path], min_finance_skills: int) -> dict[str, Any]:
    grouped: dict[str, dict[str, Any]] = {}
    scanned_roots: list[dict[str, Any]] = []
    total_skill_files = 0

    for root in scan_roots:
        files = skill_files_for_root(root)
        scanned_roots.append(
            {
                "path": display_path(root),
                "exists": root.exists(),
                "skill_files": len(files),
            }
        )
        for file_path in files:
            total_skill_files += 1
            text = file_path.read_text(encoding="utf-8", errors="replace")
            meta = parse_frontmatter(text)
            name = meta.get("name") or file_path.parent.name
            description = normalize_space(meta.get("description") or "")
            related = is_finance_related(name, description)
            if not related:
                continue
            categories = classify(name, description)
            item = grouped.setdefault(
                name,
                {
                    "name": name,
                    "description": description,
                    "categories": sorted(categories),
                    "paths": [],
                },
            )
            item["paths"].append(display_path(file_path.parent))
            item["categories"] = sorted(set(item["categories"]) | set(categories))
            if not item["description"] and description:
                item["description"] = description

    items = sorted(grouped.values(), key=lambda item: item["name"])
    category_counts: dict[str, int] = defaultdict(int)
    for item in items:
        for category in item["categories"]:
            category_counts[category] += 1

    names = {item["name"] for item in items}
    matched_recommended = sorted(names & set(DEFAULT_RECOMMENDED_SKILLS))
    missing_recommended = sorted(set(DEFAULT_RECOMMENDED_SKILLS) - names)
    duplicates = sorted(
        {
            item["name"]: len(item["paths"])
            for item in items
            if len(item["paths"]) > 1
        }.items()
    )
    duplicate_rows = [{"name": name, "copies": copies} for name, copies in duplicates]
    core_present = SKILL_NAME in names
    finance_count = len(items)
    status = "PASS" if core_present and finance_count >= min_finance_skills else "FAIL"

    return {
        "schema_version": "1.0",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "scan_roots": scanned_roots,
        "total_skill_files_seen": total_skill_files,
        "unique_finance_skill_count": finance_count,
        "category_counts": dict(sorted(category_counts.items())),
        "recommended_skill_count": len(DEFAULT_RECOMMENDED_SKILLS),
        "matched_recommended_skills": matched_recommended,
        "missing_recommended_skills": missing_recommended,
        "duplicate_skill_names": duplicate_rows,
        "skills": items,
        "checks": {
            "core_router_present": core_present,
            "minimum_finance_skills": finance_count >= min_finance_skills,
            "min_finance_skills": min_finance_skills,
        },
        "evidence_boundary": "Local SKILL.md inventory only. It proves discoverable local routing surfaces and duplicate copies, not tool authentication, API availability, live model behavior, or trading performance.",
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# stark-finance-trading Local Skill Inventory",
        "",
        f"- Status: {report['status']}",
        f"- Unique finance/trading skills: {report['unique_finance_skill_count']}",
        f"- Total SKILL.md files seen: {report['total_skill_files_seen']}",
        f"- Recommended matched: {len(report['matched_recommended_skills'])}/{report['recommended_skill_count']}",
        "",
        "## Category Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for category, count in report["category_counts"].items():
        lines.append(f"| `{category}` | {count} |")
    lines.extend(["", "## Matched Recommended Skills", ""])
    for name in report["matched_recommended_skills"]:
        lines.append(f"- `{name}`")
    if report["duplicate_skill_names"]:
        lines.extend(["", "## Duplicate Installed Names", ""])
        for item in report["duplicate_skill_names"]:
            lines.append(f"- `{item['name']}`: {item['copies']} copies")
    lines.extend(["", "## Skill Routes", "", "| Skill | Categories | Copies |", "|---|---|---:|"])
    for item in report["skills"]:
        categories = ", ".join(f"`{category}`" for category in item["categories"])
        lines.append(f"| `{item['name']}` | {categories} | {len(item['paths'])} |")
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover local finance/trading skill inventory.")
    parser.add_argument("--skill-root", default=".")
    parser.add_argument("--scan-root", action="append", default=[])
    parser.add_argument("--min-finance-skills", type=int, default=1)
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_root = Path(args.skill_root).expanduser().resolve()
    scan_roots = [Path(item).expanduser() for item in args.scan_root] or default_scan_roots(skill_root)
    report = discover(skill_root, scan_roots, args.min_finance_skills)

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
        print(f"local skill inventory: {report['status']} {report['unique_finance_skill_count']} skills")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
