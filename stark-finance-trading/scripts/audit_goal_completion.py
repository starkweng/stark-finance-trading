#!/usr/bin/env python3
"""Audit stark-finance-trading against Stark's original completion goal."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"
REQUIRED_PUBLIC_TOOL_IDS = {
    "dune-mcp",
    "alchemy-mcp",
    "etherscan-mcp",
    "binance-skills-hub",
    "alpaca-mcp",
    "openbb",
    "ibkr-tws-api",
    "hummingbot",
    "freqtrade",
}
DEFAULT_INSTALL_PATHS = [
    Path("/Users/mac/.agents/skills/stark-finance-trading"),
    Path("/Users/mac/.codex/skills/stark-finance-trading"),
    Path("/Users/mac/Documents/AI Space/Projects/Skill&Plugin repo/.agents/skills/stark-finance-trading"),
    Path("/Users/mac/Documents/AI Space/Projects/Skill&Plugin repo/.codex/skills/stark-finance-trading"),
]
INSTALLED_COPY_FRESHNESS_FILES = [
    "SKILL.md",
    "scripts/audit_goal_completion.py",
    "scripts/audit_external_proofs.py",
    "scripts/discover_github_finance_tools.py",
    "scripts/analyze_competitive_gaps.py",
    "scripts/generate_competitive_route_backlog.py",
    "scripts/generate_integration_activation_plan.py",
    "scripts/run_quality_suite.py",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_entry_count(path: Path) -> int:
    if not path.exists():
        return 0
    with zipfile.ZipFile(path) as archive:
        return len([item for item in archive.infolist() if not item.is_dir()])


def requirement(
    req_id: str,
    label: str,
    passed: bool,
    *,
    evidence: str,
    required_action: str = "",
    required_for_goal_completion: bool = True,
    status: str | None = None,
) -> dict[str, Any]:
    if status is None:
        status = "PROVEN" if passed else "MISSING"
    return {
        "id": req_id,
        "label": label,
        "status": status,
        "passed": passed,
        "required_for_goal_completion": required_for_goal_completion,
        "evidence": evidence,
        "required_action": required_action,
    }


def proof_by_id(external_audit: dict[str, Any], proof_id: str) -> dict[str, Any]:
    for item in external_audit.get("required_proofs") or []:
        if item.get("id") == proof_id:
            return item
    return {}


def audit_installed_copies(skill_root: Path) -> dict[str, Any]:
    source_hashes = {
        rel: sha256_file(skill_root / rel)
        for rel in INSTALLED_COPY_FRESHNESS_FILES
        if (skill_root / rel).exists()
    }
    copies: list[dict[str, Any]] = []
    for path in DEFAULT_INSTALL_PATHS:
        file_checks = []
        for rel, source_hash in source_hashes.items():
            target = path / rel
            copy_hash = sha256_file(target) if target.exists() else ""
            file_checks.append(
                {
                    "path": rel,
                    "exists": target.exists(),
                    "hash_matches_source": bool(source_hash and copy_hash and source_hash == copy_hash),
                }
            )
        copies.append(
            {
                "path": str(path),
                "exists": path.exists(),
                "file_checks": file_checks,
                "hash_matches_source": bool(file_checks) and all(item["hash_matches_source"] for item in file_checks),
            }
        )
    existing = [item for item in copies if item["exists"]]
    return {
        "status": "PASS" if existing and all(item["hash_matches_source"] for item in existing) else "WARN",
        "source_hashes": source_hashes,
        "copies": copies,
        "existing_count": len(existing),
        "matching_count": sum(1 for item in existing if item["hash_matches_source"]),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    skill_root = Path(args.skill_root).resolve()
    dist = Path(args.dist).resolve()
    skill_md = read_text(skill_root / "SKILL.md")
    tool_router = read_text(skill_root / "references" / "tool-router.md")
    local_router = read_text(skill_root / "references" / "local-skill-router.md")
    public_catalog = read_json(skill_root / "references" / "public-tool-catalog.json")
    public_tools = public_catalog.get("catalog") or []
    public_tool_ids = {item.get("id") for item in public_tools}

    quality = read_json(dist / f"{SKILL_NAME}.quality-suite.json")
    runtime = read_json(dist / f"{SKILL_NAME}.runtime-capabilities.json")
    activation_plan = read_json(dist / f"{SKILL_NAME}.integration-activation-plan.json")
    route_plan = read_json(dist / f"{SKILL_NAME}.tool-route-plan.json")
    inventory = read_json(dist / f"{SKILL_NAME}.local-skill-inventory.json")
    public_benchmark = read_json(dist / f"{SKILL_NAME}.public-benchmark.json")
    competitive_gap = read_json(dist / f"{SKILL_NAME}.competitive-gap-analysis.json")
    competitive_route_backlog = read_json(dist / f"{SKILL_NAME}.competitive-route-backlog.json")
    release_readiness = read_json(dist / f"{SKILL_NAME}.release-readiness.json")
    external_audit = read_json(dist / f"{SKILL_NAME}.external-proof-audit.json")
    github_smoke = read_json(dist / f"{SKILL_NAME}.github-export-smoke.json")

    package_path = dist / f"{SKILL_NAME}.skill"
    github_zip_path = dist / f"{SKILL_NAME}-github-repo.zip"
    package_hash = sha256_file(package_path) if package_path.exists() else ""
    github_zip_hash = sha256_file(github_zip_path) if github_zip_path.exists() else ""
    installed = audit_installed_copies(skill_root)

    remote_ci = proof_by_id(external_audit, "remote_github_actions_run")
    live_eval = proof_by_id(external_audit, "approved_live_model_eval")
    comparative_eval = proof_by_id(external_audit, "reviewed_comparative_live_eval")
    public_repo = proof_by_id(external_audit, "public_repo_url")

    etherscan_tool = next((item for item in (runtime.get("tools") or []) if item.get("id") == "etherscan-mcp"), {})
    etherscan_env_present = bool((etherscan_tool.get("required_env_present") or {}).get("ETHERSCAN_API_KEY"))
    core_runtime_ids = {
        item.get("id"): item.get("runtime_status")
        for item in (runtime.get("tools") or [])
        if item.get("id") in {"dune-mcp", "alchemy-mcp", "etherscan-mcp", "binance-skills-hub"}
    }

    requirements = [
        requirement(
            "stark_named_single_front_door",
            "A single stark-prefixed finance/trading front door exists",
            "name: stark-finance-trading" in skill_md
            and "Load when" in skill_md
            and "Do not load" in skill_md
            and "User-facing entry: stark-finance-trading" in local_router,
            evidence="SKILL.md frontmatter and local-skill-router keep stark-finance-trading as the user-facing entry.",
            required_action="Restore SKILL.md frontmatter and local router entry.",
        ),
        requirement(
            "merged_vendor_and_local_routing",
            "Vendor MCP/API surfaces and local finance skills are merged behind the router",
            "Do not create separate user-facing skills for every vendor" in tool_router
            and "references/local-skill-router.md" in tool_router
            and inventory.get("status") == "PASS"
            and not inventory.get("missing_recommended_skills"),
            evidence=(
                f"inventory_status={inventory.get('status')}; "
                f"recommended={inventory.get('recommended_skill_count')}; "
                f"missing={len(inventory.get('missing_recommended_skills') or [])}"
            ),
            required_action="Regenerate local skill inventory and restore one-skill merge policy.",
        ),
        requirement(
            "public_tool_catalog_coverage",
            "Major public finance/trading/Web3 tools are represented",
            len(public_tools) >= 30 and REQUIRED_PUBLIC_TOOL_IDS.issubset(public_tool_ids),
            evidence=f"catalog_tools={len(public_tools)}; required_missing={sorted(REQUIRED_PUBLIC_TOOL_IDS - public_tool_ids)}",
            required_action="Add missing required public tool IDs to references/public-tool-catalog.json.",
        ),
        requirement(
            "critical_runtime_alignment",
            "Critical local Web3 surfaces are runtime-aligned",
            runtime.get("status") == "PASS"
            and core_runtime_ids.get("dune-mcp") == "configured_mcp"
            and core_runtime_ids.get("alchemy-mcp") == "configured_mcp"
            and core_runtime_ids.get("binance-skills-hub") == "enabled_plugin"
            and core_runtime_ids.get("etherscan-mcp") in {"configured_mcp", "configured_mcp_needs_env"},
            evidence=f"core_runtime={core_runtime_ids}; etherscan_env_present={etherscan_env_present}",
            required_action="Set ETHERSCAN_API_KEY if Etherscan live calls are required.",
            status="PARTIAL" if not etherscan_env_present else None,
        ),
        requirement(
            "route_regression_coverage",
            "Prompt-to-tool routing regression passes",
            route_plan.get("status") == "PASS" and route_plan.get("passed_cases") == route_plan.get("case_count"),
            evidence=f"route_plan_status={route_plan.get('status')}; cases={route_plan.get('passed_cases')}/{route_plan.get('case_count')}",
            required_action="Fix scripts/plan_tool_route.py or evals/tool-routing-cases.json.",
        ),
        requirement(
            "source_level_public_benchmark",
            "Source-level public benchmark passes without superiority claims",
            public_benchmark.get("status") == "PASS"
            and public_benchmark.get("score", 0) >= public_benchmark.get("minimum_pass_score", 90)
            and public_benchmark.get("claim_status") == "source_level_benchmark_pass_live_comparison_pending",
            evidence=(
                f"benchmark_status={public_benchmark.get('status')}; "
                f"score={public_benchmark.get('score')}; claim_status={public_benchmark.get('claim_status')}"
            ),
            required_action="Regenerate public benchmark and keep superiority claims evidence-labeled.",
        ),
        requirement(
            "competitive_gap_backlog_generated",
            "GitHub discovery is converted into a competitive coverage/backlog analysis",
            competitive_gap.get("status") in {"PASS", "WARN"}
            and competitive_gap.get("candidate_count", 0) > 0
            and "PARTIAL_RUNTIME" in (competitive_gap.get("coverage_status_counts") or {}),
            evidence=(
                f"gap_status={competitive_gap.get('status')}; "
                f"candidates={competitive_gap.get('candidate_count')}; "
                f"high_priority_backlog={competitive_gap.get('high_priority_backlog_count')}; "
                f"actions={competitive_gap.get('backlog_action_counts')}"
            ),
            required_action="Run scripts/analyze_competitive_gaps.py after GitHub discovery, runtime scan, and route planning.",
        ),
        requirement(
            "competitive_route_eval_backlog_generated",
            "Competitive backlog is converted into route/eval proposals",
            competitive_route_backlog.get("status") == "PASS"
            and competitive_route_backlog.get("case_count", 0) > 0
            and "route_eval_proposal" in (competitive_route_backlog.get("stage_counts") or {})
            and "auth_or_env_needed" in (competitive_route_backlog.get("stage_counts") or {}),
            evidence=(
                f"route_backlog_status={competitive_route_backlog.get('status')}; "
                f"cases={competitive_route_backlog.get('case_count')}; "
                f"stages={competitive_route_backlog.get('stage_counts')}; "
                f"actions={competitive_route_backlog.get('backlog_action_counts')}"
            ),
            required_action="Run scripts/generate_competitive_route_backlog.py after competitive gap analysis.",
        ),
        requirement(
            "integration_activation_plan_generated",
            "Public tool catalog is converted into an activation plan",
            activation_plan.get("status") == "PASS"
            and activation_plan.get("ready_now_count", 0) > 0
            and activation_plan.get("quick_activation_count", 0) > 0
            and activation_plan.get("high_risk_requires_confirmation_count", 0) > 0
            and not activation_plan.get("required_core_missing"),
            evidence=(
                f"activation_status={activation_plan.get('status')}; "
                f"ready_now={activation_plan.get('ready_now_count')}; "
                f"quick={activation_plan.get('quick_activation_count')}; "
                f"priority_backlog={activation_plan.get('priority_backlog_count')}; "
                f"high_risk={activation_plan.get('high_risk_requires_confirmation_count')}"
            ),
            required_action="Run scripts/generate_integration_activation_plan.py after runtime capability scan.",
        ),
        requirement(
            "quality_suite_green",
            "Portable quality suite is green",
            quality.get("status") == "PASS" and not [item for item in quality.get("steps", []) if item.get("status") != "PASS"],
            evidence=f"quality_status={quality.get('status')}; steps={len(quality.get('steps') or [])}",
            required_action="Rerun scripts/run_quality_suite.py and fix failing steps.",
        ),
        requirement(
            "package_and_export_ready",
            "Installable package and GitHub export are clean and current",
            release_readiness.get("status") == "PASS"
            and release_readiness.get("local_release_status") == "LOCAL_RELEASE_READY"
            and package_path.exists()
            and github_zip_path.exists()
            and github_smoke.get("status") == "PASS",
            evidence=(
                f"release_status={release_readiness.get('status')}; "
                f"package_sha={package_hash}; package_entries={package_entry_count(package_path)}; "
                f"github_zip_sha={github_zip_hash}; github_zip_entries={package_entry_count(github_zip_path)}; "
                f"github_smoke={github_smoke.get('status')}"
            ),
            required_action="Regenerate package, GitHub export, export smoke, and release readiness.",
        ),
        requirement(
            "installed_copies_synced",
            "Local installed skill copies are synced where present",
            installed["status"] == "PASS",
            evidence=f"existing={installed['existing_count']}; matching={installed['matching_count']}; checked_files={sorted(installed['source_hashes'])}",
            required_action="Rsync stark-finance-trading to .agents/.codex skill roots and rerun validators.",
        ),
        requirement(
            "public_repository_published",
            "Public GitHub repository proof is available",
            public_repo.get("status") in {"PROVIDED", "PROVEN"} and bool(args.public_repo_url or public_repo.get("value")),
            evidence=f"public_repo_status={public_repo.get('status')}; url={args.public_repo_url or public_repo.get('value') or ''}",
            required_action="Publish or provide the public GitHub repository URL.",
        ),
        requirement(
            "remote_github_actions_proven",
            "Remote GitHub Actions CI has completed successfully",
            remote_ci.get("status") in {"PROVEN", "PROVIDED"},
            evidence=f"remote_ci_status={remote_ci.get('status')}; evidence={remote_ci.get('evidence')}",
            required_action=remote_ci.get("required_action") or "Enable and run remote GitHub Actions CI.",
        ),
        requirement(
            "approved_live_model_eval_proven",
            "Approved live model eval proof exists",
            live_eval.get("status") in {"PROVEN", "PROVIDED"},
            evidence=f"live_eval_status={live_eval.get('status')}; evidence={live_eval.get('evidence')}",
            required_action=live_eval.get("required_action") or "Run and review an approved live model eval.",
        ),
        requirement(
            "reviewed_comparative_live_eval_proven",
            "Reviewed comparative live eval proof exists",
            comparative_eval.get("status") in {"PROVEN", "PROVIDED"},
            evidence=f"comparative_eval_status={comparative_eval.get('status')}; evidence={comparative_eval.get('evidence')}",
            required_action=comparative_eval.get("required_action") or "Run and review the comparative live eval.",
        ),
    ]

    incomplete = [
        item
        for item in requirements
        if item["required_for_goal_completion"] and item["status"] != "PROVEN"
    ]
    return {
        "schema_version": "1.0",
        "status": "PASS",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "skill_root": str(skill_root),
        "dist": str(dist),
        "goal_completion_status": "COMPLETE" if not incomplete else "NOT_COMPLETE_REQUIREMENTS_PENDING",
        "summary": {
            "requirements": len(requirements),
            "proven": sum(1 for item in requirements if item["status"] == "PROVEN"),
            "partial": sum(1 for item in requirements if item["status"] == "PARTIAL"),
            "missing_or_blocked": len(incomplete),
        },
        "requirements": requirements,
        "blocking_requirements": incomplete,
        "installed_copies": installed,
        "artifacts": {
            "package": str(package_path),
            "package_sha256": package_hash,
            "github_export_zip": str(github_zip_path),
            "github_export_zip_sha256": github_zip_hash,
        },
        "evidence_boundary": (
            "This audit maps Stark's original objective to machine-checkable evidence. PASS means the audit ran. "
            "The goal is complete only when every required requirement is PROVEN. PARTIAL, MISSING, BLOCKED, "
            "or dry-run evidence keeps the goal active."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Goal Completion Audit",
        "",
        f"- Status: {report['status']}",
        f"- Goal completion status: `{report['goal_completion_status']}`",
        f"- Proven requirements: {report['summary']['proven']}/{report['summary']['requirements']}",
        f"- Partial requirements: {report['summary']['partial']}",
        f"- Missing or blocked requirements: {report['summary']['missing_or_blocked']}",
        "",
        "## Requirements",
        "",
        "| Requirement | Status | Evidence | Required Action |",
        "|---|---|---|---|",
    ]
    for item in report["requirements"]:
        lines.append(
            f"| `{item['id']}` | {item['status']} | {item['evidence']} | {item['required_action'] or '-'} |"
        )
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit stark-finance-trading against the original goal.")
    parser.add_argument("--skill-root", default=".")
    parser.add_argument("--dist", default="dist")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--public-repo-url", default="")
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
        print(f"goal completion audit: {report['goal_completion_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
