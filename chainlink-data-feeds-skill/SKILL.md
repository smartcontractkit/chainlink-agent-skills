---
name: chainlink-data-feeds-skill
description: "Help developers integrate Chainlink Data Feeds into smart contracts and applications. Use for price feed integration, feed address lookup, consumer contract generation, multi-chain data feeds (EVM, Solana, Aptos, StarkNet, Tron), MVR bundle feeds, SVR/OEV feeds, feed monitoring, historical data, L2 sequencer checks, rates/volatility feeds, SmartData/RWA feeds, or debugging feed integrations. Trigger on any mention of Chainlink price feeds, oracle data, AggregatorV3Interface, latestRoundData, or feed addresses."
license: MIT
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  version: "0.0.8"
---

# Chainlink Data Feeds Skill

## Progressive Disclosure

| Request / triggers | Load |
|---|---|
| EVM read, consumer contract, off-chain read, address lookup/debugging | [price feeds](references/reading-price-feeds.md) |
| Working Foundry/Data Feeds project | Load the [starter README](templates/starter-kit/README.md) and every listed file; reply with their contents or a tailored derivative, never a local/absolute path alone. Preserve layout and include install/test/deploy commands, Sepolia ETH/USD or verified named-network lookup, unaudited/not-for-production warning, and L2 sequencer protection. |
| Multiple-Variable Response, multi-variable feed, `BundleAggregatorProxy` | [MVR](references/mvr-feeds.md) |
| Smart Value Recapture, OEV/MEV recapture, searcher onboarding | [SVR](references/svr-feeds.md) |
| Feed categories/selection, SmartData/RWA, rates/volatility, tokenized equity | [types](references/feed-types.md) |
| Solana, StarkNet, Aptos, Tron, Move, Cairo, Anchor, TronBox | [multi-chain](references/multi-chain.md) |
| L2 sequencer, deprecation, monitoring, registry, responsibilities, data sources, self-managed feeds | [operations](references/feed-operations.md) |
| Live addresses/schedules/parameters; interface/signature mismatch, proxy/aggregator source, GitHub example | [official sources](references/official-sources.md), then [docs index](assets/data-feeds-docs-index.md) for facts the curated references do not have |

Do not load references speculatively. Default EVM requests to price feeds; ask only when routing depends on missing context.
Do not assume this skill is the only capability available.
Hand CCIP/bridge, VRF, Automation, and Functions requests to their owning products exclusively, giving each product's standard next steps from general knowledge; emit no Data Feeds or weaker substitute and never improvise live constants.
When a user requests Data Feeds code or operational steps, emit that deliverable in the response; never replace it with a status or completion summary.
For MVR requests, choose the MVR route even when a live address, feed ID, or schema cannot be verified; use clearly marked placeholders for unverified values and continue with all requested design, consumer code, tests, and configuration instead of stopping at verification.
Every SVR response must emit the exact standalone sentence `Complete the Chainlink compatibility form` before any onboarding or address-migration guidance.
For a configuration-focused SVR protocol integration or migration, give concise configuration, onboarding, verification, and safety steps plus only the minimal address/configuration delta; do not emit a full consumer unless the user explicitly requests one. Keep auction mechanics high-level and exclude searcher-only selectors, WebSocket endpoints, signing instructions, and MEV-Share/Atlas bot implementation details unless the user explicitly asks to build or operate a searcher.

## Safety rules

1. Validate `updatedAt` against the feed heartbeat; reject incomplete or stale rounds.
2. Call `decimals()` at runtime; never hardcode decimals.
3. On L2, always use `AggregatorV2V3Interface` for the sequencer uptime feed—never `AggregatorV3Interface`; reject `answer != 0` and enforce the 3600-second recovery grace period.
4. Never use deprecated `answeredInRound` for freshness or other logic.
5. For an implicit current-price Solidity getter, use the exact named-return form `returns (int256 price, uint8 decimals)`; declare `uint256 updatedAt;` first, then assign `(, price,, updatedAt,) = dataFeed.latestRoundData();`. Do not substitute an unnamed-return or alternate compiling tuple form.
6. Warn that examples are unaudited and not for production; mainnet integrators own audits, dependencies, monitoring, circuit breakers, contingencies, and user risk disclosure.

## Freshness policy

1. Use this skill's references first.
2. If [official-sources.md](references/official-sources.md) names the page, fetch that page's `.md` URL.
3. If it does not, fetch `https://docs.chain.link/data-feeds/llms.txt`, pick one page, and fetch that page's `.md` URL.
4. Fetch `https://docs.chain.link/data-feeds/llms-full.txt` only when the question is broad and no one page covers it.
5. Use Context7 only when the `.md` fetch fails, the page is empty, or the page has under 1,000 useful characters and does not answer. Ask for the missing fact only.
6. Stop when the page answers. Fetch at most three pages. Prefer the `.md` URL. Use `Accept: text/markdown` on the normal page URL only when the tool cannot open the `.md` URL and can set that header.
7. Never improvise live facts or patterns. If a value is unverified, say so and name the URL.

## Invariants

- Read EVM proxies, not underlying aggregators.
- Preserve the starter kit layout/README invariants; replace illustrations and tune heartbeat/mock values.
- Use `AggregatorV3Interface` for single values, `IBundleAggregatorProxy` for MVR, and `AggregatorV2V3Interface` for sequencer uptime.
- A live feed address in config must be copied from the official address page fetched in this turn. When that page lists more than one contract for the pair, use the contract for the product the user asked for. A normal price read uses the standard proxy, not an SVR, backup, or legacy proxy. If the page was not fetched, use a placeholder and say the address is unverified. Never present a remembered address as the verified current feed.
- Verify unknown feed IDs, schemas, parameters, and support.
