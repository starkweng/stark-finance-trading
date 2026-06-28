# Live Eval Signoff

- Status: PASS
- Approval: PENDING
- Skill: `.`
- Eval set: `benchmarks/competitive-task-cases.json`
- Cases: 12
- Sandbox: `read-only`

## Exact Command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/codex_eval.py --skill-path . --eval-set benchmarks/competitive-task-cases.json --out-dir ../dist/competitive-eval --sandbox read-only --timeout 180 --require-approved-signoff --signoff ../dist/stark-finance-trading.competitive-eval-signoff.json
```

## Data Surfaces
- skill source files
- eval prompts identified by hashes
- no broker credentials
- no wallet keys
- no CEX API secrets
- no live order tools unless separately approved

## Must Not Do
- place live trades
- send wallet transactions
- approve token allowances
- start live bots
- claim benchmark superiority from dry-run or signoff evidence

## Case Hashes

| Case | Prompt SHA256 |
|---|---|
| `multi_asset_market_snapshot` | `5ff440241cb79337e87e74c0f3ad5524f3adcc5aca076d8cee1e01eb19227d0f` |
| `pumpfun_daily_issuance` | `0062882f5a657da31f203717d2b37428a236b798022819e01e2982aa2d86f590` |
| `options_flow_to_order_draft` | `98e509c58eabf9e43af3d800dbf2dc71f51bd89f030e56d8c0f11a53f6392142` |
| `crypto_bot_strategy_review` | `c47ec8871629925dc5c99f8e8c02cbcfb556e2509d73ae79a545b9a5d87643f8` |
| `fx_cfd_xau_margin_review` | `a41f8bdfb40c7eb19af91e1e16212dc41cdc97b9ba1b357df3425bab3a91346f` |
| `web3_wallet_payment_action` | `c058b924024884a639f357a47ed083c7ee3a95308f5d00b72e6750d15b563bf1` |
| `defi_protocol_market_research` | `e599c04268c8cfe0e3c998ac864c75d92282ffeccbc1a521b4d3d3cebd47f099` |
| `ibkr_api_wrapper_boundary` | `c825fd18c9d3e1274796d270c8b28f9d5444cdb9eceecfdc6f4072357e5873f9` |
| `solana_meme_launch_route` | `a2f210de1ebf84e21382c270be69ef1f5f2764cead50fcc6321a72a6130d8cb0` |
| `protocol_fundamentals_router` | `c57a1c663cf51f16dd070bd59639b037cb1f03af5bf0c64d1c818e04cff06c66` |
| `finance_infra_not_trading` | `f28e313b64d60e212d43543f93b6de392f2c2cad4b2550e12fa39e1f1f813bc2` |
| `local_skill_consolidation_router` | `519201fc222d41bc0f636de65293ce1cd6863c8cff8437979c6e4621b9de5782` |

## Evidence Boundary

This packet proves live-eval readiness and approval status only. It does not prove model behavior.
