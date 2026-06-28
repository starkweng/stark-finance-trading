# Benchmark Notes

This skill should compete on workflow quality, not instruction volume.

## Acceptance Criteria

- One primary user-facing route instead of a vendor-skill pile.
- Clear positive and negative triggers.
- Installed tool surfaces are separated from external candidates.
- Public MCP/API/framework candidates are also represented in a machine-readable catalog with source status, route tags, action tier, installed status, merge policy, and safety notes.
- Execution-capable tools are gated by a risk-tier policy.
- Routing evals cover explicit, implicit, contextual, negative, gotcha, backtest, and live-action cases.
- Validator checks required files, routing terms, safety phrases, eval structure, and obvious secret patterns.

## Evidence Labels

- Static validation: available through `scripts/validate_stark_finance_trading.py`.
- Frontmatter validation: available through `scripts/quick_validate.py`.
- Routing evals: seeded but not live-run.
- Comparative public benchmark: criteria defined; live comparative runs pending.
- Public comparison snapshot: `benchmarks/PUBLIC_COMPARISON_2026-06-28.md` and `benchmarks/public-comparison-2026-06-28.json`.
- Public source audit: `scripts/audit_public_sources.py` checks candidate classification and can optionally probe public URLs.
- Public tool catalog: `references/public-tool-catalog.json` and `scripts/validate_public_tool_catalog.py` keep official MCP/API/framework candidates machine-checkable.
- Public benchmark cases: `benchmarks/public-benchmark-cases.json`.
- Public benchmark generator: `scripts/generate_public_benchmark.py`.
- Competitive task cases: `benchmarks/competitive-task-cases.json`.
- Competitive task benchmark generator: `scripts/generate_competitive_task_benchmark.py`.
- Adversarial coverage: `evals/adversarial-evals.json`.
- Live behavior eval definitions: `evals/live-behavior-evals.json`.
- Portable quality suite: `scripts/run_quality_suite.py`.
- Live eval signoff generator: `scripts/generate_live_eval_signoff.py`.
- Eval review bundle generator: `scripts/generate_eval_review_bundle.py` creates `review.md`, `review.html`, and `review.json` from dry-run or live eval output.
- Eval review scorecard generator: `scripts/score_eval_review_bundle.py` turns review bundles into public, evidence-labeled scorecards.
- Release manifest generator: `scripts/generate_release_manifest.py` records package hash, entry inventory, and install smoke.
- Release notes generator: `scripts/generate_release_notes.py` records version, changelog, package evidence, signoff status, and evidence boundaries.
- GitHub Actions workflow validator: `scripts/validate_github_actions_workflow.py` checks CI triggers, validation/build steps, and uploaded release evidence artifacts.
- GitHub export smoke: `scripts/smoke_github_export.py` extracts the standalone repository ZIP and reruns core gates from the exported layout.
- Remote CI proof helper: `scripts/enable_remote_ci.py` copies the workflow template into a public export, pushes it when the GitHub CLI token has `workflow` scope, and records the latest remote run status.
- Release readiness validator: `scripts/validate_release_readiness.py` checks local release artifacts, package hashes, export ZIP cleanliness, public-claim boundaries, and external proof status.
- Package smoke: available through `scripts/install_package_smoke.py`.
- CI smoke: available through `.github/workflows/ci.yml`.

Avoid public superiority claims until comparative evidence is added.

## Public Comparison Candidates

These are not enemies; they are the bar this skill should learn from.

| Candidate | Strength | What `stark-finance-trading` must beat or complement |
|---|---|---|
| Alpaca MCP | Official market-data/trading surface, paper/live account integration | Stronger routing and safety around when not to execute. |
| OpenBB | Broad finance research platform | Lighter skill-level routing across Web3, TradFi, and execution risk. |
| QuantConnect / LEAN | Serious backtest and algorithm deployment stack | Better natural-language intake and risk-gated handoff into backtest/paper/live phases. |
| Alpha Vantage / FMP / Twelve Data MCPs | Useful official data APIs | Unified source selection and cross-check policy. |
| Unusual Whales MCP | Options/dark-pool/flow specialty | Better distinction between signal, thesis, and execution. |
| Massive/Polygon.io / Databento | Higher-grade market-data layers | Route by dataset, venue, entitlement, latency, and subscription limits. |
| FactSet MCP | Institutional financial-data layer | Use only when entitlement and redistribution constraints are clear; preserve metric definitions. |
| Robinhood / cTrader / IBKR candidates | Broker/platform agent surfaces | Treat as Tier 4; preserve account, margin, lot, paper/live, and wrapper provenance boundaries. |
| Binance Skills Hub | Strong crypto/Web3 execution and market data skills | One Stark-level router that calls Binance only when it is the right surface. |
| Dune / Alchemy / Etherscan / Coinbase / QuickNode / CoinGecko / CoinMarketCap MCPs | Best-in-class onchain, wallet, infra, and crypto-data surfaces | Better workflow for table semantics, wallet truth, token identity, endpoint admin, and state-changing action gates. |
| Token Terminal / DeFiLlama | Crypto protocol fundamentals and aggregate data | Use methodology-aware evidence, not direct safety or trade labels. |
| Helius / Jupiter / DexScreener | Solana, liquidity, and DEX market surfaces | Resolve token identity, separate quotes from swaps, and cross-check display liquidity. |
| Stripe / Plaid | Financial infrastructure rather than trading surfaces | Route payments/account connectivity separately from market signals and broker execution. |
| Hummingbot / Freqtrade / NautilusTrader / CCXT | Real bot/framework/library surfaces | Safer review, dry-run handoff, connector risk controls, and adapter boundaries before live bots. |

