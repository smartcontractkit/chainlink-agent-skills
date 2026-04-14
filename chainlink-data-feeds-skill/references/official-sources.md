# Official Sources

Use this file only when the answer depends on live Data Feeds facts that the other reference files do not contain — feed addresses for a specific chain, current deprecation schedules, or specific network parameters.

## Freshness Policy

1. Do not hardcode live Data Feeds facts such as specific feed addresses, proxy addresses, deprecation dates, or network-specific Flags contract addresses.
2. Re-check official sources whenever the request depends on a specific feed address, current deprecation status, or network-specific configuration.
3. Distinguish between conceptual guidance (stable — use reference files directly) and live configuration data (changes — check sources below).
4. If a live source conflicts with cached assumptions, prefer the live source and say so.

## Source Map

### Chainlink Data Feeds Docs

URL:
- `https://docs.chain.link/data-feeds`

Use for:
- concepts and architecture
- integration tutorials and patterns
- interface documentation (AggregatorV3Interface, IBundleAggregatorProxy)
- feed type explanations (Price, SmartData, MVR, SVR, Rates)
- developer responsibilities and best practices

Do not use as the primary source for:
- specific feed addresses (use the address pages below)
- current deprecation schedules (use the deprecation page)

### Feed Address Pages

URLs:
- Price Feeds: `https://docs.chain.link/data-feeds/price-feeds/addresses`
- SmartData / MVR Feeds: `https://docs.chain.link/data-feeds/smartdata/addresses`
- Rate and Volatility Feeds: `https://docs.chain.link/data-feeds/rates-feeds/addresses`
- US Government Macroeconomic: `https://docs.chain.link/data-feeds/us-government-macroeconomic/addresses`

Use for:
- looking up the correct proxy address for a specific pair on a specific network
- confirming feed availability on a given chain
- checking feed parameters (heartbeat, deviation threshold, decimals)

### Feed Deprecation Schedule

URL:
- `https://docs.chain.link/data-feeds/deprecating-feeds`

Use for:
- checking if a specific feed is scheduled for deprecation
- finding deprecation dates, affected networks, and replacement guidance
- advising users whose contracts reference potentially deprecated feeds

### Contract Registry

URL:
- `https://docs.chain.link/data-feeds/contract-registry`

Use for:
- finding the IFlags contract address for a specific network
- verifying whether a feed proxy address is officially operated by Chainlink

### GitHub Repositories

URLs:
- Example contracts: `https://github.com/smartcontractkit/documentation/tree/main/public/samples/DataFeeds`
- Contract source (v0.6 legacy): `https://github.com/smartcontractkit/chainlink-evm/tree/develop/contracts/src/v0.6/data-feeds`
- Contract source (v0.8 MVR): `https://github.com/smartcontractkit/chainlink-evm/tree/develop/contracts/src/v0.8/data-feeds`

Use for:
- inspecting actual contract implementations when debugging interface mismatches
- verifying function signatures against deployed code
- finding working example contracts as reference

Do not use as the primary source for:
- integration guidance (use the reference files instead)
- feed addresses or configuration (use the address pages)

### Full-Text Documentation Dump

URL:
- `https://docs.chain.link/data-feeds/llms-full.txt`

Use only as a last resort when:
- no specific doc page covers the topic
- you need broad coverage across multiple Data Feeds topics
- other sources failed to load

## Practical Selection Rules

1. For "what is the feed address for X on Y" → fetch the matching address page.
2. For "is feed X being deprecated" → fetch the deprecation page.
3. For "how do I read a price feed" → use `reading-price-feeds.md` directly, no fetch needed.
4. For "what interface does MVR use" → use `mvr-feeds.md` directly, no fetch needed.
5. For "what's the IFlags address on Arbitrum" → fetch the contract registry page.
6. For everything else → try to answer from reference files first. Fetch only if a specific detail is missing.
