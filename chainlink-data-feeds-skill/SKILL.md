---
name: chainlink-data-feeds-skill
description: "Help developers integrate Chainlink Data Feeds into smart contracts and applications. Use for price feed integration, feed address lookup, consumer contract generation, multi-chain data feeds (EVM, Solana, Aptos, StarkNet, Tron), MVR bundle feeds, SVR/OEV feeds, feed monitoring, historical data, L2 sequencer checks, rates/volatility feeds, SmartData/RWA feeds, or debugging feed integrations. Trigger on any mention of Chainlink price feeds, oracle data, AggregatorV3Interface, latestRoundData, or feed addresses."
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  purpose: Chainlink Data Feeds developer assistance and reference
  version: "0.0.2"
---

# Chainlink Data Feeds Skill

This skill helps developers integrate Chainlink Data Feeds into smart contracts and applications across EVM chains, Solana, Aptos, StarkNet, and Tron.

## Progressive Disclosure

1. Keep this file as the default guide.
2. Read `references/getting-started.md` only when the user is new to Data Feeds or asks for a basic tutorial.
3. Read `references/price-feeds.md` only when the user needs price feed addresses or a price feed overview.
4. Read `references/using-data-feeds.md` only when the user needs EVM integration code (Solidity, ethers.js, viem, web3.js, Python) or feed selection/historical data guidance.
5. Read `references/feed-types.md` only when the user asks about feed categories, tokenized equity feeds, SmartData/RWA, or rates/volatility feeds.
6. Read `references/mvr-feeds.md` only when the user asks about Multiple-Variable Response bundle feeds or BundleAggregatorProxy.
7. Read `references/svr-feeds.md` only when the user asks about Smart Value Recapture, OEV recapture, or searcher onboarding.
8. Read `references/multi-chain.md` only when the user targets Solana, StarkNet, Aptos, or Tron (non-EVM chains).
9. Read `references/operations.md` only when the user asks about developer responsibilities, feed deprecation, L2 sequencer feeds, self-managed feeds, contract registry, or data sources.
10. Read `references/api-reference.md` only when the user needs AggregatorV3Interface or IBundleAggregatorProxy function signatures, return types, or deprecated methods.
11. Read `references/general.md` only when no other reference file matches, or the user needs the llms-full.txt dump, ENS integration, or macroeconomic feeds.
12. Read `references/repo-documentation.md` only when the user needs working code examples from GitHub (consumer contracts, off-chain readers, SVR searcher examples, Solana examples).
13. Read `references/repo-chainlink-evm.md` only when debugging interface mismatches, verifying function signatures, or inspecting proxy/aggregator source code.
14. Do not load reference files speculatively.

## WebFetch Cascade

> **Apply to all fetches:**
> 1. **WebFetch** -> if the response has <1000 chars of useful content, it returned a shell.
> 2. **Bash curl** (fallback) -> `curl -s -L -A "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "<url>"`
> 3. **Tell the user** -> report the URL if both fail.
>
> Assess content quality after every fetch. Do not use shell responses.

## Runtime Pattern

Follow this pattern when assisting with Data Feeds queries:

1. **Determine the chain** — If the user has not specified, ask: EVM (which network?), Solana, Aptos, StarkNet, or Tron? Default to EVM if context strongly implies it. Non-EVM chains route to `references/multi-chain.md`.
2. **Match user intent** to a reference file topic (e.g., "how do I read a price feed in Solidity?" -> `using-data-feeds.md` or `price-feeds.md`)
3. **Read the matching reference file** — use the descriptions to orient. Do not fetch yet.
4. **Act immediately** — write the answer or code from knowledge and reference descriptions. Do not fetch as preparation.
5. **Iterate** — present to the user, ask them to test or compile. Then loop:
   - Error or gap blocks progress -> fetch exactly what the error names -> fix -> repeat
   - Cannot write a specific part -> mark inline (e.g. `// NEED: exact feed address for ETH/USD on Sepolia`) -> fetch that one thing -> fill in -> continue
   - No error -> done

> **Do not fetch as preparation. Fetch as resolution.** Only fetch when you can state the exact piece of information you need.

## Feed Integration Checklist

Follow these steps when **generating a consumer contract or integrating a data feed**:

1. **Determine blockchain** — Ask the user which chain they're targeting: EVM (which network?), Solana, Aptos, StarkNet, or Tron.
2. **Determine feed type** — Ask the user what type of feed they need: Price Feed, MVR Feed, SmartData, Rates, Tokenized Equity, or SVR. Default to Price Feed if unsure, and explain the options.
3. **Determine integration method** — For EVM: Solidity (on-chain), ethers.js (off-chain), or viem (off-chain). For other chains: use chain-specific patterns.
4. **Write the consumer contract/code immediately** — Generate the complete integration code from knowledge. Do not fetch first. Mark specific uncertainties inline (e.g. `// NEED: exact AggregatorV3Interface import path`, `// NEED: feed address for BTC/USD on Arbitrum`).
5. **Present and iterate** — Give the user the code. Ask them to compile/test. Then loop:
   - Compilation error -> fetch exactly what the error names -> fix -> ask user to re-test
   - Missing feed address -> fetch the address list page for that chain -> fill in -> continue
   - No error -> done
   - One fetch per gap. Never fetch speculatively.
