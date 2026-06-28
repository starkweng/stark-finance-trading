# Source Ledger

Last refreshed: 2026-06-28. Live-check before installing or citing exact capabilities.

`references/public-tool-catalog.json` is the machine-readable companion to this ledger. When adding or changing a public MCP/API/framework source, update both files and rerun `scripts/validate_public_tool_catalog.py`.

## Official / Primary Sources

| Source | URL | Use |
|---|---|---|
| Alpaca MCP docs | https://docs.alpaca.markets/us/docs/alpaca-mcp-server | Official Alpaca MCP setup and tool scope. |
| OpenBB Docs MCP | https://github.com/OpenBB-finance/openbb-docs-mcp | Official OpenBB documentation MCP server. |
| OpenBB | https://github.com/OpenBB-finance/OpenBB | Open-source finance platform and research workbench. |
| QuantConnect MCP | https://www.quantconnect.com/mcp | Official QuantConnect AI/MCP workflow for strategy and backtesting. |
| Alpha Vantage MCP | https://github.com/alphavantage/alpha_vantage_mcp | Official Alpha Vantage MCP server. |
| Financial Modeling Prep MCP | https://site.financialmodelingprep.com/developer/docs/mcp-server | Official FMP MCP server docs. |
| FactSet MCP | https://developer.factset.com/mcp | Official FactSet MCP developer surface for institutional financial data. |
| Twelve Data MCP | https://github.com/twelvedata/mcp | Official Twelve Data MCP server. |
| Unusual Whales MCP | https://unusualwhales.com/public-api/mcp | Official options/dark-pool/congressional-trading MCP and skill. |
| Massive / Polygon.io MCP | https://github.com/massive-com/mcp_massive | Official market-data MCP for the Polygon.io/Massive ecosystem. |
| Tradier MCP | https://docs.tradier.com/docs/tradier-mcp | Official Tradier MCP docs. |
| Robinhood Agentic Trading | https://robinhood.com/us/en/agentic-trading/ | Official Robinhood agentic trading product page. |
| cTrader AI Agent Connect | https://help.ctrader.com/ctrader-ai-agent-connect/ | Official cTrader MCP / AI agent connection docs. |
| Coinbase CDP CLI MCP | https://docs.cdp.coinbase.com/get-started/build-with-ai/cdp-cli/mcp | Official Coinbase CDP CLI MCP integration. |
| Coinbase AgentKit MCP | https://docs.cdp.coinbase.com/agent-kit/core-concepts/model-context-protocol | Official AgentKit MCP extension docs. |
| QuickNode MCP | https://www.quicknode.com/docs/build-with-ai/quicknode-mcp | Official QuickNode MCP for endpoint and Web3 infrastructure management. |
| CoinGecko MCP | https://docs.coingecko.com/ai-integration/mcp-server.md | Official CoinGecko MCP server docs. |
| CoinGecko Agent Skill | https://docs.coingecko.com/ai-integration/agent-skill.md | Official CoinGecko skill integration docs. |
| CoinMarketCap MCP | https://coinmarketcap.com/api/mcp/ | Official CoinMarketCap MCP/API agent integration. |
| Token Terminal MCP | https://tokenterminal.com/docs/mcp/introduction | Official Token Terminal MCP docs for crypto and protocol fundamentals. |
| DeFiLlama API | https://api-docs.defillama.com/ | Official DeFiLlama API docs. |
| Helius MCP | https://www.helius.dev/docs/agents/mcp | Official Helius MCP and agent docs for Solana data/infrastructure. |
| Jupiter APIs | https://dev.jup.ag/docs | Official Jupiter developer docs for Solana liquidity/swap APIs. |
| DexScreener API | https://docs.dexscreener.com/api/reference | Official DexScreener public API docs; community MCP wrappers must be treated as non-official unless verified. |
| Stripe MCP / Agent Toolkit | https://docs.stripe.com/agents/toolkit | Official Stripe agent toolkit and MCP-style integration for payments and financial operations, not trading signals. |
| Plaid docs | https://plaid.com/docs/ | Official Plaid docs for bank/account connectivity; use as financial data infrastructure, not broker execution. |
| Databento docs | https://databento.com/docs | Official Databento data API docs. |
| IBKR TWS API | https://interactivebrokers.github.io/tws-api/ | Official Interactive Brokers TWS API docs; community MCPs must not be treated as official. |
| Binance Skills Hub | https://github.com/binance/binance-skills-hub | Official Binance skill set. |
| Dune MCP docs | https://docs.dune.com/api-reference/agents/mcp | Official Dune MCP docs. |
| Alchemy MCP | https://github.com/alchemyplatform/alchemy-mcp-server | Official Alchemy MCP server. |
| Etherscan MCP docs | https://docs.etherscan.io/etherscan-mcp-server | Official Etherscan MCP docs. |
| The Graph Subgraph MCP | https://thegraph.com/docs/en/subgraphs/subgraph-mcp/introduction/ | Official The Graph Subgraph MCP docs for subgraph discovery, schemas, and GraphQL query workflows. |
| Goldsky MCP / AI Skills | https://docs.goldsky.com/mcp-server | Official Goldsky MCP server docs for AI access to Goldsky docs and Web3 data tooling. |
| Moralis Cortex API / MCP | https://docs.moralis.com/data-api/cortex-api/overview | Official Moralis Cortex docs for AI/Web3 data layer and MCP-oriented access. |
| GoldRush MCP | https://github.com/covalenthq/goldrush-mcp-server | Official Covalent/GoldRush MCP server source. |
| SQD Portal MCP | https://docs.sqd.dev/en/ai/mcp-server | Official SQD Portal MCP docs for indexed multichain data access. |
| Hummingbot | https://hummingbot.org/ | Open-source crypto market-making and trading bot framework. |
| Freqtrade | https://www.freqtrade.io/en/stable/ | Open-source crypto trading bot framework. |
| LEAN | https://www.lean.io/ | Open-source QuantConnect algorithmic trading engine. |
| NautilusTrader | https://github.com/nautechsystems/nautilus_trader | Official open-source event-driven trading platform. |
| CCXT | https://github.com/ccxt/ccxt | Official open-source crypto exchange library. |

## Candidate Classification Rules

- `official_mcp`: first-party MCP server or MCP docs from the product/vendor.
- `official_mcp_and_skill`: first-party MCP plus installable skill or agent integration package.
- `official_docs_mcp`: first-party documentation MCP, useful for source context but not market data or execution.
- `official_docs_mcp_and_skill`: first-party documentation MCP plus skill/AI integration docs.
- `official_api`: first-party API/docs without a first-party MCP surface.
- `official_open_source`: first-party open-source framework or engine.
- `official_api_with_community_mcp_candidates`: first-party API exists, but MCP wrappers are community-maintained unless separately verified.

## Drift Policy

Always live-verify:

- package install commands;
- API key names;
- paper vs live trading support;
- supported markets and venues;
- auth method;
- order types;
- pricing/subscription limits;
- official vs community MCP status.

Treat non-official MCP repos as candidates only. Prefer official APIs or a controlled local adapter for broker/exchange execution.
