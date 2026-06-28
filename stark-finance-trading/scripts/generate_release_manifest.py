#!/usr/bin/env python3
"""Generate release manifest sidecars for a stark-finance-trading package."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from install_package_smoke import smoke


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def entry_manifest(package_path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with zipfile.ZipFile(package_path) as archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            with archive.open(info) as handle:
                content = handle.read()
            entries.append(
                {
                    "path": info.filename,
                    "size": info.file_size,
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
    return entries


def build_manifest(package_path: Path, skill_root: Path | None = None) -> dict[str, Any]:
    package_path = package_path.resolve()
    install_smoke = smoke(package_path)
    entries = entry_manifest(package_path)
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package": {
            "path": str(package_path),
            "name": package_path.name,
            "size_bytes": package_path.stat().st_size,
            "sha256": sha256_file(package_path),
            "entry_count": len(entries),
        },
        "install_smoke": {
            "status": install_smoke.get("status"),
            "checks": install_smoke.get("checks", {}),
            "entry_count": install_smoke.get("entry_count"),
        },
        "entries": entries,
        "evidence_boundary": "Local package manifest and install-smoke evidence only; does not prove live model behavior, remote GitHub Actions, market-data accuracy, or trading performance.",
    }
    if skill_root is not None:
        manifest["source"] = {"skill_root": str(skill_root.resolve())}
    manifest["status"] = "PASS" if install_smoke.get("status") == "PASS" else "FAIL"
    return manifest


def write_markdown(path: Path, manifest: dict[str, Any]) -> None:
    package = manifest["package"]
    install = manifest["install_smoke"]
    lines = [
        "# stark-finance-trading Release Manifest",
        "",
        f"- Status: {manifest.get('status')}",
        f"- Package: `{package.get('name')}`",
        f"- Size bytes: {package.get('size_bytes')}",
        f"- SHA256: `{package.get('sha256')}`",
        f"- Entry count: {package.get('entry_count')}",
        f"- Install smoke: {install.get('status')}",
        "",
        "## Install Smoke Checks",
        "",
    ]
    for name, value in install.get("checks", {}).items():
        lines.append(f"- {name}: {'PASS' if value else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            manifest["evidence_boundary"],
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate package release manifest sidecars.")
    parser.add_argument("package_path", type=Path)
    parser.add_argument("--skill-root", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    manifest = build_manifest(args.package_path, args.skill_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(args.markdown, manifest)
    if args.json:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    else:
        print(f"release manifest: {manifest['status']} {args.out}")
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
