# Operations, Signing, and Smart Accounts

Read this file for outbound writes, EIP-712 authorization, Smart Accounts, gas sponsorship, lifecycle handling, and safe submission design.

## Operation Model

An Operation is one atomic, ordered batch of EVM calls:

| Field | Meaning |
| --- | --- |
| `id` | Monotonically increasing wallet operation ID chosen by the application; orders operations and detects duplicates. |
| `account` | Smart Account that executes the batch. |
| `deadline` | Unix-second expiry; `0` means no expiration. Expired operations are not broadcast. |
| `transactions` | Ordered `(to, value, data)` calls executed with the Smart Account as sender. |

If any call reverts, the whole batch reverts. Use one Operation for intentionally indivisible flows. Use separate Operations for independent actions that need partial success.

## Lifecycle

| Status | Meaning |
| --- | --- |
| `accepted` | CRE Connect accepted the signed Operation. |
| `sending` | The internal workflow is preparing the write. |
| `sent` | The chain transaction was broadcast. |
| `broadcasting` | Awaiting block inclusion. |
| `confirmed` | The Smart Account emitted `OperationExecuted`; the verifiable status includes the chain transaction hash. |
| `failed` | Execution cannot complete; inspect the reason. |

Treat lifecycle transitions as verifiable events. A missed deadline produces `failed`; construct and sign a new Operation only after deciding that retry is still valid. Never mutate and reuse an old signature.

## EIP-712 Authorization

The published typed-data shape is:

```text
Operation(uint256 id,address account,uint256 deadline,Transaction[] transactions)
Transaction(address to,uint256 value,bytes data)
```

The documented domain is:

| Field | Value |
| --- | --- |
| `name` | `CLLSmartAccount` |
| `version` | `1` |
| `chainId` | Numeric chain ID where the account is deployed. |
| `verifyingContract` | Smart Account address. |

The domain prevents reuse across accounts and chains. The deadline, ID, account, call order, destinations, values, and calldata are authorization-critical; show them to the approver and never alter them after signing.

The public source describes the signing boundary conceptually but does not publish a CRE Connect client or signer API. Require the organization's provisioned API/SDK types and use its canonical typed-data construction. Do not invent methods or manually approximate a hidden serialization contract.

## Smart Accounts

A Wallet is the off-chain resource; its Smart Account is the on-chain executor. Each account is tenant-owned, bound to one chain, and configured with allowed signers. Signer configuration is fixed at creation; create a new wallet to rotate it.

| Wallet state | Meaning |
| --- | --- |
| `pending` | Record exists; deployment has not started. |
| `deploying` | Awaiting on-chain deployment inclusion. |
| `deployed` | Account is live and can execute Operations. |
| `archived` | Read-only; new Operations are rejected. |
| `failed` | Deployment failed; inspect the latest `wallet.status` reason. |

The account verifies authorization and executes the batch. The DON writer broadcasts and pays gas. This is Chainlink-native account abstraction: there is no ERC-4337 EntryPoint, `UserOperation`, paymaster, or bundler. Do not model the application signer as `tx.origin`; the DON writer is `tx.origin`, while authorization comes from the recovered signed payload and the account's allow-list.

## Gas and Asset Boundaries

Gas sponsorship covers the transaction broadcast, the `OperationExecuted` log, and the status read. It does not fund call `value`, token transfers/approvals, or application infrastructure. Ensure the Smart Account owns every asset/value the batch consumes.

## Submission Preflight

Before a real submission, present and confirm:

- environment and current supported network; chain selector and EIP-712 `chainId`
- Smart Account address and deployed state
- operation ID and replay/ordering check
- deadline and expected backend/finality latency
- every ordered call's destination, native value, decoded intent, and calldata provenance
- required Smart Account assets/allowances
- authorized signer identity and custody boundary
- atomic revert behavior and expected resulting events

Never read signing secrets. Do not submit until the user explicitly confirms this exact payload through the approved custody workflow.

## Sources

- `https://docs.chain.link/crec/concepts/operations.md`
- `https://docs.chain.link/crec/concepts/eip712-signing.md`
- `https://docs.chain.link/crec/concepts/smart-accounts.md`
- `https://docs.chain.link/crec/concepts/account-abstraction.md`
