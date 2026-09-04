# VRF v2.5 Security and Best Practices

Apply all ten guardrails. They protect different failure modes and are not optional substitutes for one another.

## 1. Match Every Fulfillment by `requestId`

Always bind each fulfillment to its originating commitment with `requestId`; never assume FIFO. Validators control transaction ordering, so requests A, B, C may fulfill C, A, B. Do not let arrival order drive user-significant behavior.

## 2. Choose Confirmations from Value at Risk

Set `requestConfirmations` high enough that a chain rewrite costs more than the application outcome. A validator cannot predict a VRF value but can attempt a reorg to obtain a fresh one. Higher confirmation counts improve reorg resistance at the cost of latency; there is no chain-independent universal value.

## 3. Forbid Rerolls

Never let any party repeat a randomness request for the same commitment or choose between results. Discarding an unfavorable result and trying again creates selection bias. Paid raffles must follow the complete [Paid Raffle Safety Contract](#paid-raffle-safety-contract).

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

## Paid Raffle Safety Contract

A paid raffle must satisfy this entire contract:

1. Lock a nonempty, duplicate-free entrant set and every paid commitment before making exactly one randomness request for the round.
2. Bind the request ID to that locked round. Fulfillment ignores unknown, empty, repeated, or terminal-round callbacks and otherwise records the committed word with bounded, non-reverting state updates; winner selection and payouts happen later.
3. Select the winner with [`uniformIndex`](#unbiased-winner-indices) outside the callback, using the committed word and its deterministic expansion only. Never use raw modulo reduction, request replacement randomness, or let any party choose between outcomes.
4. Set a fixed timeout before requesting. After it expires, provide one terminal recovery path only while no random word is recorded or otherwise usable: cancel the whole round, or enter a state in which each player pulls their own refund. Record the terminal state before external transfers, ensure all paid participants can recover their funds, and ignore late fulfillment.
5. Once randomness is recorded or otherwise usable, disable cancellation and refunds and finalize only the committed outcome. The operator must never re-request, reroll, or cancel after learning an outcome.

## Unbiased Winner Indices

Every winner-selection example must reduce a VRF word with rejection sampling outside the callback; a raw `word % entrantCount` is biased unless the entrant count divides $2^{256}$. Validate a nonzero bound first, lock a duplicate-free entrant set before requesting, and use the same committed word even when rejection requires deterministic expansion:

```solidity
error InvalidWinnerRange();

function uniformIndex(uint256 word, uint256 upperBound) internal pure returns (uint256) {
    if (upperBound == 0) revert InvalidWinnerRange();
    uint256 threshold = (type(uint256).max - upperBound + 1) % upperBound;
    uint256 nonce;
    while (word < threshold) {
        word = uint256(keccak256(abi.encode(word, nonce++)));
    }
    return word % upperBound;
}

uint256 winnerIndex = uniformIndex(storedRandomWord, entrants.length);
```

This derives one deterministic outcome from the original fulfillment; it is not a new VRF request or an operator-selectable reroll.

## Focused Raffle Tests

Generated raffle tests must separately cover empty `randomWords` without settlement or state corruption, invalid configuration, duplicate entries, a winner index outside the entrant range, repeated fulfillment, every reroll or replacement-request attempt, and the selected timeout cancellation or per-player pull-refund path. Prove paid participants cannot remain locked after the timeout, late fulfillment cannot revive a terminal round, and recovery cannot activate after randomness is recorded or otherwise usable.

## Official Dependency and Mock Coordinator API

Use the normal official `@chainlink/contracts` dependency or a tagged `smartcontractkit/chainlink-evm` contracts release for consumer bases, client libraries, interfaces, and mocks. Never vendor selected Chainlink source files. The subscription-consumer mock is:

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
