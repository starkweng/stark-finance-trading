# stark-finance-trading

`stark-finance-trading` is a single high-signal router skill for financial markets, crypto markets, onchain data, trading research, backtests, signals, market-making analysis, and guarded execution prep.

It is designed for Stark's workflow: one natural entry point that quietly routes to the right MCP, plugin, CLI, or local skill without forcing the user to remember vendor names.

## What It Routes

- Web3/onchain: Dune, Alchemy, Etherscan, Coinbase CDP/AgentKit, CoinGecko, DeFiLlama, Binance Web3 skills, GMGN, BNB Agent Studio.
- CEX/DEX trading research: Binance CLI, Binance Agentic Wallet, GMGN, token audit/info/rank/signal skills.
- TradFi/market data candidates: Alpaca, OpenBB, Alpha Vantage, Financial Modeling Prep, Twelve Data, Massive/Polygon.io, Databento.
- Options and flow candidates: Unusual Whales, Alpaca options, Tradier, IBKR/TWS candidates.
- Quant/backtest frameworks: QuantConnect, LEAN, NautilusTrader, Hummingbot, Freqtrade, CCXT-backed local adapters.
- Execution-capable candidates: Binance, Coinbase CDP/AgentKit wallet actions, Alpaca, Tradier, Robinhood Agentic Trading, cTrader, IBKR/TWS, Hummingbot, Freqtrade, CCXT, NautilusTrader, QuantConnect live.

## Why One Skill

Finance/trading work fails when the agent treats every vendor as a separate mental mode. This skill keeps one front door and uses internal route maps:

```text
market question -> data source
token question -> onchain + token risk sources
signal question -> signal + liquidity + audit
strategy question -> backtest + risk
execution question -> safety policy first
```

## Safety Model

Default path:

```text
read-only -> simulation/backtest -> paper/demo -> explicit live confirmation
```

Live orders, swaps, transfers, approvals, leverage changes, and bot starts are never default actions. The skill must show venue, account, instrument, side, quantity, order type, price/slippage, fees, max loss/stop rule, and kill switch before asking for confirmation.

## Usage

Example prompts:

- `/stark-finance-trading 查一下 BTC 和 ETH 当前盘口、近 1 小时波动、主要风险`
- `/stark-finance-trading 看这个 BSC token 的 liquidity、holder、smart money 和合约风险`
- `/stark-finance-trading 用 Dune 做 pump.fun 最近 30 天每日发币量`
- `/stark-finance-trading 帮我回测 ETHUSDT 网格策略，重点看 MDD 和爆仓条件`
- `/stark-finance-trading 准备一个 Binance 下单草案，但先不要执行`

## Validation

Run from this directory:

