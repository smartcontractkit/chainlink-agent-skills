---
name: chainlink-data-feeds-skill
description: "Help developers integrate Chainlink Data Feeds into smart contracts and applications. Use for price feed integration, feed address lookup, consumer contract generation, multi-chain data feeds (EVM, Solana, Aptos, StarkNet, Tron), MVR bundle feeds, SVR/OEV feeds, feed monitoring, historical data, L2 sequencer checks, rates/volatility feeds, SmartData/RWA feeds, or debugging feed integrations. Trigger on any mention of Chainlink price feeds, oracle data, AggregatorV3Interface, latestRoundData, or feed addresses."
license: MIT
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  version: "0.0.6"
---

# Chainlink Data Feeds Skill

## Routing

| Request / triggers | Load |
|---|---|
| EVM read, consumer contract, off-chain read, address lookup/debugging | [price feeds](references/reading-price-feeds.md) |
| Working Foundry/Data Feeds project | Load the [starter README](templates/starter-kit/README.md) and every listed file; reply with their contents or a tailored derivative, never a local/absolute path alone. Preserve layout and include install/test/deploy commands, Sepolia ETH/USD or verified named-network lookup, unaudited/not-for-production warning, and L2 sequencer protection. |
| Multiple-Variable Response, multi-variable feed, `BundleAggregatorProxy` | [MVR](references/mvr-feeds.md) |
| Smart Value Recapture, OEV/MEV recapture, searcher onboarding | [SVR](references/svr-feeds.md) |
| Feed categories/selection, SmartData/RWA, rates/volatility, tokenized equity | [types](references/feed-types.md) |
| Solana, StarkNet, Aptos, Tron, Move, Cairo, Anchor, TronBox | [multi-chain](references/multi-chain.md) |
| L2 sequencer, deprecation, monitoring, registry, responsibilities, data sources, self-managed feeds | [operations](references/feed-operations.md) |
| Live addresses/schedules/parameters; interface/signature mismatch, proxy/aggregator source, GitHub example | [official sources](references/official-sources.md) |

Do not load references speculatively. Default EVM requests to price feeds; ask only when routing depends on missing context.
Hand CCIP/bridge, VRF, Automation, and Functions requests to their owning products exclusively, giving each product's standard next steps from general knowledge; emit no Data Feeds or weaker substitute and never improvise live constants.

## Safety rules

1. Validate `updatedAt` against the feed heartbeat; reject incomplete or stale rounds.
2. Call `decimals()` at runtime; never hardcode decimals.
3. On L2, check sequencer uptime, reject `answer != 0`, and enforce the 3600-second recovery grace period.
4. Never use deprecated `answeredInRound` for freshness or other logic.
5. Warn that examples are unaudited and not for production; mainnet integrators own audits, dependencies, monitoring, circuit breakers, contingencies, and user risk disclosure.

## Freshness policy

1. Use embedded references first.
2. Fetch the smallest official URL for a live gap.
3. If insufficient, use Context7.
4. Never improvise live facts or patterns.
5. If unverified, say so and name the URL.

## Invariants

- Read EVM proxies, not underlying aggregators.
- Preserve the starter kit layout/README invariants; replace illustrations and tune heartbeat/mock values.
- Use `AggregatorV3Interface` for single values, `IBundleAggregatorProxy` for MVR, and `AggregatorV2V3Interface` for sequencer uptime.
- Verify unknown addresses, feed IDs, schemas, parameters, and support.
