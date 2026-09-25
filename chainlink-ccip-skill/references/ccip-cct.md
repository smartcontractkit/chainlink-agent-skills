# CCT Workflow

Use only to create or register a Cross-Chain Token (CCT), configure pools/rate limits, or add networks. Generic sender/receiver, discovery, and monitoring use their dedicated references.

## Decision and source map

Name this Chainlink CCIP CCT onboarding and verify source, destination, and mainnet/testnet against the current [CCIP Directory](https://docs.chain.link/ccip/directory/testnet) — the source of truth for route and token availability. Before any write artifact, if source, destination, or mainnet/testnet is missing, ask one focused question that establishes those route facts.

At the token stage, establish whether the token is new or existing and who controls token ownership and mint/burn authority. When the user asks for the simplest registration path, immediately offer **Chainlink Token Manager** before asking for route or authority details, then collect those facts to confirm it fits; otherwise choose Token Manager or the repository's official framework and burn-and-mint or lock-and-mint from those facts. At the registration stage, establish pool ownership and administrator permissions. Never guess the control model or authority.

- overview: `https://docs.chain.link/ccip/concepts/cross-chain-token/overview.md`
- registration/admin: `https://docs.chain.link/ccip/concepts/cross-chain-token/token-issuer-guide.md`
- Token Manager: `https://docs.chain.link/ccip/evm/tutorials/token-manager.md`
- EOA burn/mint: `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/register-from-eoa-burn-mint-foundry.md`; Hardhat: `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/register-from-eoa-burn-mint-hardhat.md`
- EOA lock/mint: `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/register-from-eoa-lock-mint-foundry.md`; Hardhat: `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/register-from-eoa-lock-mint-hardhat.md`
- rate limits: `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/update-rate-limiters-foundry.md`
- more networks (1.x tutorial): `https://docs.chain.link/ccip/v1/evm/tutorials/cross-chain-tokens/configure-additional-networks-foundry.md`

## Auditable sequence

1. Establish the source, destination, and testnet/mainnet environment, then verify the route and token support against the CCIP Directory — see [discovery](ccip-discovery.md) for the full workflow.
2. At the current token or registration stage, offer Token Manager first when simplicity is requested; then establish only the authority facts needed to confirm it or choose the matching official Foundry/Hardhat flow.
3. Explain the whole sequence, but request approval only for the current stage.
4. After explicit approval, emit the [main preflight](../SKILL.md#boundary-and-preflight) for that step. Every CCT registration or administrative write artifact is signed and broadcast by the user outside this skill's runtime and must end, after all commands and steps, with exactly: “This skill never signs or sends. You must sign and broadcast from your own wallet.” Verify the result before preparing the next approved step.

CCT registration and pool configuration require their own user-run approval and execution.

Rate-limit changes require a separate user-run approval and execution.

Each additional-network configuration requires a separate user-run approval and execution.

Keep ownership/admin authority explicit; use rate limits deliberately; prefer official administration over improvised scripts and the smallest safe rollout. Never collapse admin operations into an implicit action or proceed without required permission. Prepare write artifacts only for testnets; refuse mainnet write artifacts.

## CCIP 2.0 pools

Install `@chainlink/contracts-ccip` 2.0 (Foundry: `forge install smartcontractkit/chainlink-ccip@contracts-ccip-v2.0.0` plus the remappings in [Contracts](ccip-contracts.md#project-setup)):

```bash
npm install @chainlink/contracts-ccip@2.0.0
```

The npm package ships its own `remappings.txt`, so Hardhat 3 resolves its internal `@chainlink/contracts`, `@chainlink/policy-management`, and `@openzeppelin/contracts@5.3.0` imports. Import with the full package paths (the API reference's `chainlink-ccip/...` paths do not resolve):

```solidity
import {TokenPool} from "@chainlink/contracts-ccip/contracts/pools/TokenPool.sol";
import {BurnMintTokenPool} from "@chainlink/contracts-ccip/contracts/pools/BurnMintTokenPool.sol";
import {LockReleaseTokenPool} from "@chainlink/contracts-ccip/contracts/pools/LockReleaseTokenPool.sol";
import {ERC20LockBox} from "@chainlink/contracts-ccip/contracts/pools/ERC20LockBox.sol";
import {IAdvancedPoolHooks} from "@chainlink/contracts-ccip/contracts/interfaces/IAdvancedPoolHooks.sol";
import {AdvancedPoolHooks} from "@chainlink/contracts-ccip/contracts/pools/AdvancedPoolHooks.sol";
import {IBurnMintERC20} from "@chainlink/contracts-ccip/contracts/interfaces/IBurnMintERC20.sol";
import {TokenAdminRegistry} from "@chainlink/contracts-ccip/contracts/tokenAdminRegistry/TokenAdminRegistry.sol";
import {RegistryModuleOwnerCustom} from "@chainlink/contracts-ccip/contracts/tokenAdminRegistry/RegistryModuleOwnerCustom.sol";
import {RateLimiter} from "@chainlink/contracts-ccip/contracts/libraries/RateLimiter.sol";
import {FinalityCodec} from "@chainlink/contracts-ccip/contracts/libraries/FinalityCodec.sol";
```

Enable the optimizer (pools are close to the contract size limit). Look up Router, RMN proxy, TokenAdminRegistry, and RegistryModuleOwnerCustom per chain in the Directory; never embed them. Docs: `https://docs.chain.link/ccip/concepts/cross-chain-token/token-issuer-guide.md`.

- Constructors:
  - `BurnMintTokenPool(IBurnMintERC20 token, uint8 localTokenDecimals, address advancedPoolHooks, address rmnProxy, address router)`. Variants for other burn signatures: `BurnFromMintTokenPool`, `BurnWithFromMintTokenPool`, `BurnToAddressMintTokenPool`.
  - `LockReleaseTokenPool(IERC20 token, uint8 localTokenDecimals, address advancedPoolHooks, address rmnProxy, address router, address lockBox)`. Liquidity lives in `ERC20LockBox(address token)`; the lockbox owner authorizes the pool with `applyAuthorizedCallerUpdates(AuthorizedCallers.AuthorizedCallerArgs({addedCallers: pools, removedCallers: new address[](0)}))`.
  - Pass `address(0)` as `advancedPoolHooks` unless the token needs a hook (below). Token, decimals, RMN proxy, and lockbox are immutable.
- Registration: `RegistryModuleOwnerCustom.registerAdminViaGetCCIPAdmin` / `registerAdminViaOwner` / `registerAccessControlDefaultAdmin` → `TokenAdminRegistry.acceptAdminRole(token)` → pool `applyChainUpdates` → `TokenAdminRegistry.setPool(token, pool)`. For burn/mint, grant the pool mint and burn roles first.
- Rate limits: `setRateLimitConfig(RateLimitConfigArgs[])` with `fastFinality` false or true; `isEnabled: false` means unlimited, so keep limits enabled. Removing a chain in `applyChainUpdates` wipes its remote pools and both buckets; prefer `addRemotePool` / `setRateLimitConfig`.
- Destination gas: 2.0 pools set their own per-destination `destGasOverhead` in `applyTokenTransferFeeConfigUpdates`. It must cover the remote pool's `releaseOrMint`, including any inbound hook.
- Token Manager docs predate 2.0 pools; do not claim it configures Fast Transfers, fees, or hooks.

### Fast Transfers on a pool

FTF is a pool setting; the token contract has none and needs no change. Pool owner: `setAllowedFinalityConfig(FinalityCodec._encodeBlockDepth(n))` (one `bytes4` per pool, all outbound lanes; `bytes4(0)` disables), read `getAllowedFinalityConfig()`. Requests below `n` revert `InvalidRequestedFinality` in `getFee`/`ccipSend` on the source. Optional per-destination knobs: FTF rate-limit bucket (`fastFinality: true`; falls back to the default bucket when disabled) and fees in `applyTokenTransferFeeConfigUpdates` (`fastFinalityFeeUSDCents`, `fastFinalityTransferFeeBps`). Each pool on each chain is its own user-run step. Senders, CCVs, executor, and receivers must also allow the depth: [CCIP 2.0](ccip-v2.md#fast-transfers-ftf). Docs: `https://docs.chain.link/ccip/concepts/execution-latency/fast-transfers-token-issuers.md`.

### Pool hooks

Most pools need no hook. Add one only for per-transfer policy: compliance checks, allowlists, pausing, or extra CCVs above an amount. A hook is any contract implementing `IAdvancedPoolHooks`; the pool calls it only when set (`updateAdvancedPoolHooks(IAdvancedPoolHooks(address(hook)))`, detach with `address(0)`, read `getAdvancedPoolHooks()`):

- `preflightCheck(Pool.LockOrBurnInV1 calldata lockOrBurnIn, bytes4 requestedFinalityConfig, bytes calldata tokenArgs, uint256 amountPostFee)`: outbound, before burn/lock. A revert rolls back the send on the source chain, so put checks here where possible.
- `postflightCheck(Pool.ReleaseOrMintInV1 calldata releaseOrMintIn, uint256 localAmount, bytes4 requestedFinalityConfig)`: inbound, before mint/release. A revert leaves the message unexecutable until the cause is fixed; tokens are already burned or locked on the source. Keep it deterministic and cheap.
- `getRequiredCCVs(address localToken, uint64 remoteChainSelector, uint256 amount, bytes4 requestedFinalityConfig, bytes calldata extraData, IPoolV2.MessageDirection direction) returns (address[] memory)`: extra CCVs the pool requires; return an empty array for none.
- Restrict callers to your pool(s); every hook call costs gas on every transfer.

`AdvancedPoolHooks` is ans example hook, often called the ACE pool hook. It bundles three features that few tokens need together: an outbound sender allowlist (on only if the constructor list is non-empty, fixed at deploy), per-chain CCVs with an amount threshold, and an optional policy engine on both directions. Use it as is only when you want those features; otherwise trim a copy or write your own hook for a lower gas cost.

- Deploy `AdvancedPoolHooks(address[] allowlist, uint256 thresholdAmountForAdditionalCCVs, address policyEngine, address[] authorizedCallers)`. Authorize the pool (`applyAuthorizedCallerUpdates`) before the pool owner attaches the hook, or the first transfer reverts `UnauthorizedCaller`.
- Compliance: `setPolicyEngine(engine)` wires any `IPolicyEngine` from `@chainlink/policy-management`; `AdvancedPoolHooksExtractor` (`@chainlink/contracts-ccip/contracts/pools/extractors/AdvancedPoolHooksExtractor.sol`) maps hook calldata to policy parameters. Chainlink ACE is one option for that engine; route ACE setup and policies to the chainlink-ace-skill.
- Docs: `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/set-advanced-pool-hooks-foundry.md`, `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/set-advanced-pool-hooks-hardhat.md`.

Minimal custom hook (caps each outbound transfer):

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {IAdvancedPoolHooks} from "@chainlink/contracts-ccip/contracts/interfaces/IAdvancedPoolHooks.sol";
import {IPoolV2} from "@chainlink/contracts-ccip/contracts/interfaces/IPoolV2.sol";
import {Pool} from "@chainlink/contracts-ccip/contracts/libraries/Pool.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";

contract TransferCapPoolHook is IAdvancedPoolHooks, OwnerIsCreator {
    error OnlyPool(address caller);
    error ZeroAddress();
    error AmountAboveCap(uint256 amount, uint256 cap);

    address public immutable i_pool;
    uint256 public s_maxAmount;

    constructor(address pool, uint256 maxAmount) {
        if (pool == address(0)) revert ZeroAddress();
        i_pool = pool;
        s_maxAmount = maxAmount;
    }

    modifier onlyPool() {
        if (msg.sender != i_pool) revert OnlyPool(msg.sender);
        _;
    }

    function setMaxAmount(uint256 maxAmount) external onlyOwner {
        s_maxAmount = maxAmount;
    }

    // Outbound, before burn/lock: a revert rolls back the send on the source chain.
    function preflightCheck(Pool.LockOrBurnInV1 calldata lockOrBurnIn, bytes4, bytes calldata, uint256)
        external view onlyPool
    {
        if (lockOrBurnIn.amount > s_maxAmount) revert AmountAboveCap(lockOrBurnIn.amount, s_maxAmount);
    }

    // Inbound, before mint/release: a revert leaves the message unexecutable until fixed, so keep it permissive.
    function postflightCheck(Pool.ReleaseOrMintInV1 calldata, uint256, bytes4) external view onlyPool {}

    // No pool-required CCVs; lane defaults still apply.
    function getRequiredCCVs(address, uint64, uint256, bytes4, bytes calldata, IPoolV2.MessageDirection)
        external pure returns (address[] memory)
    {
        return new address[](0);
    }
}
```

### v1 → v2 migration

Deploy v2 pools, list both old and new remote pools in `applyChainUpdates`, cut over with `setPool` (no re-registration), and remove v1 remote pools only after in-flight v1 messages succeed. Lock/mint also moves liquidity into the lockbox. v2 features need both ends on v2. Docs: `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/migrate-from-v1-to-v2-burn-mint-foundry.md`, `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/migrate-from-v1-to-v2-burn-mint-hardhat.md`, `https://docs.chain.link/ccip/evm/tutorials/cross-chain-tokens/migrate-from-v1-to-v2-lock-mint-foundry.md`.

### Pool tests

Unit (Foundry or Hardhat 3 Solidity tests, as upstream): mock RMN `isCursed(bytes16)` with `vm.mockCall`, deploy a real `Router` and register fake ramps with `applyRampUpdates`, deploy the token and pool, then prank as the on/off ramp to call `lockOrBurn`/`releaseOrMint`. Cover finality floors (`expectRevert` `InvalidRequestedFinality`), both rate-limit buckets, and hooks: an unauthorized hook caller, each hook revert path, and a mock policy engine. `CCIPLocalSimulator` does not run pools; end-to-end pool tests use the fork simulator ([Local](chainlink-local.md)).
