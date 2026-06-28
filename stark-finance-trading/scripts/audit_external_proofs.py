#!/usr/bin/env python3
"""Audit external proof status for stark-finance-trading release completion."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"
PROVEN_STATUSES = {"PROVEN", "PROVIDED"}


def read_json(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if not path.exists():
        return {}, {"path": str(path), "status": "MISSING", "error": ""}
    try:
        return json.loads(path.read_text(encoding="utf-8")), {"path": str(path), "status": "PRESENT", "error": ""}
    except json.JSONDecodeError as exc:
        return {}, {"path": str(path), "status": "INVALID_JSON", "error": str(exc)}


def proof(
    proof_id: str,
    label: str,
    status: str,
    *,
    source: str,
    evidence: str,
    required_action: str,
    required_for_goal_completion: bool = True,
    value: str = "",
    evidence_boundary: str = "",
) -> dict[str, Any]:
    return {
        "id": proof_id,
        "label": label,
        "status": status,
        "required_for_goal_completion": required_for_goal_completion,
        "value": value,
        "source": source,
        "evidence": evidence,
        "required_action": required_action,
        "evidence_boundary": evidence_boundary,
    }


def audit_public_repo(public_repo_url: str) -> dict[str, Any]:
    if public_repo_url.startswith("https://github.com/"):
        return proof(
            "public_repo_url",
            "Public GitHub repository URL",
            "PROVIDED",
            source="argument",
            value=public_repo_url,
            evidence="A public GitHub repository URL was supplied.",
            required_action="",
            evidence_boundary="URL presence proves the publication target, not source freshness or remote CI.",
        )
    return proof(
        "public_repo_url",
        "Public GitHub repository URL",
        "PENDING",
        source="argument",
        evidence="No public GitHub repository URL was supplied.",
        required_action="Publish or provide the public repository URL.",
        evidence_boundary="URL absence keeps goal completion pending.",
    )


def run_item_from_remote_ci(remote_ci: dict[str, Any]) -> dict[str, Any]:
    remote_run = remote_ci.get("remote_run") or {}
    if isinstance(remote_run.get("run"), dict):
        return remote_run["run"]
    return remote_run if isinstance(remote_run, dict) else {}


def audit_remote_ci(remote_ci: dict[str, Any], meta: dict[str, Any], github_run_url: str) -> dict[str, Any]:
    if github_run_url:
        return proof(
            "remote_github_actions_run",
            "Remote GitHub Actions run",
            "PROVIDED",
            source="argument",
            value=github_run_url,
            evidence="A remote GitHub Actions run URL was supplied.",
            required_action="Review the linked run before claiming full completion.",
            evidence_boundary="A supplied URL still needs human review unless the proof packet records success.",
        )
    if meta["status"] != "PRESENT":
        return proof(
            "remote_github_actions_run",
            "Remote GitHub Actions run",
            "PENDING",
            source=meta["path"],
            evidence=f"Remote CI proof file is {meta['status']}.",
            required_action="Run scripts/enable_remote_ci.py after publishing the exported repository.",
            evidence_boundary="No remote run proof has been observed.",
        )

    run_item = run_item_from_remote_ci(remote_ci)
    proof_status = remote_ci.get("status")
    conclusion = run_item.get("conclusion")
    run_status = run_item.get("status")
    run_url = run_item.get("url") or run_item.get("html_url") or ""
    if proof_status == "PASS" and run_item and conclusion == "success":
        return proof(
            "remote_github_actions_run",
            "Remote GitHub Actions run",
            "PROVEN",
            source=meta["path"],
            value=run_url,
            evidence=f"Remote workflow completed with conclusion={conclusion}.",
            required_action="",
            evidence_boundary="Remote CI success proves repository CI execution, not live model behavior or market accuracy.",
        )

    auth = remote_ci.get("auth") or {}
    workflow_file = ((remote_ci.get("remote_state") or {}).get("workflow_file") or {}).get("status")
    required_action = remote_ci.get("required_action") or "Rerun scripts/enable_remote_ci.py with --wait."
    if auth.get("has_workflow_scope") is False:
        status = "BLOCKED"
        evidence = "GitHub CLI token is missing workflow scope."
    elif workflow_file == "MISSING_OR_INACCESSIBLE":
        status = "BLOCKED"
        evidence = "Remote .github/workflows/ci.yml is missing or inaccessible."
    elif proof_status == "FAIL":
        status = "BLOCKED"
        evidence = f"Remote CI proof status is FAIL; remote_run={run_status or 'unknown'}."
    else:
        status = "PENDING"
        evidence = f"Remote CI proof status={proof_status}; run_status={run_status or 'missing'}; conclusion={conclusion or 'missing'}."

    return proof(
        "remote_github_actions_run",
        "Remote GitHub Actions run",
        status,
        source=meta["path"],
        value=run_url,
        evidence=evidence,
        required_action=required_action,
        evidence_boundary="Remote CI is required for public release completion but does not prove live model behavior.",
    )


def audit_scorecard(
    proof_id: str,
    label: str,
    scorecard: dict[str, Any],
    meta: dict[str, Any],
    external_url: str,
) -> dict[str, Any]:
    if external_url:
        return proof(
            proof_id,
            label,
            "PROVIDED",
            source="argument",
            value=external_url,
            evidence="An external reviewed live-eval URL was supplied.",
            required_action="Review the linked evidence before claiming final completion.",
            evidence_boundary="A supplied URL is external evidence; local scorecard status is still reported separately.",
        )
    if meta["status"] != "PRESENT":
        return proof(
            proof_id,
            label,
            "PENDING",
            source=meta["path"],
            evidence=f"Scorecard file is {meta['status']}.",
            required_action="Generate and review a live eval scorecard.",
            evidence_boundary="Missing scorecard keeps live behavior proof pending.",
        )

    source_mode = str(scorecard.get("source_mode") or "")
    behavior_status = str(scorecard.get("behavior_proof_status") or "")
    status = str(scorecard.get("status") or "")
    if status == "PASS" and behavior_status == "REVIEWABLE_LIVE_EVIDENCE" and source_mode in {"live", "reviewed_live", "live_run"}:
        return proof(
            proof_id,
            label,
            "PROVEN",
            source=meta["path"],
            evidence=f"Scorecard is PASS with source_mode={source_mode} and behavior_proof_status={behavior_status}.",
            required_action="",
            evidence_boundary="Live eval proof covers behavior reviewability, not trading performance or public superiority by itself.",
        )
    return proof(
        proof_id,
        label,
        "PENDING",
        source=meta["path"],
        evidence=f"Scorecard status={status}; source_mode={source_mode}; behavior_proof_status={behavior_status}.",
        required_action="Run an approved live eval, generate the review bundle, and score it after human review.",
        evidence_boundary="Dry-run or fixture scorecards are reviewability proof only, not live model behavior proof.",
    )


def audit_harness(label: str, smoke: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    if meta["status"] != "PRESENT":
        status = "PENDING"
        evidence = f"Harness smoke file is {meta['status']}."
    elif smoke.get("status") == "PASS":
        status = "HARNESS_ONLY_NOT_MODEL_PROOF"
        evidence = f"Harness smoke PASS; mode={smoke.get('mode')}; runner_kind={smoke.get('runner_kind')}."
    else:
        status = "FAIL"
        evidence = f"Harness smoke status={smoke.get('status')}."
    return proof(
        label.replace(" ", "_").lower(),
        label,
        status,
        source=meta["path"],
        evidence=evidence,
        required_action="" if status == "HARNESS_ONLY_NOT_MODEL_PROOF" else "Rerun scripts/run_live_eval_harness_smoke.py.",
        required_for_goal_completion=False,
        evidence_boundary="Harness smoke proves the approved-runner path only. It is not live model behavior proof.",
    )


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    dist = Path(args.dist).resolve()
    remote_ci, remote_ci_meta = read_json(dist / f"{SKILL_NAME}.remote-ci-proof.json")
    live_scorecard, live_scorecard_meta = read_json(dist / f"{SKILL_NAME}.live-eval-scorecard.json")
    comp_scorecard, comp_scorecard_meta = read_json(dist / f"{SKILL_NAME}.competitive-eval-scorecard.json")
    live_smoke, live_smoke_meta = read_json(dist / f"{SKILL_NAME}.live-eval-harness-smoke.json")
    comp_smoke, comp_smoke_meta = read_json(dist / f"{SKILL_NAME}.competitive-eval-harness-smoke.json")

    proofs = [
        audit_public_repo(args.public_repo_url),
        audit_remote_ci(remote_ci, remote_ci_meta, args.github_run_url),
        audit_scorecard(
            "approved_live_model_eval",
            "Approved live model eval",
            live_scorecard,
            live_scorecard_meta,
            args.live_eval_url,
        ),
        audit_scorecard(
            "reviewed_comparative_live_eval",
            "Reviewed comparative live eval",
            comp_scorecard,
            comp_scorecard_meta,
            args.comparative_eval_url,
        ),
    ]
    supporting = [
        audit_harness("Live eval harness smoke", live_smoke, live_smoke_meta),
        audit_harness("Competitive eval harness smoke", comp_smoke, comp_smoke_meta),
    ]
    pending = [item for item in proofs if item["status"] not in PROVEN_STATUSES]
    blocked = [item for item in proofs if item["status"] == "BLOCKED"]
    return {
        "schema_version": "1.0",
        "status": "PASS",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "dist": str(dist),
        "external_proof_status": "COMPLETE" if not pending else "PENDING",
        "goal_completion_status": "READY_FOR_COMPLETION_AUDIT" if not pending else "NOT_COMPLETE_EXTERNAL_PROOFS_PENDING",
        "summary": {
            "required_proofs": len(proofs),
            "proven_or_provided": len(proofs) - len(pending),
            "pending_or_blocked": len(pending),
            "blocked": len(blocked),
            "supporting_evidence_items": len(supporting),
        },
        "required_proofs": proofs,
        "supporting_evidence": supporting,
        "required_actions": [item["required_action"] for item in proofs if item["required_action"]],
        "evidence_boundary": (
            "This audit classifies external completion proofs. PASS means the audit ran and labeled the evidence. "
            "Goal completion remains pending until every required proof is PROVEN or PROVIDED. Harness smokes, "
            "dry-run scorecards, and local package checks are useful release evidence but are not live model behavior, "
            "remote CI success, market-data correctness, trading performance, or public superiority proof."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# External Proof Audit",
        "",
        f"- Status: {report['status']}",
        f"- External proof status: `{report['external_proof_status']}`",
        f"- Goal completion status: `{report['goal_completion_status']}`",
        f"- Proven/provided required proofs: {report['summary']['proven_or_provided']}/{report['summary']['required_proofs']}",
        f"- Pending or blocked required proofs: {report['summary']['pending_or_blocked']}",
        "",
        "## Required Proofs",
        "",
        "| Proof | Status | Evidence | Required Action |",
        "|---|---|---|---|",
    ]
    for item in report["required_proofs"]:
        lines.append(
            f"| `{item['id']}` | {item['status']} | {item['evidence']} | {item['required_action'] or '-'} |"
        )
    lines.extend(["", "## Supporting Evidence", "", "| Evidence | Status | Boundary |", "|---|---|---|"])
    for item in report["supporting_evidence"]:
        lines.append(f"| `{item['label']}` | {item['status']} | {item['evidence_boundary']} |")
    if report["required_actions"]:
        lines.extend(["", "## Required Actions", ""])
        lines.extend(f"- {item}" for item in report["required_actions"])
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit external proofs for stark-finance-trading release completion.")
    parser.add_argument("--dist", default="dist")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--public-repo-url", default="")
    parser.add_argument("--github-run-url", default="")
    parser.add_argument("--live-eval-url", default="")
    parser.add_argument("--comparative-eval-url", default="")
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
        print(f"external proof audit: {report['external_proof_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
