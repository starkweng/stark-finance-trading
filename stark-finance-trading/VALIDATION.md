# Validation

Last local validation: 2026-06-28.

## Static Checks

```text
python3 scripts/validate_stark_finance_trading.py .
PASS
{
  "ok": true,
  "skill": "stark-finance-trading",
  "required_files": 38,
  "routing_cases": 11,
  "adversarial_cases": 12,
  "live_behavior_cases": 9,
  "public_comparison_candidates": 34,
  "public_benchmark_dimensions": 7,
  "competitive_task_cases": 12,
  "router_terms": 31,
  "local_skill_terms": 14,
  "public_tool_catalog_tools": 34,
  "tool_routing_cases": 13
}
```

```text
python3 scripts/validate_public_readiness.py .
PASS
candidates: 34
official_or_primary_sources: 34
adversarial_cases: 12
live_behavior_cases: 9
public_benchmark_dimensions: 7
competitive_task_cases: 12
public_tool_catalog_tools: 34
tool_routing_cases: 13
```

```text
python3 scripts/audit_public_sources.py --root . --json
PASS
candidates: 34
official_or_primary_sources: 34
execution_capable_candidates: 7
community_wrapper_candidates: 1
```

```text
python3 scripts/audit_public_sources.py --root . --live --json
WARN
candidates: 34
PASS: 30
WARN: 4
FAIL: 0
```

```text
python3 scripts/generate_public_benchmark.py --root . --json
PASS
score: 100/100
dimensions: 7
```

```text
python3 scripts/validate_public_tool_catalog.py --root . --json
PASS
tool_count: 34
official_or_primary_count: 34
high_risk_surface_count: 5
core_priority_tools: 13
missing_required_tool_ids: 0
missing_required_route_tags: 0
```

```text
python3 scripts/plan_tool_route.py --root . --json
PASS
passed_cases: 13/13
failed_cases: 0
```

```text
python3 scripts/runtime_capability_scan.py --root . --json
PASS
catalog_tool_count: 34
observed_runtime_tool_count: 13
configured_mcp_servers: 8
enabled_plugin_count: 27
local_skill_name_count: 519
env_missing_tool_ids: 1
```

```text
python3 scripts/discover_local_skill_inventory.py --skill-root . --json
PASS
unique_finance_skill_count: 81
total_skill_files_seen: 190
recommended_matched: 45/45
duplicate_skill_names: 13
```

```text
python3 scripts/generate_competitive_task_benchmark.py --root . --json
PASS
score: 100/100
cases: 12
average_router_static_edge: 31.67
```

```text
python3 scripts/quick_validate.py .
PASS
Skill is valid!
```

```text
python3 scripts/run_quality_suite.py --dist ../dist --json
PASS
quick_validate: PASS
skill_validator: PASS
public_readiness: PASS
tool_routing_cases_json: PASS
public_tool_catalog_json: PASS
github_actions_workflow: PASS
public_source_audit_offline: PASS
public_tool_catalog: PASS
public_benchmark: PASS
runtime_capability_scan: PASS
tool_route_plan: PASS
competitive_task_benchmark: PASS
local_skill_inventory: PASS
package: PASS
install_smoke: PASS
release_manifest: PASS
live_eval_signoff: PASS
release_notes: PASS
codex_eval_dry_run: PASS
live_eval_review_bundle: PASS
live_eval_review_scorecard: PASS
competitive_eval_signoff: PASS
competitive_codex_eval_dry_run: PASS
competitive_eval_review_bundle: PASS
competitive_eval_review_scorecard: PASS
github_export: PASS
github_export_smoke: PASS
release_readiness: PASS
steps: 36
```

```text
python3 scripts/validate_github_actions_workflow.py --root . --json
PASS
required_snippet_count: 13
required_artifact_count: 40
failed_checks: 0
```

