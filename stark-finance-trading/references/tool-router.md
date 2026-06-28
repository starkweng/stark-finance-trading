# Tool Router

This router keeps one user-facing skill while preserving tool-specific safety and capability boundaries.

For deterministic routing and public-release validation, keep the machine-readable catalog in `references/public-tool-catalog.json` aligned with this human router. The catalog records official source status, route tags, installed status, default action tier, auth/setup needs, merge policy, and safety notes for each major public MCP/API/framework candidate.

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
| Local finance/trading skill inventory | Installed across `.agents` and `.codex` skill roots | Earnings, equity research, valuation, bonds/rates/FX, portfolio, PE/deal, finance ops, GMGN/Binance/Web3 helper workflows | Route through `references/local-skill-router.md`; keep `stark-finance-trading` as the user-facing front door. |
| Alpaca connector | Lazy-loadable via Codex app tools | US equities, options, crypto market data, snapshots, bars, order books | Treat current tool surface as market-data first unless authenticated trading tools are explicitly available. |
| QuickNode connector | Lazy-loadable via Codex app tools | Web3 endpoint inventory, endpoint creation, chain support, endpoint security rules | Infrastructure/admin route only. Do not expose endpoint secrets; avoid changing endpoint security without explicit confirmation. |

## Public Official Or High-Quality External Candidates

Use these when installing new data/execution surfaces or writing a public README. Verify docs live before install.

| Surface | Type | Best for | Default stance |
|---|---|---|---|
| Alpaca MCP | Official broker/data MCP | Stocks, ETFs, options, crypto, account, paper/live trading | Paper first. Good first execution sandbox. |
| OpenBB | Open finance platform / MCP-capable ecosystem | Research terminal, macro, equities, ETFs, crypto, fundamentals, notebooks | Research and data workbench, not first execution layer. |
| QuantConnect MCP / LEAN | Official quant platform | Strategy creation, backtests, optimization, live algorithm deployment | Backtest and paper before live. |
| Alpha Vantage MCP | Official MCP | Stocks, ETFs, FX, crypto, indicators, macro | Low-cost research/data fallback. |
| Financial Modeling Prep MCP | Official MCP | Fundamentals, financial statements, valuation, news, analyst-style data | Equity/DD and comps layer. |
| FactSet MCP | Official MCP | Institutional financial data, estimates, fundamentals, portfolio/security analytics | High-grade data route; check entitlement, usage limits, and redistribution constraints. |
| Twelve Data MCP | Official MCP | Global market data, FX, crypto, indicators, WebSocket | Multi-asset market-data layer. |
| Unusual Whales MCP | Official MCP + skill | Options flow, dark pool, congressional trading, Greek exposure, vol/flow | Research only unless paired with broker execution. |
| Massive / Polygon.io MCP | Official market-data MCP | Stocks, options, FX, crypto, futures, news, fundamentals | Strong institutional data layer. |
| Tradier MCP | Official broker MCP | Stocks/options quotes, orders, multi-leg options, paper/live | Execution-capable; paper first. |
| Robinhood Agentic Trading | Official agentic account | Budget-isolated AI trading account | Very high risk; use only with explicit user setup and limits. |
| cTrader MCP / AI Agent Connect | Official trading-platform MCP | FX/CFD broker workflows, local/remote AI agent connection | Demo first; broker rules matter. |
| TradeStation MCP | Official broker connection announced | Broker-account AI integration | Verify availability and account constraints before use. |
| Coinbase CDP / AgentKit MCP | Official Web3 agent MCP stack | CDP API operations, AgentKit, wallet actions, x402/payment-adjacent workflows | Separate docs/context from wallet actions; transfers/payments are Tier 4. |
| CoinGecko MCP / Skill | Official crypto data MCP + skill | Prices, OHLCV, market cap, NFT, DeFi/onchain data, token metadata | Resolve token IDs/contracts; market data is not execution advice. |
| CoinMarketCap MCP | Official crypto market-data MCP/API | Crypto rankings, quotes, market pairs, exchange/category market data | Good neutral market-rank cross-check. Resolve IDs/contracts; data is not execution advice. |
| Token Terminal MCP | Official crypto fundamentals MCP | Protocol revenue, fees, users, sectors, chain/project financial metrics | Use for protocol DD and investable narrative evidence; methodology caveats required. |
| DeFiLlama API | Official DeFi API | TVL, yields, fees, stablecoins, protocol revenue/category data | Methodology caveats; aggregate data is evidence, not a safety label. |
| Helius MCP | Official Solana MCP / agent tools | Solana wallet, tx, token/NFT/DAS, webhooks, streaming, token launch analysis | Solana and pump.fun-adjacent route; distinguish reads, infra changes, and transactions. |
| Jupiter APIs | Official Solana liquidity APIs | Solana swap quotes, routing, token/lending/liquidity integrations | Quote/intelligence route unless wallet signing is explicitly requested and confirmed. |
| DexScreener API | Official DEX market API | DEX pairs, liquidity, price action, token market display behavior | Market-display cross-check only; community MCP wrappers are non-official until verified. |
| Stripe MCP / Agent Toolkit | Official financial/payment agent toolkit | Payment, billing, checkout, treasury/revenue operations | Finance-ops route, not trading research or market signal. State changes require confirmation. |
| Plaid API | Official financial connectivity API | Bank/account connectivity, balances, transactions, cashflow evidence | Finance-data route, not brokerage execution. Sensitive financial data requires minimal-scope handling. |
| Databento API | Official institutional data API | Historical/live market data for serious strategy research | Check dataset, venue, entitlement, latency, and cost before relying on it. |
| IBKR TWS API / community MCP candidates | Official API plus community MCP wrappers | Multi-asset broker API via TWS/Gateway | Do not treat community MCP as official; paper/live and permissions must be explicit. |
| Hummingbot | Open-source trading framework | Crypto market-making, arbitrage, exchange connectors | Use sandbox/config review before any live bot. |
| Freqtrade | Open-source trading bot | Crypto strategy research, backtesting, dry-run bot execution | Dry-run first, strict risk config. |
| LEAN engine | Open-source QuantConnect engine | Multi-asset backtest/live architecture | Prefer reproducible backtests before deployment. |
| NautilusTrader | Open-source quant trading platform | Event-driven backtest/live architecture, advanced strategy engineering | Require formal strategy spec before live adapters. |
| CCXT | Open-source exchange library | Crypto exchange connector substrate for custom adapters | Low-level power surface; rate-limit, cancel, balance, and order-id safety required. |

