# Reading Price Feeds

Use this file for any request that involves reading Chainlink price feed data on EVM chains, whether onchain via Solidity or offchain via JavaScript/Python.

## Trigger Conditions

Use this workflow for requests like:

- "I need to read the ETH/USD price in my Solidity contract."
- "How do I get a Chainlink price feed in ethers.js?"
- "Add a staleness check to my price feed consumer."
- "My protocol runs on Arbitrum. How do I safely read a price feed?"
- "Show me how to fetch historical price data from Chainlink."

Do not use this workflow for non-EVM chains (Solana, StarkNet, Aptos), MVR/bundle feeds, Data Streams, or CCIP.

## Core Interface

All EVM price feeds expose `AggregatorV3Interface` through a proxy contract.

Import path:

```solidity
import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
```

Functions:

- `decimals() -> uint8` -- number of decimal places in the answer
- `description() -> string` -- human-readable pair name (e.g., "ETH / USD")
- `version() -> uint256` -- interface version of the aggregator
- `latestRoundData() -> (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)`
- `getRoundData(uint80 _roundId)` -- same return tuple, for historical queries

Important notes:

1. `answeredInRound` is deprecated. Do not use it for freshness checks.
2. Always read through the proxy contract, never directly from the underlying aggregator. Aggregators can be upgraded behind the proxy; reading the proxy keeps your integration stable.

## Solidity Consumer Pattern

