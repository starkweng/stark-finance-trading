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
3. Use CoinGecko and token sources for token identity, market cap, volume, liquidity, and listing context.
4. Use Alchemy/Etherscan for wallet, transaction, and contract truth where needed.
5. State methodology gaps, missing coverage, and whether metrics are estimated, delayed, or protocol-reported.

Aggregate TVL, yield, or fee data is not a direct safety or trade signal. Treat it as evidence for further due diligence, not as a recommendation.
