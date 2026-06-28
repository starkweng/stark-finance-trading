# Security Policy

This skill touches financial and trading workflows, so the security boundary is part of the product.

## Never Include

- wallet private keys or seed phrases;
- broker, CEX, or API secrets;
- OAuth tokens, JWTs, or session cookies;
- production RPC secrets;
- account screenshots that expose sensitive balances or identifiers.

## Reporting Issues

Report issues that could cause:

- live order execution without explicit confirmation;
- leaking credentials or account data;
- treating untrusted token metadata as instructions;
- bypassing paper/demo mode;
- incorrect routing from marketing or tokenomics into live trading.

## Execution Safety

Any live state-changing action must show venue/account/network, instrument, side/action, quantity, order type, price/slippage, fee/gas, max loss/stop rule, and kill-switch path before confirmation.

Ambiguous confirmation is not enough.
