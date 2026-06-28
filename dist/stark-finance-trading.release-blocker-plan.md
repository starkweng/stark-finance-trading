# Release Blocker Plan

- Status: PASS
- Plan status: `ACTIONABLE_BLOCKERS_OPEN`
- Goal completion status: `NOT_COMPLETE_REQUIREMENTS_PENDING`
- Release status: `LOCAL_RELEASE_READY`
- Blockers: 4
- Actionable blockers: 4
- External/user-gated blockers: 4
- No secret values: True

## Category Counts

| Category | Count |
|---|---:|
| `needs_github_permission` | 1 |
| `needs_live_eval_approval` | 2 |
| `needs_secret_or_env` | 1 |

## Blockers

| Blocker | Status | Category | Owner | Required Action |
|---|---|---|---|---|
| `critical_runtime_alignment` | PARTIAL | `needs_secret_or_env` | Stark/local secret setup | Set ETHERSCAN_API_KEY if Etherscan live calls are required. |
| `remote_github_actions_proven` | MISSING | `needs_github_permission` | Stark/GitHub auth | Run `gh auth refresh -h github.com -s workflow`, then rerun this script with `--wait`. |
| `approved_live_model_eval_proven` | MISSING | `needs_live_eval_approval` | Stark/live eval reviewer | Run an approved live eval, generate the review bundle, and score it after human review. |
| `reviewed_comparative_live_eval_proven` | MISSING | `needs_live_eval_approval` | Stark/live eval reviewer | Run an approved live eval, generate the review bundle, and score it after human review. |

## Verification Commands

### `critical_runtime_alignment`

```bash
python3 scripts/runtime_capability_scan.py --root . --out dist/stark-finance-trading.runtime-capabilities.json --markdown dist/stark-finance-trading.runtime-capabilities.md --json
```

Success evidence: etherscan-mcp no longer appears in env_missing_tool_ids and ETHERSCAN_API_KEY presence is true.

### `remote_github_actions_proven`

```bash
gh auth refresh -h github.com -s workflow; python3 scripts/enable_remote_ci.py --repo-root . --repo starkweng/stark-finance-trading --wait --out dist/stark-finance-trading.remote-ci-proof.json --markdown dist/stark-finance-trading.remote-ci-proof.md --json
```

Success evidence: remote_github_actions_run is PROVEN or PROVIDED in external proof audit.

### `approved_live_model_eval_proven`

```bash
python3 scripts/generate_live_eval_signoff.py --skill-path . --eval-set evals/live-behavior-evals.json --live-out-dir dist/live-eval --out dist/stark-finance-trading.live-eval-signoff.json --markdown dist/stark-finance-trading.live-eval-signoff.md
```

Success evidence: approved_live_model_eval is PROVEN or PROVIDED and scorecard source_mode is live/reviewed.

### `reviewed_comparative_live_eval_proven`

```bash
python3 scripts/generate_live_eval_signoff.py --skill-path . --eval-set benchmarks/competitive-task-cases.json --live-out-dir dist/competitive-eval --out dist/stark-finance-trading.competitive-eval-signoff.json --markdown dist/stark-finance-trading.competitive-eval-signoff.md
```

Success evidence: reviewed_comparative_live_eval is PROVEN or PROVIDED and scorecard source_mode is live/reviewed.

## Evidence Boundary

Release blocker plan is an actionable routing artifact. PASS means the plan was generated from local audits without printing secret values. It does not prove remote GitHub Actions, live model behavior, API entitlement, market-data correctness, trading performance, or public superiority.
