#!/usr/bin/env python3
"""Generate a task-level competitive router benchmark."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


SOURCE_FILES = [
    "SKILL.md",
    "README.md",
    "BENCHMARK.md",
    "references/tool-router.md",
    "references/safety-policy.md",
    "references/workflows.md",
    "references/source-ledger.md",
    "references/gotchas.md",
    "evals/routing-evals.json",
    "evals/adversarial-evals.json",
    "evals/live-behavior-evals.json",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def read_json(path: Path) -> dict:
    return json.loads(read_text(path)) if path.exists() else {}


def corpus(root: Path) -> str:
    return "\n".join(read_text(root / rel) for rel in SOURCE_FILES)


def contains_term(text: str, term: str) -> bool:
    return term.lower() in text.lower()


def score_case(text: str, case: dict) -> dict:
    required_terms = case.get("required_terms") or []
    required_safety_terms = case.get("required_safety_terms") or []
    checks = []
    for term in required_terms:
        checks.append({"type": "coverage", "term": term, "passed": contains_term(text, term)})
    for term in required_safety_terms:
        checks.append({"type": "safety", "term": term, "passed": contains_term(text, term)})
    passed = sum(1 for item in checks if item["passed"])
    total = len(checks)
    router_score = round(100 * passed / total, 2) if total else 0.0
    single_surface_ceiling = int(case.get("best_single_surface_static_ceiling", 0))
    return {
        "id": case.get("id"),
        "prompt": case.get("prompt"),
        "status": "PASS" if passed == total and router_score >= single_surface_ceiling else "FAIL",
        "router_static_score": router_score,
        "best_single_surface_static_ceiling": single_surface_ceiling,
        "router_static_edge": round(router_score - single_surface_ceiling, 2),
        "checks": checks,
        "best_single_surface": case.get("best_single_surface"),
        "router_edge": case.get("router_edge"),
    }


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# stark-finance-trading Competitive Task Benchmark",
        "",
        f"- Status: {report['status']}",
        f"- Score: {report['score']}/{report['max_score']}",
        f"- Cases: {report['case_count']}",
        f"- Average router score: {report['average_router_static_score']}",
        f"- Average single-surface ceiling: {report['average_single_surface_static_ceiling']}",
        f"- Average router edge: {report['average_router_static_edge']}",
        "",
        "## Task Scorecard",
        "",
        "| Task | Router score | Single-surface ceiling | Edge | Result |",
        "|---|---:|---:|---:|---|",
    ]
    for item in report["cases"]:
        lines.append(
            f"| `{item['id']}` | {item['router_static_score']} | {item['best_single_surface_static_ceiling']} | {item['router_static_edge']} | {item['status']} |"
        )
    lines.extend([
        "",
        "## Evidence Boundary",
        "",
        report["evidence_boundary"],
        "",
        "## Pending Proof",
        "",
        "- Run the same prompts through a reviewed live model-service eval.",
        "- Run comparable public vendor workflows where credentials and terms allow it.",
        "- Publish remote GitHub Actions results after repository publication.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--cases", default="benchmarks/competitive-task-cases.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    case_file = read_json(root / args.cases)
    text = corpus(root)
    cases = [score_case(text, item) for item in case_file.get("cases", [])]
    case_count = len(cases)
    passed = sum(1 for item in cases if item["status"] == "PASS")
    score = round(100 * passed / case_count, 2) if case_count else 0.0
    avg_router = round(sum(item["router_static_score"] for item in cases) / case_count, 2) if case_count else 0.0
    avg_single = round(sum(item["best_single_surface_static_ceiling"] for item in cases) / case_count, 2) if case_count else 0.0
    report = {
        "schema_version": "1.0",
        "skill": "stark-finance-trading",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "benchmark_type": case_file.get("benchmark_type"),
        "claim_status": "scenario-static-router-advantage-live-review-pending",
        "status": "PASS" if case_count and score >= int(case_file.get("minimum_pass_score", 90)) and passed == case_count else "FAIL",
        "score": score,
        "max_score": 100,
        "case_count": case_count,
        "passed_cases": passed,
        "average_router_static_score": avg_router,
        "average_single_surface_static_ceiling": avg_single,
        "average_router_static_edge": round(avg_router - avg_single, 2),
        "cases": cases,
        "evidence_boundary": "Task-level static benchmark over source coverage. It shows router workflow coverage and safety boundary design, not live output quality, API availability, execution performance, or public superiority.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown:
        markdown = Path(args.markdown)
        markdown.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(markdown, report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"competitive task benchmark: {report['status']} {score}/100")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