Full working consumer with all required validation:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract DataConsumerV3 {
    AggregatorV3Interface internal dataFeed;
    uint256 public constant STALENESS_THRESHOLD = 3600; // 1 hour; adjust to feed heartbeat + buffer

    constructor(address feedAddress) {
        dataFeed = AggregatorV3Interface(feedAddress);
    }

    function getLatestPrice() public view returns (int256) {
        (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = dataFeed.latestRoundData();

        // Round completeness
        require(updatedAt > 0, "Round not complete");
        // Staleness
        require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price");
        // Answer bounds
        require(answer > 0, "Invalid price");

        return answer;
    }

    function getDecimals() public view returns (uint8) {
        return dataFeed.decimals();
    }
}
```

### Validation Requirements

Every consumer must include these checks:

1. **Staleness**: `require(block.timestamp - updatedAt <= STALENESS_THRESHOLD)`. Set the threshold to the feed's heartbeat interval plus a reasonable buffer. ETH/USD on Ethereum mainnet has a 3600s heartbeat; other feeds differ.
2. **Answer bounds**: `require(answer > 0)` at minimum. For production, consider tighter min/max bounds appropriate for the specific asset.
3. **Round completeness**: `require(updatedAt > 0)`. A zero `updatedAt` indicates the round has not completed.
4. **Decimals**: Always call `decimals()` at runtime or store the result in an immutable. Never hardcode 8. ETH/USD uses 8 decimals, but other feeds (especially non-USD quote pairs) may use 18.

## L2 Sequencer Uptime Check

Required on Arbitrum, Optimism, Base, Scroll, and all other L2 rollups with a sequencer. If the sequencer is down, price feeds on the L2 are not updated and stale data can cause incorrect liquidations or trades.

The sequencer uptime feed uses `AggregatorV2V3Interface` (not `AggregatorV3Interface`).

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
import {AggregatorV2V3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV2V3Interface.sol";

contract DataConsumerWithSequencerCheck {
    AggregatorV3Interface internal dataFeed;
    AggregatorV2V3Interface internal sequencerUptimeFeed;

    uint256 public constant STALENESS_THRESHOLD = 3600;
    uint256 public constant GRACE_PERIOD_TIME = 3600;

    error SequencerDown();
    error GracePeriodNotOver();

    constructor(address feedAddress, address sequencerFeedAddress) {
        dataFeed = AggregatorV3Interface(feedAddress);
        sequencerUptimeFeed = AggregatorV2V3Interface(sequencerFeedAddress);
    }

    function getLatestPrice() public view returns (int256) {
        // Step 1: Check sequencer status
        (
            /*uint80 roundId*/,
            int256 sequencerAnswer,
            uint256 startedAt,
            /*uint256 updatedAt*/,
            /*uint80 answeredInRound*/
        ) = sequencerUptimeFeed.latestRoundData();

        // answer == 0: sequencer is up
        // answer == 1: sequencer is down
        if (sequencerAnswer != 0) {
            revert SequencerDown();
        }

        // Enforce grace period after sequencer recovery
        // startedAt is the timestamp when the status last changed
        uint256 timeSinceUp = block.timestamp - startedAt;
        if (timeSinceUp < GRACE_PERIOD_TIME) {
            revert GracePeriodNotOver();
        }

        // Step 2: Read and validate price feed
        (
            uint80 roundId,
            int256 answer,
            uint256 priceStartedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = dataFeed.latestRoundData();

        require(updatedAt > 0, "Round not complete");
        require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price");
        require(answer > 0, "Invalid price");

        return answer;
    }
}
```

Key details:

- `answer == 0` means the sequencer is up. `answer == 1` means it is down.
- `startedAt` from the uptime feed is the timestamp when the sequencer status last changed.
- After sequencer recovery, enforce a grace period (typically 3600 seconds) before trusting price data. This prevents acting on prices that may be stale or manipulated immediately after the sequencer resumes.
- Sequencer uptime feed proxy addresses are network-specific. Check the official L2 Sequencer Uptime Feeds documentation for the correct address per chain.

## Off-Chain Reading

### ethers.js

```javascript
const { ethers } = require("ethers");

const provider = new ethers.providers.JsonRpcProvider(RPC_URL);

const ABI = [
  "function latestRoundData() external view returns (uint80, int256, uint256, uint256, uint80)",
  "function decimals() external view returns (uint8)",
];

const priceFeed = new ethers.Contract(FEED_ADDRESS, ABI, provider);

async function getPrice() {
  const [roundId, answer, startedAt, updatedAt, answeredInRound] =
    await priceFeed.latestRoundData();
  const decimals = await priceFeed.decimals();

  const now = Math.floor(Date.now() / 1000);
  if (now - updatedAt.toNumber() > STALENESS_THRESHOLD) {
    throw new Error("Stale price data");
  }

  console.log(`Price: ${ethers.utils.formatUnits(answer, decimals)}`);
}
```

### web3.js

```javascript
const Web3 = require("web3");
const web3 = new Web3(RPC_URL);

const ABI = [
  /* AggregatorV3Interface ABI JSON array */
];

const priceFeed = new web3.eth.Contract(ABI, FEED_ADDRESS);

async function getPrice() {
  const roundData = await priceFeed.methods.latestRoundData().call();
  const decimals = await priceFeed.methods.decimals().call();

  console.log(`Price: ${roundData.answer} (${decimals} decimals)`);
}
```

### Python (web3.py)

```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(RPC_URL))

abi = [...]  # AggregatorV3Interface ABI JSON array

contract = w3.eth.contract(address=FEED_ADDRESS, abi=abi)

round_data = contract.functions.latestRoundData().call()
decimals = contract.functions.decimals().call()

# round_data is a tuple: (roundId, answer, startedAt, updatedAt, answeredInRound)
answer = round_data[1]
updated_at = round_data[3]

print(f"Price: {answer / 10**decimals}")
```

## Historical Data

Use `getRoundData(uint80 roundId)` to query past rounds. The proxy roundId encodes both phase and aggregator round:

```
proxyRoundId = (phaseId << 64) | aggregatorRoundId
```

- `phaseId` increments each time the proxy upgrades to a new underlying aggregator.
- `aggregatorRoundId` starts at 1 for each new aggregator.
- Extract phase: `phaseId = roundId >> 64`
- Extract aggregator round: `aggregatorRoundId = uint64(roundId)`

Important caveats:

1. Looping through rounds on-chain is extremely gas-expensive. Prefer off-chain queries for historical data.
2. Round IDs are not guaranteed to be continuous. You must know a valid roundId.
3. A zero `updatedAt` timestamp indicates an incomplete round.
4. When iterating a phase, start at `(phaseId << 64) | 1` and increment until `getRoundData` reverts, which signals the end of that aggregator's history.

## Feed Address Lookup

- Price feed addresses by network: `https://docs.chain.link/data-feeds/price-feeds/addresses`
- SmartData feed addresses: `https://docs.chain.link/data-feeds/smartdata/addresses`
- Contract registry (IFlags): use `getFlag(proxyAddress)` to verify a feed is official and active on-chain. Flags contract addresses are network-specific.

Common testnet examples (Sepolia):

| Pair    | Address                                      | Decimals |
|---------|----------------------------------------------|----------|
| BTC/USD | `0x1b44F3514812d835EB1BDB0acB33d3fA3351Ee43` | 8        |
| ETH/USD | `0x694AA1769357215DE4FAC081bf1f309aDC325306` | 8        |

Always verify addresses against the official documentation before use. Feed addresses change across networks and can be deprecated.

## Common Errors

1. **Using AggregatorV3Interface for the L2 sequencer uptime feed.** The sequencer feed requires `AggregatorV2V3Interface`. Using the wrong interface will cause compilation errors or missing data.
2. **Not checking `updatedAt` for staleness.** Without a staleness check, your contract can act on arbitrarily old prices during network congestion, sequencer downtime, or feed deprecation.
3. **Hardcoding 8 decimals.** Most USD-quoted feeds use 8 decimals, but this is not universal. Always call `decimals()`.
4. **Using `answeredInRound` for freshness checks.** This field is deprecated and should not be used for any logic.
5. **Not checking the sequencer on L2 chains.** On rollups, the sequencer being down means feeds are not updated. Skipping the sequencer check can lead to acting on stale or manipulable prices.
6. **Using a deprecated or incorrect feed address.** Feed addresses are network-specific and can be deprecated. Always verify against the official address list and consider checking the on-chain Flags contract registry.

## Freshness Rules

1. Feed addresses, heartbeat intervals, and deviation thresholds change over time. When generating code for a specific network and pair, verify the address and parameters against the official feed address pages.
2. The `AggregatorV3Interface` and `AggregatorV2V3Interface` contract interfaces are stable. Code patterns using these interfaces do not require re-verification.
3. L2 sequencer uptime feed proxy addresses are network-specific and should be verified against the official L2 Sequencer Uptime Feeds documentation.
4. When in doubt about whether a feed is still active, check the deprecation schedule at `https://docs.chain.link/data-feeds/deprecating-feeds`.

## Triggering Tests

These prompts should trigger this reference:

- "I need to read the ETH/USD price in my Solidity contract."
- "How do I use Chainlink price feeds with ethers.js?"
- "Add price feed validation to this contract."
- "My DeFi protocol runs on Arbitrum and needs a price oracle."
- "How do I get historical price data from a Chainlink feed?"

These prompts should not trigger this reference:

- "How do I read a Chainlink feed on Solana?"
- "Send tokens cross-chain with CCIP."
- "How do I use Chainlink Data Streams?"
- "Decode an MVR bundle."

## Functional Tests

1. If the user asks for a Solidity price feed consumer, the generated code includes a staleness check using `updatedAt`.
2. If the user asks for a Solidity price feed consumer, the generated code includes `require(answer > 0)` or equivalent bounds check.
3. If the user asks for a consumer on an L2 chain (Arbitrum, Optimism, Base, Scroll, etc.), the generated code includes a sequencer uptime check using `AggregatorV2V3Interface` and a grace period after recovery.
4. If the user asks for decimals handling, the code calls `decimals()` rather than hardcoding a value.
5. If the user asks for offchain reading, the code uses the correct library pattern (ethers.js, web3.js, or web3.py) and includes a staleness check.
6. If the user asks for historical data, the response explains proxy roundId encoding and warns against on-chain iteration.
7. If the user provides a target network, the response uses the correct feed address or directs the user to the official address page.

## Eval Checks

The workflow passes if it:

1. generates a consumer contract that compiles without errors
2. includes all three validation checks (staleness, answer bounds, round completeness)
3. uses `AggregatorV2V3Interface` (not `AggregatorV3Interface`) for the L2 sequencer uptime feed when targeting an L2
4. never hardcodes decimals in the consumer logic
5. never uses `answeredInRound` for freshness logic
6. reads through the proxy contract, not directly from an aggregator
7. provides correct import paths from `@chainlink/contracts`

## A/B Prompt Pack

Use these prompts with and without the skill installed:

1. "Write a Solidity contract that reads the ETH/USD Chainlink price feed on Ethereum mainnet with proper validation."
2. "I am building a lending protocol on Arbitrum. Write the price feed consumer with all necessary safety checks."
3. "Show me how to read a Chainlink price feed in ethers.js and handle stale data."
4. "I need to query historical Chainlink price data for the last 100 rounds. What is the best approach?"
