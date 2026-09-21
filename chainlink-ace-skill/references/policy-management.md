# Policy Management

Read for PolicyEngine/PolicyProtected, policy chains, extractors, mappers, context/default behavior/order, protected functions, or custom components.

## Model

Policy Management separates enforcement from business logic:
- applications inherit `PolicyProtected` or implement `IPolicyProtected`;
- protected functions use `runPolicy` or `runPolicyWithContext`;
- PolicyEngine runs policies by target and function selector;
- policies, extractors, and mappers can change without replacing application logic.

See [architecture.md](architecture.md#canonical-protected-transaction-flow) for the single canonical nine-step runtime flow.

The engine completes successful policy checks and any `postRun()` hooks before the protected function body or token balance update, never after (see architecture.md's canonical flow).

| Outcome | Effect |
| --- | --- |
| `PolicyRejected(reason)` | Revert immediately; skip remaining policies |
| `Allowed` | Allow immediately; skip remaining policies |
| `Continue` | Advance to the next policy or engine default |

Both rejection and `Allowed` are terminal, so ordering is part of the security design.

## Parameters and Context

Register an extractor per target/selector to decode calldata into named parameters such as `to`, `amount`, or `account`. When attaching a policy, configure which parameters it receives; a configured mapper or default name-based mapping selects/transforms them.

Custom extractors/mappers are supported when standard parsing or mapping does not fit. They are trusted code: a dishonest extractor can bypass correct policies.

`context` is arbitrary `bytes` for authorization/compliance evidence such as offchain signatures, Merkle proofs, approval metadata, or policy-specific evidence. Per-sender stored context must be set and consumed atomically; otherwise a later call can reuse stale context.

## Existing-Policy Edits

Treat an existing-policy request as a configuration delta, not a redesign. Inventory the current target/selector attachments, default behavior, policy instances and order, exact `setExtractor` and mapper mappings, owners/admins, and proxy version before proposing a change. Prefer the existing policy's owner setter or membership edit over replacement. Keep setup fail closed; if a migration is unavoidable, retain the pinned-commit reinitializer and existing upgrade governance rather than introducing a new upgrade path.

For a rate-limit request scoped to one wallet, never propose or include in the write preflight any addition or configuration of a shared `VolumeRatePolicy`; its maximum and period would apply to every account reaching it. Obey the top-level **Policy Edit Answer Contract** before selecting a change. If the current policy configuration has no daily cap, require an existing wallet-scoped rule or an audited account-aware custom policy.

Route every discovered holder-outflow selector through the same owner-volume rule. When an unchanged shared rule already has the requested limit and a bypass is intended to skip only that rate limit, preserve `PausePolicy` → `BypassPolicy` → `VolumeRatePolicy`: pause cannot be bypassed, listed accounts return `Allowed` before the limit, and all others continue to the unchanged shared limit.

## Ordering and Administration

Policies execute in attachment order. PolicyEngine provides `addPolicy()` (append), `addPolicyAt()` (insert), `removePolicy()`, and `getPolicies()`; reorder by remove then add at the desired position.

Default order:
1. hard restrictions and business limits a bypass must never skip;
2. a permissive bypass, only when intentional;
3. exactly the amount/volume/time/reserve checks that listed accounts may skip.

Restrict `addPolicy`, `removePolicy`, `setExtractor`, `setPolicyMapper`, and default-behavior changes; production systems should consider timelocks.

## Minimal Integration

```solidity
import {PolicyProtected} from "@chainlink/policy-management/core/PolicyProtected.sol";

contract MyContract is PolicyProtected {
    function sensitiveAction(uint256 amount) public runPolicy {
        // business logic
    }
}
```

Deploy PolicyEngine, the protected contract, and policies behind proxies where required, then attach policies to selectors with `policyEngine.addPolicy(...)`. Existing upgradeable contracts use `PolicyProtectedUpgradeable` plus a pinned-commit reinitializer (see onchain-contracts.md); use direct `IPolicyProtected` only for bytecode/custom constraints.

## Security

- Audit policies, extractors, mappers, and state-mutating `postRun()` hooks. External policy calls add denial-of-service, gas, and consistency risks.
- Direct `IPolicyProtected` implementations must correctly own storage, context clearing, attach/detach, and ERC-165.
- Test complete order/default/outcome behavior, not only each policy in isolation.
