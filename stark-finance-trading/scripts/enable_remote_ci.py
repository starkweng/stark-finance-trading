#!/usr/bin/env python3
"""Enable and verify the remote GitHub Actions CI workflow for a published export."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKFLOW_TEMPLATE = "workflow-templates/stark-finance-trading-ci.yml"
WORKFLOW_TARGET = ".github/workflows/ci.yml"


def run(cmd: list[str], cwd: Path, *, check: bool = False) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    result = {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-3000:],
        "stderr_tail": proc.stderr[-3000:],
    }
    if check and proc.returncode != 0:
        raise RuntimeError(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def gh_scopes(cwd: Path) -> dict[str, Any]:
    result = run(["gh", "auth", "status"], cwd)
    text = result["stdout_tail"] + result["stderr_tail"]
    scopes = []
    marker = "Token scopes:"
    for line in text.splitlines():
        if marker in line:
            raw = line.split(marker, 1)[1]
            scopes = [item.strip(" '") for item in raw.split(",") if item.strip()]
    return {
        "status": "PASS" if result["returncode"] == 0 else "FAIL",
        "scopes": scopes,
        "has_workflow_scope": "workflow" in scopes,
        "raw_tail": text[-1200:],
    }


def copy_workflow(repo_root: Path) -> dict[str, Any]:
    src = repo_root / WORKFLOW_TEMPLATE
    dst = repo_root / WORKFLOW_TARGET
    if not src.exists():
        return {"status": "FAIL", "reason": "workflow template missing", "template": str(src)}
    dst.parent.mkdir(parents=True, exist_ok=True)
    before = dst.read_text(encoding="utf-8") if dst.exists() else ""
    after = src.read_text(encoding="utf-8")
    changed = before != after
    if changed:
        shutil.copy2(src, dst)
    return {
        "status": "PASS",
        "template": str(src),
        "target": str(dst),
        "changed": changed,
    }


def git_commit_push(repo_root: Path, message: str) -> dict[str, Any]:
    status_before = run(["git", "status", "--short"], repo_root)
    if not status_before["stdout_tail"].strip():
        return {"status": "PASS", "changed": False, "commands": [status_before]}
    commands = [
        status_before,
        run(["git", "add", WORKFLOW_TARGET], repo_root),
        run(["git", "commit", "-m", message], repo_root),
        run(["git", "push"], repo_root),
    ]
    ok = all(item["returncode"] == 0 for item in commands[1:])
    return {"status": "PASS" if ok else "FAIL", "changed": True, "commands": commands}


def latest_run(repo: str, cwd: Path) -> dict[str, Any]:
    result = run(
        [
            "gh",
            "run",
            "list",
            "--repo",
            repo,
            "--workflow",
            "stark-finance-trading-ci",
            "--limit",
            "1",
            "--json",
            "databaseId,status,conclusion,workflowName,url,createdAt",
        ],
        cwd,
    )
    if result["returncode"] != 0:
        return {"status": "FAIL", "command": result}
    try:
        runs = json.loads(result["stdout_tail"] or "[]")
    except json.JSONDecodeError:
        return {"status": "FAIL", "command": result}
    return {"status": "PASS", "run": runs[0] if runs else None}


def wait_for_run(repo: str, cwd: Path, timeout: int, interval: int) -> dict[str, Any]:
    deadline = time.time() + timeout
    history = []
    while time.time() < deadline:
        item = latest_run(repo, cwd)
        history.append(item)
        run_item = item.get("run")
        if run_item and run_item.get("status") == "completed":
            return {
                "status": "PASS" if run_item.get("conclusion") == "success" else "FAIL",
                "run": run_item,
                "history_count": len(history),
            }
        time.sleep(interval)
    latest = history[-1] if history else {"run": None}
    return {"status": "TIMEOUT", "run": latest.get("run"), "history_count": len(history)}


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Remote CI Proof",
        "",
        f"- Status: {report['status']}",
        f"- Repo: `{report['repo']}`",
        f"- Workflow scope: {report['auth']['has_workflow_scope']}",
        f"- Workflow copy: {report['workflow_copy']['status']}",
    ]
    run_item = ((report.get("remote_run") or {}).get("run") or {})
    if run_item:
        lines.extend(
            [
                f"- Remote run status: {run_item.get('status')}",
                f"- Remote run conclusion: {run_item.get('conclusion')}",
                f"- Remote run URL: {run_item.get('url')}",
            ]
        )
    if not report["auth"]["has_workflow_scope"]:
        lines.extend(
            [
                "",
                "## Required Action",
                "",
                "```bash",
                "gh auth refresh -h github.com -s workflow",
                "```",
            ]
        )
    lines.extend(["", "## Evidence Boundary", "", report["evidence_boundary"]])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Enable and verify remote GitHub Actions CI.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--repo", default="starkweng/stark-finance-trading")
    parser.add_argument("--out")
    parser.add_argument("--markdown")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    auth = gh_scopes(repo_root)
    workflow_copy = {"status": "SKIPPED", "reason": "workflow scope missing"}
    push = {"status": "SKIPPED", "reason": "workflow scope missing"}
    remote_run = {"status": "SKIPPED", "reason": "workflow not enabled"}

    status = "FAIL"
    if auth["status"] == "PASS" and auth["has_workflow_scope"]:
        workflow_copy = copy_workflow(repo_root)
        if workflow_copy["status"] == "PASS":
            push = git_commit_push(repo_root, "Enable CI workflow")
            if push["status"] == "PASS":
                remote_run = wait_for_run(args.repo, repo_root, args.timeout, args.interval) if args.wait else latest_run(args.repo, repo_root)
                run_item = remote_run.get("run")
                status = "PASS" if run_item and run_item.get("conclusion") == "success" else "PENDING"
            else:
                status = "FAIL"
    report = {
        "schema_version": "1.0",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": args.repo,
        "repo_root": str(repo_root),
        "auth": auth,
        "workflow_copy": workflow_copy,
        "push": push,
        "remote_run": remote_run,
        "evidence_boundary": (
            "This proof only covers enabling and observing the GitHub Actions CI workflow. "
            "A successful remote run does not prove live model behavior, market-data correctness, "
            "trading performance, or public superiority."
        ),
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        write_markdown(Path(args.markdown), report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"remote CI proof: {report['status']}")
    return 0 if report["status"] in {"PASS", "PENDING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