## Adversarial Coverage

The adversarial eval set covers prompt injection, secret requests, live trade pressure, public overclaiming, stale market data, wrong-skill routing, token symbol confusion, legal/tax certainty, malicious tool output, and Dune table-semantics traps.

## Live Behavior Gate

`evals/live-behavior-evals.json` defines six live behavior cases for routing/source discipline, token DD, Dune semantics, strategy validation, execution safety, and public claim boundaries. `scripts/generate_live_eval_signoff.py` creates a PENDING approval packet. `scripts/codex_eval.py` only produces dry-run review artifacts unless an approved signoff packet is supplied. `scripts/generate_eval_review_bundle.py` converts those dry-run or live outputs into human-review Markdown, HTML, and JSON.

## Eval Review Bundle

The review bundle is the handoff layer between automated checks and human judgment. It records case IDs, prompt hashes, prompt text from the eval set, required review items, source mode, approval status, and evidence boundaries. A PASS here means the eval artifacts are reviewable; it does not mean live model behavior, market-data correctness, trading performance, or public superiority has been proven.

## Eval Review Scorecard Gate

`scripts/score_eval_review_bundle.py` scores live and competitive review bundles for case coverage, prompt hashes, required review items, source-mode labeling, approval labeling, and evidence boundaries. A PASS on a dry-run bundle means the eval package is ready for human review and later live scoring. It does not prove live model behavior, market-data correctness, trading performance, or public superiority.

## Public Benchmark Gate

`scripts/audit_public_sources.py` validates candidate URL shape, source classification, and optional live reachability. `scripts/generate_public_benchmark.py` generates a source-level scorecard from the current skill tree and `benchmarks/public-benchmark-cases.json`. A PASS here means the source package meets the static public-readiness rubric. It does not mean live model behavior passed or that the skill has defeated public competitors in reviewed live runs.

## Public Tool Catalog Gate

`scripts/validate_public_tool_catalog.py` validates `references/public-tool-catalog.json` against required public finance/trading/Web3 tool IDs, required route tags, official or primary source status, source-ledger alignment, high-risk execution/admin/payment surfaces, and the one-skill merge policy. A PASS here means the router has a machine-readable substrate for major public MCP/API/framework candidates. It does not prove credentials, entitlement, live availability, market-data correctness, or execution quality.

## Competitive Task Benchmark

`scripts/generate_competitive_task_benchmark.py` runs eight representative finance/trading/Web3 task scenarios against the current skill source. It checks whether the router covers multi-source workflows and safety boundaries that a single vendor surface usually cannot cover alone. The same case set can also produce a PENDING live-eval signoff packet and a dry-run human-review bundle. A PASS means the source tree contains task-level routing coverage for those scenarios and the eval set is reviewable. It does not prove live model quality, live data accuracy, or public superiority.

## GitHub Actions Workflow Gate

`scripts/validate_github_actions_workflow.py` statically validates that `.github/workflows/ci.yml` runs the quality suite, builds and smoke-tests the package, and uploads the package, public benchmark, release manifest/notes, live/competitive eval review bundles, workflow validation report, and GitHub export ZIP. A PASS here means the workflow has the expected coverage. It does not prove the workflow has run on GitHub.

## Remote CI Proof Gate

`scripts/enable_remote_ci.py` is the post-publication helper for the exported repository. It requires GitHub CLI auth with `workflow` scope, copies `workflow-templates/stark-finance-trading-ci.yml` into `.github/workflows/ci.yml`, commits and pushes the workflow, then records the latest remote GitHub Actions run. A PASS here proves the remote CI workflow completed successfully. PENDING or FAIL keeps the full public-release goal incomplete.

## GitHub Export Smoke Gate

`scripts/smoke_github_export.py` extracts `stark-finance-trading-github-repo.zip`, checks the standalone repository layout, reruns core validators from the exported skill directory, validates the exported workflow from the repository root, and smoke-tests the exported `.skill` package. A PASS means the handoff ZIP is locally executable as a repository bundle. It does not prove remote GitHub Actions completion, uploaded artifact availability, live market-data correctness, trading performance, or live model behavior.

## Release Readiness Gate

`scripts/validate_release_readiness.py` runs after packaging, release sidecars, review scorecards, GitHub export, and export smoke. It reports `LOCAL_RELEASE_READY` only when local source files, release artifacts, package hashes, clean ZIP checks, status artifacts, and public-claim boundaries are internally consistent. It keeps public repo URL, remote GitHub Actions run, approved live model eval, and reviewed comparative live eval as explicit external proofs. A PASS here does not mean the full "best finance/trading skill on GitHub" goal is complete.

## Scoring Rubric

| Dimension | Weight | Requirement |
|---|---:|---|
| Routing precision | 20 | Correctly chooses finance/trading route and rejects marketing/tokenomics/design tasks. |
| Source discipline | 15 | Prefers official/live sources and labels venue/timestamp/data gaps. |
| Safety boundary | 20 | Live execution is impossible without explicit preview and confirmation. |
| Workflow coverage | 15 | Covers market data, token DD, signals, options flow, backtest, MM, execution prep. |
| Portability | 10 | Can validate, package, and smoke-test without machine-specific paths. |
| Eval coverage | 10 | Has explicit, implicit, contextual, negative, gotcha, and live-gated cases. |
| Public readiness | 10 | README, license, contributing, security, CI, validation, package evidence. |

Current local static score: 100/100 by the bundled quality scorer. This is not a live comparative benchmark.
