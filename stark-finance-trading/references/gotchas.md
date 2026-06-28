# Gotchas

## Routing

- Do not split every vendor into a visible user skill. Use `stark-finance-trading` as the primary entry and route internally.
- `stark-mkt-ops` is for market operations and growth. Use this skill only when financial/trading evidence, data, risk, strategy, or execution is central.
- A broker/data MCP being "installed" does not mean it is authenticated or safe for live execution.

## Dune / Onchain

- Dune table names can look authoritative but encode a narrow event surface. Validate table semantics before presenting platform totals.
- Example: `pumpdotfun_solana.pump_call_create` undercounted pump.fun issuance for a total-platform question; `tokens_solana.transfers` with Pump.fun program mint actions was the better daily issuance proxy.
- Broad `information_schema` searches can be slow or time out. Prefer targeted known schemas or docs/table search tools.

## Binance / Wallets

- Binance Skills Hub includes read-only market skills and execution-capable wallet/order skills. Do not treat all Binance skills as read-only.
- Binance Agentic Wallet can send, swap, place limit orders, manage approvals, and handle prediction markets. Every state change needs confirmation.
- Show full token contract addresses for token actions. Symbols alone are unsafe.

## Signals

- Smart-money, whale, dark-pool, and options-flow data are signals, not recommendations.
- High signal count after a large move can mean the opportunity is already gone.
- Always check liquidity, spread, exit rate, concentration, and invalidation condition.

## Backtests

- Backtests without fees, slippage, position sizing, and max drawdown are not decision-grade.
- Grid/martingale results are especially sensitive to liquidation, stop-out, and capital scaling assumptions.
- A strategy that survives one market regime can fail in volatility expansion or liquidity gaps.

## Broker / FX / CFD

- XAUUSD and CFD tasks are broker-specific. Always preserve lot size, contract size, leverage, margin mode, and stop-out assumptions before using cTrader or another execution-capable surface.
- An order preview is a review artifact, not permission to submit. It still needs explicit confirmation before any live action.
- IBKR has official TWS/API surfaces, while most IBKR MCP wrappers are community-maintained. Do not treat community MCP as official without fresh verification.

## DeFi Data

- DeFiLlama aggregates such as TVL, yields, and fees have methodology gaps and can differ from protocol dashboards or raw onchain data.
- Aggregate DeFi metrics are not a direct safety or trade signal. Cross-check with Dune, token/liquidity data, and contract/account truth when the decision is high stakes.

## Public Claims

- Do not make public superiority claims without comparative evidence. Say "GitHub-ready", "benchmark-driven", or "designed to compete with top public finance/trading skills" unless live benchmark evidence exists.
