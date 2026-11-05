# 24/7 Smoothed Tokenized Equity Feeds

Scope: Chainlink 24/7 Smoothed Tokenized Equity Feeds only. Source of truth: `https://docs.chain.link/data-feeds/tokenized-equity-feeds/24-7.md`; the matching streams page is `https://docs.chain.link/data-streams/rwa-streams/24-7-us-equities.md`. Plain 24/5 tokenized equity questions do not use this file (see [feed-types.md](feed-types.md)).

## Contents

- Product routing
- What the feed publishes
- Reading and staleness
- Risk guidance
- Reopen and corporate actions
- Access and support

## Product routing

| Use case | Product |
|---|---|
| Lending, collateral, liquidations, borrow limits | **24/7 Smoothed Tokenized Equity Feeds** (this file): slow Oracle Price onchain |
| Perpetual futures mark or index price | Data Streams "24/7 for Perpetual Markets" (v11) — hand off to `chainlink-data-streams-skill` |
| Short-duration prediction markets (e.g. up/down markets) | Data Streams "24/7 TWAP" (v2) — hand off to `chainlink-data-streams-skill` |

One stream or feed per asset per product. Do not build session-switching logic and do not switch products by session or by `marketStatus`.

## What the feed publishes

- Each feed publishes the **Oracle Price** (the slow price built for collateral valuation) multiplied by the asset issuer's multiplier. The answer is the value of the token, not the raw equity price. Multiplier sourcing is unchanged from 24/5 tokenized equity feeds (see the Asset Issuer Catalog `https://docs.chain.link/data-feeds/tokenized-equity-feeds/providers.md`).
- The Oracle Price is the same source as `lastTradedPrice` on the 24/7 v11 streams: unsmoothed active-session price in regular and extended hours; EMA of the overnight price overnight; a smoothed price following a perpetual-futures composite in off-hours (8:00pm Fri–8:00pm Sun ET plus US market holidays), referenced to the last equity close; short smoothed blend at session transitions, except pre-market into regular hours, where it steps at 9:30am ET.
- Off-hours prices come from perpetual futures, not from spot trading in the shares or from secondary-market prices of the tokens. Never describe them as exchange quotes.
- Not every tokenized equity has a 24/7 feed: each asset is reviewed individually, and the asset issuer must support it. Never list assets, feed addresses, or heartbeat/deviation values from memory. Use the feed table on the docs page and the address page (`https://docs.chain.link/data-feeds/price-feeds/addresses.md`), and follow the address rules in SKILL.md.

## Reading and staleness

- Read it like any Data Feed: `AggregatorV3Interface.latestRoundData()` and `decimals()` (decimals at runtime).
- Updates onchain when the price moves beyond the deviation threshold or the heartbeat elapses, including weekends. Deviation is measured on the smoothed Oracle Price, not the live market, so long stretches without updates while the market moves are expected. Do not state heartbeat or deviation numbers; point to the feed page.
- No market-status or session flag onchain. US market holidays are priced as off-hours and are not flagged; tell integrators to use an authoritative exchange holiday calendar.
- `updatedAt` is the time of the last onchain update, not when inputs were last observed.
- Staleness: compare `updatedAt` with the feed's heartbeat; a missed heartbeat means stale. A quiet healthy weekend and a stopped feed look similar onchain until the heartbeat is missed, so do not read "no update" as "healthy" or as "stopped".
- "How do I know the market is closed?": there is no onchain flag. Use a holiday/session calendar. For finer signals, subscribe to the matching 24/7 US equities stream and read `marketStatus` (`5` = closed, which includes US holidays; `0` = unavailable) and `lastSeenTimestampNs` (freshness of `mid` only) — hand the streams detail to `chainlink-data-streams-skill`.

```solidity
// Staleness only; heartbeat comes from the feed page for this exact feed, never a guess.
(, int256 answer,, uint256 updatedAt,) = feed.latestRoundData();
require(answer > 0, "invalid answer");
require(block.timestamp - updatedAt <= HEARTBEAT_FROM_FEED_PAGE, "stale: heartbeat missed");
```

## Risk guidance

State the relevant risks whenever recommending this feed:

- Slow price, delayed liquidations: the Oracle Price follows large moves over time (a large weekend move can take hours to be fully reflected); liquidations after a sustained move can come later than against a live price and arbitrage can appear. Do not size positions, LTVs, liquidation thresholds, close factors, liquidation bonuses, or supply caps as if the feed were real time; test against historical weekend moves and earnings gaps.
- Consider tighter limits on new borrowing during off-hours. Set supply caps with the off-hours market in mind.
- Off-hours prices derive from perpetual futures: basis to the shares (funding rates, venue contract design), thin weekend volume, manipulation risk that smoothing reduces but does not prevent. Monitor against independent references off-hours.
- The feed can stop updating: perpetual-futures data currently comes from a single data provider (an outage means no new off-hours price, and after inputs return the Oracle Price needs a recovery period); if the Friday equity close cannot be determined, there is no Oracle Price for that off-hours period, worst case a whole weekend. The last onchain answer stands.
- Define protocol behavior for a full weekend without updates, e.g. pause new borrowing and cap liquidations.
- Never tell integrators they no longer need to pause or protect weekend markets. The honest answer to "can I stop pausing on weekends?" is no blanket yes: 24/7 lets risk build in view instead of all at once at the reopen, but the integrator must define weekend behavior per the docs (parameters sized for a lagging price, tighter off-hours limits, full-weekend-outage behavior).

## Reopen and corporate actions

- Reopen: the remaining weekend gap closes over a short window, much smaller than a 24/5 single jump, but positions degraded over the weekend can become liquidatable around the reopen. Watch positions near their liquidation threshold ahead of the Sunday 8:00pm ET open.
- Corporate actions: the existing pause workflow for tokenized equity feeds is unchanged. Pauses and unpauses happen while the equity market is open, and the unpause check uses the regular-hours equity price, never the off-hours price. A corporate action over a weekend without a pause (split, large special dividend) can move the true value sharply and the Oracle Price follows slowly because it is referenced to the pre-event close. Monitor corporate action announcements for every listed asset.

## Access and support

- All developers must contact `chainlink_data_feeds@smartcontract.com` before integrating these feeds. They have different behavior and risks from both standard price feeds and 24/5 tokenized equity feeds.
- Data outage support: `data_support@chain.link` (listed on the streams 24/7 page).
- Do not state launch status beyond what the docs say.