6. **Always include validation** — Consumer contracts MUST check: answer freshness (updatedAt timestamp), answer bounds (reasonable min/max), and round completeness. Remind users of developer responsibilities.

## Feed Address Lookup Priority

When looking up feed addresses:

1. **Address list pages** — Fetch the chain-specific address page (e.g., `/data-feeds/price-feeds/addresses`).
2. **Contract registry** — Consult `/data-feeds/contract-registry` for programmatic registry lookup.
3. **Full-text doc dump** — Last resort.

## Debugging Checklist

Follow these steps when **diagnosing errors or fixing broken Data Feed integrations**:

1. **Identify the feed type and chain** — Determine which feed type (Price, MVR, SVR, Rates, SmartData) and chain (EVM network, Solana, etc.) is involved.
2. **Check Known Issues first** — Review the Known Issues section below. Many Data Feeds bugs have well-known patterns that do not require fetching.
3. **Diagnose from knowledge** — Common issues include: wrong feed address, missing decimals conversion, stale price checks, wrong interface version, L2 sequencer not checked, deprecated feeds, MVR struct field order mismatch, and answeredInRound misuse. If the error matches a known pattern, fix immediately without fetching.
4. **Fetch only if diagnosis is inconclusive** — If the error does not match a known pattern, read the matching reference file, find the specific doc page URL, and fetch it. One fetch per gap.
5. **Check repo examples if doc page is insufficient** — Consult `references/repo-documentation.md` for working implementations, or `references/repo-chainlink-evm.md` for contract source code.
6. **Propose a fix only after evidence** — Do not guess. Data Feeds have chain-specific and feed-type-specific requirements.
7. **If a fix fails, re-consult docs** — Do not iterate by guessing alternatives. Go back to step 4.

## Known Issues

### Wrong interface for L2 sequencer check
**Problem:** Using AggregatorV3Interface for the L2 Sequencer Uptime Feed.
**Fix:** Use AggregatorV2V3Interface for the sequencer feed. AggregatorV3Interface is for the price feed.

### Stale price not checked
**Problem:** Consumer calls latestRoundData() but does not validate the updatedAt timestamp. Stale prices cause incorrect liquidations or valuations.
**Fix:** Add: `require(block.timestamp - updatedAt <= STALENESS_THRESHOLD, "Stale price")`. Set the threshold based on the feed's heartbeat interval plus a buffer.

### Wrong decimals assumption
**Problem:** Assuming all feeds return 8 decimals. Different feeds use different decimal counts (e.g., ETH/USD uses 8, but some feeds use 18).
**Fix:** Always call `decimals()` on the feed. Never hardcode decimal counts.

### answeredInRound misuse
**Problem:** Using `answeredInRound` for freshness validation. This field is deprecated.
**Fix:** Use `updatedAt` for freshness checks. Remove any `answeredInRound >= roundId` checks.

### MVR struct field order mismatch
**Problem:** The Solidity struct used for `abi.decode` of MVR bundle bytes does not match the feed's documented field order/types. Decoding silently produces wrong values.
**Fix:** Match struct field order and types exactly to the feed schema on the SmartData Addresses page under "MVR Bundle Info."

### Deprecated feed still in use
**Problem:** Contract uses a feed address that has been deprecated. Monitoring ceases 2 weeks before the deprecation date.
**Fix:** Check the deprecation schedule via `references/operations.md` -> deprecating-feeds doc page. Migrate to an active feed address.

### L2 sequencer not checked on rollup
**Problem:** Consumer on Arbitrum, Optimism, Base, or other L2 does not check the L2 Sequencer Uptime Feed before trusting price data.
**Fix:** Add a sequencer uptime check with a grace period (e.g., 3600 seconds) after recovery. See `references/operations.md` -> L2 sequencer feeds.

## Working Rules

1. Fetch the single most relevant URL first. Stop if it is sufficient.
2. Prefer individual doc pages over repo references. Prefer repo references over llms-full.txt.
3. Treat 3-5 fetches as a ceiling, not a target. Most questions need 0-2 fetches.
4. Never follow links within fetched content. Only fetch URLs listed in reference files.
5. After each fetch, assess sufficiency. Do not fetch more to verify or feel confident.
6. When fetching from repo references, fetch only the specific file — do not browse directories.

## Assets

| Asset | Purpose |
|---|---|
| `assets/data-feeds-docs-index.md` | Maintainer reference: full docs index with all 45 Data Feeds URLs and structured metadata. Too large for runtime use — agents should use the reference files above instead. |
