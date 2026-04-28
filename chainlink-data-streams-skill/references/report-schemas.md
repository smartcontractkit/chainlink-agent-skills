# Report Schemas

Use this file when the user asks to decode reports, understand schema properties, choose a schema, or check whether a stream is available or deprecated.

## Source Of Truth

Schema versions are stable once published; Chainlink can add new schema versions over time. Keep the local catalog below as the offline fallback, but verify current availability, deprecation, SDK package versions, and stream entitlement from:

- `https://docs.chain.link/data-streams/reference/report-schema-overview`
- `https://docs.chain.link/data-streams/deprecating-streams`
- `https://github.com/smartcontractkit/data-streams-sdk`

This local catalog was derived from the official Go SDK report packages in `github.com/smartcontractkit/data-streams-sdk/go@v1.2.4`, which exposes decoders for v1 through v13. TypeScript docs also describe automatic report decoding through v13.

## Common Fields

These fields appear across many schema versions:

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. The feed ID also encodes the report schema version used by SDK decoders. |
| `validFromTimestamp` | `uint32` | Earliest Unix timestamp, in seconds, from which the report is valid. |
| `observationsTimestamp` | `uint32` | Unix timestamp, in seconds, for the DON observation/consensus time. |
| `nativeFee` | `uint192` | Native-token verification fee value used by onchain verification flows. |
| `linkFee` | `uint192` | LINK-denominated verification fee value used by onchain verification flows. |
| `expiresAt` | `uint32` | Unix timestamp, in seconds, after which the report should be treated as expired. |
| `marketStatus` | `uint32` | Market state signal. Interpret through current docs/SDK constants before using in risk logic. |
| `ripcord` | `uint32` | Issuer/source risk flag. When active, consumers should not treat the value as normal market data. |

Treat `int192` and `uint192` values as large fixed-point/integer values. Do not convert through floating point in generated code.

## Local Schema Catalog

Use this catalog if live docs cannot be fetched. Still tell the user that current availability/deprecation could not be verified.

### v1

Early crypto-style report with block metadata.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `benchmarkPrice` | `int192` | Consensus benchmark price. |
| `bid` | `int192` | Bid-side price estimate. |
| `ask` | `int192` | Ask-side price estimate. |
| `currentBlockNum` | `uint64` | Current block number used by the report. |
| `currentBlockHash` | `bytes32` | Current block hash used by the report. |
| `validFromBlockNum` | `uint64` | Earliest block number from which the report is valid. |
| `currentBlockTimestamp` | `uint64` | Current block timestamp in seconds. |

### v2

Basic benchmark-price report with validity and fee fields.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `benchmarkPrice` / `price` / `benchmark_price` | `int192` | Consensus benchmark price. Use `benchmarkPrice` / `BenchmarkPrice` in Go, `price` in TypeScript, and `benchmark_price` in Rust. |

### v3

Crypto Advanced report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `benchmarkPrice` / `price` / `benchmark_price` | `int192` | Consensus benchmark price. Use `benchmarkPrice` / `BenchmarkPrice` in Go, `price` in TypeScript, docs, and EVM examples, and `benchmark_price` in Rust. |
| `bid` | `int192` | Bid-side price estimate. |
| `ask` | `int192` | Ask-side price estimate. |

### v4

Benchmark-price report with market status.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `benchmarkPrice` / `price` | `int192` | Consensus benchmark price. Use `benchmarkPrice` / `BenchmarkPrice` in Go and `price` in TypeScript, docs, Rust, and EVM examples. |
| `marketStatus` | `uint32` | Market state signal. |

### v5

Rate report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `rate` | `int192` | Reported rate value. |
| `timestamp` | `uint32` | Rate timestamp in seconds. |
| `duration` | `uint32` | Duration window in seconds. |

### v6

Multi-price report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `price` | `int192` | Primary price value. |
| `price2` | `int192` | Secondary price value. |
| `price3` | `int192` | Third price value. |
| `price4` | `int192` | Fourth price value. |
| `price5` | `int192` | Fifth price value. |

