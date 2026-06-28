# Validation

Last local validation: 2026-06-28.

## Static Checks

```text
python3 scripts/validate_stark_finance_trading.py .
PASS
{
  "ok": true,
  "skill": "stark-finance-trading",
  "required_files": 29,
  "routing_cases": 8,
  "adversarial_cases": 10,
  "live_behavior_cases": 6,
  "public_comparison_candidates": 25,
  "public_benchmark_dimensions": 7,
  "competitive_task_cases": 8,
  "router_terms": 22
}
```

```text
python3 scripts/validate_public_readiness.py .
PASS
candidates: 25
official_or_primary_sources: 25
adversarial_cases: 10
live_behavior_cases: 6
public_benchmark_dimensions: 7
competitive_task_cases: 8
```

```text
python3 scripts/audit_public_sources.py --root . --json
PASS
candidates: 25
official_or_primary_sources: 25
execution_capable_candidates: 7
community_wrapper_candidates: 1
```

```text
python3 scripts/audit_public_sources.py --root . --live --json
WARN
candidates: 25
PASS: 21
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
python3 scripts/generate_competitive_task_benchmark.py --root . --json
PASS
score: 100/100
cases: 8
average_router_static_edge: 30.62
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
github_actions_workflow: PASS
public_source_audit_offline: PASS
public_benchmark: PASS
competitive_task_benchmark: PASS
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
steps: 30
```

```text
python3 scripts/validate_github_actions_workflow.py --root . --json
PASS
required_snippet_count: 13
required_artifact_count: 32
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
files_scanned: 46
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
entry_count: 46
```

```text
python3 scripts/package_skill.py . ../dist
python3 scripts/install_package_smoke.py ../dist/stark-finance-trading.skill --json
PASS
entry_count: 46
```

```text
python3 scripts/export_github_repo.py --skill-root . --out-dir ../dist/github-export/stark-finance-trading --release-artifacts-dir ../dist --zip ../dist/stark-finance-trading-github-repo.zip --json
PASS
skill_files_copied: 47
release_artifacts_copied: 30
release_package_install_smoke: true
zip_entry_count: 83
```

```text
python3 scripts/smoke_github_export.py --zip ../dist/stark-finance-trading-github-repo.zip --out ../dist/stark-finance-trading.github-export-smoke.json --markdown ../dist/stark-finance-trading.github-export-smoke.md --json
PASS
zip_entry_count: 83
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
python3 scripts/validate_release_readiness.py --skill-root . --dist ../dist --out ../dist/stark-finance-trading.release-readiness.json --markdown ../dist/stark-finance-trading.release-readiness.md --json
PASS
local_release_status: LOCAL_RELEASE_READY
goal_completion_status: NOT_COMPLETE_EXTERNAL_PROOFS_PENDING
package_entry_count: 46
github_export_zip_entry_count: 83
source_freshness: PASS
missing_required_package_files: 0
hash_mismatches: 0
external_public_repo_url: PENDING
external_remote_github_actions_run_url: PENDING
external_approved_live_model_eval: PENDING
external_reviewed_comparative_live_eval: PENDING
```

```text
python3 scripts/generate_eval_review_bundle.py ../dist/live-eval-dry-run --eval-set evals/live-behavior-evals.json --out-dir ../dist/stark-finance-trading.live-eval-review --json
PASS
cases: 6
review_md: ../dist/stark-finance-trading.live-eval-review/review.md
review_html: ../dist/stark-finance-trading.live-eval-review/review.html
```

```text
python3 scripts/score_eval_review_bundle.py ../dist/stark-finance-trading.live-eval-review --out ../dist/stark-finance-trading.live-eval-scorecard.json --markdown ../dist/stark-finance-trading.live-eval-scorecard.md --json
PASS
score: 100/100
behavior_proof_status: UNPROVEN_DRY_RUN_ONLY
cases: 6
```

```text
python3 scripts/generate_eval_review_bundle.py ../dist/competitive-eval-dry-run --eval-set benchmarks/competitive-task-cases.json --out-dir ../dist/stark-finance-trading.competitive-eval-review --json
PASS
cases: 8
review_md: ../dist/stark-finance-trading.competitive-eval-review/review.md
review_html: ../dist/stark-finance-trading.competitive-eval-review/review.html
```

```text
python3 scripts/score_eval_review_bundle.py ../dist/stark-finance-trading.competitive-eval-review --out ../dist/stark-finance-trading.competitive-eval-scorecard.json --markdown ../dist/stark-finance-trading.competitive-eval-scorecard.md --json
PASS
score: 100/100
behavior_proof_status: UNPROVEN_DRY_RUN_ONLY
cases: 8
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
- Public benchmark scorecard is source-level and checks routing coverage, evidence depth, safety gates, eval coverage, reproducible packaging, and GitHub readiness. It does not prove market accuracy or live trading performance.
- Competitive task benchmark is source-level and checks task coverage against representative workflows. It does not prove live model output quality or public superiority.
- GitHub Actions workflow validation is static coverage validation. It does not prove the workflow has run remotely on GitHub.
- Adversarial evals are seeded as regression prompts, not live-run.
- Live behavior evals and competitive task evals are defined and dry-run reviewed through human-review bundles, not live-run.
- Eval review bundles prove that cases are reviewable by humans. They do not prove live model behavior, market-data correctness, trading performance, or public superiority.
- Eval review scorecards prove reviewability and evidence labeling. Dry-run scorecard PASS still does not prove live model behavior.
- Package smoke, GitHub export validation, and GitHub export smoke passed locally.
- GitHub export smoke proves the standalone repository ZIP can be extracted and core gates rerun locally. It does not prove remote GitHub Actions completion or uploaded artifact availability.
- Release readiness proves local package/source freshness, release artifact consistency, clean package/export ZIPs, status artifacts, and public-claim boundaries. It does not prove public repo publication, remote GitHub Actions completion, approved live model evals, or reviewed comparative live evals.
- Comparative live benchmark is pending.
- Live model-service eval is pending and requires explicit approval.
- Live eval signoff tooling exists at `scripts/generate_live_eval_signoff.py`.
- No live trading or broker execution test was run.
