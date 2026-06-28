#!/usr/bin/env python3
"""Package stark-finance-trading into a deterministic .skill archive."""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path


FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
EXCLUDED_DIRS = {"__pycache__", "dist", ".git", ".github"}
EXCLUDED_FILE_NAMES = {".DS_Store", ".gitignore"}
EXCLUDED_SUFFIXES = {".pyc", ".skill"}


def validate_skill(root: Path) -> None:
    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        raise SystemExit("SKILL.md not found")
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit("SKILL.md missing frontmatter")
    match = re.search(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        raise SystemExit("invalid frontmatter")
    frontmatter = match.group(1)
    if "name: stark-finance-trading" not in frontmatter:
        raise SystemExit("frontmatter name must be stark-finance-trading")
    if "description:" not in frontmatter:
        raise SystemExit("frontmatter description missing")


def should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDED_FILE_NAMES:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if len(rel.parts) >= 2 and rel.parts[0] == "evals" and rel.parts[1] == "artifacts":
        return False
    return True


def mode_for(path: Path) -> int:
    if path.suffix == ".py":
        return 0o755
    return 0o644


def package(root: Path, output_dir: Path) -> Path:
    root = root.resolve()
    output_dir = output_dir.resolve()
    validate_skill(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    package_path = output_dir / f"{root.name}.skill"

    files = sorted(
        [path for path in root.rglob("*") if path.is_file() and should_include(path, root)],
        key=lambda path: path.relative_to(root).as_posix(),
    )
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            arcname = path.relative_to(root.parent)
            info = zipfile.ZipInfo(arcname.as_posix(), date_time=FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = mode_for(path) << 16
            archive.writestr(info, path.read_bytes())
    return package_path


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: package_skill.py <skill-root> [output-dir]", file=sys.stderr)
        return 1
    root = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    package_path = package(root, output_dir)
    print(package_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
