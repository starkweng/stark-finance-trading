#!/usr/bin/env python3
"""Export stark-finance-trading as a standalone GitHub repository bundle."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path


FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
EXCLUDED_DIRS = {"__pycache__", "dist", ".git"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".skill", ".zip"}
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def should_copy(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDED_NAMES:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if len(rel.parts) >= 2 and rel.parts[0] == "evals" and rel.parts[1] == "artifacts":
        return False
    return True


def copy_tree(src: Path, dst: Path, *, skip_github: bool = False) -> int:
    count = 0
    for path in sorted(src.rglob("*")):
        if not path.is_file() or not should_copy(path, src):
            continue
        rel = path.relative_to(src)
        if skip_github and rel.parts and rel.parts[0] == ".github":
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    return count


def copy_release_artifacts(skill_name: str, release_dir: Path, out_dir: Path) -> list[str]:
    copied: list[str] = []
    if not release_dir.exists():
        return copied
    target_dir = out_dir / "dist"
    allowed_names = {f"{skill_name}.skill"}
    allowed_prefixes = (
        f"{skill_name}.release-",
        f"{skill_name}.live-eval-signoff",
        f"{skill_name}.loop-blueprint",
        f"{skill_name}.quality-suite",
        f"{skill_name}.github-actions-workflow",
        f"{skill_name}.public-benchmark",
        f"{skill_name}.public-tool-catalog",
        f"{skill_name}.tool-route-plan",
        f"{skill_name}.local-skill-inventory",
        f"{skill_name}.public-source-audit",
        f"{skill_name}.competitive-task-benchmark",
        f"{skill_name}.competitive-eval-signoff",
        f"{skill_name}.competitive-eval-review",
        f"{skill_name}.competitive-eval-scorecard",
        f"{skill_name}.live-eval-review",
        f"{skill_name}.live-eval-scorecard",
    )
    excluded_prefixes = (
        f"{skill_name}.release-readiness",
    )

    def copy_release_file(src: Path, dst: Path) -> None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in {".json", ".md", ".html"}:
            text = src.read_text(encoding="utf-8", errors="replace")
            repo_root = release_dir.resolve().parent
            sanitized = text.replace(str(repo_root) + "/", "").replace(str(repo_root), ".")
            dst.write_text(sanitized, encoding="utf-8")
            shutil.copystat(src, dst)
        else:
            shutil.copy2(src, dst)

    for path in sorted(release_dir.iterdir()):
        if path.name.startswith(excluded_prefixes):
            continue
        if path.is_dir():
            if not path.name.startswith(allowed_prefixes):
                continue
            for child in sorted(path.rglob("*")):
                if not child.is_file():
                    continue
                if child.name in EXCLUDED_NAMES or child.suffix in {".pyc", ".pyo", ".skill", ".zip"}:
                    continue
                target = target_dir / path.name / child.relative_to(path)
                copy_release_file(child, target)
                copied.append(target.relative_to(out_dir).as_posix())
            continue
        if path.name not in allowed_names and not path.name.startswith(allowed_prefixes):
            continue
        target = target_dir / path.name
        copy_release_file(path, target)
        copied.append(target.relative_to(out_dir).as_posix())
    return copied


def validate_export(skill_name: str, out_dir: Path) -> dict:
    required = [
        "README.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        ".gitignore",
        ".github/workflows/ci.yml",
        "PUBLICATION_STATUS.md",
        "workflow-templates/stark-finance-trading-ci.yml",
        f"{skill_name}/SKILL.md",
        f"{skill_name}/README.md",
        f"{skill_name}/BENCHMARK.md",
        f"{skill_name}/VALIDATION.md",
        f"{skill_name}/scripts/package_skill.py",
        f"{skill_name}/scripts/install_package_smoke.py",
        f"{skill_name}/scripts/enable_remote_ci.py",
        f"{skill_name}/scripts/run_quality_suite.py",
        f"{skill_name}/scripts/discover_local_skill_inventory.py",
        f"{skill_name}/scripts/plan_tool_route.py",
        f"{skill_name}/scripts/validate_public_tool_catalog.py",
        f"{skill_name}/scripts/audit_public_sources.py",
        f"{skill_name}/scripts/generate_competitive_task_benchmark.py",
        f"{skill_name}/scripts/generate_eval_review_bundle.py",
        f"{skill_name}/scripts/generate_public_benchmark.py",
        f"{skill_name}/scripts/generate_live_eval_signoff.py",
        f"{skill_name}/scripts/generate_release_manifest.py",
        f"{skill_name}/scripts/generate_release_notes.py",
        f"{skill_name}/scripts/validate_github_actions_workflow.py",
        f"{skill_name}/scripts/validate_release_readiness.py",
        f"{skill_name}/scripts/smoke_github_export.py",
        f"{skill_name}/scripts/score_eval_review_bundle.py",
        f"{skill_name}/scripts/codex_eval.py",
        f"{skill_name}/benchmarks/public-benchmark-cases.json",
        f"{skill_name}/benchmarks/competitive-task-cases.json",
        f"{skill_name}/evals/live-behavior-evals.json",
        f"{skill_name}/evals/tool-routing-cases.json",
    ]
    missing = [rel for rel in required if not (out_dir / rel).exists()]
    workflow_path = out_dir / ".github/workflows/ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8") if workflow_path.exists() else ""
    workflow_ok = (
        "working-directory: stark-finance-trading" in workflow_text
        and "scripts/run_quality_suite.py" in workflow_text
        and "generate_eval_review_bundle.py" in workflow_text
        and "stark-finance-trading.live-eval-scorecard.json" in workflow_text
        and "stark-finance-trading.competitive-eval-scorecard.json" in workflow_text
        and "stark-finance-trading.github-actions-workflow.json" in workflow_text
        and "stark-finance-trading.public-tool-catalog.json" in workflow_text
        and "stark-finance-trading.tool-route-plan.json" in workflow_text
        and "stark-finance-trading.local-skill-inventory.json" in workflow_text
        and "stark-finance-trading.github-export-smoke.json" in workflow_text
        and "stark-finance-trading.release-readiness.json" in workflow_text
        and "stark-finance-trading-github-repo.zip" in workflow_text
    )
    transient = []
    for path in out_dir.rglob("*"):
        if path.is_file() and (
            "__pycache__" in path.parts
            or path.suffix in {".pyc", ".pyo"}
            or path.name in EXCLUDED_NAMES
        ):
            transient.append(path.relative_to(out_dir).as_posix())
    package_path = out_dir / "dist" / f"{skill_name}.skill"
    package_ok = False
    entry_count = 0
    if package_path.exists():
        with zipfile.ZipFile(package_path) as archive:
            entry_count = len([info for info in archive.infolist() if not info.is_dir()])
            bad = archive.testzip()
            roots = {
                Path(info.filename).parts[0]
                for info in archive.infolist()
                if not info.is_dir() and Path(info.filename).parts
            }
            unsafe = [
                info.filename
                for info in archive.infolist()
                if Path(info.filename).is_absolute() or ".." in Path(info.filename).parts
            ]
            dirty = [
                info.filename
                for info in archive.infolist()
                if "__pycache__" in Path(info.filename).parts
                or info.filename.endswith((".pyc", ".pyo", ".DS_Store", ".skill"))
            ]
            package_ok = bad is None and roots == {skill_name} and not unsafe and not dirty
    checks = {
        "required_files": not missing,
        "github_actions_subdir_workflow": workflow_ok,
        "no_transient_files": not transient,
        "release_package_install_smoke": package_ok,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "missing_required_files": missing,
        "transient_files": transient,
        "release_package_entry_count": entry_count,
    }


def zip_dir(src: Path, zip_path: Path) -> dict:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    files = sorted([path for path in src.rglob("*") if path.is_file()], key=lambda path: path.relative_to(src).as_posix())
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            rel = path.relative_to(src)
            info = zipfile.ZipInfo(rel.as_posix(), date_time=FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.suffix == ".py" else 0o644) << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(zip_path) as archive:
        return {
            "path": str(zip_path.resolve()),
            "status": "PASS" if archive.testzip() is None else "FAIL",
            "entry_count": len([info for info in archive.infolist() if not info.is_dir()]),
        }


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# stark-finance-trading GitHub Export",
        "",
        f"- Status: {report['status']}",
        f"- Skill files copied: {report['skill_files_copied']}",
        f"- Release artifacts copied: {len(report['release_artifacts_copied'])}",
        f"- Validation: {report['validation']['status']}",
    ]
    if report.get("archive"):
        lines.append(f"- ZIP: `{report['archive']['path']}`")
    if report["validation"]["missing_required_files"]:
        lines.append("")
        lines.append("## Missing Required Files")
        lines.extend(f"- `{item}`" for item in report["validation"]["missing_required_files"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_root_readme(out_dir: Path, skill_name: str) -> None:
    lines = [
        f"# {skill_name}",
        "",
        "Standalone GitHub handoff for the Stark finance/trading router skill.",
        "",
        "## Source Layout",
        "",
        f"- `{skill_name}/` contains the installable skill source.",
        "- `.github/workflows/ci.yml` runs the portable quality suite from that subdirectory.",
        "- `dist/` contains release artifacts copied during export when available.",
        "",
        "## Quick Validation",
        "",
        "```bash",
        f"cd {skill_name}",
        "python3 scripts/run_quality_suite.py --json",
        "```",
        "",
        "## Evidence Boundary",
        "",
        "Local validation and package smoke do not prove remote GitHub Actions completion or live model behavior.",
    ]
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_root_gitignore(out_dir: Path, skill_name: str) -> None:
    lines = [
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
        ".env",
        ".env.*",
        f"{skill_name}/dist/",
        f"{skill_name}/evals/artifacts/",
        "",
        "# Root dist/ is intentionally committed as release evidence.",
    ]
    (out_dir / ".gitignore").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_workflow_template(out_dir: Path, skill_root: Path) -> None:
    src = skill_root / ".github" / "workflows" / "ci.yml"
    if not src.exists():
        return
    target = out_dir / "workflow-templates" / "stark-finance-trading-ci.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, target)


def write_publication_status(out_dir: Path, skill_name: str) -> None:
    lines = [
        "# Publication Status",
        "",
        "Current public repository:",
        "",
        "- Repo: https://github.com/starkweng/stark-finance-trading",
        "- Visibility: public after publication.",
        "- Main branch: `main`.",
        "- Published commit: see the latest `main` commit on GitHub.",
        "",
        "## Completed External Proofs",
        "",
        "- Public repository URL: provided after push.",
        "- Source package and release evidence: included in this export.",
        "- Local release readiness: generated by `scripts/validate_release_readiness.py`.",
        "",
        "## Pending External Proofs",
        "",
        "- Remote GitHub Actions run: pending until `.github/workflows/ci.yml` is pushed and completes.",
        "- Approved live model eval: pending.",
        "- Reviewed comparative live eval: pending.",
        "",
        "## CI Scope Note",
        "",
        "The CI workflow is available as `workflow-templates/stark-finance-trading-ci.yml`.",
        "",
        "If GitHub rejects workflow-file pushes, refresh GitHub CLI auth with the `workflow` scope, then enable CI:",
        "",
        "```bash",
        "gh auth refresh -h github.com -s workflow",
        f"python3 {skill_name}/scripts/enable_remote_ci.py --repo-root . --repo starkweng/stark-finance-trading --wait --out dist/{skill_name}.remote-ci-proof.json --markdown dist/{skill_name}.remote-ci-proof.md --json",
        "```",
        "",
        "## Evidence Boundary",
        "",
        "This repository proves public publication and local release evidence after push. It does not by itself prove remote GitHub Actions completion, live model behavior, market-data correctness, trading performance, or public superiority.",
    ]
    (out_dir / "PUBLICATION_STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-root", default=".")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--release-artifacts-dir")
    parser.add_argument("--zip")
    parser.add_argument("--report")
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_root = Path(args.skill_root).resolve()
    skill_name = skill_root.name
    out_dir = Path(args.out_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    skill_dst = out_dir / skill_name
    skill_files = copy_tree(skill_root, skill_dst, skip_github=True)
    if (skill_root / ".github").exists():
        copy_tree(skill_root / ".github", out_dir / ".github")

    for name in ["CONTRIBUTING.md", "SECURITY.md", ".gitignore", "LICENSE.txt"]:
        src = skill_root / name
        if src.exists():
            shutil.copy2(src, out_dir / name)
    write_root_readme(out_dir, skill_name)
    write_root_gitignore(out_dir, skill_name)
    write_workflow_template(out_dir, skill_root)
    write_publication_status(out_dir, skill_name)

    release_artifacts = []
    if args.release_artifacts_dir:
        release_artifacts = copy_release_artifacts(skill_name, Path(args.release_artifacts_dir), out_dir)

    validation = validate_export(skill_name, out_dir)
    report = {
        "schema_version": "1.0",
        "status": validation["status"],
        "export_root": str(out_dir),
        "skill_name": skill_name,
        "skill_files_copied": skill_files,
        "release_artifacts_copied": release_artifacts,
        "validation": validation,
        "archive": None,
        "evidence_boundary": "Local export validation only; does not prove remote GitHub Actions completion.",
    }
    if args.zip:
        report["archive"] = zip_dir(out_dir, Path(args.zip).resolve())
        if report["archive"]["status"] != "PASS":
            report["status"] = "FAIL"
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(Path(args.markdown), report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"GitHub export: {report['status']} {out_dir}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
