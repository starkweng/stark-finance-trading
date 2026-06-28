# stark-finance-trading Integration Activation Plan

- Status: PASS
- Catalog tools: 50
- Runtime report status: `PASS`
- Ready now: 11
- Quick activations: 2
- Priority install/auth backlog: 23
- High-risk confirmation surfaces: 14

## Activation Stage Counts

| Stage | Count |
|---|---:|
| `install_or_auth_candidate` | 23 |
| `lazy_load_available` | 1 |
| `needs_env` | 1 |
| `ready_now` | 11 |
| `watchlist` | 14 |

## Top Activation Actions

| Tool | Stage | Safety | Next action |
|---|---|---|---|
| `etherscan-mcp` | `needs_env` | `auth_or_install_review` | Set missing env vars for etherscan-mcp: ETHERSCAN_API_KEY; rerun runtime capability scan. |
| `alpaca-mcp` | `lazy_load_available` | `auth_or_install_review` | Use deferred connector discovery when the prompt needs this surface; confirm auth/entitlement before use. |
| `helius-mcp` | `install_or_auth_candidate` | `auth_or_install_review` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `coingecko-mcp` | `install_or_auth_candidate` | `auth_or_install_review` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `massive-polygon-mcp` | `install_or_auth_candidate` | `auth_or_install_review` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `the-graph-subgraph-mcp` | `install_or_auth_candidate` | `auth_or_install_review` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `token-terminal-mcp` | `install_or_auth_candidate` | `auth_or_install_review` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `unusual-whales-mcp` | `install_or_auth_candidate` | `auth_or_install_review` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `nautilus-trader` | `install_or_auth_candidate` | `auth_or_install_review` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `bingx-ai-skills` | `install_or_auth_candidate` | `high_risk_requires_confirmation` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `bybit-ai-trading-skills` | `install_or_auth_candidate` | `high_risk_requires_confirmation` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `ctrader-ai-agent-connect` | `install_or_auth_candidate` | `high_risk_requires_confirmation` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `deribit-api` | `install_or_auth_candidate` | `high_risk_requires_confirmation` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `ibkr-tws-api` | `install_or_auth_candidate` | `high_risk_requires_confirmation` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |
| `kraken-mcp` | `install_or_auth_candidate` | `high_risk_requires_confirmation` | Live-check the official source, install/connect only if Stark needs this route, then rerun runtime scan and route evals. |

## Ready Now

| Tool | Runtime | Best for |
|---|---|---|
| `lean` | `local_skill_backed` | Reproducible multi-asset strategy research and local/CI backtest infrastructure. |
| `quantconnect-mcp` | `local_skill_backed` | Strategy creation, LEAN backtesting, optimization, and deployment workflow preparation. |
| `binance-skills-hub` | `enabled_plugin` | Binance account/API workflows and Binance Web3 token intelligence helpers. |
| `alchemy-mcp` | `configured_mcp` | Wallet, token, NFT, transaction, and chain-state checks across EVM/Solana routes. |
| `dune-mcp` | `configured_mcp` | Onchain SQL, dashboard-backed metrics, holder/transfer cohorts, protocol or token historical analysis. |
| `openbb` | `local_skill_backed` | Open finance research terminal, multi-source datasets, notebooks, macro/equity/fundamental research. |
| `freqtrade` | `local_skill_backed` | Crypto strategy research, backtesting, hyperopt, dry-run bot execution, and risk config review. |
| `hummingbot` | `local_skill_backed` | Crypto market-making, arbitrage, exchange connector configuration, and bot risk review. |
| `quicknode-mcp` | `enabled_plugin` | Web3 endpoint inventory, endpoint setup, chain support, and infrastructure security rules. |
| `fmp-mcp` | `local_skill_backed` | Fundamentals, statements, valuation, market news, and equity DD scaffolding. |
| `ccxt` | `local_skill_backed` | Crypto exchange connector substrate for custom data and execution adapters. |

## High-Risk Requires Confirmation

| Tool | Tier | Gate |
|---|---:|---|
| `bingx-ai-skills` | 4 | `high_risk_requires_confirmation` |
| `bybit-ai-trading-skills` | 4 | `high_risk_requires_confirmation` |
| `ctrader-ai-agent-connect` | 4 | `high_risk_requires_confirmation` |
| `deribit-api` | 4 | `high_risk_requires_confirmation` |
| `ibkr-tws-api` | 4 | `high_risk_requires_confirmation` |
| `kraken-mcp` | 4 | `high_risk_requires_confirmation` |
| `metatrader5-python` | 4 | `high_risk_requires_confirmation` |
| `oanda-v20-api` | 4 | `high_risk_requires_confirmation` |
| `okx-api` | 4 | `high_risk_requires_confirmation` |
| `tradestation-mcp` | 4 | `high_risk_requires_confirmation` |
| `tradier-mcp` | 4 | `high_risk_requires_confirmation` |
| `tradingview-broker-api` | 4 | `high_risk_requires_confirmation` |
| `coinbase-cdp-agentkit` | 4 | `high_risk_requires_confirmation` |
| `stripe-agent-toolkit` | 4 | `high_risk_requires_confirmation` |

## Evidence Boundary

Integration activation plan is a local routing and setup plan. It uses catalog metadata and runtime-scan statuses without printing secret values. It does not prove OAuth validity, API entitlement, live tool availability, market-data correctness, trading performance, remote CI completion, or public superiority.
