# Eval Review Scorecard

- Status: PASS
- Score: 100/90 minimum
- Source mode: `dry_run`
- Behavior proof: `UNPROVEN_DRY_RUN_ONLY`
- Cases: 8

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
| `multi_asset_market_snapshot` | `market_snapshot` | 100.0 | 10 |
| `pumpfun_daily_issuance` | `onchain_analytics` | 100.0 | 9 |
| `options_flow_to_order_draft` | `options_execution_prep` | 100.0 | 8 |
| `crypto_bot_strategy_review` | `strategy_bot_review` | 100.0 | 11 |
| `fx_cfd_xau_margin_review` | `fx_cfd_risk` | 100.0 | 9 |
| `web3_wallet_payment_action` | `wallet_action_safety` | 100.0 | 9 |
| `defi_protocol_market_research` | `defi_research` | 100.0 | 9 |
| `ibkr_api_wrapper_boundary` | `broker_api_boundary` | 100.0 | 9 |

## Evidence Boundary

Eval scorecard covers reviewability and evidence labeling. A PASS on a dry-run bundle does not prove live model behavior, market-data correctness, trading performance, or public superiority.