### v7

Exchange-rate report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `exchangeRate` | `int192` | Redemption or exchange-rate value. |

### v8

RWA Standard report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `lastUpdateTimestamp` | `uint64` | Last source update timestamp. Confirm units from docs for the target stream. |
| `midPrice` | `int192` | Consensus mid price. |
| `marketStatus` | `uint32` | Market state signal. |

### v9

SmartData/NAV-style report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `navPerShare` | `int192` | Net asset value per share. |
| `navDate` | `uint64` | NAV date/timestamp. Confirm units from docs for the target stream. |
| `aum` | `int192` | Assets under management value. |
| `ripcord` | `uint32` | Issuer/source risk flag. |

### v10

Tokenized-asset report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `lastUpdateTimestamp` | `uint64` | Last source update timestamp. |
| `price` | `int192` | Underlying asset price. |
| `marketStatus` | `uint32` | Market state signal. |
| `currentMultiplier` | `int192` | Current underlying-share multiplier. |
| `newMultiplier` | `int192` | Future multiplier after a corporate action. |
| `activationDateTime` | `uint32` | Corporate-action activation timestamp. |
| `tokenizedPrice` | `int192` | Tokenized asset price when available. |

### v11

RWA Advanced report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `mid` | `int192` | Liquidity-weighted mid price. |
| `lastSeenTimestampNs` | `uint64` | Last-seen timestamp in nanoseconds. |
| `bid` | `int192` | Consensus bid price. |
| `bidVolume` | `int192` | Resting bid-side volume/depth. |
| `ask` | `int192` | Consensus ask price. |
| `askVolume` | `int192` | Resting ask-side volume/depth. |
| `lastTradedPrice` | `int192` | Most recent traded price. |
| `marketStatus` | `uint32` | Market state signal. |

### v12

NAV report with next NAV.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `navPerShare` | `int192` | Current NAV per share. |
| `nextNavPerShare` | `int192` | Next NAV per share. |
| `navDate` | `uint64` | NAV date/timestamp. Confirm units from docs for the target stream. |
| `ripcord` | `uint32` | Issuer/source risk flag. |

### v13

Best-bid/best-ask market data report.

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `validFromTimestamp` | `uint32` | Earliest valid timestamp in seconds. |
| `observationsTimestamp` | `uint32` | Observation timestamp in seconds. |
| `nativeFee` | `uint192` | Native-token verification fee. |
| `linkFee` | `uint192` | LINK verification fee. |
| `expiresAt` | `uint32` | Expiration timestamp in seconds. |
| `bestAsk` | `int192` | Best ask price. |
| `bestBid` | `int192` | Best bid price. |
| `askVolume` | `uint64` | Best ask volume. |
| `bidVolume` | `uint64` | Best bid volume. |
| `lastTradedPrice` | `int192` | Most recent traded price. |

## Decoding Rules

1. Identify the schema version from the feed ID/report metadata or SDK decoder type.
2. Use the official SDK decoder for the target language whenever available.
3. Preserve the raw full report alongside decoded fields when storing data.
4. Treat numeric values as fixed-point or large integer values until the docs confirm scaling and display units.
5. Do not assume every schema has `price`, `bid`, and `ask`.
6. Explain `marketStatus`, `ripcord`, timestamp, and corporate-action fields as application-level risk signals, not generic fields to ignore.

## Response Shape For Schema Questions

For "what schemas exist?" answer with:

1. official source checked, or say that live verification failed
2. schema version and stream category where known
3. purpose
4. field list with ABI types
5. whether current/deprecated status was verified
6. any SDK decoder caveats

For "decode this report" answer with:

1. target language and SDK decoder path
2. schema version used
3. decoded fields
4. raw report preservation recommendation
5. verification warning if the user plans to use the report in value-securing logic

## Deprecation Guidance

Do not guess deprecation status. If docs cannot be fetched, say:

```text
I could not verify the current Data Streams deprecation page: <URL>. I can explain schema field definitions from the local skill reference, but you should confirm current availability before shipping.
```
