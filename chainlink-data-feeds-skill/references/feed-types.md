# Feed Types

## Trigger Conditions

Read this file when:
- The user asks about different types of Chainlink Data Feeds
- The user needs help choosing which feed type to use
- The user asks about SmartData, Proof of Reserve, NAV, AUM, or RWA feeds
- The user asks about rate or volatility feeds (Bitcoin Interest Rate, ETH Staking APR, Realized Volatility)
- The user asks about tokenized equity feeds or Ondo Finance feeds

## Feed Type Overview

| Feed Type | Purpose | Interface |
|-----------|---------|-----------|
| **Price Feeds** | Aggregated decentralized asset prices (crypto, forex, commodities, equities) | AggregatorV3Interface |
| **SmartData** | RWA-focused: reserves (PoR), NAV, AUM — single-value and MVR bundle variants | AggregatorV3Interface (single) or IBundleAggregatorProxy (MVR) |
| **SVR Feeds** | Price feeds with MEV/OEV recapture for liquidation-related value | AggregatorV3Interface (same as standard, different address) |
| **Rate and Volatility** | Interest rate curves, staking APR, realized volatility benchmarks | AggregatorV3Interface |
| **L2 Sequencer Uptime** | Real-time sequencer status for circuit breakers on L2 rollups | AggregatorV2V3Interface |
| **Self-Managed** | Updates written by chain/third party, not Chainlink node operators | AggregatorV3Interface (different operational model) |

## Decision Path

1. **Reading an asset price** (ETH/USD, BTC/USD, etc.) → Use a **Price Feed**. See `reading-price-feeds.md`.
2. **Reading multiple related values in one call** (e.g., NAV + AUM + total return) → Use an **MVR Feed**. See `mvr-feeds.md`.
3. **Recapturing MEV from liquidations** → Use an **SVR Feed**. See `svr-feeds.md`.
4. **Interest rates, staking APR, or volatility** → Use a **Rate and Volatility Feed** (see below).
5. **Proof of Reserve, NAV, or AUM** → Use a **SmartData Feed** (see below).
6. **Tokenized equity pricing** → Use a **Tokenized Equity Feed** (see below).
7. **L2 sequencer health** → Use the **L2 Sequencer Uptime Feed**. See `feed-operations.md`.

## SmartData Feeds (RWA)

SmartData provides onchain data for tokenized real-world assets. It includes two variants:

### Single-Value SmartData

Read like standard Price Feeds via AggregatorV3Interface and `latestRoundData()`. Feed categories:
- **Proof of Reserve (PoR)**: confirms reserve backing for asset-backed tokens. Answers may be in non-price units (e.g., ounces, token counts).
- **NAVLink**: Net Asset Value for funds and structured products.
- **SmartAUM**: Assets Under Management.

Sourcing models for PoR:
- **Offchain**: data from custodian, fund administrator, auditor, or asset manager via external adapter.
- **Cross-chain**: reads reserves from the source chain where assets are held.
- **Self-reported**: issuer provides reserve data via API. Higher risk — issuers could manipulate reported reserves by adding addresses they do not control.

### MVR SmartData

Multi-variable response feeds return multiple fields per update. See `mvr-feeds.md` for integration.

### Addresses

SmartData feed addresses: `https://docs.chain.link/data-feeds/smartdata/addresses`

Filter using "Show Multiple-Variable Response (MVR) feeds" checkbox for MVR variants.

## Rate and Volatility Feeds

Read rate and volatility feeds exactly like standard Price Feeds — only the feed address differs.

### Bitcoin Interest Rate Curve

- Base rates for lending/borrowing risk, derivatives valuation, and swaps.
- Normalized methodology with daily rates.
- Sources: OTC lending desks, DeFi lending pools, perpetual futures markets.

### ETH Staking APR

- Annualized trust-minimized APR for Ethereum validator staking.
- Computed offchain at epoch level across data providers.
- Available in 30-day and 90-day rolling windows.
- Updates at least once per day.

### Realized Volatility

- Percent of asset price movement over specified intervals (24h, 7d, 30d).
- Not implied volatility — this measures actual historical price movement.
- Providers sample prices every 10 minutes.
- Onchain updates when heartbeat or deviation threshold is met.

### Addresses

Rate and volatility feed addresses: `https://docs.chain.link/data-feeds/rates-feeds/addresses`

## Tokenized Equity Feeds

Continuous 24/5 pricing for tokenized representations of US equities and ETFs. These feeds differ significantly from standard crypto price feeds.

### Key characteristics

- **Continuous pricing** across US market sessions: pre-market (04:00-09:30 ET), regular (09:30-16:00), post-market (16:00-20:00), overnight (20:00-04:00).
- **Calculated value**: returns a primary market token value based on issuer methodology, not a simple market price. May include total return adjustments (dividends, corporate actions).
- **Session-aware smoothing**: dampens brief spikes during illiquid sessions but can introduce tracking lag during rapid moves.
- **Variable data quality**: regular session has highest coverage (multiple providers), extended/overnight is limited.
- **Weekend**: no traditional trading — data may be stale.

### Risks

- Limited provider coverage during extended/overnight sessions.
- Price jumps at session transitions.
- Corporate actions trigger pauses in the feed.
- Halts are not explicitly flagged.

### Best practices

- Monitor staleness via last update timestamp.
- Configure protocol risk parameters to match feed behavior.
- Consider restricting high-risk operations (large liquidations, new positions) during extended/overnight sessions.
- Contact Chainlink Labs (`datafeeds@chain.link`) before integrating tokenized equity feeds.

### Ondo Finance (Total Return Value)

Ondo GM feeds report Total Return Value: `Token Price = Underlying Equity Market Price * sValue`

- sValue comes from Ondo's SyntheticSharesOracle (reflects dividend reinvestment and corporate actions).
- Small sValue changes (<=1% per 24h) apply automatically.
- Large sValue changes (>1%) require a scheduled pause and manual confirmation.
- During corporate action pauses, the feed freezes at the last known good token price until unpaused.
- Minimum pause duration enforced (>=10 minutes).

## Freshness Rules

1. Feed type definitions and categories are stable — use this file directly.
2. Specific feed addresses, parameters, and availability by network change — fetch the relevant address page from `official-sources.md`.
3. Tokenized equity feed provider details and issuer-specific behaviors may change — fetch the provider page when the user needs current operational specifics.

## Triggering Tests

- "What types of data feeds does Chainlink offer?"
- "I need a Proof of Reserve feed for my RWA token"
- "How do I read the Bitcoin interest rate curve from Chainlink?"
- "What's the difference between SmartData and a regular price feed?"

## Functional Tests

1. Response correctly maps the user's use case to the right feed type.
2. SmartData guidance distinguishes between single-value and MVR variants.
3. Rate/Volatility guidance says to read like a standard price feed with a different address.
4. Tokenized equity response mentions the contact requirement and session-specific risks.

## Eval Checks

1. Decision path correctly routes: asset prices → Price Feed, multiple values → MVR, reserves → SmartData PoR.
2. PoR guidance mentions risk levels for self-reported vs. audited sourcing.
3. Tokenized equity response includes pausing/corporate action behavior.
4. Response does not conflate MVR with single-value SmartData.
5. Rate/Volatility response does not introduce a special interface — it uses AggregatorV3Interface.

## A/B Prompt Pack

- "What kind of Chainlink feed do I need for my lending protocol that holds tokenized treasury bills?"
- "I want to use Chainlink's ETH staking APR feed in my yield optimizer"
- "How do I integrate Ondo tokenized equity feeds?"
- "What's a SmartData feed and how is it different from a price feed?"
