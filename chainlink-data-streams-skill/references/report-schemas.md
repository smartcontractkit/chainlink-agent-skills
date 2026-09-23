# Report Schemas

Use this for schema choice, fields, decoding, or deprecation. Published schemas are stable, but availability changes. This offline catalog comes from `github.com/smartcontractkit/data-streams-sdk/go@v1.2.4` (decoders v1–v13); language SDK support may differ, so check current package docs before claiming automatic decoding. Re-check current availability, deprecation, package versions, and entitlements at:

- `https://docs.chain.link/data-streams/reference/report-schema-overview.md`
- `https://docs.chain.link/data-streams/deprecating-streams.md`
- `https://github.com/smartcontractkit/data-streams-sdk`

## Types and Base Fields

Do not pass `int192`/`uint192` fixed-point or integer values through floating point.

For v2–v13, **Base** is this ordered typed declaration:

```text
feedId bytes32; validFromTimestamp uint32; observationsTimestamp uint32;
nativeFee uint192; linkFee uint192; expiresAt uint32
```

Meanings: stream identifier (the feed ID also encodes the decoder schema); earliest-valid Unix seconds; DON observation/consensus Unix seconds; native-token verification fee; LINK-denominated verification fee; expiration Unix seconds. Each version below is **Base + delta**, in the listed order.

Repeated risk fields retain these meanings: `marketStatus uint32` is the market-state signal; interpret current SDK constants before risk use. `ripcord uint32` is an issuer/source risk flag; an active flag means the value is not normal market data.

## Local Catalog

Use this only when live docs cannot be fetched, and disclose that current availability/deprecation is unverified.

### v1 — early crypto with block metadata

| Field | ABI type | Meaning |
|---|---:|---|
| `feedId` | `bytes32` | Stream identifier. |
| `observationsTimestamp` | `uint32` | Observation Unix seconds. |
| `benchmarkPrice` | `int192` | Consensus benchmark price. |
| `bid` | `int192` | Bid-side estimate. |
| `ask` | `int192` | Ask-side estimate. |
| `currentBlockNum` | `uint64` | Current block number used by the report. |
| `currentBlockHash` | `bytes32` | Current block hash used by the report. |
| `validFromBlockNum` | `uint64` | Earliest valid block number. |
| `currentBlockTimestamp` | `uint64` | Current block timestamp in seconds. |

### v2 — basic benchmark price

Base + consensus benchmark price: Go `BenchmarkPrice`; TypeScript/EVM `price`; Rust `benchmark_price`.

### v3 — Crypto Advanced

Base + consensus benchmark price (Go `BenchmarkPrice`; TypeScript/EVM `price`; Rust `benchmark_price`); `bid int192`; `ask int192`.

### v4 — benchmark price and market status

Base + consensus benchmark price (Go `BenchmarkPrice`; TypeScript/Rust/EVM `price`); `marketStatus uint32`.

### v5 — rate

Base + `rate int192` (reported rate); `timestamp uint32` (rate timestamp in seconds); `duration uint32` (duration window in seconds).

### v6 — multiple prices

Base + `price int192` (primary); `price2 int192` (secondary); `price3 int192` (third); `price4 int192` (fourth); `price5 int192` (fifth).

### v7 — exchange rate

Base + `exchangeRate int192` — redemption or exchange-rate value.

### v8 — RWA Standard

Base + `lastUpdateTimestamp uint64` (last source update; confirm units for the stream); `midPrice int192` (consensus mid); `marketStatus uint32`.

### v9 — SmartData/NAV

Base + `navPerShare int192` (NAV per share); `navDate uint64` (NAV date/timestamp; confirm units); `aum int192` (assets under management); `ripcord uint32`.

### v10 — tokenized asset

Base + `lastUpdateTimestamp uint64` (last source update); `price int192` (underlying asset price); `marketStatus uint32`; `currentMultiplier int192` (current underlying-share multiplier); `newMultiplier int192` (future multiplier after a corporate action); `activationDateTime uint32` (corporate-action activation timestamp); `tokenizedPrice int192` (tokenized-asset price when available).

### v11 — RWA Advanced

Base + `mid int192` (liquidity-weighted mid); `lastSeenTimestampNs uint64` (last-seen nanoseconds); `bid int192` (consensus bid); `bidVolume int192` (resting bid depth); `ask int192` (consensus ask); `askVolume int192` (resting ask depth); `lastTradedPrice int192` (most recent trade); `marketStatus uint32`.

### v12 — NAV with next NAV

Base + `navPerShare int192` (current NAV per share); `nextNavPerShare int192` (next NAV per share); `navDate uint64` (NAV date/timestamp; confirm units); `ripcord uint32`.

### v13 — best bid/ask

Base + `bestAsk int192` (best ask); `bestBid int192` (best bid); `askVolume uint64` (best-ask volume); `bidVolume uint64` (best-bid volume); `lastTradedPrice int192` (most recent trade).

## Decoding Rules

1. Derive the schema version encoded in `feedId`, then use that language's matching official SDK decoder.
2. Preserve raw `full_report`; retain large/fixed-point numbers until official scaling/display units are known.
3. Never assume every schema has `price`, `bid`, and `ask`.
4. Treat `marketStatus`, `ripcord`, timestamps, and corporate-action fields as application risk signals.

For a schema catalog answer, give source/check status, version/category, purpose, typed fields, current/deprecated status, and decoder caveats. For decoding, give language/decoder, version, decoded fields, raw preservation, and an onchain-verification warning for value-securing use.

Never guess deprecation. If it cannot be fetched, say:

```text
I could not verify the current Data Streams deprecation page: <URL>. I can explain schema field definitions from the local skill reference, but you should confirm current availability before shipping.
```
