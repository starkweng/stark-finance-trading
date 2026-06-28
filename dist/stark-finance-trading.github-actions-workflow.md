# GitHub Actions Workflow Validation

- Status: PASS
- Workflow: `.github/workflows/ci.yml`
- Required snippets: 13
- Required artifacts: 59

## Checks

| Check | Status | Evidence |
|---|---|---|
| `workflow_name` | PASS | `name: stark-finance-trading-ci` |
| `push_trigger` | PASS | `push:` |
| `pull_request_trigger` | PASS | `pull_request:` |
| `manual_trigger` | PASS | `workflow_dispatch:` |
| `ubuntu_runner` | PASS | `runs-on: ubuntu-latest` |
| `checkout` | PASS | `actions/checkout@v4` |
| `python_setup` | PASS | `actions/setup-python@v5` |
| `python_312` | PASS | `python-version: "3.12"` |
| `subdir_working_directory` | PASS | `working-directory: stark-finance-trading` |
| `quality_suite` | PASS | `python3 scripts/run_quality_suite.py --json` |
| `package_build` | PASS | `python3 scripts/package_skill.py . dist` |
| `install_smoke` | PASS | `python3 scripts/install_package_smoke.py dist/stark-finance-trading.skill --json` |
| `artifact_upload` | PASS | `actions/upload-artifact@v4` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.skill` | PASS | `stark-finance-trading/dist/stark-finance-trading.skill` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.quality-suite.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.quality-suite.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.github-tool-discovery.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.github-tool-discovery.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.github-tool-discovery.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.github-tool-discovery.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-gap-analysis.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-gap-analysis.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-gap-analysis.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-gap-analysis.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-route-backlog.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-route-backlog.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-route-backlog.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-route-backlog.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.release-manifest.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.release-manifest.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.release-manifest.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.release-manifest.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.release-notes.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.release-notes.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.release-notes.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.release-notes.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.public-source-audit.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.public-source-audit.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.public-source-audit.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.public-source-audit.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.public-benchmark.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.public-benchmark.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.public-benchmark.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.public-benchmark.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.public-tool-catalog.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.public-tool-catalog.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.public-tool-catalog.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.public-tool-catalog.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.runtime-capabilities.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.runtime-capabilities.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.runtime-capabilities.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.runtime-capabilities.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.integration-activation-plan.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.integration-activation-plan.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.integration-activation-plan.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.integration-activation-plan.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.release-blocker-plan.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.release-blocker-plan.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.release-blocker-plan.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.release-blocker-plan.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.tool-route-plan.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.tool-route-plan.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.tool-route-plan.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.tool-route-plan.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.local-skill-inventory.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.local-skill-inventory.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.local-skill-inventory.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.local-skill-inventory.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-task-benchmark.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-task-benchmark.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-task-benchmark.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-task-benchmark.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.live-eval-signoff.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.live-eval-signoff.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.live-eval-signoff.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.live-eval-signoff.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.live-eval-harness-smoke.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.live-eval-harness-smoke.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.live-eval-harness-smoke.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.live-eval-harness-smoke.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.live-eval-review/**` | PASS | `stark-finance-trading/dist/stark-finance-trading.live-eval-review/**` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.live-eval-scorecard.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.live-eval-scorecard.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.live-eval-scorecard.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.live-eval-scorecard.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-eval-signoff.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-eval-signoff.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-eval-signoff.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-eval-signoff.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-eval-harness-smoke.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-eval-harness-smoke.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-eval-harness-smoke.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-eval-harness-smoke.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-eval-review/**` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-eval-review/**` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-eval-scorecard.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-eval-scorecard.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.competitive-eval-scorecard.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.competitive-eval-scorecard.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.external-proof-audit.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.external-proof-audit.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.external-proof-audit.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.external-proof-audit.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.goal-completion-audit.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.goal-completion-audit.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.goal-completion-audit.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.goal-completion-audit.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.github-export-report.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.github-export-report.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.github-export-report.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.github-export-report.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.github-export-smoke.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.github-export-smoke.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.github-export-smoke.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.github-export-smoke.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.release-readiness.json` | PASS | `stark-finance-trading/dist/stark-finance-trading.release-readiness.json` |
| `artifact:stark-finance-trading/dist/stark-finance-trading.release-readiness.md` | PASS | `stark-finance-trading/dist/stark-finance-trading.release-readiness.md` |
| `artifact:stark-finance-trading/dist/stark-finance-trading-github-repo.zip` | PASS | `stark-finance-trading/dist/stark-finance-trading-github-repo.zip` |
| `artifact:stark-finance-trading/VALIDATION.md` | PASS | `stark-finance-trading/VALIDATION.md` |
| `artifact:stark-finance-trading/BENCHMARK.md` | PASS | `stark-finance-trading/BENCHMARK.md` |
| `artifact:stark-finance-trading/references/release-closeout-2026-06-28.md` | PASS | `stark-finance-trading/references/release-closeout-2026-06-28.md` |
| `artifact:stark-finance-trading/benchmarks/PUBLIC_COMPARISON_2026-06-28.md` | PASS | `stark-finance-trading/benchmarks/PUBLIC_COMPARISON_2026-06-28.md` |

## Evidence Boundary

Static workflow coverage validation only. It does not prove remote GitHub Actions execution, uploaded artifact availability, or live model behavior.
