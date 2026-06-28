#!/usr/bin/env python3
"""Scan local runtime capability alignment for stark-finance-trading."""

from __future__ import annotations

import argparse
import json
import os
import re
import tomllib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"

DEFAULT_CODEX_CONFIG = Path.home() / ".codex/config.toml"
DEFAULT_SKILL_ROOTS = [
    Path.home() / ".agents/skills",
    Path.home() / ".codex/skills",
    Path.cwd().parent / ".agents/skills",
    Path.cwd().parent / ".codex/skills",
]

RUNTIME_HINTS: dict[str, dict[str, list[str]]] = {
    "dune-mcp": {"mcp": ["dune"], "skills": ["dune"]},
    "alchemy-mcp": {"mcp": ["alchemy"], "skills": ["alchemy"]},
    "etherscan-mcp": {"mcp": ["etherscan"], "env": ["ETHERSCAN_API_KEY"]},
    "binance-skills-hub": {
        "plugins": ["binance@openai-curated"],
        "skills": [
            "binance",
            "binance-agentic-wallet",
            "query-token-info",
            "query-token-audit",
            "query-address-info",
            "crypto-market-rank",
            "trading-signal",
            "meme-rush",
        ],
    },
    "quicknode-mcp": {"plugins": ["quicknode@openai-curated"]},
    "alpaca-mcp": {"deferred_tool_sources": ["Alpaca"]},
    "openbb": {"skills": ["equity-research", "earnings-preview", "earnings-analysis"]},
    "fmp-mcp": {"skills": ["equity-research", "dcf-model", "comps-analysis"]},
    "quantconnect-mcp": {"skills": ["trading-signal"]},
    "lean": {"skills": ["trading-signal"]},
    "hummingbot": {"skills": ["stark-liquidity-strategy"]},
    "freqtrade": {"skills": ["trading-signal"]},
    "ccxt": {"skills": ["binance", "derivatives-trading-coin-futures"]},
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_codex_config(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, [f"config missing: {path}"]
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")), []
    except Exception as exc:  # pragma: no cover - defensive report path
        return {}, [f"config parse error: {exc}"]


def normalize_plugin_name(name: str) -> str:
    return name.strip().lower()


def mcp_servers(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    servers = config.get("mcp_servers") or {}
    return {str(key).lower(): value for key, value in servers.items() if isinstance(value, dict)}


def enabled_plugins(config: dict[str, Any]) -> set[str]:
    plugins = config.get("plugins") or {}
    result = set()
    for name, data in plugins.items():
        if isinstance(data, dict) and data.get("enabled") is True:
            result.add(normalize_plugin_name(str(name)))
    return result


def skill_names(skill_roots: list[Path]) -> dict[str, list[str]]:
    names: dict[str, list[str]] = {}
    for root in skill_roots:
        if not root.exists():
            continue
        for skill_md in root.rglob("SKILL.md"):
            try:
                text = skill_md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            match = re.search(r"^name:\s*['\"]?([^'\"\n]+)", text, flags=re.MULTILINE)
            name = (match.group(1).strip() if match else skill_md.parent.name).lower()
            names.setdefault(name, []).append(str(skill_md.parent))
    return names


def env_status(names: list[str]) -> dict[str, bool]:
    return {name: bool(os.environ.get(name)) for name in names}


def classify_tool(item: dict[str, Any], config: dict[str, Any], skills: dict[str, list[str]]) -> dict[str, Any]:
    tool_id = item["id"]
    hints = RUNTIME_HINTS.get(tool_id, {})
    servers = mcp_servers(config)
    plugins = enabled_plugins(config)
    configured_mcp = [name for name in hints.get("mcp", []) if name.lower() in servers]
    enabled_plugin_matches = [name for name in hints.get("plugins", []) if normalize_plugin_name(name) in plugins]
    local_skill_matches = [name for name in hints.get("skills", []) if name.lower() in skills]
    env_names = hints.get("env", [])
    env_presence = env_status(env_names)
    deferred_sources = hints.get("deferred_tool_sources", [])

    if configured_mcp and env_names and not all(env_presence.values()):
        runtime_status = "configured_mcp_needs_env"
    elif configured_mcp:
        runtime_status = "configured_mcp"
    elif enabled_plugin_matches:
        runtime_status = "enabled_plugin"
    elif local_skill_matches:
        runtime_status = "local_skill_backed"
    elif deferred_sources:
        runtime_status = "deferred_tool_source"
    elif item.get("installed_status") in {"installed_on_stark_machine", "installed_needs_key_check"}:
        runtime_status = "declared_installed_not_observed"
    else:
        runtime_status = "external_candidate"

    availability_rank = {
        "configured_mcp": 100,
        "enabled_plugin": 90,
        "local_skill_backed": 80,
        "configured_mcp_needs_env": 70,
        "deferred_tool_source": 60,
        "declared_installed_not_observed": 40,
        "external_candidate": 10,
    }[runtime_status]

    return {
        "id": tool_id,
        "name": item["name"],
        "provider": item["provider"],
        "catalog_installed_status": item.get("installed_status", ""),
        "runtime_status": runtime_status,
        "availability_rank": availability_rank,
        "configured_mcp": configured_mcp,
        "enabled_plugins": enabled_plugin_matches,
        "local_skills": local_skill_matches,
        "required_env_present": env_presence,
        "deferred_tool_sources": deferred_sources,
        "default_action_tier": item.get("default_action_tier"),
        "priority": item.get("priority"),
    }


def scan(root: Path, config_path: Path, skill_roots: list[Path]) -> dict[str, Any]:
    catalog_doc = read_json(root / "references/public-tool-catalog.json")
    config, warnings = read_codex_config(config_path)
    skills = skill_names(skill_roots)
    tools = [classify_tool(item, config, skills) for item in catalog_doc.get("catalog", [])]
    counts = Counter(item["runtime_status"] for item in tools)
    observed = [item for item in tools if item["runtime_status"] not in {"external_candidate", "declared_installed_not_observed"}]
    env_missing = [
        item["id"]
        for item in tools
        if item["required_env_present"] and not all(item["required_env_present"].values())
    ]
    declared_installed_not_observed = [
        item["id"] for item in tools if item["runtime_status"] == "declared_installed_not_observed"
    ]
    return {
        "schema_version": "1.0",
        "status": "PASS",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "catalog_tool_count": len(tools),
        "observed_runtime_tool_count": len(observed),
        "runtime_status_counts": dict(sorted(counts.items())),
        "configured_mcp_servers": sorted(mcp_servers(config)),
        "enabled_plugin_count": len(enabled_plugins(config)),
        "local_skill_name_count": len(skills),
        "env_missing_tool_ids": env_missing,
        "declared_installed_not_observed": declared_installed_not_observed,
        "tools": tools,
        "warnings": warnings,
        "evidence_boundary": "Local runtime capability scan only. It reads local MCP/plugin/skill configuration and environment-variable presence without exposing secret values. It does not prove OAuth validity, API entitlement, live tool availability, market-data correctness, or trading performance.",
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# stark-finance-trading Runtime Capabilities",
        "",
        f"- Status: {report['status']}",
        f"- Catalog tools: {report['catalog_tool_count']}",
        f"- Observed runtime-backed tools: {report['observed_runtime_tool_count']}",
        f"- Configured MCP servers: {len(report['configured_mcp_servers'])}",
        f"- Enabled plugins: {report['enabled_plugin_count']}",
        f"- Local skill names: {report['local_skill_name_count']}",
        "",
        "## Runtime Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for key, value in report["runtime_status_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "## Observed Tools",
        "",
        "| Tool | Runtime status | Rank |",
        "|---|---|---:|",
    ])
    for item in sorted(report["tools"], key=lambda row: (-row["availability_rank"], row["id"])):
        if item["runtime_status"] == "external_candidate":
            continue
        lines.append(f"| `{item['id']}` | `{item['runtime_status']}` | {item['availability_rank']} |")
    if report["env_missing_tool_ids"]:
        lines.extend(["", "## Env Needed", ""])
        for tool_id in report["env_missing_tool_ids"]:
            lines.append(f"- `{tool_id}`")
    if report["warnings"]:
        lines.extend(["", "## Warnings", ""])
        for warning in report["warnings"]:
            lines.append(f"- {warning}")
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_skill_roots(values: list[str] | None) -> list[Path]:
    roots = list(DEFAULT_SKILL_ROOTS)
    for value in values or []:
        roots.append(Path(value).expanduser())
    seen = set()
    unique = []
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--codex-config", default=str(DEFAULT_CODEX_CONFIG))
    parser.add_argument("--skill-root", action="append")
    parser.add_argument("--out")
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = scan(root, Path(args.codex_config).expanduser(), parse_skill_roots(args.skill_root))
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
        print(f"runtime capability scan: {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
