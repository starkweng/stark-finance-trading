# Remote CI Proof

- Status: FAIL
- Repo: `starkweng/stark-finance-trading`
- Workflow scope: False
- Remote workflow file: MISSING_OR_INACCESSIBLE
- Actions enabled: True
- Workflow publish: SKIPPED
- Dispatch: SKIPPED

## Required Action

```bash
gh auth refresh -h github.com -s workflow
```

Then rerun:

```bash
python3 stark-finance-trading/scripts/enable_remote_ci.py --repo-root . --repo starkweng/stark-finance-trading --wait --out dist/stark-finance-trading.remote-ci-proof.json --markdown dist/stark-finance-trading.remote-ci-proof.md --json
```

## Evidence Boundary

This proof only covers enabling and observing the GitHub Actions CI workflow. A successful remote run does not prove live model behavior, market-data correctness, trading performance, or public superiority.
