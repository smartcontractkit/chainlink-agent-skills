# Feed Operations

Use this file for operational concerns around Chainlink Data Feeds: L2 sequencer checks, feed deprecation, contract registry verification, developer responsibilities, data sourcing, and self-managed feeds.

## Trigger Conditions

Use this workflow for requests like:

- "My consumer is on Arbitrum, do I need to add anything for L2?"
- "How do I check if a feed is officially managed by Chainlink?"
- "Is this feed being deprecated?"
- "What are my responsibilities as a data feed integrator?"
- "Where does the price data actually come from?"
- "What is a self-managed feed?"

Do not use this workflow for basic price feed reading, feed address lookup, or Data Streams / VRF integrations.

## L2 Sequencer Uptime Feed

On L2 rollups, sequencer downtime breaks normal read/write access and can leave stale data in the pipeline. Any contract that reads a price feed on a supported L2 must check the sequencer uptime feed before trusting the price.

### Full consumer contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";
import {AggregatorV2V3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV2V3Interface.sol";

contract PriceConsumerWithSequencerCheck {
    AggregatorV3Interface internal priceFeed;
    AggregatorV2V3Interface internal sequencerUptimeFeed;

    uint256 private constant GRACE_PERIOD_TIME = 3600; // 1 hour

    error SequencerDown();
    error GracePeriodNotOver();

    constructor(address _priceFeed, address _sequencerUptimeFeed) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        sequencerUptimeFeed = AggregatorV2V3Interface(_sequencerUptimeFeed);
    }

    function getLatestPrice() public view returns (int256) {
        // Check sequencer status
        (, int256 answer, uint256 startedAt, ,) = sequencerUptimeFeed.latestRoundData();

        // answer == 0: Sequencer is up
        // answer == 1: Sequencer is down
        if (answer != 0) revert SequencerDown();

        // Enforce grace period after recovery
        uint256 timeSinceUp = block.timestamp - startedAt;
        if (timeSinceUp < GRACE_PERIOD_TIME) revert GracePeriodNotOver();

        // Now safe to read price feed
        (, int256 price, , uint256 updatedAt, ) = priceFeed.latestRoundData();
        require(block.timestamp - updatedAt <= 3600, "Stale price");
        require(price > 0, "Invalid price");

        return price;
    }
}
```

### Critical implementation details

1. The sequencer uptime feed uses `AggregatorV2V3Interface`, NOT `AggregatorV3Interface`. Using the wrong interface will compile but may produce incorrect behavior.
2. `answer == 0` means the sequencer is up. `answer == 1` means the sequencer is down. This is inverted from what many developers expect.
3. `startedAt` is the timestamp when the status last changed, not the timestamp of the current round.
4. The grace period prevents trusting price data immediately after sequencer recovery. Stale data may still be in the pipeline while the sequencer catches up. One hour (3600 seconds) is the standard default.
5. Always combine the sequencer check with staleness and sanity checks on the price feed itself (`updatedAt` freshness, `price > 0`).

### Update mechanics

- Arbitrum: OCR round approximately every 30s. Nodes call `ArbitrumValidator.validate` via `ValidatorProxy` -> Arbitrum inbox -> L2 `ArbitrumSequencerUptimeFeed.updateStatus` sets status and records L1 timestamp.
- Other networks (Base, OP, Scroll, etc.): L1 `AggregatorProxy` -> `OptimismValidator.validate` -> `L1CrossDomainMessenger.sendMessage` -> `CanonicalTransactionChain.enqueue` -> sequencer -> `L2CrossDomainMessenger` -> `OptimismSequencerUptimeFeed.updateStatus`. Messages are processed in arrival order after sequencer return, so the "sequencer down" flip executes before later dependent transactions.

### Supported networks

Proxy addresses available for: Arbitrum, Base, Celo, Mantle, MegaETH, Metis, OP, Scroll, Soneium, X Layer, zkSync. Retrieve the correct address from `https://docs.chain.link/data-feeds/l2-sequencer-feeds`.

### Decision path

If the consumer is on a supported L2: add the sequencer uptime check. If on Ethereum L1 or a network without a sequencer: omit the check but retain staleness and sanity validation.

## Feed Deprecation

Chainlink may deprecate feeds due to low usage or lack of economic sustainability under Chainlink Economics 2.0.

1. Data quality monitoring stops 2 weeks before the deprecation date. After that point the feed may return stale or unreliable data.
2. Deprecation schedule: `https://docs.chain.link/data-feeds/deprecating-feeds`
3. Subscribe to the Chainlink Discord `data-feeds-user-notifications` channel for advance alerts.
4. The deprecation table includes: Network, Pair, Deprecation date, Deviation threshold, Heartbeat (seconds), Decimals, Aggregator address, Asset name/type, Market hours.
5. Feeds listed in official Chainlink documentation are reviewed. Community or custom deployments may carry additional risks and require independent due diligence.

Action: before integrating any feed, check the deprecation schedule. Before any mainnet launch, confirm the feed is not scheduled for shutdown.

## Contract Registry

The Flags contract is an onchain registry of official, active Chainlink feeds. Use it to verify that a proxy address is Chainlink-owned and currently active.

### Interface and usage pattern

```solidity
interface IFlags {
    function getFlag(address) external view returns (bool);
}

contract FeedVerifier {
    IFlags internal flags;

    constructor(address _flagsContract) {
        flags = IFlags(_flagsContract);
    }

    function isOfficialChainlinkFeed(address proxy) public view returns (bool) {
        return flags.getFlag(proxy);
    }
}
```

### Behavior

