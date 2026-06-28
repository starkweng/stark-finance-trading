#!/usr/bin/env python3
"""Smoke-test a packaged stark-finance-trading .skill archive."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk_[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*=\s*['\"][^'\"]{12,}['\"]"),
]


def is_safe_name(name: str) -> bool:
    path = Path(name)
    return not path.is_absolute() and ".." not in path.parts and name.strip() == name


def scan_text(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return True
    return not any(pattern.search(text) for pattern in SECRET_PATTERNS)


def smoke(package_path: Path) -> dict:
    report = {
        "package": str(package_path.resolve()),
        "status": "FAIL",
        "checks": {},
        "entry_count": 0,
    }
    try:
        with zipfile.ZipFile(package_path) as archive:
            bad = archive.testzip()
            names = [info.filename for info in archive.infolist() if not info.is_dir()]
            report["entry_count"] = len(names)
            safe_paths = all(is_safe_name(name) for name in names)
            clean = not any("__pycache__" in Path(name).parts or name.endswith((".pyc", ".DS_Store", ".skill")) for name in names)
            roots = {Path(name).parts[0] for name in names if Path(name).parts}
            single_root = roots == {"stark-finance-trading"}
            report["checks"].update({
                "zip_integrity": bad is None,
                "safe_paths": safe_paths,
                "archive_clean": clean,
                "single_skill_root": single_root,
            })
            with tempfile.TemporaryDirectory(prefix="stark-finance-trading-smoke-") as tmp:
                archive.extractall(tmp)
                root = Path(tmp) / "stark-finance-trading"
                skill_md = root / "SKILL.md"
                text = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
                quick_validate = "name: stark-finance-trading" in text and "description:" in text
                no_secrets = all(scan_text(path) for path in root.rglob("*") if path.is_file())
                report["checks"].update({
                    "skill_md": skill_md.exists(),
                    "quick_validate": quick_validate,
                    "security_scan": no_secrets,
                })
    except Exception as exc:  # pragma: no cover - CLI diagnostic path
        report["error"] = str(exc)

    report["status"] = "PASS" if report["checks"] and all(report["checks"].values()) else "FAIL"
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package_path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = smoke(Path(args.package_path))
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"install package smoke: {report['status']}")
        for name, ok in report.get("checks", {}).items():
            print(f"{name}: {'PASS' if ok else 'FAIL'}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
