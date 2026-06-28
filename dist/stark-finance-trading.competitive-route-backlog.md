# Competitive Route Backlog

- Status: PASS
- Source gap status: `PASS`
- Source candidates: 25
- Backlog cases: 20

## Stage Counts

| Stage | Count |
|---|---:|
| `auth_or_env_needed` | 8 |
| `route_eval_proposal` | 12 |

## Cases

| Case | Candidate | Stage | Action | Categories | Priority |
|---|---|---|---|---|---:|
| `01-hummingbot-hummingbot` | hummingbot/hummingbot | `auth_or_env_needed` | `requires_secret_or_auth` | backtest, bot_framework, broker_execution, onchain | 140.95 |
| `02-edtechre-pybroker` | edtechre/pybroker | `auth_or_env_needed` | `requires_secret_or_auth` | backtest, broker_execution | 135.75 |
| `03-ccxt-ccxt` | ccxt/ccxt | `auth_or_env_needed` | `requires_secret_or_auth` | backtest, bot_framework, onchain | 133.44 |
| `04-51bitquant-howtrader` | 51bitquant/howtrader | `auth_or_env_needed` | `requires_secret_or_auth` | backtest, bot_framework, broker_execution | 131.78 |
| `05-nirholas-ucai` | nirholas/UCAI | `auth_or_env_needed` | `requires_secret_or_auth` | market_data, mcp, onchain | 121.72 |
| `06-nirholas-cryptocurrency-cv` | nirholas/cryptocurrency.cv | `auth_or_env_needed` | `requires_secret_or_auth` | bot_framework, mcp, onchain | 117.76 |
| `07-freqtrade-freqtrade` | freqtrade/freqtrade | `route_eval_proposal` | `add_route_eval` | bot_framework | 115.01 |
| `08-openbb-finance-openbb` | OpenBB-finance/OpenBB | `auth_or_env_needed` | `requires_secret_or_auth` | options_flow, research | 114.91 |
| `09-wilsonfreitas-awesome-quant` | wilsonfreitas/awesome-quant | `route_eval_proposal` | `add_route_eval` | bot_framework | 113.03 |
| `10-demcp-awesome-web3-mcp-servers` | demcp/awesome-web3-mcp-servers | `auth_or_env_needed` | `requires_secret_or_auth` | mcp, onchain | 110.5 |
| `11-ccxt-binance-trade-bot` | ccxt/binance-trade-bot | `route_eval_proposal` | `add_route_eval` | bot_framework | 109.58 |
| `12-paperswithbacktest-awesome-systematic-trading` | paperswithbacktest/awesome-systematic-trading | `route_eval_proposal` | `add_route_eval` | backtest, bot_framework | 109.49 |
| `13-deviavir-zenbot` | DeviaVir/zenbot | `route_eval_proposal` | `add_route_eval` | backtest, bot_framework | 109.42 |
| `14-jesse-ai-jesse` | jesse-ai/jesse | `route_eval_proposal` | `add_route_eval` | bot_framework | 109.36 |
| `15-thysrael-horizon` | Thysrael/Horizon | `route_eval_proposal` | `add_route_eval` | bot_framework, mcp | 109.14 |
| `16-blankly-finance-blankly` | blankly-finance/blankly | `route_eval_proposal` | `add_route_eval` | backtest, bot_framework | 105.73 |
| `17-barter-rs-barter-rs` | barter-rs/barter-rs | `route_eval_proposal` | `add_route_eval` | backtest, bot_framework | 105.37 |
| `18-kernc-backtesting-py` | kernc/backtesting.py | `route_eval_proposal` | `add_route_eval` | backtest | 83.53 |
| `19-ricequant-rqalpha` | ricequant/rqalpha | `route_eval_proposal` | `add_route_eval` | backtest | 82.7 |
| `20-fasiondog-hikyuu` | fasiondog/hikyuu | `route_eval_proposal` | `add_route_eval` | backtest | 80.62 |

## Next Actions

- Promote route_eval_proposal cases into evals/tool-routing-cases.json only when they represent recurring Stark workflows.
- Resolve auth_or_env_needed cases through explicit env/API entitlement checks before claiming runtime support.
- Keep broker, bot, swap, wallet, and order flows under Tier 4 and no_live_execution default behavior.
- Use this backlog as the learn sink for future public-tool discovery changes.

## Evidence Boundary

Competitive route backlog is a generated learn-loop artifact. It turns discovery/gap evidence into candidate eval prompts and integration gates, but it does not prove live model behavior, installability, official status, API entitlement, remote CI completion, market-data correctness, trading performance, or public superiority.
