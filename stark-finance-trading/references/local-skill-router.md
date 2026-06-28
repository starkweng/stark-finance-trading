# Local Skill Router

This file maps Stark's installed finance, trading, Web3-market, and investment skills into one user-facing route: `stark-finance-trading`.

Refresh machine-specific evidence with:

```bash
python3 scripts/discover_local_skill_inventory.py --skill-root . --out dist/stark-finance-trading.local-skill-inventory.json --markdown dist/stark-finance-trading.local-skill-inventory.md --json
```

Default stance:

```text
User-facing entry: stark-finance-trading
Implementation detail: vendor/local skill/MCP/API
Escalation: read-only -> research/model -> paper/demo -> explicit live confirmation
```

Do not create a new user-facing `stark-*` skill for every vendor or finance workflow. Add a separate user-facing skill only when the workflow has a different primary intent, such as tokenomics design, market operations, legal work, or visual packaging.

## Merge Classes

| Class | Merge stance | Examples | When to use |
|---|---|---|---|
| Core router | Primary front door | `stark-finance-trading` | Market data, trading research, onchain DD, backtests, signals, portfolio/risk, execution prep. |
| Web3 market/onchain helpers | Internal read-only or guarded delegation | `dune`, `alchemy`, `query-token-info`, `query-token-audit`, `query-address-info`, `crypto-market-rank`, `trading-signal`, `meme-rush`, `gmgn-market`, `gmgn-token`, `gmgn-portfolio`, `gmgn-track` | Token DD, pump.fun/Solana/BSC scans, holder/liquidity/smart-money research. |
| Execution-capable helpers | Guarded delegation only | `binance`, `derivatives-trading-coin-futures`, `binance-agentic-wallet`, `gmgn-swap`, `gmgn-cooking`, `alpha` | Order drafts, wallet/swap prep, bot or launchpad actions. Tier 4 confirmation required before state change. |
| Equity and public-market research | Internal research delegation | `daisy-financial-research`, `equity-research`, `earnings-analysis`, `earnings-preview`, `earnings-preview-beta`, `idea-generation`, `catalyst-calendar`, `morning-note`, `thesis-tracker`, `tear-sheet` | Stock/sector DD, earnings preview/update, catalyst watch, investment memo inputs. |
| Valuation and model helpers | Internal modeling delegation | `dcf-model`, `comps-analysis`, `3-statement-model`, `lbo-model`, `merger-model`, `model-update`, `deck-refresh`, `returns-analysis` | DCF, comps, estimates, financial-model refresh, deal math. Research output is not a trade order. |
| Fixed-income, FX, and derivatives helpers | Internal specialist delegation | `bond-futures-basis`, `bond-relative-value`, `fixed-income-portfolio`, `fx-carry-trade`, `swap-curve-strategy`, `option-vol-analysis`, `derivatives-trading-coin-futures` | Rates, bonds, FX carry, options vol, futures basis, coin futures research. |
| Portfolio and client/institutional workflows | Internal portfolio delegation | `portfolio-monitoring`, `portfolio-rebalance`, `client-report`, `client-review` | Portfolio drift, rebalancing drafts, performance review, client-ready market commentary. |
| Deal and private-market workflows | Boundary-aware delegation | `deal-screening`, `deal-sourcing`, `deal-tracker`, `dd-checklist`, `ic-memo`, `cim-builder` | PE/M&A/deal diligence. Use finance evidence, but do not convert CIM/deal data into public-market trade pressure. |
| Finance ops and accounting-adjacent helpers | Finance-ops route, not trading signal | `audit-xls`, `accrual-schedule`, `gl-recon`, `break-trace`, `roll-forward`, `kyc-rules` | Model audit, reconciliation, compliance evidence, close support. Not market signals by default. |
| Stark adjacent strategic skills | Route out when primary intent differs | `stark-liquidity-strategy`, `stark-capital-strategy`, `stark-tokenomics-planner`, `stark-data-analytics`, `stark-market-ops`, `stark-mkt-ops` | Liquidity mechanism, capital strategy, tokenomics, broad data analytics, market/community ops. |

## Routing Rules

1. Keep `stark-finance-trading` loaded when the user asks for market evidence, investment research, risk, portfolio implications, backtest, trading setup, onchain token DD, or execution prep.
2. Use local helper skills as specialist references or implementation details. Name them only when it helps the user understand the route.
3. If a helper can place trades, swaps, transfers, approvals, launch tokens, or change account/bot state, load `safety-policy.md` first and keep the output at draft/preflight unless the user gives exact confirmation.
4. If the request is pure tokenomics, campaign ops, copywriting, design, legal/tax, or project governance without market/trading evidence, route away from this skill.
5. If the request mixes domains, keep finance/trading evidence inside this skill and explicitly hand off the non-finance part.

## Common Routes

| User intent | Primary route | Helper route | Safety note |
|---|---|---|---|
| Earnings preview or update | `workflows.md` Equity / Macro / Fundamentals Research | `earnings-preview`, `earnings-preview-beta`, `earnings-analysis`, `equity-research` | Do not turn earnings view into a live order without fresh quote/risk and confirmation. |
| DCF/comps valuation | Equity / Macro / Fundamentals Research | `dcf-model`, `comps-analysis`, `model-update` | Valuation is one input, not a full-position recommendation. |
| Options vol or flow | Options Flow | `option-vol-analysis`, Unusual Whales, Tradier/Alpaca | Flow and vol signals require liquidity, spread, and max-loss checks. |
| Bond/futures/rates trade | Market Snapshot or Strategy Backtest | `bond-futures-basis`, `bond-relative-value`, `swap-curve-strategy`, `fixed-income-portfolio` | State assumptions, curve source, funding, margin, and stress path. |
| Portfolio rebalance | Portfolio/Risk workflow | `portfolio-rebalance`, `portfolio-monitoring`, `client-report` | Draft only; tax, account, and execution details need confirmation. |
| Meme token research | Token Due Diligence / Smart-Money Scan | `gmgn-token`, `gmgn-market`, `gmgn-track`, `query-token-info`, `query-token-audit`, `meme-rush` | Resolve chain/address before any quote or draft. |
| Meme/token swap or launch | Execution Prep | `gmgn-swap`, `gmgn-cooking`, `binance-agentic-wallet` | Tier 4. Show full address, notional, slippage, gas, max loss, and kill path. |
| Binance spot/futures order prep | Execution Prep / Strategy Backtest | `binance`, `derivatives-trading-coin-futures`, `alpha` | Testnet/paper where possible; live requires explicit confirmation. |
| Liquidity or market-making design | Market-Making / Liquidity War Room | `stark-liquidity-strategy`, Hummingbot, Freqtrade, CCXT | Strategy and mechanism can be designed here; live bot deployment is Tier 4. |
| Deal screen / CIM / IC memo | Private-market finance route | `deal-screening`, `ic-memo`, `cim-builder`, `dd-checklist` | Private deal evidence is not a public-market signal by itself. |
| Accounting or workbook audit | Finance ops route | `audit-xls`, `gl-recon`, `break-trace`, `roll-forward` | Keep as evidence/model integrity; do not infer market action from accounting breaks alone. |

## Learn Loop

When Stark corrects a route, promote the correction to one of:

- this file, if it changes helper selection;
- `references/gotchas.md`, if it is a repeated failure mode;
- `evals/routing-evals.json`, if trigger accuracy changed;
- `evals/adversarial-evals.json`, if the failure involved unsafe escalation or overclaiming;
- `benchmarks/competitive-task-cases.json`, if the route strengthens the public benchmark claim.
