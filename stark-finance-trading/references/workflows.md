# Workflows

## 1. Market Snapshot

Use when the user asks "现在价格", "行情", "spread", "depth", "走势", "volume", or a ticker/pair.

Steps:

1. Identify market and venue/feed.
2. Fetch latest quote/trade/bar/order book if available.
3. Add recent context: 1m/1h/1d/7d depending on task.
4. If trading relevance is implied, include spread/depth/liquidity and source timestamp.
5. Output concise table plus caveats.

Done when the answer names source, timestamp, market, and delay/live status.

## 2. Token Due Diligence

Use for token contract, meme coin, DEX pair, holder, transfer, or launchpad checks.

Steps:

1. Resolve chain and contract address. Never invent an address.
2. Query metadata and market fields.
3. Query audit/risk flags.
4. Check liquidity/depth/route quality.
5. Use Dune for historical holder/transfer/volume cohorts if deeper evidence is needed.
6. Use Alchemy/Etherscan for contract/tx/wallet truth.
7. Classify risks: liquidity, concentration, owner/admin, mint/proxy, honeypot/tax, wash trading, route/display issue.

Output:

- Summary verdict.
- Evidence table.
- Risk table.
- Next verification step.

## 3. Smart-Money / Signal Scan

Use for "alpha", "smart money", "whale bought", "copy-trade", "meme rush", or "trending".

Steps:

1. Select chain and time window.
2. Use rank/signal tools.
3. Keep only fresh and liquid-enough cases.
4. Check whether the signal is active or already exited when fields exist.
5. Cross-check top candidates with token info/audit.

Output must include "why now", "why risky", and an invalidation or stop condition.

## 4. Equity / Macro / Fundamentals Research

Use for stocks, ETFs, macro, financial statements, valuation, peer comps, or news-driven research.

Steps:

1. Identify ticker/universe and exchange.
2. Fetch market snapshot.
3. Fetch fundamentals/news/macro data from an official or high-quality source.
4. Separate facts from interpretation.
5. Include catalyst, risk, and data gaps.

For high-stakes output, verify with official filings or exchange/company pages.

## 5. Options Flow

Use for unusual options, dark pool, Greek exposure, volatility, and flow.

Steps:

1. Identify ticker and expiry/strike if provided.
2. Pull flow/dark-pool/vol source.
3. Cross-check option quotes/contracts.
4. Separate directional flow from hedging/market-making possibilities.
5. Warn if liquidity/open-interest/spread makes execution poor.
6. If the user asks for an order draft, create an order preview path only; do not submit without Tier 4 confirmation.

Never call flow alone a trade.

## 6. Strategy Backtest

Use for "回测", "策略", "胜率", "MDD", "Sharpe", "grid", "martingale", "bot", or "QuantConnect".

Steps:

1. Write hypothesis.
2. Define instrument universe, timeframe, data source, fees, slippage, position sizing.
3. Run or design a backtest.
4. Report return, drawdown, exposure, turnover, worst period, and failure mode.
5. Propose out-of-sample, walk-forward, or paper-trading validation.

Reject results that omit fees/slippage or position sizing.

## 7. Market-Making / Liquidity War Room

Use for CEX/DEX liquidity, orderbook, quote bands, inventory, LP range, or listing prep.

Steps:

1. Identify venue and pair.
2. Check depth, spread, trade cadence, volatility, route health, and liquidity source.
3. Compare CEX and DEX if both exist.
4. Define inventory limits, quote refresh, range, slippage, stop rules.
5. Output a command package, not an unguarded trading bot.

Required fields:

- max inventory;
- max notional exposure;
- max daily loss or drawdown;
- cancel failure handling;
- stale data rule;
- kill switch.

## 8. Execution Prep

Use only when user asks to place, cancel, swap, transfer, approve, deploy, or run a bot.

Steps:

1. Classify Tier 3 draft or Tier 4 live action.
2. Read `safety-policy.md`.
3. Build a preview, not execution.
4. Ask for explicit confirmation if Tier 4.
5. Execute only with exact confirmation and available tool-specific skill rules.

If any field is missing, ask only the missing field that changes risk.

## 9. FX / CFD / XAUUSD Margin Review

Use for XAUUSD, FX, CFD, cTrader, broker margin, lot sizing, stop-out, liquidation, or account-risk questions.

Steps:

1. Identify broker/platform, instrument, account currency, leverage, contract size, lot size, margin mode, and stop-out rule.
2. Preserve user worksheet or statement logic when provided.
3. Recalculate exposure, used margin, free margin, floating P&L path, and stop-out distance.
4. If cTrader or another MCP can read account/platform state, treat it as read-only until the user explicitly asks for a draft action.
5. Separate demo/paper from live account actions and apply Tier 4 confirmation before any order, close, leverage, or bot action.

