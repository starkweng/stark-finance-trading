#!/usr/bin/env python3
"""Generate an actionable release blocker plan for stark-finance-trading."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def proof_by_id(external_audit: dict[str, Any], proof_id: str) -> dict[str, Any]:
    for item in external_audit.get("required_proofs") or []:
        if item.get("id") == proof_id:
            return item
    return {}


def classify_blocker(item: dict[str, Any]) -> dict[str, Any]:
    blocker_id = str(item.get("id") or "")
    text = " ".join(
        str(item.get(field) or "")
        for field in ["id", "label", "status", "evidence", "required_action"]
    ).lower()

    if "etherscan" in text or "eth_scan" in text or "etherscan_api_key" in text or "api_key" in text:
        return {
            "category": "needs_secret_or_env",
            "owner": "Stark/local secret setup",
            "automation_allowed": False,
            "automation_boundary": "Do not ask the model to print or store API keys. Set the key in a local secret environment, then rerun the scan.",
            "verification_command": (
                "python3 scripts/runtime_capability_scan.py --root . "
                "--out dist/stark-finance-trading.runtime-capabilities.json "
                "--markdown dist/stark-finance-trading.runtime-capabilities.md --json"
            ),
            "success_evidence": "etherscan-mcp no longer appears in env_missing_tool_ids and ETHERSCAN_API_KEY presence is true.",
        }
    if "github actions" in text or "workflow scope" in text or blocker_id == "remote_github_actions_run":
        return {
            "category": "needs_github_permission",
            "owner": "Stark/GitHub auth",
            "automation_allowed": False,
            "automation_boundary": "The helper can publish and wait only after GitHub CLI auth has workflow scope.",
            "verification_command": (
                "gh auth refresh -h github.com -s workflow; "
                "python3 scripts/enable_remote_ci.py --repo-root . --repo starkweng/stark-finance-trading "
                "--wait --out dist/stark-finance-trading.remote-ci-proof.json "
                "--markdown dist/stark-finance-trading.remote-ci-proof.md --json"
            ),
            "success_evidence": "remote_github_actions_run is PROVEN or PROVIDED in external proof audit.",
        }
    if "comparative" in text:
        return {
            "category": "needs_live_eval_approval",
            "owner": "Stark/live eval reviewer",
            "automation_allowed": False,
            "automation_boundary": "Live eval prompts must be explicitly approved before sending them to a model service.",
            "verification_command": (
                "python3 scripts/generate_live_eval_signoff.py --skill-path . "
                "--eval-set benchmarks/competitive-task-cases.json --live-out-dir dist/competitive-eval "
                "--out dist/stark-finance-trading.competitive-eval-signoff.json "
                "--markdown dist/stark-finance-trading.competitive-eval-signoff.md"
            ),
            "success_evidence": "reviewed_comparative_live_eval is PROVEN or PROVIDED and scorecard source_mode is live/reviewed.",
        }
    if "live eval" in text or "model eval" in text:
        return {
            "category": "needs_live_eval_approval",
            "owner": "Stark/live eval reviewer",
            "automation_allowed": False,
            "automation_boundary": "Live eval prompts must be explicitly approved before sending them to a model service.",
            "verification_command": (
                "python3 scripts/generate_live_eval_signoff.py --skill-path . "
                "--eval-set evals/live-behavior-evals.json --live-out-dir dist/live-eval "
                "--out dist/stark-finance-trading.live-eval-signoff.json "
                "--markdown dist/stark-finance-trading.live-eval-signoff.md"
            ),
            "success_evidence": "approved_live_model_eval is PROVEN or PROVIDED and scorecard source_mode is live/reviewed.",
        }
    return {
        "category": "needs_release_repair",
        "owner": "Codex/local maintainer",
        "automation_allowed": True,
        "automation_boundary": "Local repair is allowed when it does not require secrets, live trading, or external account permissions.",
        "verification_command": "python3 scripts/run_quality_suite.py --dist dist --json",
        "success_evidence": "The corresponding requirement becomes PROVEN in goal completion audit.",
    }


def normalize_status(item: dict[str, Any]) -> str:
    status = str(item.get("status") or "").upper()
    if status in {"PROVEN", "PROVIDED", "PASS"}:
        return status
    if status in {"PARTIAL", "BLOCKED", "PENDING", "MISSING", "FAIL", "WARN"}:
        return status
    return "MISSING"


def make_blocker(item: dict[str, Any], source: str, unblocks: str) -> dict[str, Any]:
    classifier = classify_blocker(item)
    blocker_id = str(item.get("id") or unblocks)
    status = normalize_status(item)
    return {
        "id": blocker_id,
        "label": item.get("label") or blocker_id.replace("_", " ").title(),
        "status": status,
        "category": classifier["category"],
        "source": source,
        "evidence": item.get("evidence") or "",
        "required_action": item.get("required_action") or "Regenerate the relevant proof artifact.",
        "owner": classifier["owner"],
        "automation_allowed": classifier["automation_allowed"],
        "automation_boundary": classifier["automation_boundary"],
        "unblocks": unblocks,
        "verification_command": classifier["verification_command"],
        "success_evidence": classifier["success_evidence"],
    }


def fallback_runtime_blockers(runtime: dict[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for tool in runtime.get("tools") or []:
        missing_env = [
            name
            for name, present in (tool.get("required_env_present") or {}).items()
            if not present
        ]
        if not missing_env:
            continue
        tool_id = str(tool.get("id") or "unknown-tool")
        blockers.append(
            {
                "id": f"{tool_id}_missing_env",
                "label": f"{tool.get('name') or tool_id} missing required environment",
                "status": "PARTIAL",
                "evidence": f"runtime_status={tool.get('runtime_status')}; missing_env={missing_env}",
                "required_action": f"Set missing env vars for {tool_id}: {', '.join(missing_env)}; rerun runtime capability scan.",
            }
        )
    return blockers


def fallback_external_blockers(external_audit: dict[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for proof in external_audit.get("required_proofs") or []:
        status = normalize_status(proof)
        if status not in {"PROVEN", "PROVIDED"} and proof.get("required_for_goal_completion", True):
            blockers.append(proof)
    return blockers


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    dist = Path(args.dist).resolve()
    goal_audit = read_json(dist / f"{SKILL_NAME}.goal-completion-audit.json")
    external_audit = read_json(dist / f"{SKILL_NAME}.external-proof-audit.json")
    runtime = read_json(dist / f"{SKILL_NAME}.runtime-capabilities.json")
    release_readiness = read_json(dist / f"{SKILL_NAME}.release-readiness.json")

    source_items: list[tuple[dict[str, Any], str, str]] = []
    for item in goal_audit.get("blocking_requirements") or []:
        source_items.append((item, "goal_completion_audit", str(item.get("id") or "")))

    if not source_items:
        for item in fallback_runtime_blockers(runtime):
            source_items.append((item, "runtime_capability_scan", "critical_runtime_alignment"))
        for proof in fallback_external_blockers(external_audit):
            mapped = {
                "remote_github_actions_run": "remote_github_actions_proven",
                "approved_live_model_eval": "approved_live_model_eval_proven",
                "reviewed_comparative_live_eval": "reviewed_comparative_live_eval_proven",
            }.get(str(proof.get("id")), str(proof.get("id") or "external_proof"))
            source_items.append((proof, "external_proof_audit", mapped))

    # Enrich and deduplicate against external proof IDs when goal audit is present.
    seen: set[str] = set()
    blockers: list[dict[str, Any]] = []
    external_by_goal = {
        "remote_github_actions_proven": proof_by_id(external_audit, "remote_github_actions_run"),
        "approved_live_model_eval_proven": proof_by_id(external_audit, "approved_live_model_eval"),
        "reviewed_comparative_live_eval_proven": proof_by_id(external_audit, "reviewed_comparative_live_eval"),
    }
    for item, source, unblocks in source_items:
        normalized = dict(item)
        external = external_by_goal.get(str(item.get("id") or "")) or {}
        if external:
            normalized["source"] = external.get("source") or source
            normalized["evidence"] = external.get("evidence") or normalized.get("evidence")
            normalized["required_action"] = external.get("required_action") or normalized.get("required_action")
        blocker = make_blocker(normalized, source, unblocks)
        if blocker["id"] in seen:
            continue
        seen.add(blocker["id"])
        blockers.append(blocker)

    category_counts = dict(Counter(item["category"] for item in blockers))
    status_counts = dict(Counter(item["status"] for item in blockers))
    actionable = [item for item in blockers if item["status"] not in {"PROVEN", "PROVIDED", "PASS"}]
    blocked_external = [
        item
        for item in actionable
        if item["category"] in {"needs_secret_or_env", "needs_github_permission", "needs_live_eval_approval"}
    ]
    next_actions = []
    for item in actionable:
        next_actions.append(
            {
                "id": item["id"],
                "category": item["category"],
                "owner": item["owner"],
                "action": item["required_action"],
                "verify": item["verification_command"],
            }
        )

    return {
        "schema_version": "1.0",
        "status": "PASS",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "dist": str(dist),
        "release_blocker_plan_status": "ACTIONABLE_BLOCKERS_OPEN" if actionable else "NO_BLOCKERS",
        "goal_completion_status": goal_audit.get("goal_completion_status") or "UNKNOWN",
        "release_status": release_readiness.get("local_release_status") or release_readiness.get("status") or "UNKNOWN",
        "blocker_count": len(blockers),
        "actionable_blocker_count": len(actionable),
        "blocked_external_count": len(blocked_external),
        "category_counts": category_counts,
        "status_counts": status_counts,
        "blockers": blockers,
        "next_actions": next_actions,
        "no_secret_values": True,
        "evidence_boundary": (
            "Release blocker plan is an actionable routing artifact. PASS means the plan was generated "
            "from local audits without printing secret values. It does not prove remote GitHub Actions, "
            "live model behavior, API entitlement, market-data correctness, trading performance, or public superiority."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Release Blocker Plan",
        "",
        f"- Status: {report['status']}",
        f"- Plan status: `{report['release_blocker_plan_status']}`",
        f"- Goal completion status: `{report['goal_completion_status']}`",
        f"- Release status: `{report['release_status']}`",
        f"- Blockers: {report['blocker_count']}",
        f"- Actionable blockers: {report['actionable_blocker_count']}",
        f"- External/user-gated blockers: {report['blocked_external_count']}",
        f"- No secret values: {report['no_secret_values']}",
        "",
        "## Category Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]
    for category, count in sorted(report["category_counts"].items()):
        lines.append(f"| `{category}` | {count} |")
    lines.extend(
        [
            "",
            "## Blockers",
            "",
            "| Blocker | Status | Category | Owner | Required Action |",
            "|---|---|---|---|---|",
        ]
    )
    for item in report["blockers"]:
        action = str(item.get("required_action") or "-").replace("|", "\\|")
        lines.append(
            f"| `{item['id']}` | {item['status']} | `{item['category']}` | {item['owner']} | {action} |"
        )
    lines.extend(["", "## Verification Commands", ""])
    for item in report["blockers"]:
        lines.extend(
            [
                f"### `{item['id']}`",
                "",
                "```bash",
                str(item.get("verification_command") or ""),
                "```",
                "",
                f"Success evidence: {item.get('success_evidence') or '-'}",
                "",
            ]
        )
    lines.extend(["## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate release blocker plan for stark-finance-trading.")
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
        print(f"release blocker plan: {report['release_blocker_plan_status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
