#!/usr/bin/env python3
"""Smoke-test the standalone GitHub repository export ZIP."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXCLUDED_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
SKILL_NAME = "stark-finance-trading"

REQUIRED_EXPORT_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".gitignore",
    ".github/workflows/ci.yml",
    "PUBLICATION_STATUS.md",
    "workflow-templates/stark-finance-trading-ci.yml",
    f"{SKILL_NAME}/SKILL.md",
    f"{SKILL_NAME}/README.md",
    f"{SKILL_NAME}/BENCHMARK.md",
    f"{SKILL_NAME}/VALIDATION.md",
    f"{SKILL_NAME}/scripts/quick_validate.py",
    f"{SKILL_NAME}/scripts/validate_stark_finance_trading.py",
    f"{SKILL_NAME}/scripts/validate_public_readiness.py",
    f"{SKILL_NAME}/scripts/validate_github_actions_workflow.py",
    f"{SKILL_NAME}/scripts/validate_release_readiness.py",
    f"{SKILL_NAME}/scripts/audit_external_proofs.py",
    f"{SKILL_NAME}/scripts/enable_remote_ci.py",
    f"{SKILL_NAME}/scripts/install_package_smoke.py",
    f"{SKILL_NAME}/scripts/smoke_github_export.py",
    f"{SKILL_NAME}/scripts/score_eval_review_bundle.py",
    "dist/stark-finance-trading.skill",
    "dist/stark-finance-trading.release-manifest.json",
    "dist/stark-finance-trading.release-notes.json",
    "dist/stark-finance-trading.github-actions-workflow.json",
    "dist/stark-finance-trading.live-eval-scorecard.json",
    "dist/stark-finance-trading.competitive-eval-scorecard.json",
    "dist/stark-finance-trading.external-proof-audit.json",
]


def safe_member(name: str) -> bool:
    path = Path(name)
    return not path.is_absolute() and ".." not in path.parts and name.strip() == name


def sanitize_output(text: str, export_root: Path) -> str:
    replacements = [
        (str(export_root), "<export-root>"),
        (str(export_root.parent), "<tmp-parent>"),
    ]
    sanitized = text
    for old, new in replacements:
        sanitized = sanitized.replace(old, new)
    return sanitized[-3000:]


def run_command(name: str, cmd: list[str], cwd: Path, export_root: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)
    return {
        "name": name,
        "command": " ".join(cmd),
        "cwd": str(cwd.relative_to(export_root)) if cwd != export_root else ".",
        "returncode": proc.returncode,
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "stdout_tail": sanitize_output(proc.stdout, export_root),
        "stderr_tail": sanitize_output(proc.stderr, export_root),
    }


def find_transient_files(export_root: Path) -> list[str]:
    transient: list[str] = []
    for path in sorted(export_root.rglob("*")):
        if not path.is_file():
            continue
        if (
            "__pycache__" in path.parts
            or path.suffix in {".pyc", ".pyo"}
            or path.name in EXCLUDED_NAMES
        ):
            transient.append(path.relative_to(export_root).as_posix())
    return transient


def smoke(zip_path: Path, py: str | None = None) -> dict[str, Any]:
    py = py or sys.executable or "python3"
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "zip": str(zip_path.resolve()),
        "status": "FAIL",
        "checks": {},
        "commands": [],
        "missing_required_files": [],
        "transient_files": [],
        "entry_count": 0,
        "evidence_boundary": (
            "Local smoke test of the exported GitHub repository ZIP only. "
            "It proves the archive can be extracted and core gates can run from the standalone layout. "
            "It does not prove remote GitHub Actions completion, uploaded artifact availability, "
            "live market-data correctness, live trading performance, or live model behavior."
        ),
    }

    if not zip_path.exists():
        report["error"] = "export zip is missing"
        return report

    with tempfile.TemporaryDirectory(prefix="stark-finance-github-export-") as tmp:
        tmp_root = Path(tmp)
        export_root = tmp_root / "repo"
        export_root.mkdir()

        try:
            with zipfile.ZipFile(zip_path) as archive:
                bad = archive.testzip()
                names = [info.filename for info in archive.infolist() if not info.is_dir()]
                report["entry_count"] = len(names)
                report["checks"]["zip_integrity"] = bad is None
                report["checks"]["safe_paths"] = all(safe_member(name) for name in names)
                if report["checks"]["safe_paths"]:
                    archive.extractall(export_root)
        except Exception as exc:  # pragma: no cover - CLI diagnostic path
            report["error"] = str(exc)
            return report

        if not report["checks"].get("safe_paths"):
            report["error"] = "archive contains unsafe paths"
            return report

        missing = [rel for rel in REQUIRED_EXPORT_FILES if not (export_root / rel).exists()]
        transient = find_transient_files(export_root)
        report["missing_required_files"] = missing
        report["transient_files"] = transient
        report["checks"]["required_files"] = not missing
        report["checks"]["no_transient_files"] = not transient

        skill_root = export_root / SKILL_NAME
        commands = [
            (
                "quick_validate_exported_skill",
                [py, "scripts/quick_validate.py", "."],
                skill_root,
            ),
            (
                "validate_exported_skill",
                [py, "scripts/validate_stark_finance_trading.py", "."],
                skill_root,
            ),
            (
                "validate_exported_public_readiness",
                [py, "scripts/validate_public_readiness.py", "."],
                skill_root,
            ),
            (
                "validate_exported_workflow",
                [py, f"{SKILL_NAME}/scripts/validate_github_actions_workflow.py", "--root", ".", "--json"],
                export_root,
            ),
            (
                "install_smoke_exported_package",
                [py, f"{SKILL_NAME}/scripts/install_package_smoke.py", "dist/stark-finance-trading.skill", "--json"],
                export_root,
            ),
        ]
        if not missing:
            report["commands"] = [run_command(name, cmd, cwd, export_root) for name, cmd, cwd in commands]
        else:
            report["commands"] = []

        report["checks"]["exported_core_commands"] = bool(report["commands"]) and all(
            item["status"] == "PASS" for item in report["commands"]
        )
        report["status"] = "PASS" if all(report["checks"].values()) else "FAIL"
    return report


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# GitHub Export Smoke Test",
        "",
        f"- Status: {report['status']}",
        f"- ZIP: `{report['zip']}`",
        f"- Archive entries: {report['entry_count']}",
        "",
        "## Checks",
        "",
        "| Check | Status |",
        "|---|---|",
    ]
    for name, passed in report.get("checks", {}).items():
        lines.append(f"| `{name}` | {'PASS' if passed else 'FAIL'} |")
    if report.get("commands"):
        lines.extend(["", "## Command Smoke", "", "| Command | Status |", "|---|---|"])
        for item in report["commands"]:
            lines.append(f"| `{item['name']}` | {item['status']} |")
    if report.get("missing_required_files"):
        lines.extend(["", "## Missing Required Files", ""])
        lines.extend(f"- `{item}`" for item in report["missing_required_files"])
    if report.get("transient_files"):
        lines.extend(["", "## Transient Files", ""])
        lines.extend(f"- `{item}`" for item in report["transient_files"])
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test a standalone GitHub export ZIP.")
    parser.add_argument("--zip", required=True, help="Path to stark-finance-trading-github-repo.zip")
    parser.add_argument("--out", help="Write JSON report to this path.")
    parser.add_argument("--markdown", help="Write Markdown report to this path.")
    parser.add_argument("--python", help="Python executable to use for smoke commands.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = smoke(Path(args.zip), py=args.python)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(Path(args.markdown), report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"github export smoke: {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
