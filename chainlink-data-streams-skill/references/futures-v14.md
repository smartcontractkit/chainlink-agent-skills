# Chainlink Data Streams Futures (v14)

Scope: Chainlink Data Streams **Futures** streams, which publish exchange-traded futures contract prices on the **v14** report schema. Sources of truth: `https://docs.chain.link/data-streams/rwa-streams/futures.md`, `https://docs.chain.link/data-streams/reference/report-schema-v14.md`, `https://docs.chain.link/data-streams/market-hours.md` (section "Futures (v14)"). Re-fetch the Futures page for any live fact (available streams, stream IDs, coverage). Field list and per-language SDK names: [report-schemas.md](report-schemas.md) (v14).

**Not the 24/7 perpetual-futures product.** The 24/7 US equities streams use *perpetual* futures markets only as an off-hours price input and publish on v11 (and v2); see [24-7-us-equities.md](24-7-us-equities.md). Futures (v14) has its own fields, its own `marketStatus` mapping, and no off-hours composite. Never apply one product's fields, mapping, or behavior to the other.

## Contents

- What the streams are
- Access and coverage
- `marketStatus` and trading hours
- Contract expiry and rolls
- Which field to use
- Freshness and staleness
- Risks to surface
- Consuming and safety rules

## What the streams are

- Price data for exchange-traded futures contracts, so protocols can build markets around futures price exposure. The docs mark the product **beta** and still **in development**; guidance on later feeds is "subject to change". State no launch status beyond that.
- Expiring contracts are served by **generic feeds** that track the active contract, so there is no feed per expiry. Each instrument currently has **one front feed** (nearest unexpired eligible contract). Second and third feeds (next eligible contracts) are **planned, not available**: never write code or advice that assumes they exist, and never confirm they are live. The schema overview says three generic feeds per instrument; the Futures page says only the front feed is available now. Follow the Futures page.
- Each feed is sourced from a **single** institutional data provider with no cross-validation and no fallback.
- Contract specifications (size, tick size, quotation units) are outside these streams; the integrator sources them independently. Feed names may change as coverage expands.
- The integrator is responsible for choosing the feed and checking that its behavior matches their expectations (Developer Responsibilities).

## Access and coverage

- Beta access is by contacting `chainlink_data_feeds@smartcontract.com` (also the data-outage contact on the docs page).
- Coverage per the docs page when checked: US Oil, UK Oil, Natural Gas; more commodities planned. Treat that as a dated docs statement: the docs "Available Streams" table is the authoritative list and carries a risk category per stream. Never list stream IDs, feed IDs, contract months, or expiry dates from memory. Point to that table and to the Discovery endpoint (`https://docs.chain.link/data-streams/reference/data-streams-api/discovery-endpoint`). Read the tracked contract from each report's `contractMonth` and `expiryTime`.
- No heartbeat, deviation, or numeric staleness thresholds are documented for these streams; never state any.

## `marketStatus` and trading hours

Always read `marketStatus` from each report. Never infer open/closed from `observationsTimestamp`, `lastSeenTimestampNs`, or any timestamp, from the local clock, or from an assumed session schedule.

| `marketStatus` | Status | Rule |
|---|---|---|
| 0 | Unknown | Status cannot be determined. Treat as **not open** and the price as unavailable for market-gated logic |
| 1 | Closed | Market is closed |
| 2 | Open | Market is open |

- This is the v14 mapping from Market Hours. It is **not** the v11 mapping (v11 uses `5` for Closed and `1`–`4` for sessions) and not the 24/7 mapping. Do not read `5` as Closed on a v14 feed. Treat any value other than `2` as not open.
- The v8 Forex/Precious Metals/Commodities table uses the same three numbers, but those are fixed-schedule streams (including the WTI Synthetic Spot commodity stream). Futures hours are not that schedule.
- Hours follow the **underlying contract's** trading hours (the docs also say "underlying market"), with a **scheduled break each trading day**. Holidays and early closes follow the underlying market's calendar. The docs give **no** open/close or break times for futures; state none. The docs also do not say which value is reported during the daily break: only `2` means open.
- Schedules can change, which is why `marketStatus` per report beats any schedule. The v14 schema page says the mapping "varies by feed"; the Futures and Market Hours pages say it is the same for every v14 futures feed. Use 0/1/2 as documented, and confirm against the Market Hours page (`#futures-v14`) before relying on it.

## Contract expiry and rolls

