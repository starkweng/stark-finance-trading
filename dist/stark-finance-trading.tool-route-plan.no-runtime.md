# stark-finance-trading Tool Route Plan

- Status: PASS
- Cases: 24/24

| Case | Status | Risk | Tools |
|---|---|---:|---|
| `stock-market-snapshot` | PASS | 2 | `binance-skills-hub, alpaca-mcp, openbb, fmp-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api, coingecko-mcp, twelve-data-mcp` |
| `options-flow-draft` | PASS | 4 | `alpaca-mcp, unusual-whales-mcp, tradier-mcp, deribit-api, openbb, fmp-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `pumpfun-daily-issuance` | PASS | 2 | `dune-mcp, alchemy-mcp, helius-mcp, jupiter-apis, dexscreener-api, coingecko-mcp` |
| `token-contract-dd` | PASS | 2 | `binance-skills-hub, dune-mcp, alchemy-mcp, etherscan-mcp, dexscreener-api, coingecko-mcp` |
| `defi-protocol-fundamentals` | PASS | 1 | `dune-mcp, alchemy-mcp, token-terminal-mcp, defillama-api, coingecko-mcp, coinmarketcap-mcp` |
| `crypto-bot-backtest` | PASS | 3 | `binance-skills-hub, alpaca-mcp, quantconnect-mcp, lean, hummingbot, freqtrade, nautilus-trader, ccxt, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `hummingbot-market-making-dry-run` | PASS | 3 | `binance-skills-hub, alpaca-mcp, quantconnect-mcp, lean, hummingbot, freqtrade, nautilus-trader, ccxt, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `freqtrade-strategy-dry-run` | PASS | 3 | `quantconnect-mcp, lean, hummingbot, freqtrade, nautilus-trader, ccxt` |
| `ccxt-connector-boundary` | PASS | 3 | `quantconnect-mcp, lean, hummingbot, freqtrade, nautilus-trader, ccxt` |
| `openbb-options-research-boundary` | PASS | 4 | `alpaca-mcp, unusual-whales-mcp, tradier-mcp, deribit-api, openbb, fmp-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `alpaca-paper-live-boundary` | PASS | 4 | `alpaca-mcp, tradier-mcp, tradestation-mcp, ibkr-tws-api, openbb, fmp-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `tradestation-mcp-boundary` | PASS | 4 | `alpaca-mcp, tradier-mcp, tradestation-mcp, ibkr-tws-api, unusual-whales-mcp, deribit-api, openbb, fmp-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `live-binance-order` | PASS | 4 | `binance-skills-hub, alpaca-mcp, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `cex-derivatives-venue-boundary` | PASS | 4 | `binance-skills-hub, alpaca-mcp, tradier-mcp, tradestation-mcp, ibkr-tws-api, bybit-ai-trading-skills, kraken-mcp, okx-api, bingx-ai-skills, deribit-api, ccxt, openbb, fmp-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api, coingecko-mcp, twelve-data-mcp` |
| `deribit-crypto-options-route` | PASS | 4 | `binance-skills-hub, alpaca-mcp, unusual-whales-mcp, tradier-mcp, deribit-api, bybit-ai-trading-skills, kraken-mcp, okx-api, bingx-ai-skills, ccxt, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `tradingview-alert-boundary` | PASS | 4 | `tradingview-broker-api` |
| `xauusd-ctrader-risk` | PASS | 4 | `binance-skills-hub, alpaca-mcp, ctrader-ai-agent-connect, oanda-v20-api, metatrader5-python, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `xauusd-oanda-mt5-risk` | PASS | 4 | `binance-skills-hub, alpaca-mcp, ctrader-ai-agent-connect, oanda-v20-api, metatrader5-python, coingecko-mcp, massive-polygon-mcp, twelve-data-mcp, finnhub-api, nasdaq-data-link-api` |
| `ibkr-wrapper-boundary` | PASS | 4 | `alpaca-mcp, tradier-mcp, tradestation-mcp, ibkr-tws-api` |
| `finance-infra-boundary` | PASS | 4 | `stripe-agent-toolkit, plaid-api` |
| `local-earnings-router` | PASS | 2 | `alpaca-mcp, openbb, fmp-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `finnhub-nasdaq-research-data` | PASS | 2 | `alpaca-mcp, openbb, fmp-mcp, massive-polygon-mcp, alpha-vantage-mcp, finnhub-api, nasdaq-data-link-api` |
| `negative-marketing` | PASS | 0 | `` |
| `negative-tokenomics` | PASS | 0 | `` |

## Evidence Boundary

These cases validate deterministic source routing against local catalog/rules. They do not prove live tool availability, API credentials, market-data correctness, or model behavior.
