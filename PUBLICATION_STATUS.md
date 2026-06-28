# Publication Status

Current public repository:

- Repo: https://github.com/starkweng/stark-finance-trading
- Visibility: public
- Main branch: `main`
- Published commit: `52d754a`

## Completed External Proofs

- Public repository URL: provided.
- Source package and release evidence: pushed to the public repository.
- Local release readiness: `LOCAL_RELEASE_READY`.

## Pending External Proofs

- Remote GitHub Actions run: pending.
- Approved live model eval: pending.
- Reviewed comparative live eval: pending.

## CI Scope Note

The CI workflow is available as `workflow-templates/stark-finance-trading-ci.yml`.

The executable GitHub Actions path `.github/workflows/ci.yml` could not be pushed with the current GitHub CLI token because the token has `repo`, `read:org`, and `gist` scopes, but not `workflow`. GitHub rejects workflow-file pushes from OAuth tokens without that scope.

To enable remote CI, refresh GitHub CLI auth with the `workflow` scope, then add the workflow file:

```bash
gh auth refresh -h github.com -s workflow
mkdir -p .github/workflows
cp workflow-templates/stark-finance-trading-ci.yml .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "Enable CI workflow"
git push
```

## Evidence Boundary

This repository proves public publication and local release evidence. It does not yet prove remote GitHub Actions completion, live model behavior, market-data correctness, trading performance, or public superiority.