## Route By Task

### Market Snapshot

Use Alpaca for equities/options/US crypto when visible. Use Binance/GMGN/CoinGecko/CoinMarketCap for crypto venue reality. Use Alpha Vantage/Twelve Data/Massive/Databento/FactSet as external candidates. Return timestamp, venue/feed, delay status, and spread/depth if the user is trading.

### Token And Onchain Due Diligence

Use:

1. `query-token-info` for metadata and live token market fields.
2. `query-token-audit` for audit flags.
3. Dune for historical holder/transfer/volume cohorts.
4. Alchemy for wallet/token/tx state.
5. Etherscan for verified contracts and explorer truth.
6. GMGN/DexScreener/Dex surfaces for liquidity and market display behavior.
7. CoinGecko/CoinMarketCap for neutral market cap, pair, category, and price context.

Do not treat honeypot/mintable/proxy labels as final until cross-checked with contract behavior or simulation when needed.

### Solana / Pump.fun / Launch Flow

Use Helius for Solana account, transaction, token/NFT/DAS, webhook, and streaming context. Use Jupiter for Solana quote/liquidity route checks and DexScreener for pair/liquidity display. Use Dune for historical issuance/cohort metrics when the data is indexed. Use CoinGecko/CoinMarketCap only after token identity is resolved. Swaps, transfers, approvals, and wallet signatures are Tier 4.

### Smart-Money And Meme Scan

Use `crypto-market-rank`, `trading-signal`, `meme-rush`, GMGN, DexScreener, and chain-specific sources such as Helius for Solana. Summaries must include freshness, signal count, exit rate or invalidation signal when available, liquidity, holder risk, and whether smart money already exited.

### Equity / Fundamental Research

