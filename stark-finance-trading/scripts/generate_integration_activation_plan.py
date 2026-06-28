#!/usr/bin/env python3
"""Generate an integration activation plan for public finance/trading tools."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"

PRIORITY_RANK = {
    "core": 100,
    "execution_framework": 92,
    "execution_candidate": 88,
    "web3_execution_candidate": 86,
    "institutional": 78,
    "support": 60,
    "connector_substrate": 58,
    "finance_ops": 52,
}

READY_STATUSES = {"configured_mcp", "enabled_plugin", "local_skill_backed"}
ACTIONABLE_STAGES = {
    "needs_env",
    "lazy_load_available",
    "verify_local_install",
    "install_or_auth_candidate",
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def priority_rank(value: str | None) -> int:
    return PRIORITY_RANK.get(str(value or ""), 20)


def runtime_by_id(runtime_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item.get("id"): item
        for item in runtime_report.get("tools", [])
        if item.get("id")
    }


def activation_stage(catalog_item: dict[str, Any], runtime_item: dict[str, Any]) -> str:
    runtime_status = runtime_item.get("runtime_status") or ""
    if runtime_status in READY_STATUSES:
        return "ready_now"
    if runtime_status == "deferred_tool_source":
        return "lazy_load_available"
    if runtime_status == "configured_mcp_needs_env":
        return "needs_env"
    if runtime_status == "declared_installed_not_observed":
        return "verify_local_install"
    if runtime_status == "external_candidate":
        return "install_or_auth_candidate" if priority_rank(catalog_item.get("priority")) >= 78 else "watchlist"
    if catalog_item.get("installed_status") == "lazy_loadable_connector_candidate":
        return "lazy_load_available"
    if catalog_item.get("installed_status") in {"installed_on_stark_machine", "installed_needs_key_check"}:
        return "verify_local_install"
    return "watchlist"


def missing_env_names(runtime_item: dict[str, Any]) -> list[str]:
    env_presence = runtime_item.get("required_env_present") or {}
    return sorted(name for name, present in env_presence.items() if not present)


def safety_gate(catalog_item: dict[str, Any], stage: str) -> str:
    tier = int(catalog_item.get("default_action_tier") or 1)
    if tier >= 4:
        return "high_risk_requires_confirmation"
    if stage in {"needs_env", "install_or_auth_candidate", "lazy_load_available"}:
        return "auth_or_install_review"
    if tier >= 3:
        return "simulation_or_paper_first"
    return "read_only_ok"


def next_action(catalog_item: dict[str, Any], runtime_item: dict[str, Any], stage: str) -> str:
    tool_id = catalog_item.get("id")
    missing_env = missing_env_names(runtime_item)
    if stage == "ready_now":
        return "Route through stark-finance-trading when the prompt matches; keep action tier and evidence boundaries."
    if stage == "lazy_load_available":
        return "Use deferred connector discovery when the prompt needs this surface; confirm auth/entitlement before use."
    if stage == "needs_env":
        return f"Set missing env vars for {tool_id}: {', '.join(missing_env) or 'provider-specific key'}; rerun runtime capability scan."
    if stage == "verify_local_install":
        return "Verify local MCP/plugin/skill config and update runtime hints if the tool is intentionally installed."
    if stage == "install_or_auth_candidate":
        return "Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals."
    return "Keep in catalog as a watchlist source; promote only when a real task needs it."


def build_item(catalog_item: dict[str, Any], runtime_item: dict[str, Any]) -> dict[str, Any]:
    stage = activation_stage(catalog_item, runtime_item)
    return {
        "id": catalog_item["id"],
        "name": catalog_item["name"],
        "provider": catalog_item["provider"],
        "priority": catalog_item.get("priority"),
        "priority_rank": priority_rank(catalog_item.get("priority")),
        "source_status": catalog_item.get("source_status"),
        "source_url": catalog_item.get("source_url"),
        "runtime_status": runtime_item.get("runtime_status", "not_scanned"),
        "activation_stage": stage,
        "default_action_tier": catalog_item.get("default_action_tier"),
        "route_tags": catalog_item.get("route_tags", []),
        "best_for": catalog_item.get("best_for", ""),
        "auth_or_setup": catalog_item.get("auth_or_setup", ""),
        "missing_env": missing_env_names(runtime_item),
        "safety_gate": safety_gate(catalog_item, stage),
        "next_action": next_action(catalog_item, runtime_item, stage),
        "merge_policy": catalog_item.get("merge_policy", ""),
        "no_secret_values": True,
    }


def sort_activation_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stage_rank = {
        "needs_env": 0,
        "lazy_load_available": 1,
        "install_or_auth_candidate": 2,
        "verify_local_install": 3,
        "ready_now": 4,
        "watchlist": 5,
    }
    return sorted(
        items,
        key=lambda item: (
            stage_rank.get(item["activation_stage"], 9),
            -int(item.get("priority_rank") or 0),
            -int(item.get("default_action_tier") or 0),
            item["id"],
        ),
    )


def build_report(root: Path, runtime_report_path: Path) -> dict[str, Any]:
    catalog_doc = read_json(root / "references/public-tool-catalog.json")
    runtime_report = read_json(runtime_report_path)
    runtime_tools = runtime_by_id(runtime_report)
    items = [
        build_item(item, runtime_tools.get(item["id"], {}))
        for item in catalog_doc.get("catalog", [])
    ]
    counts = Counter(item["activation_stage"] for item in items)
    safety_counts = Counter(item["safety_gate"] for item in items)
    ready_now = [item for item in items if item["activation_stage"] == "ready_now"]
    quick_activations = [
        item for item in items
        if item["activation_stage"] in {"needs_env", "lazy_load_available", "verify_local_install"}
    ]
    priority_backlog = [
        item for item in items
        if item["activation_stage"] == "install_or_auth_candidate"
    ]
    high_risk = [
        item for item in items
        if item["safety_gate"] == "high_risk_requires_confirmation"
    ]
    actionable = [item for item in items if item["activation_stage"] in ACTIONABLE_STAGES]
    top_actions = sort_activation_items(actionable)[:15]

    required_core = {"dune-mcp", "alchemy-mcp", "etherscan-mcp", "binance-skills-hub", "alpaca-mcp", "openbb"}
    seen_ids = {item["id"] for item in items}
    status = "PASS" if required_core.issubset(seen_ids) and all(item["no_secret_values"] for item in items) else "FAIL"
    return {
        "schema_version": "1.0",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "catalog_tool_count": len(items),
        "runtime_report": str(runtime_report_path),
        "runtime_status": runtime_report.get("status", "MISSING"),
        "activation_stage_counts": dict(sorted(counts.items())),
        "safety_gate_counts": dict(sorted(safety_counts.items())),
        "ready_now_count": len(ready_now),
        "quick_activation_count": len(quick_activations),
        "priority_backlog_count": len(priority_backlog),
        "high_risk_requires_confirmation_count": len(high_risk),
        "required_core_missing": sorted(required_core - seen_ids),
        "top_activation_actions": top_actions,
        "ready_now": sort_activation_items(ready_now),
        "quick_activations": sort_activation_items(quick_activations),
        "priority_backlog": sort_activation_items(priority_backlog),
        "high_risk_requires_confirmation": sort_activation_items(high_risk),
        "tools": sort_activation_items(items),
        "integration_activation_status": "PASS" if status == "PASS" else "FAIL",
        "evidence_boundary": (
            "Integration activation plan is a local routing and setup plan. It uses catalog metadata and runtime-scan "
            "statuses without printing secret values. It does not prove OAuth validity, API entitlement, live tool "
            "availability, market-data correctness, trading performance, remote CI completion, or public superiority."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# stark-finance-trading Integration Activation Plan",
        "",
        f"- Status: {report['status']}",
        f"- Catalog tools: {report['catalog_tool_count']}",
        f"- Runtime report status: `{report['runtime_status']}`",
        f"- Ready now: {report['ready_now_count']}",
        f"- Quick activations: {report['quick_activation_count']}",
        f"- Priority install/auth backlog: {report['priority_backlog_count']}",
        f"- High-risk confirmation surfaces: {report['high_risk_requires_confirmation_count']}",
        "",
        "## Activation Stage Counts",
        "",
        "| Stage | Count |",
        "|---|---:|",
    ]
    for stage, count in report["activation_stage_counts"].items():
        lines.append(f"| `{stage}` | {count} |")

    lines.extend(["", "## Top Activation Actions", "", "| Tool | Stage | Safety | Next action |", "|---|---|---|---|"])
    for item in report["top_activation_actions"]:
        lines.append(
            f"| `{item['id']}` | `{item['activation_stage']}` | `{item['safety_gate']}` | {item['next_action']} |"
        )

    lines.extend(["", "## Ready Now", "", "| Tool | Runtime | Best for |", "|---|---|---|"])
    for item in report["ready_now"]:
        lines.append(f"| `{item['id']}` | `{item['runtime_status']}` | {item['best_for']} |")

    lines.extend(["", "## High-Risk Requires Confirmation", "", "| Tool | Tier | Gate |", "|---|---:|---|"])
    for item in report["high_risk_requires_confirmation"]:
        lines.append(f"| `{item['id']}` | {item['default_action_tier']} | `{item['safety_gate']}` |")

    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate integration activation plan for stark-finance-trading.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--runtime-report", default="dist/stark-finance-trading.runtime-capabilities.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    runtime_report_path = (root / args.runtime_report).resolve() if not Path(args.runtime_report).is_absolute() else Path(args.runtime_report)
    report = build_report(root, runtime_report_path)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(Path(args.markdown), report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"integration activation plan: {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
