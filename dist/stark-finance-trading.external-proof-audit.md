# External Proof Audit

- Status: PASS
- External proof status: `PENDING`
- Goal completion status: `NOT_COMPLETE_EXTERNAL_PROOFS_PENDING`
- Proven/provided required proofs: 1/4
- Pending or blocked required proofs: 3

## Required Proofs

| Proof | Status | Evidence | Required Action |
|---|---|---|---|
| `public_repo_url` | PROVIDED | A public GitHub repository URL was supplied. | - |
| `remote_github_actions_run` | BLOCKED | GitHub CLI token is missing workflow scope. | Run `gh auth refresh -h github.com -s workflow`, then rerun this script with `--wait`. |
| `approved_live_model_eval` | PENDING | Scorecard status=PASS; source_mode=dry_run; behavior_proof_status=UNPROVEN_DRY_RUN_ONLY. | Run an approved live eval, generate the review bundle, and score it after human review. |
| `reviewed_comparative_live_eval` | PENDING | Scorecard status=PASS; source_mode=dry_run; behavior_proof_status=UNPROVEN_DRY_RUN_ONLY. | Run an approved live eval, generate the review bundle, and score it after human review. |

## Supporting Evidence

| Evidence | Status | Boundary |
|---|---|---|
| `Live eval harness smoke` | HARNESS_ONLY_NOT_MODEL_PROOF | Harness smoke proves the approved-runner path only. It is not live model behavior proof. |
| `Competitive eval harness smoke` | HARNESS_ONLY_NOT_MODEL_PROOF | Harness smoke proves the approved-runner path only. It is not live model behavior proof. |

## Required Actions

- Run `gh auth refresh -h github.com -s workflow`, then rerun this script with `--wait`.
- Run an approved live eval, generate the review bundle, and score it after human review.
- Run an approved live eval, generate the review bundle, and score it after human review.

## Evidence Boundary

This audit classifies external completion proofs. PASS means the audit ran and labeled the evidence. Goal completion remains pending until every required proof is PROVEN or PROVIDED. Harness smokes, dry-run scorecards, and local package checks are useful release evidence but are not live model behavior, remote CI success, market-data correctness, trading performance, or public superiority proof.
