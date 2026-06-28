# Quality Gates - 2026-06-24

Use these gates before claiming the skill is GitHub-ready or best-in-class.

## Trigger Gate

- Description starts with `Load when`.
- Description includes `Do not load`.
- Negative routes cover marketing, tokenomics, design, and legal advice.

## Resource Gate

- `SKILL.md` stays a router.
- Long tool matrices live in `references/tool-router.md`.
- Safety rules live in `references/safety-policy.md`.
- Repeatable checks live in `scripts/`.
- Routing cases live in `evals/`.

## Loop Engineering Gate

- `references/loop-engineering-pattern-2026-06-28.md` names `entry_signal`, `state_artifacts`, `actions`, `deterministic_checks`, `repair_branch`, `stop_condition`, `human_checkpoint`, `learning_sink`, and `budget_guard`.
- Serious market, strategy, execution, release, and learn loops are present.

## Safety Gate

- No secrets or credentials.
- Read-only-first policy is visible.
- Tier 4 live actions require explicit confirmation.
- Signals are not recommendations.
- Backtests require fees, slippage, sizing, and drawdown.

## Eval Gate

- Explicit trigger case.
- Implicit trigger case.
- Contextual token/onchain case.
- Negative adjacent task.
- Gotcha regression.
- Live execution gated case.

## Live Eval Signoff Gate

- Live model-service evals are not run without explicit approval.
- Dry-run/static validation is labeled separately from live behavior proof.

## Eval Review Bundle Gate

- Live behavior and competitive task eval outputs can be converted into `review.md`, `review.html`, and `review.json`.
- Review bundles record source mode, approval status, prompt hashes, required review items, and evidence boundaries.
- A review-bundle PASS means the eval is human-reviewable, not that live model behavior or public superiority is proven.

## Eval Review Scorecard Gate

- Review bundles can be converted into scorecard JSON/Markdown.
- Scorecards record source mode, approval status, case coverage, prompt hashes, required review item coverage, and evidence boundaries.
- A dry-run scorecard PASS proves reviewability only; live behavior proof requires approved live eval outputs.

## Release Notes Gate

- `VERSION` exists.
- `CHANGELOG.md` has the current version.
- Evidence labels distinguish static validation, routing eval seeds, package smoke, and live benchmark.

## GitHub Repo Export Gate

- README, benchmark notes, source ledger, validator, and eval seeds exist.
- Package/export is not claimed until a package smoke or repo export has actually been run.

## GitHub Export Smoke Gate

- The exported GitHub repository ZIP is extracted in a fresh temporary directory.
- Core validators rerun from the exported skill subdirectory.
- Workflow validation reruns from the exported repository root.
- The exported `.skill` package passes install smoke from the standalone layout.
- Local export smoke does not prove remote GitHub Actions completion or live model behavior.

## Release Readiness Gate

- `scripts/validate_release_readiness.py` runs after package build, release sidecars, eval review scorecards, GitHub export, and export smoke.
- The gate checks local source coverage, release artifact presence, status artifacts, package hash consistency, package/export ZIP cleanliness, and public-claim boundaries.
- Public repo URL, remote GitHub Actions run, approved live model eval, and reviewed comparative live eval remain explicit external proofs.
- A local release-readiness PASS does not prove live market-data correctness, trading performance, public superiority, or remote CI completion.

## GitHub Actions Workflow Gate

- `.github/workflows/ci.yml` runs the portable quality suite from the skill subdirectory.
- CI builds and smoke-tests the `.skill` package.
- CI uploads package, public benchmark, release manifest/notes, eval review bundles, eval review scorecards, workflow validation, GitHub export artifacts, export-smoke reports, and release-readiness reports.
- Static workflow validation does not prove remote GitHub Actions completion.
