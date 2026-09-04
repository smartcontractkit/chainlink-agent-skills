# Concepts and Access

Read this file for product fit, private-beta access, architecture, channels, and top-level resource boundaries.

## Product Boundary

CRE Connect is the tenant-scoped, client-facing interface to CRE. It provides:

- **Inbound:** watched on-chain logs delivered as DON/OCR-signed verifiable events.
- **Outbound:** EIP-712-authorized batches of EVM calls executed through a Smart Account without application-managed gas, nonces, or relayers.
- **Extensions:** protocol-specific operation builders, event decoders, and watcher bundles; DTA is the published extension.

CRE Connect provisions and operates the CRE workflows behind these flows. An integrator does not author or deploy those internal workflows. Use `chainlink-cre-skill` when the requested artifact is an ordinary CRE workflow.

## Access and Integration Prerequisite

CRE Connect is private beta. An organization must contact Chainlink and be provisioned before using it. The public `llms-full.txt` explains concepts but does not publish a client package, endpoint, authentication contract, or callable API.

For implementation, require the provisioned API/SDK documentation, generated client or types, authentication requirements, tenant metadata, workflow-owner identity, DON signer configuration, and current network support. Do not invent any of them.

## Architecture

The two product flows share the platform and DON:

- **Inbound:** watched contract log → internal CRE workflow → DON/OCR proof → channel event stream → application.
- **Outbound:** application-signed Operation → CRE Connect → internal CRE workflow/DON writer → Smart Account → `OperationExecuted` log → verifiable `operation.status` event.

Watched contracts need no CRE Connect integration. A watcher can observe an application's contract, a partner contract, a public protocol contract, or a Smart Account.

## Resources

| Resource | Role | Where details live |
| --- | --- | --- |
| Channel | Top-level isolation and ordered event-stream scope | This file |
| Watcher | One-chain, one-contract log monitor | [events.md](events.md) |
| Event | Immutable DON-signed record | [events.md](events.md) |
| Wallet / Smart Account | Off-chain record / on-chain executor | [operations.md](operations.md) |
| Operation | Signed atomic batch of EVM calls | [operations.md](operations.md) |

CRE Connect identifies networks with Chainlink chain selectors, not EIP-155 chain IDs. Obtain current selectors and supported-network data from official product material.

## Channels

Every watcher, wallet, event, and operation belongs to exactly one channel. Use separate channels for independent audit trails, subscriber groups, environments, or polling cadences.

| State | Meaning |
| --- | --- |
| `active` | Accepts watchers, wallets, operations, and event polling. |
| `archived` | Read-only; historical immutable events remain queryable. |

A channel cannot be archived while it has active watchers; archive its watchers first.

## Sources

- `https://docs.chain.link/crec.md`
- `https://docs.chain.link/crec/getting-started.md`
- `https://docs.chain.link/crec/concepts/architecture.md`
- `https://docs.chain.link/crec/concepts/channels.md`
- `https://docs.chain.link/crec/supported-networks.md`
