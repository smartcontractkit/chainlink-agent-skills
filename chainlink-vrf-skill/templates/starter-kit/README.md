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
