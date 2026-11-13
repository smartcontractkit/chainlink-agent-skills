# Chainlink 24/7 US Equities (Data Streams)

Scope: Chainlink 24/7 US equities pricing only. Source of truth: `https://docs.chain.link/data-streams/rwa-streams/24-7-us-equities.md`, `https://docs.chain.link/data-streams/reference/report-schema-v11.md`, `https://docs.chain.link/data-streams/market-hours.md`. Re-fetch the page for any live fact (stream IDs, assets, verifier addresses). Plain 24/5 questions do not use this file.

## Contents

- Product routing
- Access and coverage
- 24/7 TWAP (v2)
- 24/7 for Perpetual Markets (v11)
- Risks to surface
- Safety rules for answers

## Product routing

Choose the product from the use case. Do this before any code.

| Use case | Product | Schema | Field(s) |
|---|---|---|---|
| Lending, collateral, liquidations, borrow limits | Data Feeds **24/7 Smoothed Tokenized Equity Feeds** (slow Oracle Price onchain) — hand off to `chainlink-data-feeds-skill` | n/a (`AggregatorV3Interface`) | `latestRoundData()` |
| Perpetual futures mark or index price | Data Streams **24/7 for Perpetual Markets** | v11 | `mid`, `bid`, `ask` |
| Short-duration prediction markets (e.g. up/down markets) | Data Streams **24/7 TWAP** | v2 | `price` |

- One stream per asset per product. Do not build session-switching logic. Do not switch streams by session or by `marketStatus`.
- The docs describe exactly two Data Streams products in this family (TWAP, Perpetual Markets). One docs page also says "Perpetual Markets and Lending streams"; encode the conservative reading: lending is served by the Data Feeds 24/7 feeds, and do not tell users a separate Data Streams "Lending" stream exists.
- A lending user who still wants to consume Streams directly can read `lastTradedPrice` (the slow price) from a v11 stream, with every caveat below, but the documented lending path is the Data Feeds product.

## Access and coverage

- Early access only. Request access via `chainlink_data_feeds@smartcontract.com`.
- Coverage depends on liquid off-hours perpetual futures markets, so not every US equity is covered. Each asset is reviewed individually before launch. Review lowers risk but does not remove it; covered assets can still be manipulated or dislocated off-hours. Uncovered assets stay on the 24/5 streams.
- Never list covered assets, stream IDs, or feed IDs from memory. Point to the docs streams table on the 24/7 page and the Data Streams Discovery endpoint (`https://docs.chain.link/data-streams/reference/data-streams-api/discovery-endpoint`), which also returns hidden streams the user's key is entitled to.
- Data outage support: `data_support@chain.link`.

## 24/7 TWAP (v2)

- One continuous TWAP price per asset, in the `price` field of a v2 report. SDK field naming for v2 can differ (see `report-schemas.md`); decode with the official SDK and read the single price field.
- A TWAP stream does NOT carry v11 fields. Never read `mid`, `bid`, `ask`, `lastTradedPrice`, or `marketStatus` from a TWAP stream, and never write TWAP code that references them.
- Window calculation: fetch `https://docs.chain.link/data-streams/concepts/twap-streams.md`; do not invent window lengths.

## 24/7 for Perpetual Markets (v11)

Uses the v11 schema, so an existing v11 decoder works unchanged. The v11 meaning of `lastTradedPrice` differs from 24/5 (see below).

### Session and freshness

- Always read `marketStatus` to know the session. Never infer the session from `observationsTimestamp`, `lastSeenTimestampNs`, or any timestamp.
- `marketStatus = 0` (Unknown): treat the price as unavailable. A contract must not use that report's price.
- `observationsTimestamp` judges report freshness. `lastSeenTimestampNs` judges freshness of `mid` ONLY. Never use it for `bid`, `ask`, `bidVolume`, `askVolume`, or `lastTradedPrice`. It is not guaranteed monotonic; one non-monotonic step is not by itself a concern, persistent behavior across consecutive reports is.
- A flat `lastTradedPrice` while `mid` moves is worth an alert, and a slow price that is not moving is not proof it is current.
- Staleness thresholds are the application's own choice; do not state numeric thresholds as if the docs prescribe them.

| `marketStatus` | Status | Hours (ET) | Price source |
|---|---|---|---|
| 0 | Unknown | n/a | None. Treat as unavailable |
| 1 | Pre-market | 4:00am–9:30am Mon–Fri | Extended hours session |
| 2 | Regular | 9:30am–4:00pm Mon–Fri | Regular hours session |
| 3 | Post-market | 4:00pm–8:00pm Mon–Fri | Extended hours session |
| 4 | Overnight | 8:00pm–4:00am, Sunday evening–Friday morning | Overnight session |
| 5 | Closed | 8:00pm Fri–8:00pm Sun, plus US market holidays | Off-hours perpetual futures composite |

