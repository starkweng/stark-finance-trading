#!/usr/bin/env python3
"""Audit public comparison source classification and optional URL reachability."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


PRIMARY_STATUS_TERMS = ("official", "primary")
ALLOWED_STATUS_PREFIXES = (
    "official",
    "primary",
)
EXECUTION_CATEGORIES = {
    "broker_data_execution",
    "broker_options_execution",
    "broker_agentic_execution",
    "fx_cfd_platform_mcp",
    "fx_broker_api",
    "fx_terminal_api",
    "web3_wallet_agent_mcp",
    "broker_api_community_mcp",
    "broker_integration_api",
    "crypto_cex_agent_skill",
    "crypto_exchange_mcp",
    "crypto_exchange_api",
    "crypto_derivatives_api",
    "crypto_exchange_library",
}
COMMUNITY_WRAPPER_STATUSES = {
    "official_api_with_community_mcp_candidates",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_https_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def is_primary_status(value: str) -> bool:
    return any(term in value for term in PRIMARY_STATUS_TERMS)


def curl_probe(url: str, timeout: int) -> dict:
    command = [
        "curl",
        "-L",
        "-sS",
        "-o",
        "/dev/null",
        "-w",
        "%{http_code}\t%{url_effective}",
        "--connect-timeout",
        str(min(5, max(1, timeout))),
        "--max-time",
        str(timeout),
        url,
    ]
    try:
        proc = subprocess.run(command, text=True, capture_output=True, timeout=timeout + 5)
    except subprocess.TimeoutExpired as exc:
        return {
            "reachable": False,
            "network_status": "WARN",
            "http_status": 0,
            "effective_url": url,
            "returncode": -1,
            "stderr_tail": f"subprocess timeout after {timeout + 5}s: {exc}",
        }
    stdout = proc.stdout.strip()
    code = 0
    effective_url = url
    if stdout:
        parts = stdout.split("\t", 1)
        try:
            code = int(parts[0])
        except ValueError:
            code = 0
        if len(parts) > 1 and parts[1]:
            effective_url = parts[1]
    reachable = 200 <= code < 400
    if reachable:
        network_status = "PASS"
    elif code == 0 or code in {401, 403, 405, 429} or proc.returncode in {6, 7, 28, 35, 52, 56, 60, 92}:
        network_status = "WARN"
    else:
        network_status = "FAIL"
    return {
        "reachable": reachable,
        "network_status": network_status,
        "http_status": code,
        "effective_url": effective_url,
        "returncode": proc.returncode,
        "stderr_tail": proc.stderr[-500:],
    }


def audit_candidate(item: dict, *, live: bool, timeout: int) -> dict:
    name = str(item.get("name", ""))
    source_url = str(item.get("source_url", ""))
    source_status = str(item.get("source_status", ""))
    category = str(item.get("category", ""))
    strengths = item.get("strengths") or []
    checks = {
        "name": bool(name),
        "category": bool(category),
        "https_source_url": is_https_url(source_url),
        "source_status_allowed": source_status.startswith(ALLOWED_STATUS_PREFIXES),
        "route_role": bool(item.get("route_role")),
        "stark_edge": bool(item.get("what_stark_must_do_better")),
        "strengths": isinstance(strengths, list) and len(strengths) >= 2,
        "risk_tier": isinstance(item.get("default_risk_tier"), int) and 0 <= int(item.get("default_risk_tier")) <= 4,
    }
    if category in EXECUTION_CATEGORIES:
        checks["execution_tier_nonzero"] = int(item.get("default_risk_tier", 0)) >= 3
    if source_status in COMMUNITY_WRAPPER_STATUSES:
        text = (item.get("what_stark_must_do_better") or "") + " " + (item.get("route_role") or "")
        checks["community_wrapper_disclosed"] = bool(re.search(r"community|wrapper|not treat.*official", text, re.I))

    live_probe = None
    structural_ok = all(checks.values())
    warning = False
    if live:
        live_probe = curl_probe(source_url, timeout)
        checks["live_url_not_failed"] = live_probe["network_status"] in {"PASS", "WARN"}
        warning = live_probe["network_status"] == "WARN"

    status = "FAIL" if not all(checks.values()) else "WARN" if warning or not structural_ok else "PASS"
    return {
        "name": name,
        "category": category,
        "source_url": source_url,
        "source_status": source_status,
        "status": status,
        "checks": checks,
        "live_probe": live_probe,
    }


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# stark-finance-trading Public Source Audit",
        "",
        f"- Status: {report['status']}",
        f"- Audit mode: `{report['mode']}`",
        f"- Candidates: {report['candidate_count']}",
        f"- Official or primary sources: {report['official_or_primary_sources']}",
        f"- Execution-capable candidates: {report['execution_capable_candidates']}",
        "",
        "## Candidate Results",
        "",
        "| Candidate | Source status | Result | URL |",
        "|---|---|---|---|",
    ]
    for item in report["candidates"]:
        lines.append(
            f"| {item['name']} | `{item['source_status']}` | {item['status']} | {item['source_url']} |"
        )
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
    parser.add_argument("--comparison", default="benchmarks/public-comparison-2026-06-28.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--live", action="store_true", help="Probe URLs with curl. Offline classification checks run by default.")
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--jobs", type=int, default=8, help="Concurrent live URL probes.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    comparison = read_json(root / args.comparison)
    candidates = comparison.get("candidates") or []
    if args.live and args.jobs > 1:
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            audited = list(executor.map(
                lambda item: audit_candidate(item, live=True, timeout=args.timeout),
                candidates,
            ))
    else:
        audited = [audit_candidate(item, live=args.live, timeout=args.timeout) for item in candidates]
    has_fail = any(item["status"] == "FAIL" for item in audited)
    has_warn = any(item["status"] == "WARN" for item in audited)
    status = "FAIL" if not audited or has_fail else "WARN" if has_warn else "PASS"
    report = {
        "schema_version": "1.0",
        "skill": "stark-finance-trading",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "live" if args.live else "offline",
        "status": status,
        "candidate_count": len(candidates),
        "official_or_primary_sources": sum(1 for item in candidates if is_primary_status(str(item.get("source_status", "")))),
        "execution_capable_candidates": sum(1 for item in candidates if item.get("category") in EXECUTION_CATEGORIES),
        "community_wrapper_candidates": sum(1 for item in candidates if item.get("source_status") in COMMUNITY_WRAPPER_STATUSES),
        "candidates": audited,
        "evidence_boundary": "This audit checks source classification and optional URL reachability only. It does not verify API credentials, live model behavior, trading performance, or public superiority.",
    }
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
        print(f"public source audit: {status} {len(candidates)} candidates")
    return 0 if status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
