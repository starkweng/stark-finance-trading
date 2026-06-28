# Public Comparison Snapshot - 2026-06-28

This is a source-level benchmark snapshot, not a superiority claim. It records
the public bar that `stark-finance-trading` must meet or beat through routing,
source discipline, safety boundaries, and package evidence.

## Conclusion

The strongest public finance/trading surfaces are vendor-deep: Alpaca, Tradier,
Robinhood, IBKR, and cTrader for broker/platform workflows; Dune, Alchemy,
Etherscan, Coinbase, CoinGecko, DeFiLlama, and Binance for crypto/Web3 data and
actions; QuantConnect, LEAN, NautilusTrader, Hummingbot, Freqtrade, and CCXT for
strategy or bot engineering; and OpenBB, Databento, FMP, Twelve Data, Alpha
Vantage, Massive/Polygon.io, and Unusual Whales for research and data. The
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
| Twelve Data MCP | Official | Global multi-asset data | Label venue, delay status, and decision-grade limits. |
| Unusual Whales MCP | Official | Options flow and dark-pool signals | Treat flow as signal evidence, not trade instruction. |
| Massive / Polygon.io MCP | Official | Institutional-style market data | Route by feed need and explain subscription gaps. |
| Tradier MCP | Official | Options and broker execution | Require order preview, max loss, and confirmation. |
| Robinhood Agentic Trading | Official product | Budget-isolated agentic brokerage workflow | Treat as Tier 4; require account scope, limits, and confirmation. |
| cTrader MCP servers | Official MCP | FX/CFD account, market, chart, and order operations | Preserve broker lot/margin assumptions and demo/live separation. |
| Binance Skills Hub | Official | Crypto exchange and Web3 skills | Keep vendor skills internal; gate state changes. |
| Dune MCP | Official | Onchain SQL and dashboards | Validate table semantics before platform totals. |
| Alchemy MCP | Official | Wallet/token/NFT/tx RPC data | Separate reads from signing and network/app selection. |
| Etherscan MCP | Official | Verified contracts and explorer truth | Cross-check explorer facts with behavior/risk evidence. |
| Coinbase CDP / AgentKit MCP | Official MCP | Web3 agent wallets, CDP operations, and agent tooling | Separate docs/context from wallet actions; gate transfers and payments. |
| CoinGecko MCP / Skill | Official MCP + skill | Crypto market data, token metadata, OHLCV, DeFi/onchain data | Resolve token identity and cross-check venue liquidity. |
| DeFiLlama API | Official API | TVL, yields, fees, stablecoins, protocol data | Label methodology gaps; do not treat aggregates as direct trade signals. |
| Databento API | Official API | Institutional market data and history | Require dataset, venue, entitlement, latency, and cost clarity. |
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
