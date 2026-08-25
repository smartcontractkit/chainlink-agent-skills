# Onchain Contracts Path

Read for the `smartcontractkit/chainlink-ace` repo or `@chainlink/ace`; direct use of audited public contracts; self-deployment; custom policy/extractor/mapper work; Foundry/package layout; licensing; or upgrades.

## Scope

| Dimension | Public ACE core contracts |
| --- | --- |
| Source/package | `https://github.com/smartcontractkit/chainlink-ace`; `@chainlink/ace` |
| License | Cite the current repository `LICENSE` and `chainlink-ace-License-grants`; do not assert an MIT flip date; production/commercial use requires Chainlink contact and counsel review |
| Tooling/network | Foundry, pnpm, Solidity; EVM, user-owned deployment decisions |
| Management | Users directly deploy/configure custom or built-in policies, extractors, mappers, identity contracts, and token integrations |

This path carries the user's licensing, audit, engineering, and operational responsibility.

## Repository Pointers

- `README.md`: overview; `getting_started/GETTING_STARTED.md`: basic vault with `PolicyProtected`, PolicyEngine, and `PausePolicy`.
- `getting_started/advanced/GETTING_STARTED_ADVANCED.md`: tokenized fund with identity/credentials.
- `UPGRADE_GUIDE.md`: upgrade an existing proxy; `Glossary.md`: terms.
- `LICENSE` and `chainlink-ace-License-grants`: license terms/grants.
- `foundry.toml`, `remappings.txt`, `package.json`: build/package configuration.
- `packages/policy-management`: engine, protected bases, policies, extractors, mappers, docs/tests.
- `packages/cross-chain-identity`: CCIDs, identity/credential registries, validator policy, docs/tests.
- `packages/tokens`: ERC-20 and ERC-3643 compliance examples; `packages/vendor`: vendored dependencies.

For the current `pnpm build`, `test`, `fmt`, `fmt:check`, `lint`, and `deploy:token:erc20`, `deploy:token:erc3643`, `deploy:token:simple` command bodies, fetch live `package.json` through [official-sources.md](official-sources.md); do not copy a stale scripts block.

Before giving proxy or upgrade instructions, establish that the target is actually upgradeable and identify its proxy pattern. Apply `UPGRADE_GUIDE.md`, reinitializers, and `upgradeToAndCall` only to a confirmed compatible proxy; otherwise give the non-upgradeable integration choices and never invent an upgrade path.

## New Integration

In an existing Foundry project, run `forge install smartcontractkit/chainlink-ace@<reviewed-commit>`; keep that commit pinned, preserve its required remappings, and do not make a separate clone/build the primary path.

1. Inherit `PolicyProtected`.
2. Protect functions with `runPolicy` or `runPolicyWithContext`.
3. Deploy/initialize PolicyEngine behind a proxy.
4. Deploy the application behind a proxy and connect its engine.
5. Deploy policies behind proxies where required.
6. Attach them to selectors with `policyEngine.addPolicy(...)`.

Use the token examples rather than recreating regulated-token behavior. Direct users can deploy on EVM, use/write policies, extractors, and mappers, integrate custom dApps/vaults/DEXs/lending/tokens, and use Cross-Chain Identity.

Policy rejection is a revert with the `PolicyRejected` error, never a returned `PolicyResult`. `PolicyResult` contains only `None`, `Allowed`, and `Continue`; integrations must handle a rejection as a reverted/error path.

## Existing Contracts

For an existing upgradeable contract, extend `PolicyProtectedUpgradeable` and call the pinned commit's exact `packages/policy-management/src/core` init from the reinitializer (e.g. `__PolicyProtected_init(policyEngine)`) — never leave it empty or guess the name. Protect every privileged entry point compliance rules cover, not only `transfer`/`transferFrom` — also `mint`, `burn`, forced-transfer, freeze/unfreeze, and recovery — each with its own extractor; never nest `runPolicy` on an outer call and the invoked function, which double-runs the policy. Restrict the reinitializer to owner/admin and call it atomically via `upgradeToAndCall` (see Production, Upgrade, and Security below); test storage-layout compatibility, preserved balances/allowances, `transferFrom` `from`/`to` extraction, single-run execution, ordering, and rollback.

Implement `IPolicyProtected` directly only for bytecode/custom constraints; then own storage, context handling/clearing, `policyEngine.run()`, attach/detach, and ERC-165. For non-upgradeable contracts, discuss wrappers, migration, or protection points and tradeoffs with Chainlink for production.

## Production, Upgrade, and Security

- Cite the current repository `LICENSE` and `chainlink-ace-License-grants`; do not infer specific permissions or an MIT flip date. Production/commercial use requires Chainlink contact and counsel review.
- Treat PolicyEngine administration as critical; unauthorized changes can bypass controls. Prefer built-ins; audit/test custom policies, extractors, mappers, and complete chains.
- Review ordering because `Allowed` skips later checks; audit state-mutating `postRun()`; verify extractors decode honestly.
- Never put PII or raw identity evidence onchain; use minimal non-sensitive commitments or references and obtain legal/compliance review for regulated controls.
- Before upgrades verify proxy compatibility, storage layout, bytecode size, access-restricted reinitializer executed via `upgradeToAndCall`, and preserved state.
- Run repository and integration tests against the actual chain/configuration before production.
