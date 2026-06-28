# GitHub Export Smoke Test

- Status: PASS
- ZIP: `dist/stark-finance-trading-github-repo.zip`
- Archive entries: 118

## Checks

| Check | Status |
|---|---|
| `zip_integrity` | PASS |
| `safe_paths` | PASS |
| `required_files` | PASS |
| `no_transient_files` | PASS |
| `exported_core_commands` | PASS |

## Command Smoke

| Command | Status |
|---|---|
| `quick_validate_exported_skill` | PASS |
| `validate_exported_skill` | PASS |
| `validate_exported_public_readiness` | PASS |
| `validate_exported_workflow` | PASS |
| `install_smoke_exported_package` | PASS |

## Evidence Boundary

Local smoke test of the exported GitHub repository ZIP only. It proves the archive can be extracted and core gates can run from the standalone layout. It does not prove remote GitHub Actions completion, uploaded artifact availability, live market-data correctness, live trading performance, or live model behavior.
