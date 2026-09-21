# ACE Architecture

Read for component relationships, Policy Management plus Cross-Chain Identity, protected-call flow, or a high-level diagram.

## System

The public `chainlink-ace` repository is modular:

| Component | Role | Dependency |
| --- | --- | --- |
| Policy Management | Dynamic onchain rule creation/enforcement | Standalone |
| Cross-Chain Identity | Portable EVM identity: attach credentials once, verify across addresses/chains | Policy Management |
| Token examples | Full ERC-20 and ERC-3643 integrations | Policy Management; identity when required |

Policy Management is the enforcement layer; Cross-Chain Identity is an optional credential layer that it governs and consumes.

| Component | Role |
| --- | --- |
| `PolicyProtected` / `PolicyProtectedUpgradeable` | Application bases providing `runPolicy` and context handling |
| `IPolicyProtected` | Manual integration when inheritance is unsuitable |
| `PolicyEngine` | Orchestrates policies, extractors, and mappers by target/function |
| `Policy` | One rule through `run()` and optional `postRun()` |
| Extractor | Parses calldata into named parameters |
| Mapper | Selects/transforms parameters for a policy |
| CCID | `bytes32` cross-chain identity |
| Identity Registry | Maps local addresses to CCIDs |
| Credential Registry / Issuer | Stores CCID credentials / trusted offchain verifier that writes them |
| Credential Source / validator policy | Selects trusted registries / checks credential requirements |

Identity registries are policy-governed, so issuer authorization can change without hardcoded ownership.

## Canonical Protected-Transaction Flow

1. A user calls a protected application function, such as ERC-20 `transfer(address,uint256)` or `transferFrom(address,address,uint256)`.
2. Before the protected function body or balance update, `runPolicy` or `_runPolicy()` submits the call payload to `PolicyEngine`.
3. The selector's extractor decodes calldata into named parameters.
4. A configured/default mapper supplies each policy's expected parameters.
5. Policies run in attachment order.
6. `PolicyRejected` reverts; `Allowed` skips later policies; `Continue` advances.
7. If all policies continue, the engine applies its configured default behavior.
8. After the call is allowed, optional `postRun()` hooks run before the protected function body.
9. Only then does the protected function body, such as the ERC-20 balance update, execute.

Never describe `postRun()` as occurring after `transfer` or `transferFrom`.

Example: for a tokenized bond trade, an identity policy can require KYC/accreditation before a volume/rate policy checks limits; rejection stops business logic.

## Design Rules

- Use Policy Management alone for calldata, sender, time, role, limit, or external-onchain-data rules; add identity when rules depend on credentials portable across addresses/chains.
- Restrict PolicyEngine administration. Treat policies, extractors, and mappers as trusted: a dishonest extractor can defeat correct policies.
- For production, review BUSL licensing, audit the configuration, and test complete policy chains.
