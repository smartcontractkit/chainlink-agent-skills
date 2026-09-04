# MVR Bundle Feeds (Multiple-Variable Response)

Use for Chainlink MVR/`IBundleAggregatorProxy` reads. MVR packs several typed fields into `bytes`; decode the exact documented struct/tuple. Single-value prices, SVR, and CCIP use other workflows.

## MVR Architecture

MVR feeds pack multiple typed fields (uint256, bool, etc.) into a single `bytes` bundle stored onchain via a `BundleAggregatorProxy`. Only the latest bundle is stored; there is no `getRoundData` equivalent for historical lookups. Historical data requires your own contract storage or an offchain indexer.

Core interface: `IBundleAggregatorProxy`
Import: `@chainlink/contracts/src/v0.8/data-feeds/interfaces/IBundleAggregatorProxy.sol`

Key functions:

- `latestBundle() returns (bytes memory)` -- raw bundle bytes
- `bundleDecimals() returns (uint8[] memory)` -- numeric scaling; validate the exact schema length before indexing, and never treat a boolean's position as scaling metadata
- `latestBundleTimestamp() returns (uint256)` -- block timestamp of the most recent update
- `description() returns (string memory)` -- human-readable feed description
- `version() returns (uint256)` -- feed version

Find the proxy address and exact bundle schema on the SmartData Addresses page. Filter with "Show Multiple-Variable Response (MVR) feeds" and open "MVR Bundle Info" for the target feed.

## Solidity Consumer Pattern

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {IBundleAggregatorProxy} from
    "@chainlink/contracts/src/v0.8/data-feeds/interfaces/IBundleAggregatorProxy.sol";

contract MVRConsumer {
    IBundleAggregatorProxy internal immutable bundleFeed;
    uint256 public immutable maxAge; // feed heartbeat + buffer

    error InvalidTimestamp();
    error StaleData();
    error SchemaMismatch();

    // MUST match the documented schema's order and types.
    struct FundData {
        uint256 totalReturn;
        uint256 nav;
        uint256 aum;
        bool openToNewInvestors;
    }

    constructor(address proxyAddress, uint256 maxAgeSeconds) {
        require(proxyAddress != address(0) && maxAgeSeconds != 0);
        bundleFeed = IBundleAggregatorProxy(proxyAddress);
        maxAge = maxAgeSeconds;
    }

    function getLatestData()
        external
        view
        returns (FundData memory data, uint8[3] memory numericDecimals)
    {
        uint256 updatedAt = bundleFeed.latestBundleTimestamp();
        if (updatedAt == 0 || updatedAt > block.timestamp) {
            revert InvalidTimestamp();
        }
        if (block.timestamp - updatedAt > maxAge) revert StaleData();

        uint8[] memory decimals = bundleFeed.bundleDecimals();
        if (decimals.length != 4) revert SchemaMismatch();
        numericDecimals = [decimals[0], decimals[1], decimals[2]];
        data = abi.decode(bundleFeed.latestBundle(), (FundData));
        // The bool is used directly; it is not scaled or decimals[3] metadata.
    }
}
```

Critical rules for Solidity consumers:

1. The struct field order and types MUST exactly match the feed's documented schema. Mismatched order silently produces wrong values.
2. Set `maxAge` to the feed's heartbeat plus a small buffer, not an arbitrary value.
3. `uint256` division truncates. Keep raw integers onchain and scale offchain when precision matters.
4. Check `bundleDecimals().length` before indexing; scale numeric fields only. Booleans are used directly.
5. On an L2 rollup, the consumer must also apply the L2 sequencer uptime check.

## Schema-Neutral Off-Chain Sequence

Use the caller's current EVM client; the sequence is the same for ethers, viem, web3, or raw RPC:

1. Get the `BundleAggregatorProxy` address and exact ordered field types from the SmartData Addresses page's **MVR Bundle Info**. Never infer a schema from field names.
2. Bind the proxy with the minimal `IBundleAggregatorProxy` reads: `latestBundle() returns (bytes)`, `bundleDecimals() returns (uint8[])`, and `latestBundleTimestamp() returns (uint256)`.
3. Compare `latestBundleTimestamp()` with current Unix time using the feed heartbeat plus a buffer.
4. Fetch `latestBundle()` and ABI-decode it with the exact documented field order and types.
5. Fetch `bundleDecimals()`; map entries by schema index, format numeric fields with their own precision, and leave non-numeric fields unscaled.
6. Preserve raw integers when downstream precision matters. Client-specific helpers include ethers `AbiCoder`/`formatUnits` and viem `decodeAbiParameters`/`formatUnits`.

## Freshness

Verify the current proxy, exact schema, and heartbeat before generating code. MVR stores only the latest bundle and does not support `latestRoundData()`/`getRoundData()`; persist bundles or index them offchain for history.

