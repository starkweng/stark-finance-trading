# Public Comparison Snapshot - 2026-06-28

This is a source-level benchmark snapshot, not a superiority claim. It records
the public bar that `stark-finance-trading` must meet or beat through routing,
source discipline, safety boundaries, and package evidence.

## Conclusion

The strongest public finance/trading surfaces are vendor-deep: Alpaca, Tradier,
Robinhood, IBKR, cTrader, OANDA, MetaTrader 5, and TradingView for
broker/platform workflows; Binance, Bybit, Kraken, OKX, BingX, and Deribit for
CEX, derivatives, and crypto-options workflows; Dune, Alchemy,
Etherscan, The Graph, Goldsky, Moralis, GoldRush/Covalent, SQD, Coinbase,
QuickNode, CoinGecko, CoinMarketCap, Token Terminal, DeFiLlama, Helius,
Jupiter, DexScreener, and Binance for crypto/Web3 data, infrastructure,
indexed data, and actions; QuantConnect, LEAN, NautilusTrader, Hummingbot,
Freqtrade, and CCXT for strategy or bot engineering; OpenBB, Databento,
FactSet, FMP, Twelve Data, Alpha Vantage, Massive/Polygon.io, and Unusual
Whales, Finnhub, and Nasdaq Data Link for research and data; and Stripe/Plaid for adjacent financial
infrastructure. The
Stark skill should not try to replace them. Its edge is a single Stark-facing
route that chooses the right surface, labels evidence quality, and blocks unsafe
escalation.

## Comparison Matrix

