# Report Schemas

## Contents

- Types and Base Fields
- Local Catalog
- Decoding Rules

Use this for schema choice, fields, decoding, or deprecation. Published schemas are stable, but availability changes. This offline catalog comes from `github.com/smartcontractkit/data-streams-sdk/go@v1.2.4` (decoders v1–v13), plus a v14 entry from the v14 schema page and the SDK repo (v14 decoders first appear in Go `go/v2.1.0`, TypeScript `1.3.0`, Rust `1.3.0`; Go v1.2.4 has none); language SDK support may differ, so check current package docs before claiming automatic decoding. Re-check current availability, deprecation, package versions, and entitlements at:

- `https://docs.chain.link/data-streams/reference/report-schema-overview.md`
- `https://docs.chain.link/data-streams/reference/report-schema-v14.md`
- `https://docs.chain.link/data-streams/deprecating-streams.md`
- `https://github.com/smartcontractkit/data-streams-sdk`

## Types and Base Fields

Do not pass `int192`/`uint192` fixed-point or integer values through floating point.

For v2–v14, **Base** is this ordered typed declaration:

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

24/7 TWAP streams use v2: one continuous TWAP price per asset, no v11 fields.

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

Base + `mid int192` (liquidity-weighted mid); `lastSeenTimestampNs uint64` (last-seen nanoseconds); `bid int192` (consensus bid); `bidVolume int192` (resting bid depth); `ask int192` (consensus ask); `askVolume int192` (resting ask depth); `lastTradedPrice int192` (most recent trade); `marketStatus uint32`. `lastTradedPrice` is deprecated as a production input on 24/5 US Equities streams: do not use it there. On 24/7 Perpetual Markets streams it carries the slow Oracle Price and is supported; see [24/7 US equities](24-7-us-equities.md). `lastSeenTimestampNs` tracks `mid` only.

### v12 — NAV with next NAV

Base + `navPerShare int192` (current NAV per share); `nextNavPerShare int192` (next NAV per share); `navDate uint64` (NAV date/timestamp; confirm units); `ripcord uint32`.

### v13 — best bid/ask

Base + `bestAsk int192` (best ask); `bestBid int192` (best bid); `askVolume uint64` (best-ask volume); `bidVolume uint64` (best-bid volume); `lastTradedPrice int192` (most recent trade).

### v14 — Futures

Base + `midPrice int192` (DON consensus mid); `bidPrice int192` (consensus bid); `askPrice int192` (consensus ask); `expiryTime uint64` (contract expiration, Unix seconds); `firstDayOfNotice uint64` (first day of notice for the tracked contract, Unix seconds); `lastSeenTimestampNs uint64` (last update from the data provider, nanoseconds; staleness only); `marketStatus uint32`; `contractMonth uint32` (1 Jan – 12 Dec); `goldmanRollPrice int192` (Goldman Roll, GSCI methodology: 20% shifted per business day over business days 5–9); `currentBusinessDay uint32` (business day of the month, determines the Goldman window); `interpolatedGoldmanRollPrice int192` (the 20% daily shift smoothed over each business day in the window). Prices are 18-decimal fixed point. Per the v14 page `nativeFee`/`linkFee` are legacy verification-fee fields (`linkFee` is not used for subscription billing).

`marketStatus` (v14): `0` Unknown, `1` Closed, `2` Open. Always read it; never infer open/closed from timestamps. This is not the v11 mapping (`5` = Closed) and not the 24/7 mapping. The v14 schema page says the mapping "varies by feed" while the Futures and Market Hours pages give this one mapping for every v14 futures feed; use it and confirm against Market Hours. Treat `0` as not open. Detail: [Futures (v14)](futures-v14.md).

SDK names (decoder first appears in Go `go/v2.1.0`, TypeScript `1.3.0`, Rust `1.3.0`; the feed ID encodes the version):

| Docs field | Go (`go/v2`, `report/v14`, `v14.Data`) | TypeScript (`decodeReport`, `version: "V14"`) | Rust (`ReportDataV14`) |
|---|---|---|---|
| `midPrice`, `bidPrice`, `askPrice` | `MidPrice`, `BidPrice`, `AskPrice` (`*big.Int`) | same names, `bigint` | `mid_price`, `bid_price`, `ask_price` (`BigInt`) |
| `expiryTime`, `firstDayOfNotice` | `ExpiryTime`, `FirstDayOfNotice` (`time.Time`; use `.Unix()`) | same names, `bigint` | `expiry_time`, `first_day_of_notice` (`u64`) |
| `lastSeenTimestampNs` | `LastSeenTimestampNs` (`time.Time`; use `.UnixNano()`) | same name, `bigint` | `last_seen_timestamp_ns` (`u64`) |
| `marketStatus`, `contractMonth`, `currentBusinessDay` | `MarketStatus`, `ContractMonth`, `CurrentBusinessDay` (`uint32`) | same names, `number` | `market_status`, `contract_month`, `current_business_day` (`u32`) |
| `goldmanRollPrice`, `interpolatedGoldmanRollPrice` | `GoldmanRollPrice`, `InterpolatedGoldmanRollPrice` (`*big.Int`) | same names, `bigint` | `goldman_roll_price`, `interpolated_goldman_roll_price` (`BigInt`) |

Base fields keep the usual per-language names (Go also turns the three base timestamps into `time.Time`). The Go and TypeScript ABI declare the three base timestamps (`validFromTimestamp`, `observationsTimestamp`, `expiresAt`) as `uint64` while the docs and Rust declare `uint32`: decode with the official SDK rather than a hand-written struct. Go constants `MarketStatusUnknown/Closed/Open` and the TypeScript `MarketStatus` enum (`UNKNOWN`, `INACTIVE`, `ACTIVE`) map to 0/1/2.

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