- The front feed tracks the nearest unexpired eligible contract. The roll is triggered by the front contract's **expiration** (`expiryTime`), so different instruments roll on different dates; there is no single roll day. The switch happens **after the underlying market's session closes** on the expiration date. State no clock time for it and do not schedule logic around one; read `expiryTime`, `contractMonth` and `marketStatus` from the report.
- At the roll the feed **re-maps** to the next eligible contract, which can trade at a different price. Expect a **price discontinuity** at every roll. It is not a data error. Feeds are **not back-adjusted** into a continuous series.
- Until expiration the front feed keeps tracking the expiring contract, even in its final days when liquidity has typically moved to the next contract. Thin liquidity there can increase volatility and can trigger liquidations or other price-sensitive logic.
- Detect a roll by comparing `contractMonth` and `expiryTime` between consecutive reports for the same feed. Use `expiryTime` and `firstDayOfNotice` as reported (holiday-adjusted dates are reflected in the data). Do not hardcode which contract a feed tracks, month spacing, or roll dates. Spacing between feeds varies by instrument (consecutive months for the energy instruments).
- Documented options for margining/liquidation on the raw front feed: (1) accept the step as economically correct, (2) roll early to a later feed **when one is released** (none today), (3) build an adjusted continuous series off-chain from the raw generic feeds. The docs impose no roll strategy.
- For a smoothed series instead of a hard cutover use the Goldman Roll fields (below), or build your own off-chain.

## Which field to use

| Need | Field | Note |
|---|---|---|
| Is the market open | `marketStatus` | `2` open, `1` closed, `0` unknown (not open); never timestamps |
| Price, bid, ask | `midPrice`, `bidPrice`, `askPrice` | DON consensus, 18-decimal fixed point. Raw generic-feed prices step at each roll |
| Smoothed continuous price | `goldmanRollPrice`, `interpolatedGoldmanRollPrice` | See below |
| Where the Goldman window is | `currentBusinessDay` | Current business day of the month, used to determine the Goldman Roll window |
| Which contract, when it expires | `contractMonth` (1–12), `expiryTime`, `firstDayOfNotice` | Unix seconds for the two times |
| Provider staleness | `lastSeenTimestampNs` | Last provider update, nanoseconds. Freshness only, never market state |

- `goldmanRollPrice`: Goldman Roll (GSCI methodology), shifting 20% of the position to the next contract each business day over business days 5–9 of the month preceding delivery. `interpolatedGoldmanRollPrice`: the same 20% daily shift, smoothed over the course of each of those business days. Both are alternatives to the hard cutover; Chainlink publishes them alongside the raw prices. Do not invent weighting or window details beyond this.
- Prices are fixed-point integers: divide by `10^18` only for display; never use floating point for the raw values.

## Freshness and staleness

- Monitor `lastSeenTimestampNs`. A single provider means updates can stop and the price can look normal while stale. When the timestamp lags your freshness threshold, pause trading or restrict liquidations.
- The threshold is the application's choice; do not state numbers as if the docs prescribe them.
- Define the "no fresh price" and `marketStatus != 2` behavior before launch (pause, restrict, or hold last valid price within bounds).
- `lastSeenTimestampNs` is for staleness only. It must never decide whether the market is open.

## Risks to surface

1. Single-source data: one provider per feed, no cross-validation, no fallback; a data gap may not be visible from price alone.
2. Price discontinuity at every roll; no back-adjustment.
3. Front feed tracks the expiring contract into thin liquidity near expiry.
4. Only the front feed exists today; later feeds and the full-rollout guidance are planned and may change.
5. Beta / in development; names and coverage may change.
6. Contract specifications are not in the report; source independently.
7. The integrator must add monitoring and risk mitigation (Developer Responsibilities); the docs table carries a per-stream risk category to read before integrating.

## Consuming and safety rules

- Use the official SDK to fetch/stream and decode: Go `report.Decode[v14.Data]` from the `data-streams-sdk/go/v2` module (the v1 module path used in [rest-sdk.md](rest-sdk.md) has no v14 decoder), TypeScript `decodeReport(fullReport, feedId)`, Rust `ReportDataV14`. The feed ID encodes the schema version, so use the v14 decoder for Futures feeds; docs say v14 needs the latest SDK. Names per language: [report-schemas.md](report-schemas.md).
- Keep raw `full_report`, backend env credentials, and verify onchain before any value-securing use (see [SKILL.md](../SKILL.md) invariants).
- Never invent IDs, contract months, expiry/roll dates, heartbeat or deviation values, decimals other than the documented 18, asset lists beyond the docs coverage statement, trading hours, or venue names. Name no exchange as the data source.
- Never apply 24/7 perpetual-market guidance (off-hours composite, fast/slow price, `lastTradedPrice`, `marketStatus = 5`) to Futures, or Futures fields to a 24/7, 24/5, or other v11 stream.
