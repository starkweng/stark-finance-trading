# Tool Router

This router keeps one user-facing skill while preserving tool-specific safety and capability boundaries.

## Installed Or Visible On Stark's Machine

| Surface | Status | Best for | Guardrail |
|---|---|---|---|
| Dune MCP `dune` | Installed, OAuth, 300s timeout | Onchain SQL, dashboards, token/holder/volume/protocol metrics | Use bounded queries and partition filters. Validate table semantics before conclusions. |
| Alchemy MCP `alchemy` | Installed, OAuth | EVM/Solana balances, token/NFT data, tx checks, simulation | Select app first. Read-only by default. |
| Etherscan MCP `etherscan` | Installed, needs `ETHERSCAN_API_KEY` | Verified contracts, tx/event/explorer truth | Missing key means fallback to web/explorer or ask for env setup. |
| Binance skill `binance` | Installed | Binance spot/futures/margin/options/copy-trading/account API via CLI | Auth required. State-changing commands need explicit confirmation. |
| Binance Agentic Wallet | Installed | Web3 wallet status, balances, sends, swaps, limit orders, approvals, prediction markets | High risk. Confirm every state change. Show full token addresses. |
| Binance Web3 skills | Installed | `query-token-info`, `query-token-audit`, `query-address-info`, `crypto-market-rank`, `trading-signal`, `meme-rush` | Read-only except wallet/swap surfaces. Treat upstream scores as signals, not truth. |
| GMGN skills | Installed | Meme/token market, portfolio, smart money, tracking, swap | Swap is high risk. Keep read-only unless explicitly confirmed. |
| BNB Agent Studio | Installed | BNB agent identity/job/tx/block/contract view, ERC-8004/8183/x402 workflows | Default testnet and read-only. Paid or signing actions require confirmation. |
| Alpaca connector | Lazy-loadable via Codex app tools | US equities, options, crypto market data, snapshots, bars, order books | Treat current tool surface as market-data first unless authenticated trading tools are explicitly available. |

## Public Official Or High-Quality External Candidates

Use these when installing new data/execution surfaces or writing a public README. Verify docs live before install.

| Surface | Type | Best for | Default stance |
|---|---|---|---|
| Alpaca MCP | Official broker/data MCP | Stocks, ETFs, options, crypto, account, paper/live trading | Paper first. Good first execution sandbox. |
| OpenBB | Open finance platform / MCP-capable ecosystem | Research terminal, macro, equities, ETFs, crypto, fundamentals, notebooks | Research and data workbench, not first execution layer. |
| QuantConnect MCP / LEAN | Official quant platform | Strategy creation, backtests, optimization, live algorithm deployment | Backtest and paper before live. |
| Alpha Vantage MCP | Official MCP | Stocks, ETFs, FX, crypto, indicators, macro | Low-cost research/data fallback. |
| Financial Modeling Prep MCP | Official MCP | Fundamentals, financial statements, valuation, news, analyst-style data | Equity/DD and comps layer. |
| Twelve Data MCP | Official MCP | Global market data, FX, crypto, indicators, WebSocket | Multi-asset market-data layer. |
| Unusual Whales MCP | Official MCP + skill | Options flow, dark pool, congressional trading, Greek exposure, vol/flow | Research only unless paired with broker execution. |
| Massive / Polygon.io MCP | Official market-data MCP | Stocks, options, FX, crypto, futures, news, fundamentals | Strong institutional data layer. |
| Tradier MCP | Official broker MCP | Stocks/options quotes, orders, multi-leg options, paper/live | Execution-capable; paper first. |
| Robinhood Agentic Trading | Official agentic account | Budget-isolated AI trading account | Very high risk; use only with explicit user setup and limits. |
| cTrader MCP / AI Agent Connect | Official trading-platform MCP | FX/CFD broker workflows, local/remote AI agent connection | Demo first; broker rules matter. |
| TradeStation MCP | Official broker connection announced | Broker-account AI integration | Verify availability and account constraints before use. |
| Coinbase CDP / AgentKit MCP | Official Web3 agent MCP stack | CDP API operations, AgentKit, wallet actions, x402/payment-adjacent workflows | Separate docs/context from wallet actions; transfers/payments are Tier 4. |
| CoinGecko MCP / Skill | Official crypto data MCP + skill | Prices, OHLCV, market cap, NFT, DeFi/onchain data, token metadata | Resolve token IDs/contracts; market data is not execution advice. |
| DeFiLlama API | Official DeFi API | TVL, yields, fees, stablecoins, protocol revenue/category data | Methodology caveats; aggregate data is evidence, not a safety label. |
| Databento API | Official institutional data API | Historical/live market data for serious strategy research | Check dataset, venue, entitlement, latency, and cost before relying on it. |
| IBKR TWS API / community MCP candidates | Official API plus community MCP wrappers | Multi-asset broker API via TWS/Gateway | Do not treat community MCP as official; paper/live and permissions must be explicit. |
| Hummingbot | Open-source trading framework | Crypto market-making, arbitrage, exchange connectors | Use sandbox/config review before any live bot. |
| Freqtrade | Open-source trading bot | Crypto strategy research, backtesting, dry-run bot execution | Dry-run first, strict risk config. |
| LEAN engine | Open-source QuantConnect engine | Multi-asset backtest/live architecture | Prefer reproducible backtests before deployment. |
| NautilusTrader | Open-source quant trading platform | Event-driven backtest/live architecture, advanced strategy engineering | Require formal strategy spec before live adapters. |
| CCXT | Open-source exchange library | Crypto exchange connector substrate for custom adapters | Low-level power surface; rate-limit, cancel, balance, and order-id safety required. |