```text
python3 /path/to/stark-skiller/scripts/generate_loop_blueprint.py --skill-root . --json
PASS
loop_fields: PASS
skill_terms: PASS
reference_terms: PASS
quality_gate: PASS
eval_regression: PASS
```

```text
python3 /path/to/stark-skiller/scripts/security_scan_skill.py .
PASS
files_scanned: 55
critical: 0
high: 0
medium: 0
low: 0
```

```text
python3 /path/to/stark-skiller/scripts/score_skill_quality.py .
PASS 100/100
```

```text
python3 /path/to/stark-skiller/scripts/check_reproducible_package.py --root . --json
PASS
package_commands: true
packages_exist: true
hashes_match: true
fixed_zip_metadata: true
entry_counts_match: true
install_smoke: true
entry_count: 55
```

```text
python3 scripts/package_skill.py . ../dist
python3 scripts/install_package_smoke.py ../dist/stark-finance-trading.skill --json
PASS
entry_count: 55
```

```text
python3 scripts/export_github_repo.py --skill-root . --out-dir ../dist/github-export/stark-finance-trading --release-artifacts-dir ../dist --zip ../dist/stark-finance-trading-github-repo.zip --json
PASS
skill_files_copied: 56
release_artifacts_copied: 38
release_package_install_smoke: true
zip_entry_count: 102
```

```text
python3 scripts/smoke_github_export.py --zip ../dist/stark-finance-trading-github-repo.zip --out ../dist/stark-finance-trading.github-export-smoke.json --markdown ../dist/stark-finance-trading.github-export-smoke.md --json
PASS
zip_entry_count: 102
required_files: true
no_transient_files: true
exported_core_commands: true
quick_validate_exported_skill: PASS
validate_exported_skill: PASS
validate_exported_public_readiness: PASS
validate_exported_workflow: PASS
install_smoke_exported_package: PASS
```

```text
python3 scripts/validate_release_readiness.py --skill-root . --dist ../dist --out ../dist/stark-finance-trading.release-readiness.json --markdown ../dist/stark-finance-trading.release-readiness.md --public-repo-url https://github.com/starkweng/stark-finance-trading --json
PASS
local_release_status: LOCAL_RELEASE_READY
goal_completion_status: NOT_COMPLETE_EXTERNAL_PROOFS_PENDING
package_sha256: see ../dist/stark-finance-trading.release-readiness.json
github_export_zip_sha256: see ../dist/stark-finance-trading.release-readiness.json
package_entry_count: 55
github_export_zip_entry_count: 102
source_freshness: PASS
missing_required_package_files: 0
hash_mismatches: 0
external_public_repo_url: PROVIDED
external_remote_github_actions_run_url: PENDING
external_approved_live_model_eval: PENDING
external_reviewed_comparative_live_eval: PENDING
```

```text
python3 scripts/enable_remote_ci.py --repo-root ../dist/github-export/stark-finance-trading --repo starkweng/stark-finance-trading --out ../dist/stark-finance-trading.remote-ci-proof.json --markdown ../dist/stark-finance-trading.remote-ci-proof.md --json
FAIL
workflow_scope: false
token_scopes: gist, read:org, repo
remote_workflow_file: MISSING_OR_INACCESSIBLE
actions_enabled: true
workflow_list: empty
run_list: empty
workflow_copy: SKIPPED
push: SKIPPED
dispatch: SKIPPED
remote_run: SKIPPED
required_action: gh auth refresh -h github.com -s workflow
```

```text
python3 scripts/generate_eval_review_bundle.py ../dist/live-eval-dry-run --eval-set evals/live-behavior-evals.json --out-dir ../dist/stark-finance-trading.live-eval-review --json
PASS
cases: 9
review_md: ../dist/stark-finance-trading.live-eval-review/review.md
review_html: ../dist/stark-finance-trading.live-eval-review/review.html
```

