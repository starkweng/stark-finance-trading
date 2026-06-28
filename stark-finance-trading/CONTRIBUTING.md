# Contributing

The project goal is a high-trust finance and trading skill, not a prompt dump.

## Contribution Rules

- Keep `SKILL.md` as a router. Put long rules in `references/`, checks in `scripts/`, and routing cases in `evals/`.
- Add a routing eval for every new trigger or negative boundary.
- Do not add broker, wallet, exchange, or API credentials to examples.
- Execution-capable tools must remain behind the read-only -> simulation -> paper -> explicit live confirmation ladder.
- Prefer official data/API/MCP sources over random community wrappers.

## Local Checks

```bash
python3 scripts/quick_validate.py .
python3 scripts/validate_stark_finance_trading.py .
python3 -m json.tool evals/codex-evals.json >/dev/null
python3 -m json.tool evals/routing-evals.json >/dev/null
python3 scripts/package_skill.py . dist
python3 scripts/install_package_smoke.py dist/stark-finance-trading.skill --json
```

## Evidence Labels

Use honest labels:

- static validation;
- dry-run routing eval;
- package smoke;
- live model-service eval;
- human trading-safety review.

Do not claim public superiority without comparative evidence.
