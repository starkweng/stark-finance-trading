#!/usr/bin/env python3
"""Small dependency-free SKILL.md frontmatter validator."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}


def parse_frontmatter(text: str) -> dict:
    data = {}
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line[:1].isspace():
            continue
        if ":" not in raw_line:
            raise ValueError(f"Invalid frontmatter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value and value[0] in {"'", '"'}:
            try:
                data[key] = ast.literal_eval(value)
            except (SyntaxError, ValueError) as exc:
                raise ValueError(f"Invalid quoted value for {key}: {exc}") from exc
        else:
            data[key] = value or {}
    return data


def validate(path: Path) -> tuple[bool, str]:
    if path.is_file():
        skill_md = path
    else:
        skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"
    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.S)
    if not match:
        return False, "Invalid or missing frontmatter"
    try:
        frontmatter = parse_frontmatter(match.group(1))
    except ValueError as exc:
        return False, f"Invalid frontmatter: {exc}"
    unexpected = set(frontmatter) - ALLOWED_PROPERTIES
    if unexpected:
        return False, f"Unexpected frontmatter keys: {', '.join(sorted(unexpected))}"
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        return False, "name must be hyphen-case"
    if not isinstance(description, str) or not description.strip():
        return False, "description missing"
    if len(description) > 1024:
        return False, "description exceeds 1024 characters"
    return True, "Skill is valid!"


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    ok, message = validate(target)
    print(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
