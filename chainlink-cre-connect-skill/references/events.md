# Watchers and Verifiable Events

Read this file for watcher design, event handling, local verification, confidence/finality, and failures.

## Watchers

A watcher binds one channel, one chain selector, one contract address, and one or more event signatures. A matching log becomes a `watcher.event` after reaching the watcher's confidence level and receiving a DON/OCR proof.

Two conceptual provisioning paths are documented:

- **Service-backed:** reference a published extension service such as `dta.v2`; the extension owns the ABIs and decoded event types.
- **ABI-backed:** provide an ABI and event names for contracts without an extension.

Only a watcher's name is mutable. To change its chain, address, ABI, or event set, archive it and create a replacement.

| Watcher state | Handling |
| --- | --- |
| `pending` | Wait; provisioning is incomplete. |
| `active` | Consume matching events. |
| `archiving` | Teardown is asynchronous; no new events are emitted. |
| `archived` | Read-only; historical events remain available. |
| `failed` | Inspect the latest status reason, then archive and recreate. |

`watcher.status` payloads can additionally report `archive_failed`, distinguishing failed teardown from failed creation. The platform assigns the watcher's DON family; use it to select the expected signer set and diagnose the responsible DON.

## Event Envelope and Types

Every event includes an ID, channel, type, one OCR proof, typed payload, and CRE Connect receipt timestamp. The proof contains the report, replay-protection context, and DON signatures.

| Type | Meaning |
| --- | --- |
| `watcher.event` | Decoded matching contract log plus transaction hash, block number, and confidence. |
| `watcher.status` | Watcher lifecycle transition and optional reason. |
| `wallet.status` | Smart Account provisioning transition. |
| `operation.status` | Operation transition; confirmed payloads include the chain transaction hash and per-call result. |

All events in a channel form one ordered, immutable, paginated stream. The public source does not publish pagination fields or client methods; use the provisioned contract rather than inventing cursors.

## Local Verification

Verification is event-family aware. Given the event/proof, expected tenant workflow owner, valid DON signer set, and signature threshold:

1. Reject the wrong event family or anything other than exactly one OCR proof.
2. Hash the application-visible payload bytes.
3. Confirm the report binds both the expected workflow owner and the local payload hash.
4. Recompute the OCR report hash from report bytes and replay-protection context.
5. Recover each signing address.
6. Require the configured number of **distinct** recovered addresses from the valid signer set.

A pass establishes authenticity, integrity, and replay protection. It does not establish authorization for another tenant or chain finality. Lower-level signature/threshold verification without owner/payload binding is insufficient unless that trust was established through another channel.

## Failure Handling

Fail closed on wrong type, missing or duplicate proof, owner/hash mismatch, malformed signature, or insufficient threshold. The only documented transient verification failure is an event arriving before its proof: skip it and re-poll. Do not retry other failures as though they were harmless transport lag.

## Confidence and Side Effects

Confidence is independent of proof verification:

| Level | Intended use |
| --- | --- |
| `latest` | Read-only dashboards, tailing, low-stakes notifications; reorgs remain possible. |
| `safe` | Operational alerts and reversible non-financial effects. |
| `finalized` | Irreversible actions, fund flows, regulatory reporting, and consequential downstream calls. |

Require both local verification and a confidence level suitable for the action. For irreversible business actions, require `finalized`. Check each chain's official finality semantics and read the actual confidence from the watcher/event.

For any side effect, process in this order: locally verify the event; require confidence/finality suitable for the consequence; durably deduplicate by the immutable event ID; then perform the consequential action only after its application-owned side-effect state is durable, or commit the state and action atomically. Keep that state across restarts so redelivery cannot repeat fulfillment.

## Sources

- `https://docs.chain.link/crec/concepts/watchers.md`
- `https://docs.chain.link/crec/concepts/verifiable-events.md`
- `https://docs.chain.link/crec/concepts/event-verification.md`
- `https://docs.chain.link/crec/concepts/confidence-levels.md`