- `getFlag(proxy)` returns `true` if the feed is official and active. `false` means the feed is not Chainlink-managed or has been deactivated.
- Inactive feeds are removed from the registry.
- Each network has its own Flags contract address. Retrieve the correct address from `https://docs.chain.link/data-feeds/contract-registry`.

## Developer Responsibilities

Developers are solely responsible for monitoring and mitigating risks when integrating Chainlink Data Feeds.

Market manipulation can affect feed behavior. Known attack vectors: spoofing, ramping, bear raids, cross-market manipulation, wash trading, frontrunning. Low-liquidity assets are more vulnerable. Application code must be audited before production, and all dependencies vetted. Inform end users of applicable risks.

Required mitigations in application code:

1. Data quality checks: validate staleness (`updatedAt`), sanity (`price > 0`), and sequencer status on L2.
2. Circuit breakers: pause operations when data falls outside expected bounds.
3. Contingency logic: define fallback behavior for feed failure or extreme deviation.

## Data Sources

| Feed Type | Sources | Minimum Count |
|---|---|---|
| Crypto Price | CEX and/or DEX data via aggregators/vendors | 3+ |
| Crypto State Price | DEX pool state data via vendors | 3+ |
| Forex / Precious Metals / US Oil / US Equities | Market data vendors | 3+ |
| UK and Euro ETFs | Market data vendors (15-minute delayed) | 2+ |
| SmartData PoR (offchain) | Direct from custodian / fund administrator / auditor | 1 |
| SmartData PoR (cross-chain) | On-chain data | 1 |
| SmartData NAV (offchain) | Direct from Fund Administrator or Asset Manager | 1 |
| Composite Index | DON-calculated from aggregators/vendors | 3+ |
| Data Link Long Tail Crypto | Single crypto price data aggregator | 1 |

Long-tail crypto feeds using a single source carry higher risk. Evaluate data quality, liquidity distribution, and single-source provider risks before integrating.

## Self-Managed Feeds

Self-managed feeds are written onchain by a chain or third-party operator, not Chainlink node operators. A CRE workflow reads from Chainlink Data Streams and writes updates to a proxy contract. Consumers read via the standard Data Feeds proxy interface.

Chainlink Labs does not manage monitoring, heartbeat compliance, deviation compliance, latency, correctness of onchain writes, or SLAs for these feeds. Proxy addresses are NOT published in Chainlink public feed catalogs -- obtain addresses directly from the chain or operator. Contact: datafeeds@chain.link

Treat self-managed feeds as untrusted until independently verified. Apply the same staleness, sanity, and circuit-breaker checks described in Developer Responsibilities.

## Freshness Rules

1. Retrieve sequencer uptime feed proxy addresses and Flags contract addresses from official Chainlink docs before generating code.
2. Check the deprecation schedule before recommending any specific feed.
3. Do not hardcode proxy addresses, Flags contract addresses, or feed parameters. Always point the user to the official source for current values.
4. Verify network support before recommending L2 sequencer checks.

## Triggering Tests

These prompts should trigger this reference:

- "My consumer is on Arbitrum, do I need to add anything for L2?"
- "How do I check sequencer status before reading a price feed?"
- "Is this data feed being deprecated?"
- "How do I verify a feed is officially managed by Chainlink?"
- "What are my responsibilities when using Chainlink price feeds?"
- "Where does the price data come from for crypto feeds?"
- "What is a self-managed Chainlink feed?"

These prompts should NOT trigger this reference:

- "How do I read a price feed in Solidity?" (use basic price feed reference)
- "What is the ETH/USD feed address on Ethereum?" (use feed address lookup)
- "How do I use Chainlink VRF?" (different product)

## Functional Tests

1. If the user has a consumer on a supported L2, include the full sequencer uptime check with grace period. Do not omit the grace period.
2. If the user asks about sequencer checks, use `AggregatorV2V3Interface` for the sequencer feed. Never use `AggregatorV3Interface` for the sequencer uptime feed.
3. If the user asks about feed authenticity, provide the IFlags registry pattern with the correct network Flags address.
4. If the user asks about deprecation, direct them to the deprecation schedule and Discord channel.
5. If the user integrates a self-managed feed, warn about the lack of Chainlink-managed SLAs and monitoring.
6. Sequencer check included in all L2 consumer code.
7. Grace period enforced in all sequencer check implementations.
8. Staleness check (`updatedAt`) included alongside every `latestRoundData` price read.

## Eval Checks

The workflow passes if it:

1. includes sequencer uptime check for any L2 consumer contract on a supported network
2. uses `AggregatorV2V3Interface` (not `AggregatorV3Interface`) for the sequencer feed
3. enforces the grace period after sequencer recovery
4. includes staleness and sanity checks on price data
5. directs users to official docs for current proxy addresses and Flags contract addresses
6. warns about self-managed feed limitations
7. surfaces deprecation risks before recommending a feed

## A/B Prompt Pack

Use these prompts with and without the skill installed:

1. "My consumer is on Arbitrum, do I need to add anything for L2?" -- Expected: full sequencer uptime check with grace period, AggregatorV2V3Interface, staleness validation.
2. "I want to verify onchain that a price feed proxy is an official Chainlink feed." -- Expected: IFlags registry pattern with network-specific Flags address.
3. "I am integrating a long-tail crypto feed on Base. What should I watch out for?" -- Expected: sequencer check, single-source risk warning, staleness checks, circuit breaker recommendation.
4. "Is there a way to know if a feed is going to be shut down?" -- Expected: deprecation schedule link, Discord notification channel, 2-week monitoring cutoff warning.