```bash
python3 scripts/validate_stark_finance_trading.py .
python3 scripts/validate_public_readiness.py .
python3 scripts/quick_validate.py .
python3 scripts/run_quality_suite.py --json
python3 scripts/audit_public_sources.py --root . --out dist/stark-finance-trading.public-source-audit.json --markdown dist/stark-finance-trading.public-source-audit.md --json
python3 scripts/generate_public_benchmark.py --root . --out dist/stark-finance-trading.public-benchmark.json --markdown dist/stark-finance-trading.public-benchmark.md --json
python3 scripts/generate_competitive_task_benchmark.py --root . --out dist/stark-finance-trading.competitive-task-benchmark.json --markdown dist/stark-finance-trading.competitive-task-benchmark.md --json
python3 scripts/validate_github_actions_workflow.py --root . --out dist/stark-finance-trading.github-actions-workflow.json --markdown dist/stark-finance-trading.github-actions-workflow.md --json
python3 scripts/package_skill.py . dist
python3 scripts/install_package_smoke.py dist/stark-finance-trading.skill --json
python3 scripts/generate_release_manifest.py dist/stark-finance-trading.skill --skill-root . --out dist/stark-finance-trading.release-manifest.json --markdown dist/stark-finance-trading.release-manifest.md --json
python3 scripts/generate_live_eval_signoff.py --skill-path . --eval-set evals/live-behavior-evals.json --out dist/stark-finance-trading.live-eval-signoff.json --markdown dist/stark-finance-trading.live-eval-signoff.md --sandbox read-only --max-cases 6
python3 scripts/generate_release_notes.py --skill-root . --release-manifest dist/stark-finance-trading.release-manifest.json --live-signoff dist/stark-finance-trading.live-eval-signoff.json --out dist/stark-finance-trading.release-notes.json --markdown dist/stark-finance-trading.release-notes.md --json
python3 scripts/codex_eval.py --skill-path . --eval-set evals/live-behavior-evals.json --out-dir dist/live-eval-dry-run --max-cases 6 --json
python3 scripts/generate_eval_review_bundle.py dist/live-eval-dry-run --eval-set evals/live-behavior-evals.json --out-dir dist/stark-finance-trading.live-eval-review --title "stark-finance-trading Live Behavior Eval Review" --json
python3 scripts/score_eval_review_bundle.py dist/stark-finance-trading.live-eval-review --out dist/stark-finance-trading.live-eval-scorecard.json --markdown dist/stark-finance-trading.live-eval-scorecard.md --json
python3 scripts/generate_live_eval_signoff.py --skill-path . --eval-set benchmarks/competitive-task-cases.json --out dist/stark-finance-trading.competitive-eval-signoff.json --markdown dist/stark-finance-trading.competitive-eval-signoff.md --sandbox read-only --max-cases 8
python3 scripts/codex_eval.py --skill-path . --eval-set benchmarks/competitive-task-cases.json --out-dir dist/competitive-eval-dry-run --max-cases 8 --json
python3 scripts/generate_eval_review_bundle.py dist/competitive-eval-dry-run --eval-set benchmarks/competitive-task-cases.json --out-dir dist/stark-finance-trading.competitive-eval-review --title "stark-finance-trading Competitive Task Eval Review" --json
python3 scripts/score_eval_review_bundle.py dist/stark-finance-trading.competitive-eval-review --out dist/stark-finance-trading.competitive-eval-scorecard.json --markdown dist/stark-finance-trading.competitive-eval-scorecard.md --json
python3 scripts/export_github_repo.py --skill-root . --out-dir dist/github-export/stark-finance-trading --release-artifacts-dir dist --zip dist/stark-finance-trading-github-repo.zip --json
python3 scripts/smoke_github_export.py --zip dist/stark-finance-trading-github-repo.zip --out dist/stark-finance-trading.github-export-smoke.json --markdown dist/stark-finance-trading.github-export-smoke.md --json
python3 scripts/validate_release_readiness.py --skill-root . --dist dist --out dist/stark-finance-trading.release-readiness.json --markdown dist/stark-finance-trading.release-readiness.md --json
```

After the exported repository is public, enable and prove remote GitHub Actions only from the exported repository root:

```bash
gh auth refresh -h github.com -s workflow
python3 stark-finance-trading/scripts/enable_remote_ci.py --repo-root . --repo starkweng/stark-finance-trading --wait --out dist/stark-finance-trading.remote-ci-proof.json --markdown dist/stark-finance-trading.remote-ci-proof.md --json
```

## Evidence Boundaries

This v0.1 package has static validation, routing eval seeds, adversarial eval seeds, live behavior eval definitions, live/competitive eval signoff packets, human-review bundles, eval review scorecards, a public comparison snapshot, a public source audit, a source-level public benchmark scorecard, a task-level competitive router benchmark, GitHub Actions workflow validation, release manifest/notes sidecars, reproducible package smoke, a local quality suite, a local GitHub export path, an exported-repository smoke test, a remote CI proof helper, and a local release-readiness report. It is GitHub-ready as a source package, but remote GitHub Actions completion, approved live model evals, and reviewed comparative live evals remain separate external proofs.
