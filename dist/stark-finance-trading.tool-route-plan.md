# stark-finance-trading Tool Route Plan

- Status: PASS
- Cases: 13/13

| Case | Status | Risk | Tools |
|---|---|---:|---|
| `stock-market-snapshot` | PASS | 2 | `binance-skills-hub, openbb, fmp-mcp, alpaca-mcp, massive-polygon-mcp, alpha-vantage-mcp, coingecko-mcp, twelve-data-mcp` |
| `options-flow-draft` | PASS | 4 | `openbb, fmp-mcp, alpaca-mcp, unusual-whales-mcp, tradier-mcp, massive-polygon-mcp, alpha-vantage-mcp` |
| `pumpfun-daily-issuance` | PASS | 2 | `dune-mcp, alchemy-mcp, helius-mcp, jupiter-apis, dexscreener-api, coingecko-mcp` |
| `token-contract-dd` | PASS | 2 | `dune-mcp, alchemy-mcp, binance-skills-hub, etherscan-mcp, dexscreener-api, coingecko-mcp` |
| `defi-protocol-fundamentals` | PASS | 1 | `dune-mcp, alchemy-mcp, token-terminal-mcp, defillama-api, coingecko-mcp, coinmarketcap-mcp` |
| `crypto-bot-backtest` | PASS | 3 | `binance-skills-hub, quantconnect-mcp, lean, hummingbot, freqtrade, ccxt, alpaca-mcp, nautilus-trader, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp` |
| `live-binance-order` | PASS | 4 | `binance-skills-hub, alpaca-mcp, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp` |
| `xauusd-ctrader-risk` | PASS | 4 | `binance-skills-hub, alpaca-mcp, ctrader-ai-agent-connect, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp` |
| `ibkr-wrapper-boundary` | PASS | 4 | `ibkr-tws-api` |
| `finance-infra-boundary` | PASS | 4 | `stripe-agent-toolkit, plaid-api` |
| `local-earnings-router` | PASS | 2 | `openbb, fmp-mcp, alpaca-mcp, massive-polygon-mcp, alpha-vantage-mcp` |
| `negative-marketing` | PASS | 0 | `` |
| `negative-tokenomics` | PASS | 0 | `` |

## Evidence Boundary

These cases validate deterministic source routing against local catalog/rules. They do not prove live tool availability, API credentials, market-data correctness, or model behavior.
