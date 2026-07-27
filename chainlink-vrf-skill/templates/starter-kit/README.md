# Chainlink VRF Foundry Starter Kit Template

Use this template when a user asks for a working VRF project, a Foundry starter kit, or a runnable randomness example. It is based on the Chainlink Foundry Starter Kit `VRFConsumerV2.sol` pattern, **upgraded to VRF v2.5** (`VRFConsumerBaseV2Plus`) to match this skill's safety defaults — the legacy V2 base, `uint64` subscription IDs, and positional `requestRandomWords` arguments do not compile against current coordinators.

## Files

```text
foundry.toml
remappings.txt
src/VRFConsumerV2Plus.sol
script/VRFConsumerV2Plus.s.sol
test/VRFConsumerV2Plus.t.sol
```

The test and deploy script use `VRFCoordinatorV2_5Mock` shipped with `@chainlink/contracts`, so no custom mocks are vendored.

## Dependencies

For a fresh Foundry project, install these dependencies before running the template:

```sh
forge install foundry-rs/forge-std
forge install smartcontractkit/chainlink-evm@contracts-v1.5.0
forge install openzeppelin/openzeppelin-contracts@v4.9.6
```

The included `remappings.txt` expects Chainlink contracts under `lib/chainlink-evm/`, OpenZeppelin v4.9.6 under `lib/openzeppelin-contracts/`, and forge-std under `lib/forge-std/`.

## VRF v2.5 Essentials

The consumer uses the subscription method:

- Inherits `VRFConsumerBaseV2Plus` and requests via the `VRFV2PlusClient.RandomWordsRequest` struct with `extraArgs`.
- Subscription IDs are `uint256`.
- `fulfillRandomWords` takes `calldata` random words.
- `extraArgs` selects the payment token per request: `nativePayment: false` pays in LINK, `true` pays in native coin. Fund the subscription with the matching token.

Before deploying to a live network: create and fund a subscription at https://vrf.chain.link, then add the deployed consumer as an approved consumer for that subscription ID.

## Default Network

The deploy script defaults to Ethereum Sepolia, using the live VRF v2.5 coordinator and 500 gwei key hash:

```text
Coordinator: 0x9DdfaCa8183c41ad55329BdeeD9F6A8d53168B1B
Key hash:    0x787d74caea10b2b357790d5b5247c2f63d1d91572a9846f780606e4d953677ae
```

On Sepolia the script reads the subscription ID from the `SUBSCRIPTION_ID` environment variable. On any other chain (e.g. a local Anvil node) it deploys a mock coordinator, creates and funds a subscription, and wires everything up so the project is runnable end-to-end.

Always verify coordinator addresses and key hashes against the official Chainlink docs (https://docs.chain.link/vrf/v2-5/supported-networks) before deploying.

## Commands

```sh
forge test

# Local dry run (deploys and wires up a mock coordinator):
forge script script/VRFConsumerV2Plus.s.sol:DeployVRFConsumerV2Plus

# Sepolia (requires a funded subscription):
SUBSCRIPTION_ID=<your-sub-id> \
  forge script script/VRFConsumerV2Plus.s.sol:DeployVRFConsumerV2Plus \
  --rpc-url $SEPOLIA_RPC_URL --private-key $PRIVATE_KEY --broadcast
```

Example code is unaudited and should be reviewed before production use.

## Adapt This Template

The template is a complete, compiling reference. Two layers behave differently when you adapt it.

**Must be preserved exactly** — these are protocol requirements, not style choices:

- The `VRFConsumerBaseV2Plus` base contract and its import path.
- Requesting through `s_vrfCoordinator.requestRandomWords` with the `VRFV2PlusClient.RandomWordsRequest`
  struct, including `extraArgs` built by `VRFV2PlusClient._argsToBytes(VRFV2PlusClient.ExtraArgsV1(...))`.
- `uint256` subscription IDs.
- The `fulfillRandomWords(uint256, uint256[] calldata)` override signature.
- Coordinator addresses, key hashes, and the dependency pins in `remappings.txt`. Copy these from the
  template or the official docs rather than retyping them; a mistyped address literal fails EIP-55
  checksum validation and will not compile.
- Treating fulfillment as untrusted-timing: never assume randomness arrives in the same transaction.

**Replace to fit the user's use case** — these are illustrative, not prescriptive. Do not copy them
into an application that does not need them:

- The `RequestStatus` struct, the `s_requests` mapping, `requestIds`, and `lastRequestId`. If the
  application only needs a derived result (a winner index, a trait roll, a shuffled position), store
  that instead of the raw words.
- The `RequestSent` / `RequestFulfilled` events and the `getRequestStatus` view.
- The `VRFConsumerV2Plus` contract name and file names.
- `onlyOwner` on the request function. Gate requests however the application requires.

**Tune, do not copy** — the template's values are placeholders for a 2-word request that only writes
storage. State the reasoning for whichever value you pick:

- `callbackGasLimit` (template: `100_000`). Size it to the work actually done inside
  `fulfillRandomWords`, roughly 20,000 gas per stored word plus any application logic. Under-sizing
  silently loses the fulfillment.
- `numWords` (template: `2`). Request only what the application consumes; it cannot exceed
  `VRFCoordinatorV2_5.MAX_NUM_WORDS`. One word can be expanded into many values off a single request.
- `requestConfirmations` (template: `3`). Raise it on chains with higher reorg risk or when the
  outcome is high-value.

When randomness selects from a set, reducing a random word with `%` over the set size is biased
unless the set size divides the word range. Say so, and use rejection sampling when the bias matters.
