# Policy Library

Read to select/compose a policy or answer behavior, configuration, runtime-parameter, setter, view-function, or tradeoff questions. Public policies call `initialize(address policyEngine, address initialOwner, bytes configParams)`; base `Policy` sets the engine, owner, and common modules, then one-time `configure(bytes)` decodes policy configuration.

## Policy Matrix

`PolicyRejected` means reject; otherwise rows return `Continue` except the explicit `Allowed` case.

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
| `SecureMintPolicy` | Collateral/reserve-backed minting; mint amount | Configure reserve feed, reserve margin, max staleness, and the intended supply/backed-supply calculation; reject any mint beyond verified backing and fail closed on unusable reserve data | `setReservesFeed(address)`, `setReserveMargin(...)`, `setMaxStalenessSeconds(uint256)` |

## Selection and Safety

For `SecureMintPolicy`, a failed/reverted feed read, missing update within the heartbeat, or stale reserve value must block minting. Verify token/feed decimals; max staleness `0` accepts infinitely stale data and must be explicit. Confirm the pinned implementation's supply source and backed-supply calculation, including how burns reopen mint headroom; test both sides of the boundary. Protect and monitor reserve-feed, margin, and staleness admin setters. Place hard pause/deny/credential checks first, then `SecureMintPolicy`, and any intentional `BypassPolicy` last because `Allowed` skips later checks. For product-documented negative-margin modes, multiple feeds, or feed composition, fetch the current `docs.chain.link` SecureMintPolicy page (managed-Platform scope only); cite `smartcontractkit/chainlink-ace` `packages/policy-management` — never a docs page — for OSS policy behavior. State the no-PII-onchain rule.

For custom compliance logic, use the repository custom-policies tutorial. Audit and test custom policies: they can reject, return `Allowed`, skip later policies, or mutate state in `postRun()`.
