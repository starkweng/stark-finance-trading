# stark-finance-trading

Standalone GitHub handoff for the Stark finance/trading router skill.

## Source Layout

- `stark-finance-trading/` contains the installable skill source.
- `.github/workflows/ci.yml` runs the portable quality suite from that subdirectory.
- `dist/` contains release artifacts copied during export when available.

## Quick Validation

```bash
cd stark-finance-trading
python3 scripts/run_quality_suite.py --json
```

## Evidence Boundary

Local validation and package smoke do not prove remote GitHub Actions completion or live model behavior.
