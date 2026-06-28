# stark-finance-trading Runtime Capabilities

- Status: PASS
- Catalog tools: 50
- Observed runtime-backed tools: 13
- Configured MCP servers: 8
- Enabled plugins: 27
- Local skill names: 520

## Runtime Status Counts

| Status | Count |
|---|---:|
| `configured_mcp` | 2 |
| `configured_mcp_needs_env` | 1 |
| `deferred_tool_source` | 1 |
| `enabled_plugin` | 2 |
| `external_candidate` | 37 |
| `local_skill_backed` | 7 |

## Observed Tools

| Tool | Runtime status | Rank |
|---|---|---:|
| `alchemy-mcp` | `configured_mcp` | 100 |
| `dune-mcp` | `configured_mcp` | 100 |
| `binance-skills-hub` | `enabled_plugin` | 90 |
| `quicknode-mcp` | `enabled_plugin` | 90 |
| `ccxt` | `local_skill_backed` | 80 |
| `fmp-mcp` | `local_skill_backed` | 80 |
| `freqtrade` | `local_skill_backed` | 80 |
| `hummingbot` | `local_skill_backed` | 80 |
| `lean` | `local_skill_backed` | 80 |
| `openbb` | `local_skill_backed` | 80 |
| `quantconnect-mcp` | `local_skill_backed` | 80 |
| `etherscan-mcp` | `configured_mcp_needs_env` | 70 |
| `alpaca-mcp` | `deferred_tool_source` | 60 |

## Env Needed

- `etherscan-mcp`

## Evidence Boundary

Local runtime capability scan only. It reads local MCP/plugin/skill configuration and environment-variable presence without exposing secret values. It does not prove OAuth validity, API entitlement, live tool availability, market-data correctness, or trading performance.