Use OpenBB/FMP/Alpha Vantage/Massive/Twelve Data/Databento/FactSet where installed or available. Use `references/local-skill-router.md` for local helpers such as `equity-research`, `earnings-preview`, `earnings-analysis`, `dcf-model`, `comps-analysis`, `model-update`, and `catalyst-calendar`. For DeFi protocol or crypto sector claims, add Token Terminal, DeFiLlama, Dune, CoinGecko, and CoinMarketCap where useful. DeFiLlama TVL, yields, and fees have methodology gaps and are not a direct safety or trade signal. Token Terminal financial metrics are stronger for protocol fundamentals, but still need methodology and timestamp caveats. For current public-company or macro claims, verify against official filings, exchange pages, or primary news when high stakes.

For institutional or investor-grade TradFi work, consider FactSet before lower-grade sources if entitlement exists. Preserve source timestamps, metric definitions, and redistribution limits.

### Protocol Fundamentals

Use Token Terminal for protocol revenue, fees, users, sector, chain, and project financial metrics. Cross-check DeFiLlama TVL/fees/yields, Dune onchain cohorts, and CoinGecko/CoinMarketCap token market context. Never convert revenue/TVL growth directly into a buy/sell recommendation.

### Options Flow

Use Unusual Whales for flow/dark-pool/congressional data, then Alpaca/Tradier for quotes/contracts if available. Never infer an option trade recommendation from flow alone.

### Backtest / Strategy Research

Use QuantConnect/LEAN, NautilusTrader, Freqtrade, Hummingbot, CCXT-backed local adapters, or local backtest scripts depending on venue and rigor. Include dataset, period, universe, fees/slippage, position sizing, drawdown, out-of-sample plan, and live adapter boundary. Reject overfit claims.

For local specialist skills, consult `references/local-skill-router.md`: `option-vol-analysis`, `bond-futures-basis`, `bond-relative-value`, `fx-carry-trade`, `swap-curve-strategy`, `fixed-income-portfolio`, and `portfolio-rebalance` are helper routes, not separate user-facing entry points.

### Execution

Execution-capable routes include Binance CLI, Binance Agentic Wallet, Coinbase CDP/AgentKit wallet actions, Alpaca trading, Tradier, Robinhood Agentic Trading, cTrader, IBKR/TWS wrappers, Hummingbot, Freqtrade, CCXT-backed adapters, NautilusTrader, and QuantConnect live. All must pass `references/safety-policy.md`.

### Financial Infrastructure / Payments

Use Stripe for payment, billing, checkout, treasury/revenue, and financial-ops workflows. Use Plaid for account connectivity, balances, transactions, and cashflow evidence. These are not market-data or trade-execution surfaces; route them as financial infrastructure unless the user explicitly connects them to portfolio, treasury, or risk analysis. Treat sensitive banking/payment data with minimal-scope handling.

### Web3 Infrastructure

Use QuickNode and Alchemy infrastructure routes for endpoint inventory, chain/network support, RPC access, webhook-style routing, and security rules. Endpoint creation or security-rule changes are administrative state changes and need explicit confirmation. Never print endpoint tokens or RPC secrets.

### FX / CFD / XAUUSD

Use cTrader and broker-specific evidence for FX/CFD workflows, especially XAUUSD margin, lot, leverage, stop-out, and account-risk questions. Keep account reads separate from order preview and live actions.

### IBKR / TWS

Use official IBKR/TWS API docs as the primary source. Community MCP wrappers are candidates only; do not treat community MCP as official. Before any draft action, require account scope, paper/live mode, permissions, order preview capability, max-loss rule, and kill switch.

## Merge Logic

Do not create separate user-facing skills for every vendor by default. Keep vendor wrappers only when a tool needs special auth or command syntax. The primary user-facing route is `stark-finance-trading`; vendor-specific skills remain implementation details.

Local finance skills follow the same merge logic. Keep earnings, valuation, portfolio, bond/rates/FX, PE/deal, finance-ops, GMGN, and Binance helpers behind `stark-finance-trading` unless the user's primary intent clearly belongs to another Stark skill such as `stark-tokenomics-planner`, `stark-market-ops`, `stark-mkt-ops`, `stark-liquidity-strategy`, or `stark-capital-strategy`.
