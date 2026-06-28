# Competitive Gap Analysis

- Status: PASS
- Discovery mode: `live_github_search`
- Candidates: 25
- Covered: 16
- Partial runtime: 8
- Gaps: 0
- High-priority backlog: 20

## Category Rollup

| Category | Coverage | Candidates | Runtime/Deferred | Env Missing | Top Candidate |
|---|---|---:|---:|---|---|
| bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | 13 | 3 | - | hummingbot/hummingbot |
| backtest | COVERED_SOURCE_LEVEL | 13 | 5 | - | hummingbot/hummingbot |
| onchain | PARTIAL_RUNTIME | 5 | 4 | etherscan-mcp | hummingbot/hummingbot |
| mcp | COVERED_GENERIC_MCP | 5 | 4 | etherscan-mcp | nirholas/UCAI |
| research | COVERED_SOURCE_LEVEL | 3 | 2 | - | OpenBB-finance/OpenBB |
| broker_execution | PARTIAL_RUNTIME | 3 | 1 | - | hummingbot/hummingbot |
| options_flow | PARTIAL_RUNTIME | 1 | 1 | - | OpenBB-finance/OpenBB |
| general_finance_candidate | WATCHLIST | 1 | 3 | - | jiayaoqijia/cryptoskill |
| market_data | COVERED_SOURCE_LEVEL | 1 | 3 | - | nirholas/UCAI |

## Top Backlog

| Candidate | Stars | Tags | Coverage | Action | Priority | URL |
|---|---:|---|---|---|---:|---|
| hummingbot/hummingbot | 19007 | broker_execution, onchain, backtest, bot_framework | PARTIAL_RUNTIME | requires_secret_or_auth | 140.95 | https://github.com/hummingbot/hummingbot |
| edtechre/pybroker | 3437 | broker_execution, backtest | PARTIAL_RUNTIME | requires_secret_or_auth | 135.75 | https://github.com/edtechre/pybroker |
| ccxt/ccxt | 43094 | backtest, bot_framework, onchain | PARTIAL_RUNTIME | requires_secret_or_auth | 133.44 | https://github.com/ccxt/ccxt |
| 51bitquant/howtrader | 929 | broker_execution, backtest, bot_framework | PARTIAL_RUNTIME | requires_secret_or_auth | 131.78 | https://github.com/51bitquant/howtrader |
| nirholas/UCAI | 34 | mcp, market_data, onchain | PARTIAL_RUNTIME | requires_secret_or_auth | 121.72 | https://github.com/nirholas/UCAI |
| nirholas/cryptocurrency.cv | 248 | mcp, onchain, bot_framework | PARTIAL_RUNTIME | requires_secret_or_auth | 117.76 | https://github.com/nirholas/cryptocurrency.cv |
| freqtrade/freqtrade | 51901 | bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 115.01 | https://github.com/freqtrade/freqtrade |
| OpenBB-finance/OpenBB | 69773 | options_flow, research | PARTIAL_RUNTIME | requires_secret_or_auth | 114.91 | https://github.com/OpenBB-finance/OpenBB |
| wilsonfreitas/awesome-quant | 27080 | bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 113.03 | https://github.com/wilsonfreitas/awesome-quant |
| demcp/awesome-web3-mcp-servers | 610 | mcp, onchain | PARTIAL_RUNTIME | requires_secret_or_auth | 110.5 | https://github.com/demcp/awesome-web3-mcp-servers |
| ccxt/binance-trade-bot | 8712 | bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 109.58 | https://github.com/ccxt/binance-trade-bot |
| paperswithbacktest/awesome-systematic-trading | 8443 | backtest, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 109.49 | https://github.com/paperswithbacktest/awesome-systematic-trading |
| DeviaVir/zenbot | 8261 | backtest, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 109.42 | https://github.com/DeviaVir/zenbot |
| jesse-ai/jesse | 8110 | bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 109.36 | https://github.com/jesse-ai/jesse |
| Thysrael/Horizon | 7528 | mcp, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 109.14 | https://github.com/Thysrael/Horizon |
| blankly-finance/blankly | 2451 | backtest, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 105.73 | https://github.com/blankly-finance/blankly |
| barter-rs/barter-rs | 2181 | backtest, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | add_route_eval | 105.37 | https://github.com/barter-rs/barter-rs |
| kernc/backtesting.py | 8576 | backtest | COVERED_SOURCE_LEVEL | add_route_eval | 83.53 | https://github.com/kernc/backtesting.py |
| ricequant/rqalpha | 6521 | backtest | COVERED_SOURCE_LEVEL | add_route_eval | 82.7 | https://github.com/ricequant/rqalpha |
| fasiondog/hikyuu | 3289 | backtest | COVERED_SOURCE_LEVEL | add_route_eval | 80.62 | https://github.com/fasiondog/hikyuu |

## Candidate Coverage

