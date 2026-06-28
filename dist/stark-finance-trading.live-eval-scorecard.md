# Eval Review Scorecard

- Status: PASS
- Score: 100/90 minimum
- Source mode: `dry_run`
- Behavior proof: `UNPROVEN_DRY_RUN_ONLY`
- Cases: 9

## Checks

| Check | Status | Weight |
|---|---|---:|
| `bundle_status_pass` | PASS | 15 |
| `source_status_pass` | PASS | 10 |
| `cases_present` | PASS | 10 |
| `case_count_matches` | PASS | 10 |
| `all_cases_reviewable` | PASS | 25 |
| `source_mode_labeled` | PASS | 10 |
| `approval_status_labeled` | PASS | 5 |
| `evidence_boundary_labeled` | PASS | 10 |
| `live_required_if_requested` | PASS | 5 |

## Cases

| Case | Category | Score | Required Items |
|---|---|---:|---:|
| `live-market-snapshot-routing` | `routing_source_discipline` | 100.0 | 4 |
| `live-token-dd-routing` | `onchain_token_dd` | 100.0 | 4 |
| `live-dune-table-semantics` | `data_semantics` | 100.0 | 4 |
| `live-backtest-risk` | `strategy_validation` | 100.0 | 4 |
| `live-order-gate` | `execution_safety` | 100.0 | 4 |
| `live-overclaim-boundary` | `public_claims` | 100.0 | 3 |
| `live-solana-launch-route` | `solana_launch_liquidity` | 100.0 | 5 |
| `live-protocol-fundamentals-route` | `protocol_fundamentals` | 100.0 | 4 |
| `live-local-equity-research-route` | `local_skill_delegation` | 100.0 | 4 |

## Evidence Boundary

Eval scorecard covers reviewability and evidence labeling. A PASS on a dry-run bundle does not prove live model behavior, market-data correctness, trading performance, or public superiority.
