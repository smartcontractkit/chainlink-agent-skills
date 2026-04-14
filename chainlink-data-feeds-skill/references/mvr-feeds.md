# MVR Bundle Feeds (Multiple-Variable Response)

Use this file when the user wants to read, decode, or integrate a Chainlink MVR bundle feed. MVR feeds bundle multiple related data points into a single onchain update, unlike single-value Price Feeds. They return a `bytes` payload that must be decoded into a matching struct or tuple.

## Trigger Conditions

Use this workflow for requests like:

- "Read an MVR bundle feed in Solidity."
- "Decode a multi-field Chainlink bundle feed offchain."
- "Get multiple data points from a single Chainlink feed."
- "How do I use IBundleAggregatorProxy?"
- "Read an MVR feed with ethers.js or viem."

Do not use this workflow for single-value price feeds, SVR feeds, or CCIP requests.

## MVR Architecture

MVR feeds pack multiple typed fields (uint256, bool, etc.) into a single `bytes` bundle stored onchain via a `BundleAggregatorProxy`. Only the latest bundle is stored; there is no `getRoundData` equivalent for historical lookups. Historical data requires your own contract storage or an offchain indexer.

Core interface: `IBundleAggregatorProxy`
Import: `@chainlink/contracts/src/v0.8/data-feeds/interfaces/IBundleAggregatorProxy.sol`

Key functions:

- `latestBundle() returns (bytes memory)` -- raw bundle bytes
- `bundleDecimals() returns (uint8[] memory)` -- per-field decimals; non-numeric fields (bools) typically 0
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
    IBundleAggregatorProxy internal bundleFeed;
    uint256 public constant STALENESS_THRESHOLD = 86400; // align to feed heartbeat

    error StaleData();

    // Struct MUST match feed schema exactly (same order and types)
    struct FundData {
        uint256 totalReturn;
        uint256 nav;
        uint256 aum;
        bool openToNewInvestors;
    }

    constructor(address proxyAddress) {
        bundleFeed = IBundleAggregatorProxy(proxyAddress);
    }

    function getLatestData() public view returns (FundData memory) {
        uint256 lastUpdate = bundleFeed.latestBundleTimestamp();
        if (block.timestamp - lastUpdate > STALENESS_THRESHOLD) revert StaleData();

        bytes memory rawBundle = bundleFeed.latestBundle();
        FundData memory decoded = abi.decode(rawBundle, (FundData));
        return decoded;
    }
}
```

Critical rules for Solidity consumers:

1. The struct field order and types MUST exactly match the feed's documented schema. Mismatched order silently produces wrong values.
2. Set `STALENESS_THRESHOLD` to the feed's heartbeat plus a small buffer, not an arbitrary value.
3. `uint256` division in Solidity truncates. Keep raw values onchain and scale offchain when precision matters.
4. Use `bundleDecimals()` to know per-field scaling; non-numeric fields have decimals of 0.

## Off-Chain Reading

### ethers.js v5

```javascript
const { ethers } = require("ethers");

const bundleAggregatorProxyABI = [
  "function latestBundle() view returns (bytes)",
  "function bundleDecimals() view returns (uint8[])",
  "function latestBundleTimestamp() view returns (uint256)",
];

const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL);
const contract = new ethers.Contract(
  process.env.MVR_FEED_ADDRESS,
  bundleAggregatorProxyABI,
  provider
);

// Staleness check
const timestamp = await contract.latestBundleTimestamp();
const age = Math.floor(Date.now() / 1000) - timestamp.toNumber();
if (age > STALENESS_THRESHOLD) throw new Error("Stale data");

// Decode -- dataStructure MUST exactly match feed schema
const bundleBytes = await contract.latestBundle();
const dataStructure = ["uint256", "uint256", "uint256", "bool"];
const decoded = ethers.utils.defaultAbiCoder.decode(dataStructure, bundleBytes);

// Decimal handling
const decimals = await contract.bundleDecimals();
const fieldNames = ["totalReturn", "nav", "aum", "openToNewInvestors"];
const result = {};
fieldNames.forEach((name, i) => {
  if (typeof decoded[i] === "boolean") {
    result[name] = decoded[i];
  } else {
    const raw = ethers.BigNumber.from(decoded[i]);
    result[name] = ethers.utils.formatUnits(raw, decimals[i]);
  }
});
```

Notes: ethers v6 APIs differ (providers, BigNumber removal). The `dataStructure` array must match the feed schema from the SmartData Addresses page exactly.

### Viem (TypeScript)

```typescript
import { createPublicClient, http, parseAbiItem, decodeAbiParameters, formatUnits } from "viem";

const client = createPublicClient({ transport: http(process.env.RPC_URL) });
const address = process.env.MVR_FEED_ADDRESS as `0x${string}`;

const abi = [
  parseAbiItem("function latestBundle() view returns (bytes)"),
  parseAbiItem("function bundleDecimals() view returns (uint8[])"),
  parseAbiItem("function latestBundleTimestamp() view returns (uint256)"),
];

