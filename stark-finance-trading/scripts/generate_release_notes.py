#!/usr/bin/env python3
"""Generate release notes from VERSION, CHANGELOG, manifest, and signoff evidence."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_version(skill_root: Path) -> str:
    version = (skill_root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER_RE.match(version):
        raise ValueError(f"VERSION must be semver-like, got: {version}")
    return version


def changelog_section(skill_root: Path, version: str) -> list[str]:
    lines = (skill_root / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    heading = f"## {version}"
    start: int | None = None
    for index, line in enumerate(lines):
        if line.startswith(heading):
            start = index + 1
            break
    if start is None:
        raise ValueError(f"CHANGELOG.md missing section for {version}")
    collected: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.strip():
            collected.append(line.rstrip())
    if not collected:
        raise ValueError(f"CHANGELOG.md section for {version} is empty")
    return collected


def build_notes(skill_root: Path, manifest_path: Path, live_signoff_path: Path | None) -> dict[str, Any]:
    version = read_version(skill_root)
    changes = changelog_section(skill_root, version)
    manifest = load_json(manifest_path)
    package = manifest.get("package", {}) if isinstance(manifest.get("package"), dict) else {}
    install = manifest.get("install_smoke", {}) if isinstance(manifest.get("install_smoke"), dict) else {}

    signoff_status = "NOT_PROVIDED"
    signoff_approval = "NOT_PROVIDED"
    signoff_command = ""
    if live_signoff_path and live_signoff_path.exists():
        signoff = load_json(live_signoff_path)
        signoff_status = str(signoff.get("status", "UNKNOWN"))
        approval = signoff.get("approval", {}) if isinstance(signoff.get("approval"), dict) else {}
        signoff_approval = str(approval.get("status", signoff.get("approval_status", "UNKNOWN")))
        signoff_command = str(approval.get("exact_command_to_approve", ""))

    status = "PASS"
    failure_reasons: list[str] = []
    if manifest.get("status") != "PASS":
        status = "FAIL"
        failure_reasons.append("release manifest is not PASS")
    if install.get("status") != "PASS":
        status = "FAIL"
        failure_reasons.append("install smoke is not PASS")
    if signoff_status not in {"PASS", "NOT_PROVIDED"}:
        status = "FAIL"
        failure_reasons.append("live eval signoff packet is not PASS")

    return {
        "schema_version": "1.0",
        "status": status,
        "failure_reasons": failure_reasons,
        "version": version,
        "release_date": date.today().isoformat(),
        "package": {
            "name": package.get("name"),
            "sha256": package.get("sha256"),
            "size_bytes": package.get("size_bytes"),
            "entry_count": package.get("entry_count"),
        },
        "install_smoke": install,
        "live_eval_signoff": {
            "status": signoff_status,
            "approval_status": signoff_approval,
            "exact_command": signoff_command,
        },
        "changes": changes,
        "evidence_boundary": [
            "Release notes are generated from the current local manifest, changelog, and signoff evidence.",
            "They do not prove remote GitHub Actions completion.",
            "They do not prove live model behavior, market-data accuracy, trading performance, or public superiority.",
        ],
    }


def write_markdown(path: Path, notes: dict[str, Any]) -> None:
    package = notes["package"]
    install = notes["install_smoke"]
    signoff = notes["live_eval_signoff"]
    lines = [
        f"# stark-finance-trading v{notes['version']} Release Notes",
        "",
        f"- Status: {notes['status']}",
        f"- Release date: {notes['release_date']}",
        f"- Package: `{package.get('name')}`",
        f"- SHA256: `{package.get('sha256')}`",
        f"- Entry count: {package.get('entry_count')}",
        f"- Install smoke: {install.get('status')}",
        f"- Live eval signoff: {signoff.get('status')} / approval {signoff.get('approval_status')}",
        "",
        "## Changes",
        "",
    ]
    lines.extend(str(item) for item in notes.get("changes", []))
    lines.extend(["", "## Evidence Boundary", ""])
    lines.extend(f"- {item}" for item in notes.get("evidence_boundary", []))
    if signoff.get("exact_command"):
        lines.extend(["", "## Live Eval Command Requiring Approval", "", "```bash", signoff["exact_command"], "```"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate release notes sidecars.")
    parser.add_argument("--skill-root", type=Path, default=Path("."))
    parser.add_argument("--release-manifest", type=Path, required=True)
    parser.add_argument("--live-signoff", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    notes = build_notes(args.skill_root.resolve(), args.release_manifest.resolve(), args.live_signoff.resolve() if args.live_signoff else None)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(notes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(args.markdown, notes)
    if args.json:
        print(json.dumps(notes, indent=2, ensure_ascii=False))
    else:
        print(f"release notes: {notes['status']} {args.markdown}")
    return 0 if notes["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
