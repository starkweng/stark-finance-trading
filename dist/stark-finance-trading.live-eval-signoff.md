# Live Eval Signoff

- Status: PASS
- Approval: PENDING
- Skill: `.`
- Eval set: `evals/live-behavior-evals.json`
- Cases: 6
- Sandbox: `read-only`

## Exact Command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/codex_eval.py --skill-path . --eval-set evals/live-behavior-evals.json --out-dir ../dist/live-eval --sandbox read-only --timeout 180 --require-approved-signoff --signoff ../dist/stark-finance-trading.live-eval-signoff.json --max-cases 6
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
| `live-market-snapshot-routing` | `2e148d3078a391a79e3addf6b17959aabc89038a6da9fb0059f534a9cbea3052` |
| `live-token-dd-routing` | `8e9e88d13e8d5edc3be31effe32481b3e959ffeb1cc88d24c9e2539e7e09ab60` |
| `live-dune-table-semantics` | `0062882f5a657da31f203717d2b37428a236b798022819e01e2982aa2d86f590` |
| `live-backtest-risk` | `0579693594c8c938cfac2cccd9481602a67bcccea89c3a59768083866c121db7` |
| `live-order-gate` | `8fc3f70985f32eedc52d479b7b98ad4249b141925f93a14b1170e443d5bb0a79` |
| `live-overclaim-boundary` | `366fef960227b86c122e247fa99a27dfe29314f15bdc8fcb11952924a35de1b1` |

## Evidence Boundary

This packet proves live-eval readiness and approval status only. It does not prove model behavior.
