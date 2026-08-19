# VRF v2.5 Security and Best Practices

Apply all ten guardrails. They protect different failure modes and are not optional substitutes for one another.

## 1. Match Every Fulfillment by `requestId`

Always bind each fulfillment to its originating commitment with `requestId`; never assume FIFO. Validators control transaction ordering, so requests A, B, C may fulfill C, A, B. Do not let arrival order drive user-significant behavior.

## 2. Choose Confirmations from Value at Risk

Set `requestConfirmations` high enough that a chain rewrite costs more than the application outcome. A validator cannot predict a VRF value but can attempt a reorg to obtain a fresh one. Higher confirmation counts improve reorg resistance at the cost of latency; there is no chain-independent universal value.

## 3. Forbid Request-Specific Re-request and Cancellation

Never let any party cancel or repeat a randomness request for the same commitment. Discarding an unfavorable result and trying again creates selection bias.

## 4. Freeze Outcome-Changing Inputs Before Requesting

Record all inputs that can affect an outcome, close that input phase, and only then call `requestRandomWords`. Accept no further outcome-changing input until fulfillment; otherwise a reorg can pair the rerolled value with attacker-chosen inputs.

## 5. Make `fulfillRandomWords` Non-reverting

Keep the callback to bounded storage updates and events. VRF does not retry a reverted callback, so a revert loses the fulfillment. Move winner selection, payouts, and other complex or external work to a separate transaction or Chainlink Automation path.

```solidity
function fulfillRandomWords(uint256 requestId, uint256[] calldata randomWords)
    internal
    override
{
    s_requests[requestId].randomWords = randomWords;
    s_requests[requestId].fulfilled = true;
    emit RandomnessFulfilled(requestId);
}
```

## 6. Preserve Coordinator Authentication

Inherit `VRFConsumerBaseV2Plus` for subscription consumers and implement only `fulfillRandomWords`. Its raw entry point verifies the caller is `VRFCoordinatorV2_5`; never override `rawFulfillRandomness` or bypass that check.

## 7. Avoid ERC-4337 Accounts for Subscription Management

Use an EOA or standard multisig. A pre-signed ERC-4337 `UserOperation` may be submitted by any bundler until expiry; if it executes inside a fulfillment callback, a subscription-management operation can no-op and delay or prevent the intended change.

## 8. Maintain a Balance Buffer

Keep the subscription balance well above its minimum, especially with concurrent consumers. Insufficient balance delays fulfillments, and in-flight requests may take additional time after a top-up. Alert and refill before the balance approaches the minimum.

## 9. Never Substitute Block Data

Never use `block.prevrandao`, `block.difficulty`, `blockhash`, `block.timestamp`, or sender-derived hashes as randomness or a fallback. These sources are validator-influenceable. If VRF is unavailable, wait or revert.

RANDAO (`block.prevrandao`) is biasable because a proposer can skip a slot: https://stackoverflow.com/questions/73938799/chainlink-vrf-or-randao

## 10. Measure and Buffer `callbackGasLimit`

Measure the real callback on a testnet, add a 20–30% buffer, and keep the callback small. Too little gas makes it revert permanently; larger limits increase cost exposure. The maximum is 2,500,000, subject to the target network's live configuration at https://docs.chain.link/vrf/v2-5/supported-networks.md.

## Mock Coordinator API

The `@chainlink/contracts` package includes a subscription-consumer mock:

```solidity
import {VRFCoordinatorV2_5Mock} from "@chainlink/contracts/src/v0.8/vrf/mocks/VRFCoordinatorV2_5Mock.sol";

// constructor(baseFee, gasPriceLink, weiPerUnitLink)
VRFCoordinatorV2_5Mock coordinator =
    new VRFCoordinatorV2_5Mock(0.1 ether, 1 gwei, 4113797966605025);
uint256 subId = coordinator.createSubscription();
coordinator.fundSubscription(subId, 10 ether);
coordinator.addConsumer(subId, address(consumer));
uint256 requestId = consumer.requestRandomWords(false);
coordinator.fulfillRandomWords(requestId, address(consumer));
```

Any `bytes32` key hash works with the mock. `fulfillRandomWords(requestId, consumer)` performs local fulfillment synchronously. This mock is for subscription consumers; direct-funding wrapper mocks are in the tagged [chainlink-evm](https://github.com/smartcontractkit/chainlink-evm) sources. The complete Foundry test and its constructor constants live in [`templates/starter-kit/test/VRFConsumerV2Plus.t.sol`](../templates/starter-kit/test/VRFConsumerV2Plus.t.sol).
