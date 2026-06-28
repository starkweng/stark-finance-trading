# Examples

## Market Snapshot

```text
/stark-finance-trading 查一下 BTC 和 ETH 当前盘口、近 1 小时波动、主要风险
```

Expected behavior:

- classify as market snapshot;
- use market-data route;
- include source, timestamp, spread/depth when relevant;
- avoid trade recommendation unless the user asks for a plan.

## Token Due Diligence

```text
/stark-finance-trading 看这个 BSC token 的 liquidity、holder、smart money 和合约风险
```

Expected behavior:

- resolve chain and contract;
- use token info/audit plus Dune/Alchemy/Etherscan/GMGN when useful;
- show liquidity, holder, route, contract, and market-display risks.

## Backtest

```text
/stark-finance-trading 帮我回测 ETHUSDT 网格策略，重点看 MDD 和爆仓条件
```

Expected behavior:

- require or infer dataset, fees, slippage, sizing, and period;
- report drawdown and failure path;
- recommend paper validation before live deployment.

## Live Execution Draft

```text
/stark-finance-trading 准备一个 Binance 下单草案，但先不要执行
```

Expected behavior:

- build draft only;
- classify execution risk tier;
- require explicit confirmation for any live action.
