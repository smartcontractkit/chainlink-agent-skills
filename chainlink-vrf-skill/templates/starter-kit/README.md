# Chainlink VRF Foundry Starter Kit

Use this complete VRF v2.5 subscription project for working-example, Foundry starter-kit, or runnable-project requests instead of inventing scaffolding.

```text
foundry.toml
remappings.txt
src/VRFConsumerV2Plus.sol
script/VRFConsumerV2Plus.s.sol
test/VRFConsumerV2Plus.t.sol
```

The test and script use the `VRFCoordinatorV2_5Mock` included in `@chainlink/contracts`; no custom mock is vendored.

## Install

```sh
forge install foundry-rs/forge-std
forge install smartcontractkit/chainlink-evm@contracts-v1.5.0
forge install openzeppelin/openzeppelin-contracts@v4.9.6
```

`remappings.txt` expects Chainlink under `lib/chainlink-evm/`, OpenZeppelin v4.9.6 under `lib/openzeppelin-contracts/`, and forge-std under `lib/forge-std/`.

## v2.5 Contract Rules

The consumer inherits `VRFConsumerBaseV2Plus`, requests through `VRFV2PlusClient.RandomWordsRequest` with required `extraArgs`, stores its subscription ID as `uint256`, and receives `uint256[] calldata` in `fulfillRandomWords`. `ExtraArgsV1({nativePayment: false})` selects LINK; `true` selects the native coin. Fund the subscription with the selected asset.

Before a live deployment, create and fund a subscription at https://vrf.chain.link and add the deployed consumer as an approved consumer. Legacy `VRFConsumerBaseV2`, `uint64` IDs, and positional requests do not compile against current coordinators.

## Default Network

The live branch of the script targets Ethereum Sepolia (`chainid 11155111`) and reads `SUBSCRIPTION_ID` from the environment:

```text
Coordinator: 0x9DdfaCa8183c41ad55329BdeeD9F6A8d53168B1B
500 gwei key hash: 0x787d74caea10b2b357790d5b5247c2f63d1d91572a9846f780606e4d953677ae
```

On every other chain, including local Anvil, the script deploys a mock, creates and funds a subscription, deploys and authorizes the consumer, and is runnable end-to-end. Verify live addresses and key hashes at https://docs.chain.link/vrf/v2-5/supported-networks before deploying.

## Commands

```sh
forge test

# Local dry run with the mock:
forge script script/VRFConsumerV2Plus.s.sol:DeployVRFConsumerV2Plus

# User-run Sepolia deployment with a funded subscription:
SUBSCRIPTION_ID=<your-sub-id> \
  forge script script/VRFConsumerV2Plus.s.sol:DeployVRFConsumerV2Plus \
  --rpc-url $SEPOLIA_RPC_URL --private-key $PRIVATE_KEY --broadcast
```

## Adapt the Template

Preserve these protocol requirements:

- The `VRFConsumerBaseV2Plus` base and import path.
- `s_vrfCoordinator.requestRandomWords(VRFV2PlusClient.RandomWordsRequest({...}))`, including `extraArgs` encoded by `VRFV2PlusClient._argsToBytes(VRFV2PlusClient.ExtraArgsV1(...))`.
- `uint256` subscription IDs and the `fulfillRandomWords(uint256, uint256[] calldata)` override.
- Coordinator addresses, key hashes, and dependency pins in `remappings.txt`; copy rather than retype them because a bad EIP-55 checksum does not compile.
- Untrusted fulfillment timing: randomness does not arrive in the request transaction and fulfillment order is not guaranteed.

Replace these illustrative choices when the application differs:

- `RequestStatus`, `s_requests`, `requestIds`, and `lastRequestId`; store a derived winner, trait, or position instead when raw words are unnecessary.
- `RequestSent`, `RequestFulfilled`, `getRequestStatus`, the contract/file names, and `onlyOwner`; use the application's appropriate request authorization.

Tune these placeholders and explain the chosen values:

- `callbackGasLimit = 100_000`: size for the callback, roughly 20,000 gas per stored word plus application work. Under-sizing loses the fulfillment.
- `numWords = 2`: request only what is consumed, up to `VRFCoordinatorV2_5.MAX_NUM_WORDS`; one word can derive multiple values.
- `requestConfirmations = 3`: raise for greater reorg risk or value at risk.

Reducing a word with `%` is biased unless the set size divides the word range; use rejection sampling when that bias matters.
