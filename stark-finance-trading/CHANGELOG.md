# Changelog

## 0.1.0 - 2026-06-28

- Created `stark-finance-trading` as a unified finance/trading router skill.
- Added tool matrix covering installed Web3/CEX/DEX surfaces and public official TradFi/quant candidates.
- Added read-only-first safety policy with explicit live-action confirmation gate.
- Added workflows for market snapshots, token DD, smart-money scans, options flow, backtests, market-making, and execution prep.
- Added source ledger, gotchas, routing eval seeds, and deterministic validator.
- Added standalone deterministic packager and package install smoke script for GitHub portability.
- Added standalone GitHub repository export script and release artifact handoff path.
- Added public comparison snapshot, adversarial evals, and public-readiness validator.
- Added portable quality suite, live behavior eval set, live-eval signoff generator, and guarded eval runner.
- Added source-level public benchmark cases and scorecard generator.
- Expanded the public candidate set to 25 finance/trading/Web3 surfaces and added a public source audit script.
- Added a task-level competitive router benchmark covering eight representative finance/trading/Web3 workflows.
- Added live/competitive eval review bundle generation for human-reviewable `review.md`, `review.html`, and `review.json` artifacts.
- Added eval review scorecards so dry-run and future live eval bundles become public, evidence-labeled score reports.
- Added local release manifest and release notes generators so GitHub export uses current package evidence instead of stale sidecars.
- Added GitHub Actions workflow validation so CI artifact coverage is checked before public handoff.
- Added GitHub export smoke testing so the standalone repository ZIP is extracted and core gates rerun before public handoff.
- Added local release-readiness validation to separate source-package readiness from external proofs such as public repo publication, remote GitHub Actions, approved live evals, and reviewed comparative evals.