```text
python3 scripts/score_eval_review_bundle.py ../dist/stark-finance-trading.live-eval-review --out ../dist/stark-finance-trading.live-eval-scorecard.json --markdown ../dist/stark-finance-trading.live-eval-scorecard.md --json
PASS
score: 100/100
behavior_proof_status: UNPROVEN_DRY_RUN_ONLY
cases: 9
```

```text
python3 scripts/generate_eval_review_bundle.py ../dist/competitive-eval-dry-run --eval-set benchmarks/competitive-task-cases.json --out-dir ../dist/stark-finance-trading.competitive-eval-review --json
PASS
cases: 12
review_md: ../dist/stark-finance-trading.competitive-eval-review/review.md
review_html: ../dist/stark-finance-trading.competitive-eval-review/review.html
```

```text
python3 scripts/score_eval_review_bundle.py ../dist/stark-finance-trading.competitive-eval-review --out ../dist/stark-finance-trading.competitive-eval-scorecard.json --markdown ../dist/stark-finance-trading.competitive-eval-scorecard.md --json
PASS
score: 100/100
behavior_proof_status: UNPROVEN_DRY_RUN_ONLY
cases: 12
```

```text
find . -name __pycache__ -o -name '*.pyc' -o -name '.DS_Store'
PASS
no output
```

## Evidence Boundaries

- Routing evals are seeded, not live-run.
- Public comparison snapshot is source-level, not a live comparative win.
- Public source audit checks candidate classification and URL reachability only. Live URL audit can return WARN for WAF, bot-blocking, rate-limit, or local TLS/network issues; WARN is not market-data proof and not a source invalidation.
- Public tool catalog validation checks source-ledger alignment, route tags, official-source status, action tiers, and high-risk surfaces. It does not prove credentials, entitlement, live availability, market-data correctness, or execution quality.
- Runtime capability scan checks local MCP/plugin/skill configuration and env-var presence, while redacting secret values. It does not prove OAuth validity, paid entitlement, live API reachability, market-data correctness, or trading performance.
- Tool route planner validation checks deterministic natural-language prompt routing into workflow, tool IDs, route tags, local helper hints, risk tier, and safety terms. It does not prove live tool availability, API credentials, market-data correctness, or model behavior.
- Public benchmark scorecard is source-level and checks routing coverage, evidence depth, safety gates, eval coverage, reproducible packaging, and GitHub readiness. It does not prove market accuracy or live trading performance.
- Competitive task benchmark is source-level and checks task coverage against representative workflows. It does not prove live model output quality or public superiority.
- GitHub Actions workflow validation is static coverage validation. It does not prove the workflow has run remotely on GitHub.
- Adversarial evals are seeded as regression prompts, not live-run.
- Live behavior evals and competitive task evals are defined and dry-run reviewed through human-review bundles, not live-run.
- Eval review bundles prove that cases are reviewable by humans. They do not prove live model behavior, market-data correctness, trading performance, or public superiority.
- Eval review scorecards prove reviewability and evidence labeling. Dry-run scorecard PASS still does not prove live model behavior.
- Package smoke, GitHub export validation, and GitHub export smoke passed locally.
- GitHub export smoke proves the standalone repository ZIP can be extracted and core gates rerun locally. It does not prove remote GitHub Actions completion or uploaded artifact availability.
- Remote CI proof helper exists, audits remote Actions/workflow/run state, and reports the current GitHub CLI permission blocker. It does not enable CI until the token has `workflow` scope and a remote run completes.
- Release readiness proves local package/source freshness, release artifact consistency, clean package/export ZIPs, status artifacts, and public-claim boundaries. It does not prove public repo publication, remote GitHub Actions completion, approved live model evals, or reviewed comparative live evals.
- Comparative live benchmark is pending.
- Live model-service eval is pending and requires explicit approval.
- Live eval signoff tooling exists at `scripts/generate_live_eval_signoff.py`.
- No live trading or broker execution test was run.
