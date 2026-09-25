# CCIP 2.0 (EVM)

Default for EVM contract work: `@chainlink/contracts-ccip` 2.0 (Foundry tag `contracts-ccip-v2.0.0`). Confirm the installed version; everything below is protocol surface, not live config. Code: [Solidity examples](ccip-solidity-examples.md). Pools/hooks: [CCT](ccip-cct.md). Tests: [Local](chainlink-local.md).

## Router and lane version

- Take the router (and LINK) as constructor/config parameters; never hard-code an address, selector, or lane. Resolve them per lane from the [CCIP API](ccip-api.md) or [CCIP Directory](https://docs.chain.link/ccip/directory/testnet) as a fallback.
- Pre-2.0 lanes (fallback): no V3 extraArgs, no Fast Transfers. Use `Client._argsToBytes(Client.GenericExtraArgsV2({gasLimit: ..., allowOutOfOrderExecution: true}))`; 1.x docs: `https://docs.chain.link/ccip/v1.md`. Contracts that must serve both accept `bytes extraArgs` built offchain per lane (docs best practice: keep extraArgs mutable).

## extraArgs V3

`ExtraArgsCodec.GenericExtraArgsV3` lives in `ExtraArgsCodec`, not `Client` (no `_argsToBytes` for V3). The encoding is packed; never `abi.encode` the struct. Helpers are `internal`: call them inside contracts.

```solidity
import {ExtraArgsCodec} from "@chainlink/contracts-ccip/contracts/libraries/ExtraArgsCodec.sol";
import {FinalityCodec} from "@chainlink/contracts-ccip/contracts/libraries/FinalityCodec.sol";

// Full finality (default), default CCVs and executor:
ExtraArgsCodec._getBasicEncodedExtraArgsV3(gasLimit, FinalityCodec.WAIT_FOR_FINALITY_FLAG);
// Fast Transfers: wait N source blocks (N = 0 means full finality):
ExtraArgsCodec._getBasicEncodedExtraArgsV3BlockDepth(gasLimit, n);
// Full struct: gasLimit, requestedFinalityConfig, ccvs, ccvArgs (same length), executor, executorArgs, tokenReceiver, tokenArgs
ExtraArgsCodec._encodeGenericExtraArgsV3(args);
```

- `gasLimit` (`uint32`): destination callback gas, billed as set, unused gas not refunded; `0` for EOA or token-only.
- Leave `ccvs`/`ccvArgs` empty (lane defaults), `executor = address(0)` (default executor), `tokenReceiver`/`tokenArgs` empty unless the user needs them. `Client.NO_EXECUTION_ADDRESS` disables automatic execution (manual only).
- Legacy V1/V2 args still work on 2.0 lanes: only `gasLimit` is honored, `allowOutOfOrderExecution` is ignored, finality is always full.
- One token per message on 2.0.
- Offchain: ccip-sdk, or the starter kits' `EncodeExtraArgsOffchain` script helper (`encodeV3Basic`, `encodeV3`). It is not in `@chainlink/contracts-ccip` and its signatures differ between kit versions; read the copy installed.

## Finality encoding (`FinalityCodec`, `bytes4`)

- `0x00000000` `WAIT_FOR_FINALITY_FLAG`: full finality, the default and safest.
- Low 16 bits `1..65535`: wait that many source blocks. Encode with `FinalityCodec._encodeBlockDepth(n)`.
- High 16 bits are flags (`WAIT_FOR_SAFE_FLAG`); the docs mark them not activated. Do not request them.
- An allowed config `_encodeBlockDepth(k)` admits full finality or any requested depth `>= k`; `0` admits only full finality. Otherwise `FinalityCodec.InvalidRequestedFinality(requested, allowed)`.

## Fast Transfers (FTF)

Fast Transfers (Faster-Than-Finality, FTF) is opt-in at every layer and every layer defaults to full finality. Never enable it by default; request it only when the user asks.

| Layer | Switch | If it disallows |
|---|---|---|
| Sender | `requestedFinalityConfig` in V3 extraArgs | — |
| Token pool (source, V2) | owner `setAllowedFinalityConfig(bytes4)`; read `getAllowedFinalityConfig()` | `getFee`/`ccipSend` revert `InvalidRequestedFinality`; V1 pools cannot carry FTF |
| CCVs, executor | lane config, `getAllowedFinalityConfig()` | `getFee`/`ccipSend` revert |
| Receiver (destination) | `getCCVsAndFinalityConfig` return value | not checked at source: the message is sent, execution fails, and stays failed until the receiver config allows it (waiting for finality does not help) |

- The token contract has no finality setting; FTF is a pool setting.
- Token-only transfers (no data, `gasLimit 0`) skip the receiver check; the pool governs.
- Before a send: read the pool's `getAllowedFinalityConfig()`, then `getFee` with the same extraArgs. A revert means some layer disallows the depth.
- Risk: a reorg can deliver a duplicate with a different `messageId`. The receiver, pool, and integrators carry that risk. Use an application-level idempotency key, not only `messageId`. Prefer full finality on newer chains. Docs: `https://docs.chain.link/ccip/concepts/execution-latency/ftf.md`.

## V2 receiver

`CCIPReceiver` 2.0 implements `IAny2EVMMessageReceiverV2`:

```solidity
function getCCVsAndFinalityConfig(uint64 sourceChainSelector, bytes calldata sender)
    external view returns (address[] memory requiredCCVs, address[] memory optionalCCVs,
                           uint8 optionalThreshold, bytes4 allowedFinalityConfig);
```

- The default returns empty CCVs (lane defaults) and full finality. Override it to accept FTF per source chain and only for an allowlisted source-selector/sender pair (`AllowlistedReceiver` in [examples](ccip-solidity-examples.md)). Returning a nonzero config for every chain or sender is unsafe.
- Keep the per-chain floor in owner-settable storage, not constructor immutables: a stranded FTF message only recovers when the receiver loosens its config. Do not tighten the config while FTF messages from that chain are in flight.
- `enableChain` exists only on the `CCIPClientExample` sample (`external onlyOwner`), not on `CCIPReceiver`; write an owner setter.
- CCVs: most apps keep the default verifier. A receiver-required CCV must match what the sender and lane produce; misaligned requirements fail on the destination. Docs: `https://docs.chain.link/ccip/concepts/ccvs/overview.md`.

## Setup

- `CCIPReceiver` imports `@openzeppelin/contracts@5.3.0/...`: remap that exact prefix. Core contracts need `solc >= 0.8.24`.
- Foundry forks and `forge script` against deployed 2.0 contracts need `evm_version = "cancun"`; with `paris` the simulation fails with `EvmError: NotActivated`. Hardhat: `evmVersion: "cancun"`.

## Docs

- Fast Transfers: `https://docs.chain.link/ccip/concepts/execution-latency/ftf.md`, `https://docs.chain.link/ccip/concepts/execution-latency/ftf-dapps.md`, `https://docs.chain.link/ccip/concepts/execution-latency/fast-transfers-token-issuers.md`
- extraArgs: `https://docs.chain.link/ccip/concepts/architecture/message-configuration-extraargs.md`
- Tutorials: `https://docs.chain.link/ccip/evm/tutorials/application-developers/send-arbitrary-data.md`, `https://docs.chain.link/ccip/evm/tutorials/application-developers/transfer-tokens-from-contract.md`, `https://docs.chain.link/ccip/evm/tutorials/application-developers/programmable-token-transfers.md`, `https://docs.chain.link/ccip/evm/tutorials/application-developers/programmable-token-transfers-defensive.md`
- Best practices: `https://docs.chain.link/ccip/evm/concepts/best-practices.md`
- API reference: `https://docs.chain.link/ccip/evm/api-reference/v2.0.0/ccip-receiver.md`, `https://docs.chain.link/ccip/evm/api-reference/v2.0.0/i-router-client.md`, `https://docs.chain.link/ccip/evm/api-reference/v2.0.0/extra-args-codec.md`. Source wins over the API-reference pages where they differ.