// Staleness check
const timestamp = await client.readContract({ address, abi, functionName: "latestBundleTimestamp" });
const age = BigInt(Math.floor(Date.now() / 1000)) - timestamp;
if (age > BigInt(STALENESS_THRESHOLD)) throw new Error("Stale data");

// Decode -- parameterStructure MUST match feed schema
const bundleBytes = await client.readContract({ address, abi, functionName: "latestBundle" });
const parameterStructure = [
  { type: "uint256", name: "totalReturn" },
  { type: "uint256", name: "nav" },
  { type: "uint256", name: "aum" },
  { type: "bool", name: "openToNewInvestors" },
];
const decoded = decodeAbiParameters(parameterStructure, bundleBytes);

// Decimal handling
const decimals = await client.readContract({ address, abi, functionName: "bundleDecimals" });
const formatted = parameterStructure.map((param, i) => {
  if (param.type === "bool") return { name: param.name, value: decoded[i] };
  return { name: param.name, value: formatUnits(decoded[i] as bigint, decimals[i]) };
});
```

## Decimal Handling

`bundleDecimals()` returns a `uint8[]` with one entry per field in schema order. Rules:

1. Numeric fields (uint256) have a nonzero decimal count. Divide raw value by `10 ** decimals[i]` or use `formatUnits`.
2. Non-numeric fields (bool) typically have decimals of 0. Skip decimal adjustment for these.
3. In Solidity, `uint256` division truncates. Store raw values onchain and scale offchain when precision matters.
4. Always call `bundleDecimals()` rather than assuming all numeric fields share the same precision.

## Common Errors

1. **Struct field order mismatch** -- `abi.decode` does not check field names. Wrong order silently produces garbage values. Always verify against the feed's "MVR Bundle Info" on the SmartData Addresses page.
2. **Using AggregatorV3Interface** -- MVR feeds use `IBundleAggregatorProxy`, not `AggregatorV3Interface`. The latter is for single-value price feeds only.
3. **Ignoring bundleDecimals()** -- Treating all numeric fields as having the same precision leads to values off by orders of magnitude.
4. **Arbitrary staleness threshold** -- The threshold must align to the feed's heartbeat plus a buffer. A too-short threshold causes false rejections; too-long allows genuinely stale data.

## Freshness Rules

1. Look up the proxy address and bundle schema on the SmartData Addresses page before generating code. Do not guess field types or order.
2. Set staleness thresholds based on the feed's documented heartbeat, not arbitrary constants.
3. Only the latest bundle is stored onchain. If the user needs historical data, advise storing bundles in contract state or using an offchain indexer.
4. Do not use `AggregatorV3Interface` methods (`latestRoundData`, `getRoundData`) with MVR feeds.

## Triggering Tests

These prompts should trigger this workflow:

- "Read an MVR bundle feed in Solidity."
- "How do I decode a Chainlink MVR feed offchain with ethers?"
- "Get multiple data points from a single Chainlink feed."
- "Write a viem client that reads an MVR bundle feed."

These prompts should not trigger this workflow:

- "Get the latest ETH/USD price." (single-value price feed)
- "Send a CCIP message." (CCIP, not data feeds)
- "Read a Chainlink SVR feed." (SVR-specific)

## Functional Tests

1. If the user asks for MVR integration, use `IBundleAggregatorProxy` rather than `AggregatorV3Interface`.
2. If the user provides a feed address, look up its schema before generating decode logic.
3. If the generated struct or tuple order does not match the documented schema, flag the mismatch.
4. If the user asks for historical bundle data, explain onchain limitation and suggest storage or indexer alternatives.
5. If the staleness threshold is hardcoded without reference to heartbeat, warn.
6. If Solidity code scales values via division, note truncation risk and suggest keeping raw values.

## Eval Checks

The workflow passes if it:

1. uses `IBundleAggregatorProxy` and its methods, never `AggregatorV3Interface`
2. struct or tuple matches the documented feed schema in field order and types
3. validates staleness against `latestBundleTimestamp()` with a heartbeat-aligned threshold
4. calls `bundleDecimals()` and handles per-field decimal scaling correctly
5. skips decimal adjustment for non-numeric fields like bools
6. warns about Solidity truncation when dividing scaled integers

## A/B Prompt Pack

Use these prompts with and without the skill installed:

1. "Read an MVR bundle feed in Solidity. The feed has fields: totalReturn (uint256), nav (uint256), aum (uint256), openToNewInvestors (bool)."
2. "Write a JavaScript function using ethers.js v5 to read and decode an MVR bundle feed, handling per-field decimals correctly."
3. "I used AggregatorV3Interface to read an MVR feed and got empty data. What went wrong?"
4. "Build a viem TypeScript client that reads an MVR bundle feed, checks staleness, and formats values with correct decimals."