## Route By Task

### Market Snapshot

Use Alpaca for equities/options/US crypto when visible. Use Binance/GMGN/CoinGecko for crypto venue reality. Use Alpha Vantage/Twelve Data/Massive/Databento as external candidates. Return timestamp, venue/feed, delay status, and spread/depth if the user is trading.

### Token And Onchain Due Diligence

Use:

1. `query-token-info` for metadata and live token market fields.
2. `query-token-audit` for audit flags.
3. Dune for historical holder/transfer/volume cohorts.
4. Alchemy for wallet/token/tx state.
5. Etherscan for verified contracts and explorer truth.
6. GMGN/Dex surfaces for liquidity and market display behavior.

Do not treat honeypot/mintable/proxy labels as final until cross-checked with contract behavior or simulation when needed.

### Smart-Money And Meme Scan

Use `crypto-market-rank`, `trading-signal`, `meme-rush`, and GMGN. Summaries must include freshness, signal count, exit rate or invalidation signal when available, liquidity, holder risk, and whether smart money already exited.

### Equity / Fundamental Research

Use OpenBB/FMP/Alpha Vantage/Massive/Twelve Data/Databento where installed or available. For DeFi protocol or crypto sector claims, add DeFiLlama/CoinGecko where useful. DeFiLlama TVL, yields, and fees have methodology gaps and are not a direct safety or trade signal. For current public-company or macro claims, verify against official filings, exchange pages, or primary news when high stakes.

### Options Flow

Use Unusual Whales for flow/dark-pool/congressional data, then Alpaca/Tradier for quotes/contracts if available. Never infer an option trade recommendation from flow alone.

### Backtest / Strategy Research

Use QuantConnect/LEAN, NautilusTrader, Freqtrade, Hummingbot, CCXT-backed local adapters, or local backtest scripts depending on venue and rigor. Include dataset, period, universe, fees/slippage, position sizing, drawdown, out-of-sample plan, and live adapter boundary. Reject overfit claims.

### Execution

Execution-capable routes include Binance CLI, Binance Agentic Wallet, Coinbase CDP/AgentKit wallet actions, Alpaca trading, Tradier, Robinhood Agentic Trading, cTrader, IBKR/TWS wrappers, Hummingbot, Freqtrade, CCXT-backed adapters, NautilusTrader, and QuantConnect live. All must pass `references/safety-policy.md`.

### FX / CFD / XAUUSD

Use cTrader and broker-specific evidence for FX/CFD workflows, especially XAUUSD margin, lot, leverage, stop-out, and account-risk questions. Keep account reads separate from order preview and live actions.

### IBKR / TWS

Use official IBKR/TWS API docs as the primary source. Community MCP wrappers are candidates only; do not treat community MCP as official. Before any draft action, require account scope, paper/live mode, permissions, order preview capability, max-loss rule, and kill switch.

## Merge Logic

Do not create separate user-facing skills for every vendor by default. Keep vendor wrappers only when a tool needs special auth or command syntax. The primary user-facing route is `stark-finance-trading`; vendor-specific skills remain implementation details.
