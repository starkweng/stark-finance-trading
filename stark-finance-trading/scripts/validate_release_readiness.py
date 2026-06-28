#!/usr/bin/env python3
"""Generate a local release-readiness report for stark-finance-trading."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_NAME = "stark-finance-trading"

REQUIRED_SOURCE_FILES = [
    "SKILL.md",
    "README.md",
    "BENCHMARK.md",
    "VALIDATION.md",
    "CHANGELOG.md",
    "VERSION",
    "LICENSE.txt",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".github/workflows/ci.yml",
    "references/tool-router.md",
    "references/local-skill-router.md",
    "references/safety-policy.md",
    "references/workflows.md",
    "references/source-ledger.md",
    "references/public-tool-catalog.json",
    "references/quality-gates-2026-06-24.md",
    "evals/routing-evals.json",
    "evals/adversarial-evals.json",
    "evals/live-behavior-evals.json",
    "evals/tool-routing-cases.json",
    "benchmarks/public-comparison-2026-06-28.json",
    "benchmarks/public-benchmark-cases.json",
    "benchmarks/competitive-task-cases.json",
    "scripts/run_quality_suite.py",
    "scripts/live_eval_runner_fixture.py",
    "scripts/run_live_eval_harness_smoke.py",
    "scripts/discover_local_skill_inventory.py",
    "scripts/plan_tool_route.py",
    "scripts/runtime_capability_scan.py",
    "scripts/validate_public_tool_catalog.py",
    "scripts/package_skill.py",
    "scripts/install_package_smoke.py",
    "scripts/enable_remote_ci.py",
    "scripts/export_github_repo.py",
    "scripts/smoke_github_export.py",
    "scripts/score_eval_review_bundle.py",
    "scripts/validate_release_readiness.py",
    "workflow-templates/stark-finance-trading-ci.yml",
]

REQUIRED_ARTIFACTS = [
    "stark-finance-trading.skill",
    "stark-finance-trading.release-manifest.json",
    "stark-finance-trading.release-notes.json",
    "stark-finance-trading.github-actions-workflow.json",
    "stark-finance-trading.public-source-audit.json",
    "stark-finance-trading.public-benchmark.json",
    "stark-finance-trading.public-tool-catalog.json",
    "stark-finance-trading.runtime-capabilities.json",
    "stark-finance-trading.tool-route-plan.json",
    "stark-finance-trading.local-skill-inventory.json",
    "stark-finance-trading.competitive-task-benchmark.json",
    "stark-finance-trading.live-eval-signoff.json",
    "stark-finance-trading.live-eval-harness-smoke.json",
    "stark-finance-trading.live-eval-review/review.json",
    "stark-finance-trading.live-eval-scorecard.json",
    "stark-finance-trading.competitive-eval-signoff.json",
    "stark-finance-trading.competitive-eval-harness-smoke.json",
    "stark-finance-trading.competitive-eval-review/review.json",
    "stark-finance-trading.competitive-eval-scorecard.json",
    "stark-finance-trading.github-export-report.json",
    "stark-finance-trading.github-export-smoke.json",
    "stark-finance-trading-github-repo.zip",
]

STATUS_ARTIFACTS = [
    "stark-finance-trading.release-manifest.json",
    "stark-finance-trading.release-notes.json",
    "stark-finance-trading.github-actions-workflow.json",
    "stark-finance-trading.public-source-audit.json",
    "stark-finance-trading.public-benchmark.json",
    "stark-finance-trading.public-tool-catalog.json",
    "stark-finance-trading.runtime-capabilities.json",
    "stark-finance-trading.tool-route-plan.json",
    "stark-finance-trading.local-skill-inventory.json",
    "stark-finance-trading.competitive-task-benchmark.json",
    "stark-finance-trading.live-eval-signoff.json",
    "stark-finance-trading.live-eval-harness-smoke.json",
    "stark-finance-trading.live-eval-review/review.json",
    "stark-finance-trading.live-eval-scorecard.json",
    "stark-finance-trading.competitive-eval-signoff.json",
    "stark-finance-trading.competitive-eval-harness-smoke.json",
    "stark-finance-trading.competitive-eval-review/review.json",
    "stark-finance-trading.competitive-eval-scorecard.json",
    "stark-finance-trading.github-export-report.json",
    "stark-finance-trading.github-export-smoke.json",
]

PACKAGE_SOURCE_EXCLUDES = {
    ".github/workflows/ci.yml",
}

FORBIDDEN_PUBLIC_CLAIMS = [
    re.compile(r"best on GitHub", re.I),
    re.compile(r"最牛"),
    re.compile(r"最强"),
    re.compile(r"打败所有竞品"),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_zip(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "FAIL", "entry_count": 0, "safe_paths": False, "archive_clean": False}
    with zipfile.ZipFile(path) as archive:
        names = [info.filename for info in archive.infolist() if not info.is_dir()]
        bad = archive.testzip()
        safe_paths = all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in names)
        clean = not any(
            "__pycache__" in Path(name).parts
            or name.endswith((".pyc", ".pyo", ".DS_Store"))
            for name in names
        )
    return {
        "status": "PASS" if bad is None and safe_paths and clean else "FAIL",
        "entry_count": len(names),
        "safe_paths": safe_paths,
        "archive_clean": clean,
    }


def check_package_source_freshness(package_path: Path, root: Path) -> dict[str, Any]:
    if not package_path.exists():
        return {
            "status": "FAIL",
            "checked_count": 0,
            "missing_required_package_files": REQUIRED_SOURCE_FILES,
            "hash_mismatches": [],
        }
    with zipfile.ZipFile(package_path) as archive:
        entries = {
            info.filename: archive.read(info.filename)
            for info in archive.infolist()
            if not info.is_dir()
        }

    checked_count = 0
    missing: list[str] = []
    mismatches: list[str] = []
    for rel in REQUIRED_SOURCE_FILES:
        if rel in PACKAGE_SOURCE_EXCLUDES:
            continue
        source_path = root / rel
        if not source_path.exists():
            continue
        entry_name = f"{SKILL_NAME}/{rel}"
        content = entries.get(entry_name)
        if content is None:
            missing.append(rel)
            continue
        checked_count += 1
        source_hash = sha256_file(source_path)
        entry_hash = hashlib.sha256(content).hexdigest()
        if source_hash != entry_hash:
            mismatches.append(rel)

    return {
        "status": "PASS" if not missing and not mismatches else "FAIL",
        "checked_count": checked_count,
        "missing_required_package_files": missing,
        "hash_mismatches": mismatches,
    }


def check_public_claims(root: Path) -> dict[str, Any]:
    files = [
        root / "README.md",
        root / "BENCHMARK.md",
        root / "benchmarks" / "PUBLIC_COMPARISON_2026-06-28.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in files if path.exists())
    sanitized = text.replace("Avoid public superiority claims", "")
    matches = []
    for pattern in FORBIDDEN_PUBLIC_CLAIMS:
        if pattern.search(sanitized):
            matches.append(pattern.pattern)
    return {
        "status": "PASS" if not matches else "FAIL",
        "matches": matches,
    }


def external_proof_status(args: argparse.Namespace) -> list[dict[str, Any]]:
    items = [
        ("public_repo_url", args.public_repo_url),
        ("remote_github_actions_run_url", args.github_run_url),
        ("approved_live_model_eval", args.live_eval_url),
        ("reviewed_comparative_live_eval", args.comparative_eval_url),
    ]
    return [
        {
            "id": name,
            "status": "PROVIDED" if value else "PENDING",
            "value": value or "",
            "required_for_goal_completion": True,
        }
        for name, value in items
    ]


def validate(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.skill_root).resolve()
    dist = Path(args.dist).resolve()

    source_missing = [rel for rel in REQUIRED_SOURCE_FILES if not (root / rel).exists()]
    artifact_missing = [rel for rel in REQUIRED_ARTIFACTS if not (dist / rel).exists()]

    artifact_statuses: dict[str, Any] = {}
    for rel in STATUS_ARTIFACTS:
        path = dist / rel
        if not path.exists():
            artifact_statuses[rel] = {"status": "MISSING"}
            continue
        data = read_json(path)
        artifact_statuses[rel] = {
            "status": data.get("status"),
            "score": data.get("score"),
            "behavior_proof_status": data.get("behavior_proof_status"),
            "evidence_boundary": data.get("evidence_boundary"),
        }

    status_artifacts_pass = all(item.get("status") == "PASS" for item in artifact_statuses.values())

    package_path = dist / f"{SKILL_NAME}.skill"
    package_sha = sha256_file(package_path) if package_path.exists() else ""
    release_manifest = read_json(dist / f"{SKILL_NAME}.release-manifest.json") if (dist / f"{SKILL_NAME}.release-manifest.json").exists() else {}
    manifest_sha = ((release_manifest.get("package") or {}).get("sha256") or "")
    package_hash_match = bool(package_sha and manifest_sha and package_sha == manifest_sha)
    package_zip = check_zip(package_path)
    package_source = check_package_source_freshness(package_path, root)

    github_zip_path = dist / f"{SKILL_NAME}-github-repo.zip"
    github_zip = check_zip(github_zip_path)
    public_claims = check_public_claims(root)

    external = external_proof_status(args)
    pending_external = [item for item in external if item["status"] == "PENDING"]

    local_checks = [
        ("source_files_present", not source_missing),
        ("release_artifacts_present", not artifact_missing),
        ("status_artifacts_pass", status_artifacts_pass),
        ("package_hash_matches_manifest", package_hash_match),
        ("package_zip_clean", package_zip["status"] == "PASS"),
        ("package_contains_current_required_sources", package_source["status"] == "PASS"),
        ("github_export_zip_clean", github_zip["status"] == "PASS"),
        ("public_claim_boundary", public_claims["status"] == "PASS"),
    ]
    status = "PASS" if all(passed for _, passed in local_checks) else "FAIL"
    return {
        "schema_version": "1.0",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill": SKILL_NAME,
        "skill_root": str(root),
        "dist": str(dist),
        "local_release_status": "LOCAL_RELEASE_READY" if status == "PASS" else "LOCAL_RELEASE_NOT_READY",
        "goal_completion_status": "NOT_COMPLETE_EXTERNAL_PROOFS_PENDING" if pending_external else "READY_FOR_COMPLETION_AUDIT",
        "checks": [
            {"id": name, "passed": passed}
            for name, passed in local_checks
        ],
        "source_missing": source_missing,
        "artifact_missing": artifact_missing,
        "artifact_statuses": artifact_statuses,
        "package": {
            "path": str(package_path),
            "sha256": package_sha,
            "manifest_sha256": manifest_sha,
            "hash_match": package_hash_match,
            "zip": package_zip,
            "source_freshness": package_source,
        },
        "github_export_zip": {
            "path": str(github_zip_path),
            "sha256": sha256_file(github_zip_path) if github_zip_path.exists() else "",
            "zip": github_zip,
        },
        "public_claims": public_claims,
        "external_proofs": external,
        "evidence_boundary": (
            "Local release-readiness validation only. PASS means the local package, release artifacts, "
            "GitHub export ZIP, review scorecards, and public-claim boundaries are internally consistent. "
            "It does not prove remote GitHub Actions completion, public repository publication, live model behavior, "
            "market-data correctness, trading performance, or public superiority."
        ),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Release Readiness",
        "",
        f"- Status: {report['status']}",
        f"- Local release status: `{report['local_release_status']}`",
        f"- Goal completion status: `{report['goal_completion_status']}`",
        f"- Package SHA256: `{report['package']['sha256']}`",
        f"- GitHub ZIP SHA256: `{report['github_export_zip']['sha256']}`",
        "",
        "## Local Checks",
        "",
        "| Check | Status |",
        "|---|---|",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['id']}` | {'PASS' if check['passed'] else 'FAIL'} |")
    lines.extend(["", "## External Proofs", "", "| Proof | Status | Required For Goal Completion |", "|---|---|---|"])
    for item in report["external_proofs"]:
        lines.append(f"| `{item['id']}` | {item['status']} | {item['required_for_goal_completion']} |")
    if report["source_missing"]:
        lines.extend(["", "## Missing Source Files", ""])
        lines.extend(f"- `{item}`" for item in report["source_missing"])
    if report["artifact_missing"]:
        lines.extend(["", "## Missing Release Artifacts", ""])
        lines.extend(f"- `{item}`" for item in report["artifact_missing"])
    freshness = report["package"]["source_freshness"]
    if freshness["missing_required_package_files"]:
        lines.extend(["", "## Missing Package Source Files", ""])
        lines.extend(f"- `{item}`" for item in freshness["missing_required_package_files"])
    if freshness["hash_mismatches"]:
        lines.extend(["", "## Package Source Hash Mismatches", ""])
        lines.extend(f"- `{item}`" for item in freshness["hash_mismatches"])
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate local release readiness for stark-finance-trading.")
    parser.add_argument("--skill-root", default=".")
    parser.add_argument("--dist", default="dist")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--public-repo-url", default="")
    parser.add_argument("--github-run-url", default="")
    parser.add_argument("--live-eval-url", default="")
    parser.add_argument("--comparative-eval-url", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate(args)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(Path(args.markdown), report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"release readiness: {report['status']} {report['local_release_status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