Required output:

- assumptions table;
- margin and stop-out table;
- failure path;
- broker-specific caveats.

## 10. DeFi Protocol Research

Use for TVL, fees, revenue, yields, stablecoins, protocol usage, DeFi category research, or "is this protocol worth DD".

Steps:

1. Use DeFiLlama for aggregate TVL, yields, fees, revenue, and category data when useful.
2. Use Dune for protocol-specific cohorts and onchain usage when a dashboard/table is suitable.
3. Use Token Terminal for protocol revenue, fees, users, sector, chain, and project financial metrics when available.
4. Use CoinGecko/CoinMarketCap and token sources for token identity, market cap, volume, liquidity, and listing context.
5. Use Alchemy/Etherscan for wallet, transaction, and contract truth where needed.
6. State methodology gaps, missing coverage, and whether metrics are estimated, delayed, or protocol-reported.

Aggregate TVL, yield, fee, revenue, or user data is not a direct safety or trade signal. Treat it as evidence for further due diligence, not as a recommendation. Never convert protocol fundamentals directly into trade recommendations.

## 11. Solana / Pump.fun Launch Review

Use for Solana launches, pump.fun issuance, meme token discovery, Jupiter quotes, DexScreener pairs, Helius data, or Solana wallet/token checks.

Steps:

1. Resolve mint address, chain, pool/pair, launch source, and time window. Never trade by symbol alone.
2. Use Helius for Solana wallet, asset, transaction, and launch-flow context when available.
3. Use Dune for historical issuance/cohort metrics if indexed data exists.
4. Use DexScreener for pair/liquidity/price display behavior and Jupiter for quote/liquidity route checks.
5. Cross-check market context with CoinGecko/CoinMarketCap after token identity is resolved.
6. Treat Jupiter quotes as execution prep only; swaps/signatures remain Tier 4 and require explicit confirmation.

Required output:

- mint and pair identity;
- launch/issuance method caveat;
- liquidity and holder risk;
- quote/liquidity route caveat;
- no-execution boundary.

## 12. Financial Infrastructure / Payments Boundary

Use for Stripe, Plaid, payments, billing, checkout, banking connectivity, account balances, cashflow, treasury context, or product finance ops.

Steps:

1. Classify the request as finance infrastructure, not market-data research or broker execution.
2. Use Stripe for payments, billing, checkout, revenue, and financial operations context.
3. Use Plaid for bank/account connectivity, balances, transactions, account verification, and cashflow evidence.
4. Minimize sensitive data scope and avoid exposing account/payment identifiers.
5. If the user asks for a trade based on cashflow, separate cashflow evidence from trading advice and require fresh market/risk analysis.

Payments, bank connectivity, and cashflow are not trading signals. They can inform treasury/risk context, but not a full-position recommendation by themselves.

## 13. Web3 Infrastructure Admin

Use for QuickNode, Alchemy infra, RPC endpoints, endpoint creation, chain/network support, webhooks, security rules, or endpoint hardening.

Steps:

1. Classify infra reads separately from admin changes.
2. List endpoint/chain/network context without exposing RPC secrets or endpoint tokens.
3. For endpoint creation, security rules, CORS, tokens, IP allowlists, or domain masks, prepare a preview first.
4. Require explicit confirmation before changing infrastructure state.
5. Record the network, endpoint id, rule type, and rollback path.

Infrastructure health can affect data quality and bot reliability, but it is not a market signal by itself.

## 14. Local Skill Delegation

Use when a request is finance/trading/investment work but the best implementation detail is an installed local specialist skill.

Steps:

1. Keep `stark-finance-trading` as the user-facing route.
2. Read `references/local-skill-router.md` to choose the helper family.
3. Load only the helper that matches the task, such as `earnings-preview`, `equity-research`, `dcf-model`, `comps-analysis`, `bond-futures-basis`, `option-vol-analysis`, `portfolio-rebalance`, `gmgn-token`, or `binance`.
4. Preserve the evidence and safety contract from this skill: source timestamps, assumptions, risk tier, and execution boundary.
5. If the helper produces valuation, research, a rebalance draft, or a signal, do not convert it into a live trade without fresh market data, position/risk sizing, and explicit confirmation.
6. If the primary intent is not finance/trading evidence, hand off to the better Stark skill instead of forcing this route.

Required output:

- chosen helper route;
- source/evidence plan;
- whether the output is research, model, draft, paper/demo, or live;
- safety boundary and next verification step.