| Candidate | Public status | Primary strength | Stark route edge |
|---|---|---|---|
| Alpaca MCP | Official | Broker-backed market data and paper/live trading | Separate market lookup from execution; paper first. |
| OpenBB | Official open source | Broad research workbench | Lighter route across Web3, TradFi, and execution risk. |
| QuantConnect MCP / LEAN | Official | Backtests, optimization, live algorithm handoff | Force assumptions, slippage, MDD, and approval gates. |
| Alpha Vantage MCP | Official | Market data and indicators | Cross-check data gaps and avoid indicator-as-advice. |
| Financial Modeling Prep MCP | Official | Fundamentals and valuation inputs | Tie fundamentals to timestamped DD workflow. |
| FactSet MCP | Official | Institutional financial data and analytics | Label entitlement, definitions, timestamps, and redistribution limits. |
| Twelve Data MCP | Official | Global multi-asset data | Label venue, delay status, and decision-grade limits. |
| Unusual Whales MCP | Official | Options flow and dark-pool signals | Treat flow as signal evidence, not trade instruction. |
| Massive / Polygon.io MCP | Official | Institutional-style market data | Route by feed need and explain subscription gaps. |
| Tradier MCP | Official | Options and broker execution | Require order preview, max loss, and confirmation. |
| TradeStation MCP | Official MCP | Account-connected market data, portfolio, and order-management workflows | Keep reads separate from order management; require paper/live context and explicit confirmation. |
| Robinhood Agentic Trading | Official product | Budget-isolated agentic brokerage workflow | Treat as Tier 4; require account scope, limits, and confirmation. |
| cTrader MCP servers | Official MCP | FX/CFD account, market, chart, and order operations | Preserve broker lot/margin assumptions and demo/live separation. |
| Binance Skills Hub | Official | Crypto exchange and Web3 skills | Keep vendor skills internal; gate state changes. |
| Bybit AI Trading Skills | Official | Bybit exchange market/account/trading skill workflows | Keep Bybit as a venue route; gate orders, leverage, and transfers. |
| Kraken MCP | Official MCP | Kraken market/account/execution-capable exchange workflows | Separate market reads from account mutations and orders. |
| OKX API | Official API | OKX spot, futures, perpetuals, options, account, and market data | Prefer official docs or controlled adapters; gate derivatives and margin actions. |
| BingX API AI Skills | Official | BingX exchange skill workflows | Load only for BingX-specific tasks and gate every state-changing action. |
| Deribit API | Official API | Crypto options, futures/perpetuals, IV, and volatility venue data | Treat options/margin as Tier 4 and require greeks/liquidation review. |
| Dune MCP | Official | Onchain SQL and dashboards | Validate table semantics before platform totals. |
| Alchemy MCP | Official | Wallet/token/NFT/tx RPC data | Separate reads from signing and network/app selection. |
| Etherscan MCP | Official | Verified contracts and explorer truth | Cross-check explorer facts with behavior/risk evidence. |
| The Graph Subgraph MCP | Official | Subgraph discovery, schema inspection, and GraphQL query planning | Label schema freshness, index lag, and protocol-specific assumptions. |
| Goldsky MCP / AI Skills | Official | Web3 data-pipeline, subgraph, and Goldsky docs context | Route pipeline questions separately from token-risk or execution claims. |
| Moralis Cortex MCP | Official | Natural-language Web3 data across wallets, tokens, NFTs, EVM, and Solana | Resolve contracts and freshness before using data in DD. |
| GoldRush MCP | Official | Multichain balances, transactions, NFTs, token prices, and portfolio-style data | Treat as a cross-check, not final safety judgment. |
| SQD Portal MCP | Official | Indexed multichain logs, transactions, datasets, and high-throughput chain data | Preserve dataset, chain, and query-window assumptions. |
| Coinbase CDP / AgentKit MCP | Official MCP | Web3 agent wallets, CDP operations, and agent tooling | Separate docs/context from wallet actions; gate transfers and payments. |
| QuickNode MCP | Official MCP | Web3 RPC endpoints and endpoint security | Keep infra/admin changes separate from market analysis and require confirmation. |
| CoinGecko MCP / Skill | Official MCP + skill | Crypto market data, token metadata, OHLCV, DeFi/onchain data | Resolve token identity and cross-check venue liquidity. |
| CoinMarketCap MCP | Official MCP | Crypto rankings, quotes, market pairs, and exchange/category data | Resolve IDs/contracts and do not treat rank as advice. |
| Token Terminal MCP | Official MCP | Protocol revenue, fees, users, and sector fundamentals | Cross-check methodology and separate fundamentals from trade calls. |
| DeFiLlama API | Official API | TVL, yields, fees, stablecoins, protocol data | Label methodology gaps; do not treat aggregates as direct trade signals. |
| Helius MCP | Official MCP | Solana assets, wallets, transactions, webhooks, streaming | Use for Solana/pump.fun evidence while separating reads from transactions. |
| Jupiter APIs | Official API | Solana liquidity and swap quote/routing APIs | Treat quotes as execution prep until wallet/slippage/confirmation are explicit. |
| DexScreener API | Official API | DEX pairs, liquidity, price action, token profiles | Use display data as one evidence layer, not final risk truth. |
| Stripe MCP / Agent Toolkit | Official toolkit | Payments, billing, checkout, and financial operations | Keep finance ops separate from market signals; confirm state changes. |
| Plaid API | Official API | Bank connectivity, balances, transactions, account verification | Treat account data as sensitive and not as broker execution. |
| Databento API | Official API | Institutional market data and history | Require dataset, venue, entitlement, latency, and cost clarity. |
| Finnhub API | Official API | Market data, company news, fundamentals, earnings, and sentiment | Label news/source timestamps and avoid sentiment-as-advice. |
| Nasdaq Data Link API | Official API | Dataset, macro, alternative-data, and structured research inputs | Preserve dataset vintage, entitlement, and redistribution constraints. |
| IBKR TWS API / community MCP candidates | Official API + community MCP candidates | Multi-asset brokerage API | Do not treat community MCP wrappers as official; paper/live proof first. |
| Hummingbot | Official open source | Market-making and arbitrage bots | Review inventory, rate limits, cancel failures, kill switch. |
| Freqtrade | Official open source | Crypto bot backtest and dry-run | Reject live claims without backtest and risk config. |
| LEAN Engine | Official open source | Multi-asset quant engine | Turn natural-language ideas into audited backtest specs. |
| NautilusTrader | Official open source | High-performance event-driven backtest/live engine | Force data, venue, clock, risk, and deployment specs before adapters. |
| CCXT | Official open-source library | Crypto exchange connector substrate | Enforce rate limits, order preview, balances, and exchange-specific failures. |

## Benchmark Decision

`stark-finance-trading` should be judged as a router skill, not as a broker,
RPC provider, dashboard, or bot engine. The pass condition is:

- It loads for real finance/trading questions and stays quiet for marketing,
  pure tokenomics, design, and legal-advice tasks.
- It chooses the right source family and labels currentness, venue, delay,
  authentication, and missing data.
- It makes live execution harder to misuse than any single vendor surface.
- It keeps vendor-specific tools as implementation details behind one Stark
  route.
- It ships deterministic validation, package smoke, release notes, GitHub
  export, public comparison evidence, and adversarial evals.

## Evidence Boundary

This snapshot does not prove live behavior, remote GitHub CI, or public
superiority. It proves that the source tree contains a reviewed comparison
target and a concrete score rubric for future live evals.
