#!/usr/bin/env python3
"""Plan prompt-to-tool routes for stark-finance-trading."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


NEGATIVE_RULES = [
    {
        "handoff": "stark-mkt-ops",
        "patterns": [r"\btwitter\b", r"\bkol\b", r"运营", r"社群", r"campaign", r"市场计划"],
    },
    {
        "handoff": "stark-tokenomics-planner",
        "patterns": [r"tokenomics", r"通证", r"释放机制", r"双通证", r"miniartx", r"发行机制"],
    },
    {
        "handoff": "stark-designer",
        "patterns": [r"\bui\b", r"\bdesign\b", r"figma", r"页面设计", r"视觉"],
    },
]

ROUTE_RULES = [
    {
        "id": "broker_api_execution",
        "patterns": [r"alpaca", r"tradier", r"paper trading", r"paper/live", r"live trading", r"broker api", r"order preview", r"美股.*下单", r"股票.*下单"],
        "tool_ids": ["alpaca-mcp", "tradier-mcp", "ibkr-tws-api"],
        "workflow": "Broker API / Paper-Live Execution Boundary",
        "route_tags": ["broker", "paper_trading", "orders"],
        "risk_tier": 4,
        "safety_terms": ["paper_first", "order_preview_only", "explicit_confirmation_required", "kill_switch"],
    },
    {
        "id": "options_flow",
        "patterns": [r"期权", r"options?", r"dark pool", r"unusual", r"flow", r"greek", r"iv\b"],
        "tool_ids": ["unusual-whales-mcp", "tradier-mcp", "alpaca-mcp", "deribit-api"],
        "workflow": "Options Flow",
        "route_tags": ["options_flow", "crypto_options", "broker"],
        "risk_tier": 4,
        "safety_terms": ["order_preview_only", "explicit_confirmation_required"],
    },
    {
        "id": "cex_derivatives_execution",
        "patterns": [r"bybit", r"kraken", r"\bokx\b", r"bingx", r"deribit", r"perp", r"perpetual", r"永续", r"合约交易", r"cex", r"crypto options?", r"加密期权"],
        "tool_ids": ["binance-skills-hub", "bybit-ai-trading-skills", "kraken-mcp", "okx-api", "bingx-ai-skills", "deribit-api", "ccxt"],
        "workflow": "CEX / Crypto Derivatives / Exchange Skills Boundary",
        "route_tags": ["cex", "derivatives", "perpetuals", "crypto_options"],
        "risk_tier": 4,
        "safety_terms": ["venue_specific", "order_preview_only", "explicit_confirmation_required", "max_loss", "kill_switch"],
    },
    {
        "id": "pumpfun_solana",
        "patterns": [r"pump\.?fun", r"solana", r"\bsol\b", r"jupiter", r"helius"],
        "tool_ids": ["dune-mcp", "helius-mcp", "jupiter-apis", "dexscreener-api", "coingecko-mcp", "alchemy-mcp"],
        "workflow": "Solana / Pump.fun Launch Review",
        "route_tags": ["onchain_sql", "pump_fun", "solana"],
        "risk_tier": 2,
        "safety_terms": ["token_identity", "quote_not_swap"],
    },
    {
        "id": "token_contract_dd",
        "patterns": [r"合约", r"contract", r"holder", r"liquidity", r"audit", r"smart money", r"bsc", r"honeypot", r"mint"],
        "tool_ids": ["binance-skills-hub", "dune-mcp", "alchemy-mcp", "etherscan-mcp", "dexscreener-api", "coingecko-mcp"],
        "workflow": "Token Due Diligence",
        "route_tags": ["cex", "holders", "verified_contracts", "dex"],
        "risk_tier": 2,
        "safety_terms": ["full_token_addresses", "cross_check_contract"],
    },
    {
        "id": "defi_protocol_fundamentals",
        "patterns": [r"defi", r"tvl", r"revenue", r"fees?", r"users?", r"yield", r"协议", r"链上真实使用"],
        "tool_ids": ["token-terminal-mcp", "defillama-api", "dune-mcp", "coingecko-mcp", "coinmarketcap-mcp", "alchemy-mcp"],
        "workflow": "DeFi Protocol Research",
        "route_tags": ["protocol_fundamentals", "defi", "onchain_sql"],
        "risk_tier": 1,
        "safety_terms": ["methodology_caveats", "not_trade_signal"],
    },
    {
        "id": "crypto_bot_backtest",
        "patterns": [r"回测", r"backtest", r"mdd", r"grid", r"网格", r"martingale", r"bot", r"hummingbot", r"freqtrade", r"\bccxt\b", r"nautilus", r"quantconnect", r"\blean\b", r"market making", r"dry[- ]?run", r"滑点", r"手续费", r"爆仓"],
        "tool_ids": ["quantconnect-mcp", "lean", "hummingbot", "freqtrade", "nautilus-trader", "ccxt"],
        "workflow": "Strategy Backtest",
        "route_tags": ["backtest", "market_making", "crypto_bot", "crypto_exchange"],
        "risk_tier": 3,
        "safety_terms": ["fees_slippage", "drawdown", "dry_run_first", "kill_switch"],
    },
    {
        "id": "live_order_execution",
        "patterns": [r"直接.*(买|卖|下单|swap|转账|approve|leverage)", r"(买|卖|下单).*(btc|eth|usdt|u\\b)", r"cancel order", r"live order"],
        "tool_ids": ["binance-skills-hub"],
        "workflow": "Execution Prep",
        "route_tags": ["cex"],
        "risk_tier": 4,
        "safety_terms": ["order_preview_only", "explicit_confirmation_required", "max_loss", "kill_switch"],
    },
    {
        "id": "fx_cfd_xau",
        "patterns": [r"xau", r"gold", r"黄金", r"ctrader", r"oanda", r"metatrader", r"\bmt5\b", r"cfd", r"forex", r"fx", r"stop-?out", r"lot", r"margin"],
        "tool_ids": ["ctrader-ai-agent-connect", "oanda-v20-api", "metatrader5-python"],
        "workflow": "FX / CFD / XAUUSD Margin Review",
        "route_tags": ["fx", "xauusd", "broker"],
        "risk_tier": 4,
        "safety_terms": ["demo_first", "broker_assumptions", "explicit_confirmation_required"],
    },
    {
        "id": "tradingview_signal_boundary",
        "patterns": [r"tradingview", r"pine", r"alert", r"webhook", r"图表.*信号", r"信号.*下单"],
        "tool_ids": ["tradingview-broker-api"],
        "workflow": "TradingView / Alerts / Chart Signal Boundary",
        "route_tags": ["charting", "signals", "broker"],
        "risk_tier": 4,
        "safety_terms": ["signal_not_order", "broker_preview_required", "explicit_confirmation_required"],
    },
    {
        "id": "ibkr_boundary",
        "patterns": [r"ibkr", r"interactive brokers", r"\btws\b", r"gateway", r"community mcp"],
        "tool_ids": ["ibkr-tws-api"],
        "workflow": "IBKR / TWS",
        "route_tags": ["broker", "multi_asset"],
        "risk_tier": 4,
        "safety_terms": ["official_api_vs_community_wrapper", "paper_first", "order_preview", "kill_switch"],
    },
    {
        "id": "finance_infra",
        "patterns": [r"stripe", r"plaid", r"billing", r"checkout", r"银行", r"流水", r"cashflow", r"payment", r"收款"],
        "tool_ids": ["stripe-agent-toolkit", "plaid-api"],
        "workflow": "Financial Infrastructure / Payments Boundary",
        "route_tags": ["payments", "bank_data"],
        "risk_tier": 4,
        "safety_terms": ["minimal_scope", "not_trading_signal", "explicit_confirmation_required"],
    },
    {
        "id": "equity_fundamentals",
        "patterns": [r"\b(aapl|nvda|tsla|msft|googl|meta|amzn)\b", r"股票", r"earnings", r"preview", r"dcf", r"估值", r"catalyst", r"portfolio", r"news", r"sentiment"],
        "tool_ids": ["alpaca-mcp", "openbb", "fmp-mcp", "massive-polygon-mcp", "alpha-vantage-mcp", "finnhub-api", "nasdaq-data-link-api"],
        "workflow": "Equity / Macro / Fundamentals Research",
        "route_tags": ["us_equities", "fundamentals", "market_data", "news"],
        "risk_tier": 2,
        "local_skill_hints": ["earnings-preview", "equity-research", "dcf-model", "catalyst-calendar", "portfolio-rebalance"],
        "safety_terms": ["fresh_market_data", "not_trade_order"],
    },
    {
        "id": "market_snapshot",
        "patterns": [r"行情", r"盘口", r"spread", r"depth", r"当前状态", r"1h", r"1小时", r"btc", r"eth", r"xauusd"],
        "tool_ids": ["alpaca-mcp", "binance-skills-hub", "coingecko-mcp", "massive-polygon-mcp", "twelve-data-mcp", "finnhub-api", "nasdaq-data-link-api"],
        "workflow": "Market Snapshot",
        "route_tags": ["market_data"],
        "risk_tier": 1,
        "safety_terms": ["timestamp", "venue", "delay_status"],
    },
]


def load_catalog(root: Path) -> dict[str, dict]:
    doc = json.loads((root / "references/public-tool-catalog.json").read_text(encoding="utf-8"))
    return {item["id"]: item for item in doc.get("catalog", [])}


def load_runtime_report(path: Path | None) -> dict[str, dict]:
    if not path or not path.exists():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {item["id"]: item for item in doc.get("tools", [])}


def matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def rank_tool(tool_id: str, catalog: dict[str, dict], runtime: dict[str, dict]) -> tuple[int, int]:
    runtime_rank = int((runtime.get(tool_id) or {}).get("availability_rank", 0))
    catalog_rank = {
        "installed_on_stark_machine": 50,
        "installed_needs_key_check": 45,
        "lazy_loadable_connector_candidate": 35,
        "external_candidate": 10,
    }.get(str(catalog.get(tool_id, {}).get("installed_status", "")), 0)
    return runtime_rank, catalog_rank


def plan_route(prompt: str, root: Path, runtime_report: Path | None = None) -> dict:
    text = prompt.strip()
    lowered = text.lower()
    for rule in NEGATIVE_RULES:
        if matches_any(lowered, rule["patterns"]):
            return {
                "schema_version": "1.0",
                "status": "PASS",
                "prompt": prompt,
                "should_load": False,
                "handoff": rule["handoff"],
                "reason": "Prompt matches a non-finance/trading primary intent.",
                "tool_ids": [],
                "route_tags": [],
                "workflow": "",
                "risk_tier": 0,
                "safety_terms": ["handoff_not_force_route"],
                "evidence_boundary": "Deterministic route plan only; not a live tool call or model behavior proof.",
            }

    catalog = load_catalog(root)
    runtime = load_runtime_report(runtime_report)
    matched = [rule for rule in ROUTE_RULES if matches_any(lowered, rule["patterns"])]
    if not matched:
        return {
            "schema_version": "1.0",
            "status": "PASS",
            "prompt": prompt,
            "should_load": False,
            "handoff": "none",
            "reason": "No finance/trading route signal matched.",
            "tool_ids": [],
            "route_tags": [],
            "workflow": "",
            "risk_tier": 0,
            "safety_terms": ["route_not_required"],
            "evidence_boundary": "Deterministic route plan only; not a live tool call or model behavior proof.",
        }

    tool_ids = dedupe([tool_id for rule in matched for tool_id in rule.get("tool_ids", []) if tool_id in catalog])
    tool_ids = sorted(tool_ids, key=lambda tool_id: (-rank_tool(tool_id, catalog, runtime)[0], -rank_tool(tool_id, catalog, runtime)[1], tool_ids.index(tool_id)))
    route_tags = dedupe([tag for rule in matched for tag in rule.get("route_tags", [])])
    local_skill_hints = dedupe([hint for rule in matched for hint in rule.get("local_skill_hints", [])])
    safety_terms = dedupe([term for rule in matched for term in rule.get("safety_terms", [])])
    workflows = dedupe([rule["workflow"] for rule in matched if rule.get("workflow")])
    risk_tier = max(int(rule.get("risk_tier", 1)) for rule in matched)
    if risk_tier == 4 and "explicit_confirmation_required" not in safety_terms:
        safety_terms.append("explicit_confirmation_required")
    if any(term in lowered for term in ["不要交易", "先不要执行", "不要执行", "不要直接交易", "不要下单", "不要直接下单", "不要启动", "不要直接实盘", "不要把它变成直接交易建议"]):
        safety_terms.append("no_execution_requested")

    tools = [
        {
            "id": tool_id,
            "name": catalog[tool_id]["name"],
            "provider": catalog[tool_id]["provider"],
            "source_status": catalog[tool_id]["source_status"],
            "default_action_tier": catalog[tool_id]["default_action_tier"],
            "installed_status": catalog[tool_id]["installed_status"],
            "runtime_status": (runtime.get(tool_id) or {}).get("runtime_status", "not_scanned"),
            "availability_rank": (runtime.get(tool_id) or {}).get("availability_rank", rank_tool(tool_id, catalog, runtime)[1]),
        }
        for tool_id in tool_ids
    ]
    return {
        "schema_version": "1.0",
        "status": "PASS",
        "prompt": prompt,
        "should_load": True,
        "handoff": "",
        "matched_rules": [rule["id"] for rule in matched],
        "workflow": " + ".join(workflows),
        "tool_ids": tool_ids,
        "tools": tools,
        "route_tags": route_tags,
        "local_skill_hints": local_skill_hints,
        "risk_tier": risk_tier,
        "risk_mode": "read_only_or_research" if risk_tier <= 2 else "paper_or_live_gated",
        "safety_terms": safety_terms,
        "runtime_report_used": bool(runtime),
        "next_action": "Gather read-only evidence first; produce a preview/checklist for any state-changing path.",
        "evidence_boundary": "Deterministic route plan only; it proves catalog/rule coverage, not live tool availability, API credentials, market-data correctness, or model behavior.",
    }


def validate_cases(root: Path, cases_path: Path, runtime_report: Path | None = None) -> dict:
    doc = json.loads(cases_path.read_text(encoding="utf-8"))
    results = []
    for case in doc.get("cases", []):
        plan = plan_route(case["prompt"], root, runtime_report)
        checks = [
            {"id": "should_load", "passed": plan["should_load"] is case.get("should_load")},
        ]
        expected_handoff = case.get("expected_handoff")
        if expected_handoff:
            checks.append({"id": "expected_handoff", "passed": plan.get("handoff") == expected_handoff})
        for tool_id in case.get("expected_tool_ids", []):
            checks.append({"id": f"tool:{tool_id}", "passed": tool_id in plan.get("tool_ids", [])})
        for route_tag in case.get("expected_route_tags", []):
            checks.append({"id": f"tag:{route_tag}", "passed": route_tag in plan.get("route_tags", [])})
        for hint in case.get("expected_local_skill_hints", []):
            checks.append({"id": f"local:{hint}", "passed": hint in plan.get("local_skill_hints", [])})
        for term in case.get("expected_safety_terms", []):
            checks.append({"id": f"safety:{term}", "passed": term in plan.get("safety_terms", [])})
        if "min_risk_tier" in case:
            checks.append({"id": "min_risk_tier", "passed": int(plan.get("risk_tier", 0)) >= int(case["min_risk_tier"])})
        if "max_risk_tier" in case:
            checks.append({"id": "max_risk_tier", "passed": int(plan.get("risk_tier", 0)) <= int(case["max_risk_tier"])})
        results.append({
            "id": case["id"],
            "prompt": case["prompt"],
            "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
            "checks": checks,
            "plan": plan,
        })

    passed = sum(1 for item in results if item["status"] == "PASS")
    return {
        "schema_version": "1.0",
        "status": "PASS" if passed == len(results) and results else "FAIL",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": "stark-finance-trading",
        "case_count": len(results),
        "passed_cases": passed,
        "failed_cases": [item["id"] for item in results if item["status"] != "PASS"],
        "cases": results,
        "evidence_boundary": doc.get("claim_boundary", "Deterministic route cases only."),
    }


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# stark-finance-trading Tool Route Plan",
        "",
        f"- Status: {report['status']}",
    ]
    if "case_count" in report:
        lines.extend([
            f"- Cases: {report['passed_cases']}/{report['case_count']}",
            "",
            "| Case | Status | Risk | Tools |",
            "|---|---|---:|---|",
        ])
        for item in report["cases"]:
            plan = item["plan"]
            lines.append(f"| `{item['id']}` | {item['status']} | {plan.get('risk_tier', 0)} | `{', '.join(plan.get('tool_ids', []))}` |")
    else:
        lines.extend([
            f"- Should load: {report['should_load']}",
            f"- Risk tier: {report['risk_tier']}",
            f"- Workflow: {report.get('workflow', '')}",
            f"- Tools: `{', '.join(report.get('tool_ids', []))}`",
            f"- Local helpers: `{', '.join(report.get('local_skill_hints', []))}`",
            f"- Safety terms: `{', '.join(report.get('safety_terms', []))}`",
        ])
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--prompt")
    parser.add_argument("--cases", default="evals/tool-routing-cases.json")
    parser.add_argument("--runtime-report")
    parser.add_argument("--out")
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    runtime_report = Path(args.runtime_report).resolve() if args.runtime_report else None
    if args.prompt:
        report = plan_route(args.prompt, root, runtime_report)
    else:
        report = validate_cases(root, root / args.cases, runtime_report)

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
        print(f"tool route plan: {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
