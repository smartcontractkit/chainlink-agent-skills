# Policy Library

Read to select/compose a policy or answer behavior, configuration, runtime-parameter, setter, view-function, or tradeoff questions. Public policies call `initialize(address policyEngine, address initialOwner, bytes configParams)`; base `Policy` sets the engine, owner, and common modules, then one-time `configure(bytes)` decodes policy configuration.

## Policy Matrix

`PolicyRejected` is a revert/error, not a `PolicyResult`. The only results are `None`, `Allowed`, and `Continue`; rows that reject revert with `PolicyRejected`, while non-rejecting rows return `Continue` except the explicit `Allowed` case.

| Policy | Use; extracted inputs | Configuration and runtime behavior | Owner setters / views |
| --- | --- | --- | --- |
| `AllowPolicy` | Require approved participants; variable number of addresses | Reject if any address is not allowlisted | `allowSender(address)`, `disallowSender(address)` / `senderAllowed(address)` |
| `RejectPolicy` | Sanctions, compromised-wallet, malicious-address denylist; variable number of addresses | Reject if any address is denylisted | `rejectAddress(address)`, `unrejectAddress(address)` / `addressRejected(address)` |
| `BypassPolicy` | Deliberate privileged fast path; variable number of addresses | Return **`Allowed`** only when every address is listed; otherwise `Continue`. Because `Allowed` skips only later policies, position it after every check it must never skip and before exactly the checks it is meant to skip; placed last it bypasses nothing. | `allowSender(address)`, `disallowSender(address)` / `senderAllowed(address)` |
| `OnlyAuthorizedSenderPolicy` | Caller authorization; no extractor input, reads `sender` | Reject an unauthorized sender | `authorizeSender(address)`, `unauthorizeSender(address)` / `senderAuthorized(address)` |
| `OnlyOwnerPolicy` | Policy-owner-only call; no extractor input, reads `sender` | Continue only for policy owner; otherwise revert | owner is the check |
| `RoleBasedAccessControlPolicy` | Role/function access; reads sender and operation/function selector | Operation allowances map operations to roles; assignments map addresses to roles; reject unless sender holds an allowed role | `grantOperationAllowanceToRole(bytes4,bytes32)`, `removeOperationAllowanceFromRole(bytes4,bytes32)`, `grantRole(bytes32,address)`, `revokeRole(bytes32,address)` / `hasAllowedRole(bytes4,address)` |
| `MaxPolicy` | Per-transaction ceiling; one `uint256 amount` | Configure one maximum; reject when `amount > max` | `setMax(uint256)` / `getMax()` |
| `VolumePolicy` | Per-transaction range; one `uint256 amount` | Configure min/max; max `0` means no upper limit; reject below min or above a nonzero max | `setMin(uint256)`, `setMax(uint256)` / `getMin()`, `getMax()` |
| `VolumeRatePolicy` | Per-account volume over time; `uint256 amount`, `address account` | Configure maximum per period and duration seconds; reject when current-period volume + amount exceeds max; **`postRun()` updates the account's current-period volume** | `setMaxAmount(uint256)`, `setTimePeriod(uint256)` / `getMaxAmount()`, `getTimePeriod()` |
| `IntervalPolicy` | Repeated business/weekday/maintenance windows; no input | Configure start/end slots, slot duration, cycle size/offset. Current slot is `((block.timestamp / slotDuration) % cycleSize + cycleOffset) % cycleSize`; allow `[startSlot, endSlot)` only. | `setStartSlot(uint256)`, `setEndSlot(uint256)`, `setCycleParameters(uint256,uint256,uint256)` |
| `PausePolicy` | Emergency stop/launch gate; no input | Configure paused boolean; reject while paused. Deploy/initialize paused if other policies need configuration before launch. | `pause()`, `unpause()` |
| `SecureMintPolicy` | Collateral/reserve-backed minting; extractor must supply the exact `uint256 amount` being minted | Configure reserve feed, token metadata/decimals, reserve-margin mode and amount, max staleness, and the intended supply calculation; reject any mint beyond verified backing and fail closed on unusable reserve data | `setReservesFeed(address)`, `setTokenMetadata(address,uint8)`, `setReserveMargin(...)`, `setMaxStalenessSeconds(uint256)` |

## Selection and Safety

For `SecureMintPolicy`, the reserve/margin design for asset-backed tokens requires explicit legal/compliance review in addition to technical/audit controls, and every mint path—including privileged, reserve, admin, and recovery minting—must run the reserve check; never permit a role or `BypassPolicy` to skip it. Configure the extractor to decode the exact mint amount and protect every mint selector. Verify the configured token address and metadata decimals; the policy scales the feed value to token decimals, and incorrect metadata can allow over-minting or block valid mints.

A failed/reverted feed read, negative answer, or stale reserve value must block minting. Max staleness `0` accepts data of any age and must be an explicit approved choice. Review each reserve-margin mode: positive modes keep a buffer, while negative modes permit supply above reported reserves and therefore violate a strict fully-backed invariant. Confirm the pinned implementation's supply calculation and how burns reopen mint headroom; test both sides of the boundary. Protect, approve, and monitor feed, token-metadata, margin, and staleness setters. Place hard pause/deny/credential checks first, then `SecureMintPolicy`, and only then any intentional bypass of unrelated later checks. Fetch and cite the current `docs.chain.link` SecureMintPolicy page for managed scope, but cite the pinned `smartcontractkit/chainlink-ace` source for OSS behavior. Keep PII offchain and require legal/compliance review for asset-backed issuance.

For custom compliance logic, use the repository custom-policies tutorial. Audit and test custom policies: they can reject, return `Allowed`, skip later policies, or mutate state in `postRun()`.
