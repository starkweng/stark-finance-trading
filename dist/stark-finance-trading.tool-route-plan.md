# stark-finance-trading Tool Route Plan

- Status: PASS
- Cases: 23/23

| Case | Status | Risk | Tools |
|---|---|---:|---|
| `stock-market-snapshot` | PASS | 2 | `binance-skills-hub, openbb, fmp-mcp, alpaca-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api, coingecko-mcp, twelve-data-mcp` |
| `options-flow-draft` | PASS | 4 | `openbb, fmp-mcp, alpaca-mcp, unusual-whales-mcp, tradier-mcp, deribit-api, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `pumpfun-daily-issuance` | PASS | 2 | `dune-mcp, alchemy-mcp, helius-mcp, jupiter-apis, dexscreener-api, coingecko-mcp` |
| `token-contract-dd` | PASS | 2 | `dune-mcp, alchemy-mcp, binance-skills-hub, etherscan-mcp, dexscreener-api, coingecko-mcp` |
| `defi-protocol-fundamentals` | PASS | 1 | `dune-mcp, alchemy-mcp, token-terminal-mcp, defillama-api, coingecko-mcp, coinmarketcap-mcp` |
| `crypto-bot-backtest` | PASS | 3 | `binance-skills-hub, quantconnect-mcp, lean, hummingbot, freqtrade, ccxt, alpaca-mcp, nautilus-trader, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `hummingbot-market-making-dry-run` | PASS | 3 | `binance-skills-hub, quantconnect-mcp, lean, hummingbot, freqtrade, ccxt, alpaca-mcp, nautilus-trader, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `freqtrade-strategy-dry-run` | PASS | 3 | `quantconnect-mcp, lean, hummingbot, freqtrade, ccxt, nautilus-trader` |
| `ccxt-connector-boundary` | PASS | 3 | `quantconnect-mcp, lean, hummingbot, freqtrade, ccxt, nautilus-trader` |
| `openbb-options-research-boundary` | PASS | 4 | `openbb, fmp-mcp, alpaca-mcp, unusual-whales-mcp, tradier-mcp, deribit-api, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `alpaca-paper-live-boundary` | PASS | 4 | `openbb, fmp-mcp, alpaca-mcp, tradier-mcp, ibkr-tws-api, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `live-binance-order` | PASS | 4 | `binance-skills-hub, alpaca-mcp, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `cex-derivatives-venue-boundary` | PASS | 4 | `binance-skills-hub, ccxt, openbb, fmp-mcp, alpaca-mcp, tradier-mcp, ibkr-tws-api, bybit-ai-trading-skills, kraken-mcp, okx-api, bingx-ai-skills, deribit-api, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api, coingecko-mcp, twelve-data-mcp` |
| `deribit-crypto-options-route` | PASS | 4 | `binance-skills-hub, ccxt, alpaca-mcp, unusual-whales-mcp, tradier-mcp, deribit-api, bybit-ai-trading-skills, kraken-mcp, okx-api, bingx-ai-skills, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `tradingview-alert-boundary` | PASS | 4 | `tradingview-broker-api` |
| `xauusd-ctrader-risk` | PASS | 4 | `binance-skills-hub, alpaca-mcp, ctrader-ai-agent-connect, oanda-v20-api, metatrader5-python, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `xauusd-oanda-mt5-risk` | PASS | 4 | `binance-skills-hub, alpaca-mcp, ctrader-ai-agent-connect, oanda-v20-api, metatrader5-python, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `ibkr-wrapper-boundary` | PASS | 4 | `alpaca-mcp, tradier-mcp, ibkr-tws-api` |
| `finance-infra-boundary` | PASS | 4 | `stripe-agent-toolkit, plaid-api` |
| `local-earnings-router` | PASS | 2 | `openbb, fmp-mcp, alpaca-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `finnhub-nasdaq-research-data` | PASS | 2 | `openbb, fmp-mcp, alpaca-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `negative-marketing` | PASS | 0 | `` |
| `negative-tokenomics` | PASS | 0 | `` |

## Evidence Boundary

These cases validate deterministic source routing against local catalog/rules. They do not prove live tool availability, API credentials, market-data correctness, or model behavior.