- On 24/7 streams `marketStatus = 5` does NOT mean prices stop; the stream keeps publishing the off-hours composite. A closed-market check is `marketStatus == 5`, and it includes US market holidays.
- Trading halts are not flagged in `marketStatus`. During a halt, `marketStatus` shows the active session while `lastSeenTimestampNs` stops advancing. Use an authoritative exchange holiday calendar and halt notices alongside `marketStatus`.

### Fast price and slow price

Both are published in every report, in every session.

| Price | Fields | Behavior |
|---|---|---|
| Fast price | `mid`, `bid`, `ask` | Tracks the market as closely as inputs allow. No continuous smoothing and no cap on how fast it moves (session transitions are still blended, below). |
| Slow price (Oracle Price) | `lastTradedPrice` | Smoothed; referenced to the last equity close in off-hours; follows sustained moves gradually. |

| Field | Regular and extended | Overnight | Closed (off-hours) | Session transitions |
|---|---|---|---|---|
| `mid`, `bid`, `ask` | Active session values | Overnight session values | Off-hours composite (`mid`, `bid`, `ask` all published) | Smoothed blend |
| `lastTradedPrice` | Equals `mid` | EMA of overnight `mid` | Smoothed off-hours price, referenced to the last equity close, follows the fast price gradually; large moves can take hours to register | Smoothed blend |
| `bidVolume` / `askVolume` | Active session | Overnight session | May be 0 | Active session |

- Off-hours fast price: a USD composite of quotes from several perpetual futures venues. Venues that stop updating drop out. If no venue has fresh data, no new price is computed; the stream does not fabricate one. It is NOT derived from spot trading in the underlying shares and NOT from secondary-market prices of tokenized equities. Never describe it as an exchange quote. Do not name venues or give weights.
- Exception to smoothing: pre-market into regular hours (9:30am ET) passes straight through, so the slow price can step at the open.
- The slow price is intentionally lagged. Never use it to hedge or execute against a venue.
- `bidVolume` / `askVolume`: may be 0 when closed; never rely on them off-hours; never treat them as a liquidity proxy (they come from one order book at a time).

### Which field to use

| Use | Field | Note |
|---|---|---|
| Lending, liquidations, borrow limits | `lastTradedPrice` (slow price) | Documented lending path is the Data Feeds 24/7 feed; say so |
| Perp mark or index price | `mid`, `bid`, `ask` | Not `lastTradedPrice` |
| Monitoring | Both | The gap shows divergence from the slow price |

### 24/5 vs 24/7 `lastTradedPrice`

- On 24/5 US Equities streams `lastTradedPrice` is deprecated and must not be used as a production input. Do not recommend it for 24/5.
- On 24/7 v11 Perpetual Markets streams it carries the Oracle Price and is fully supported; decoders must not discard it.
- 24/7 v11 streams carry no corporate-action fields (multiplier/activation fields exist on the v10 tokenized-asset schema). Track corporate actions offchain.

### Consuming

Use the official SDK to fetch or stream and decode (see `rest-sdk.md`, `websocket-sdk.md`, `onchain-verification.md`). Check the decoded version is v11, check `marketStatus != 0`, check `mid` freshness against the app's own threshold, then read the field for the use case. Keep `full_report` for verification; verify onchain before any value-securing use.

## Risks to surface

Whenever a 24/7 field is recommended, state the risks that apply to it (lead with the first for `lastTradedPrice`):

1. Slow-price lag: large weekend moves can take hours to register; liquidations after a sustained move can come later than against a live price. Size LTV, thresholds, and caps for a lagging price.
2. Perp basis to the underlying shares (funding rates, venue contract design).
3. Off-hours manipulation risk; smoothing reduces it but does not prevent it.
4. Thin weekend volume; less capital moves the price, and still less if venues drop out (fewer contributing venues).
5. Perp data currently comes from a single data provider; an outage or bad data there is not covered by multi-venue checks.
6. If the equity close cannot be determined, there is no slow price for that off-hours period; worst case, a whole weekend.
7. If inputs are missing too long, the slow price stops and needs a recovery period after inputs return.
8. At the reopen, both prices close the weekend gap over a short window; positions degraded over the weekend can become liquidatable around the reopen. Consider tighter limits on new positions around the Sunday 8:00pm ET open.
9. At 9:30am ET the pre-market to regular move passes straight through; the slow price can step at the open.
10. No corporate-action adjustment: splits, reverse splits, special dividends, and symbol changes can move the price sharply at the reopen.

Also: define behavior for "no fresh price" before launch (pause new borrowing, hold last valid price within bounds, or both), and treat the off-hours price as an estimate of where the equity would trade, not a traded price.

## Safety rules for answers

- Never claim off-hours prices are exchange quotes or spot prices.
- Never invent asset lists, feed IDs, stream IDs, heartbeat values, deviation values, EMA windows, or venue names/weights. Point to the docs table, Discovery endpoint, and the feed page.
- Never say 24/7 removes the need to protect weekend markets; it removes session-switching code, not market risk.
- Do not state launch status beyond "early access".