| Candidate | Stars | Categories | Coverage | Stark Response |
|---|---:|---|---|---|
| hummingbot/hummingbot | 19007 | backtest, bot_framework, broker_execution, onchain | PARTIAL_RUNTIME | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. Keep broker/order surfaces in Tier 4 with account, venue, order, margin, and kill-switch preview before confirmation. Use Dune/Alchemy/Binance where configured; keep Etherscan and endpoint-specific surfaces gated by env/auth checks. |
| edtechre/pybroker | 3437 | backtest, broker_execution | PARTIAL_RUNTIME | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Keep broker/order surfaces in Tier 4 with account, venue, order, margin, and kill-switch preview before confirmation. |
| ccxt/ccxt | 43094 | backtest, bot_framework, onchain | PARTIAL_RUNTIME | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. Use Dune/Alchemy/Binance where configured; keep Etherscan and endpoint-specific surfaces gated by env/auth checks. |
| 51bitquant/howtrader | 929 | backtest, bot_framework, broker_execution | PARTIAL_RUNTIME | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. Keep broker/order surfaces in Tier 4 with account, venue, order, margin, and kill-switch preview before confirmation. |
| nirholas/UCAI | 34 | market_data, mcp, onchain | PARTIAL_RUNTIME | Route by dataset, venue, entitlement, delay status, and timestamp before using market data in decisions. Use MCP as a substrate, but only promote concrete finance routes with source, auth, and safety metadata. Use Dune/Alchemy/Binance where configured; keep Etherscan and endpoint-specific surfaces gated by env/auth checks. |
| nirholas/cryptocurrency.cv | 248 | bot_framework, mcp, onchain | PARTIAL_RUNTIME | Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. Use MCP as a substrate, but only promote concrete finance routes with source, auth, and safety metadata. Use Dune/Alchemy/Binance where configured; keep Etherscan and endpoint-specific surfaces gated by env/auth checks. |
| freqtrade/freqtrade | 51901 | bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. |
| OpenBB-finance/OpenBB | 69773 | options_flow, research | PARTIAL_RUNTIME | Treat flow/greeks/dark-pool data as signal evidence, not execution advice; live credentials and redistribution rules remain external. Route to research/fundamentals tools with metric definitions, source provenance, and no public superiority claim. |
| wilsonfreitas/awesome-quant | 27080 | bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. |
| demcp/awesome-web3-mcp-servers | 610 | mcp, onchain | PARTIAL_RUNTIME | Use MCP as a substrate, but only promote concrete finance routes with source, auth, and safety metadata. Use Dune/Alchemy/Binance where configured; keep Etherscan and endpoint-specific surfaces gated by env/auth checks. |
| ccxt/binance-trade-bot | 8712 | bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. |
| paperswithbacktest/awesome-systematic-trading | 8443 | backtest, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. |
| DeviaVir/zenbot | 8261 | backtest, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. |
| jesse-ai/jesse | 8110 | bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. |
| Thysrael/Horizon | 7528 | bot_framework, mcp | COVERED_WITH_LIVE_GATING_REQUIRED | Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. Use MCP as a substrate, but only promote concrete finance routes with source, auth, and safety metadata. |
| blankly-finance/blankly | 2451 | backtest, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. |
| barter-rs/barter-rs | 2181 | backtest, bot_framework | COVERED_WITH_LIVE_GATING_REQUIRED | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Treat bot frameworks as strategy/runtime substrates behind live_gating_required and kill-switch review. |
| kernc/backtesting.py | 8576 | backtest | COVERED_SOURCE_LEVEL | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. |
| ricequant/rqalpha | 6521 | backtest | COVERED_SOURCE_LEVEL | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. |
| fasiondog/hikyuu | 3289 | backtest | COVERED_SOURCE_LEVEL | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. |
| akfamily/akquant | 1626 | backtest, research | COVERED_SOURCE_LEVEL | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. Route to research/fundamentals tools with metric definitions, source provenance, and no public superiority claim. |
| cinar/indicator | 1188 | backtest | COVERED_SOURCE_LEVEL | Route into backtest/research stacks, keep assumptions explicit, and require simulation or paper proof before live execution. |
| xpaysh/awesome-x402 | 243 | mcp | COVERED_GENERIC_MCP | Use MCP as a substrate, but only promote concrete finance routes with source, auth, and safety metadata. |
| Fincept-Corporation/FinceptTerminal | 27575 | research | COVERED_SOURCE_LEVEL | Route to research/fundamentals tools with metric definitions, source provenance, and no public superiority claim. |
| jiayaoqijia/cryptoskill | 66 | general_finance_candidate | WATCHLIST | Keep on watchlist until it maps to a concrete data, research, broker, onchain, or strategy workflow. |

## Evidence Boundary

Competitive gap analysis combines GitHub discovery, local runtime metadata, route regression, public benchmark, and the curated public tool catalog. It is a planning and backlog artifact, not proof of installability, official status, API entitlement, live model behavior, market-data correctness, trading performance, remote CI completion, or public superiority.
