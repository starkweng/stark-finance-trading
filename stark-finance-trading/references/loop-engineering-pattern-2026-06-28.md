# Loop Engineering Pattern - 2026-06-28

This finance/trading skill uses loops because market work is not a one-shot answer. Every serious output should preserve evidence, run checks, repair weak routes, and capture reusable lessons.

## Market Evidence Loop

| Field | Value |
|---|---|
| `entry_signal` | User asks for current price, market scan, onchain data, token DD, options flow, or liquidity state. |
| `state_artifacts` | Query URLs, source timestamps, route notes, result tables, risk caveats. |
| `actions` | Classify market, select tool route, gather data, cross-check, summarize. |
| `deterministic_checks` | Source named, timestamp present, venue/feed present, bounded query when applicable. |
| `repair_branch` | If data is missing, stale, or conflicting, switch source or report the conflict. |
| `stop_condition` | Answer names source, timestamp, instrument, venue/feed, and caveat. |
| `human_checkpoint` | Required when user asks to act on incomplete or conflicting data. |
| `learning_sink` | `references/gotchas.md`, routing evals, source ledger updates. |
| `budget_guard` | Do not run broad expensive queries before targeted discovery. |

## Strategy Validation Loop

| Field | Value |
|---|---|
| `entry_signal` | User asks for backtest, strategy, grid, martingale, bot, signal quality, or risk model. |
| `state_artifacts` | Hypothesis, dataset, parameters, backtest result, risk table. |
| `actions` | Define assumptions, run/design backtest, inspect drawdown, repair assumptions. |
| `deterministic_checks` | Fees, slippage, sizing, max drawdown, period, and data source are present. |
| `repair_branch` | Reject or rerun if fees/slippage/sizing are missing. |
| `stop_condition` | Strategy result includes failure mode and next validation step. |
| `human_checkpoint` | Required before paper/live deployment or model-service live eval. |
| `learning_sink` | Gotchas, eval cases, workflow updates. |
| `budget_guard` | Prefer small reproducible tests before wide parameter sweeps. |

## Execution Safety Loop

| Field | Value |
|---|---|
| `entry_signal` | User asks to place/cancel order, swap, transfer, approve, change leverage, or start bot. |
| `state_artifacts` | Order draft, risk-tier classification, confirmation checklist, kill-switch note. |
| `actions` | Classify risk tier, build preview, request confirmation, execute only if confirmed. |
| `deterministic_checks` | Venue, account/network, instrument, side/action, quantity, order type, price/slippage, fee/gas, max loss, kill switch. |
| `repair_branch` | Ask only for missing fields that change risk; otherwise stop at draft. |
| `stop_condition` | Draft delivered or confirmed action completed and reported with evidence. |
| `human_checkpoint` | Explicit confirmation required for every Tier 4 action. |
| `learning_sink` | Gotchas, safety policy, evals. |
| `budget_guard` | Never escalate to live execution by inference. |

## Release / GitHub Loop

| Field | Value |
|---|---|
| `entry_signal` | User asks to publish, package, benchmark, or make the skill GitHub-grade. |
| `state_artifacts` | README, VERSION, CHANGELOG, BENCHMARK, validation output, package artifacts. |
| `actions` | Validate, repair, package, smoke-test, label evidence. |
| `deterministic_checks` | Local validator, quick_validate, routing eval JSON parse, package smoke when run. |
| `repair_branch` | Patch the smallest failing file and rerun failing check. |
| `stop_condition` | Selected gates pass and unrun gates are honestly labeled pending. |
| `human_checkpoint` | Required before claiming best-on-GitHub or running live model-service evals. |
| `learning_sink` | Changelog, benchmark notes, gotchas, evals. |
| `budget_guard` | Do not package secrets, caches, bytecode, or transient artifacts. |

## Learn Loop

| Field | Value |
|---|---|
| `entry_signal` | Repeated user correction, route miss, bad source, failed check, or unsafe near-miss. |
| `state_artifacts` | Gotcha entry, eval case, validator term, changelog note. |
| `actions` | Classify the lesson, patch the smallest durable sink, validate. |
| `deterministic_checks` | New eval or validator covers the lesson. |
| `repair_branch` | Revise if lesson causes over-triggering, bloat, or false certainty. |
| `stop_condition` | Lesson is captured and check passes. |
| `human_checkpoint` | Required for persistent project-wide instruction changes. |
| `learning_sink` | `references/gotchas.md`, `evals/`, `scripts/`, `CHANGELOG.md`. |
| `budget_guard` | Do not preserve one-off market data as permanent doctrine. |
