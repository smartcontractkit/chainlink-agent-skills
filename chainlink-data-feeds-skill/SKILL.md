---
name: chainlink-data-feeds-skill
description: Help developers integrate Chainlink Data Feeds into smart contracts and applications. Trigger when user wants price feed integration, feed address lookup, data feed consumer contracts, multi-chain data feeds (EVM, Solana, Aptos, StarkNet, Tron), MVR/SVR feed usage, feed monitoring, historical data access, or understanding feed types and architecture.
license: MIT
compatibility: Designed for Claude Code and AI agents that implement https://agentskills.io/specification
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  purpose: Chainlink Data Feeds developer assistance and reference
  version: "0.0.1"
---

# Chainlink Data Feeds Skill

This skill helps developers integrate Chainlink Data Feeds into smart contracts and applications across EVM chains, Solana, Aptos, StarkNet, and Tron.

## Runtime Pattern

> **IMPORTANT — AGENTS MUST READ BEFORE FETCHING ANYTHING:**
> WebFetch may return an empty shell (nav/metadata only, no prose or code) for some URLs. After every WebFetch call, assess quality before using the content.
>
> **After every WebFetch, ask:** Does the response contain actual prose and/or code blocks with more than ~1000 chars of useful content?
>
> **Full fetch cascade — follow in order:**
> 1. **WebFetch** -> assess content quality -> proceed if substantial
> 2. **Bash curl** (if WebFetch returned a shell) — works on Windows 10+, Linux, and Mac ->
>    ```bash
>    curl -s -L -A "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" "<url>"
>    ```
> 3. **Tell the user** -> if both fail, report the URL and suggest they open it directly
>
> Apply this cascade to ALL fetches — doc pages, GitHub URLs, and text dumps.

Follow this runtime pattern when assisting with Data Feeds queries:

1. **Match user intent** to a reference file topic (e.g., "how do I read a price feed in Solidity?" -> `using-data-feeds.md` or `price-feeds.md`)
2. **Read the matching reference file** — use the descriptions to orient. Do not fetch yet.
3. **Act immediately** — write the answer or code from knowledge and reference descriptions. Do not fetch as preparation.
4. **Iterate** — present to the user, ask them to test or compile. Then loop:
   - Error or gap blocks progress -> fetch exactly what the error names -> fix -> repeat
   - Cannot write a specific part -> mark inline (e.g. `// NEED: exact feed address for ETH/USD on Sepolia`) -> fetch that one thing -> fill in -> continue
   - No error -> done

> **Do not fetch as preparation. Fetch as resolution.** Only fetch when you can state the exact piece of information you need. If you can't name it precisely, don't fetch.

## Code Example Priority Order

When looking for code examples or implementation details, use the most targeted source first. Apply the fetch cascade to any URL fetched:

1. **Individual doc pages first** — Most targeted. Fetch the specific page for the topic using the fetch cascade. Full content is accessible via curl if WebFetch returns a shell.
2. **Repo references second** (`repo-*.md`) — Use when the doc page lacks sufficient code, or the user explicitly wants a working implementation (example contracts, integration samples).
3. **Full-text doc dump last** (`llms-full.txt`) — Large plain-text dump linked from `general.md`. Use only when you can't identify a specific doc page or need broad coverage.

After each fetch, assess whether the content is sufficient. Stop if it is. Never follow links within fetched content. Fetch the minimum needed, not the maximum allowed. Treat 3-5 URLs as a ceiling, not a target. When fetching from repo reference files, fetch only the specific file needed — do not browse directories or read adjacent files.

## Feed Address Lookup Priority Order

When looking up feed addresses:

1. **Address list pages first** — Fetch the chain-specific address page (e.g. `/data-feeds/price-feeds/addresses`) which contains the canonical feed registry.
2. **Contract registry** — Consult `/data-feeds/contract-registry` for programmatic registry lookup.
3. **Full-text doc dump** — Last resort.

## Feed Integration Checklist

Follow these steps when **generating a consumer contract or integrating a data feed** (not just answering questions):

1. **Determine blockchain** — Ask the user which chain they're targeting: EVM (which network?), Solana, Aptos, StarkNet, or Tron. This determines the SDK, contract language, and address format.
2. **Determine feed type** — Ask the user what type of feed they need: Price Feed, MVR Feed, SmartData, Rates, Tokenized Equity, or SVR. If unsure, default to Price Feed and explain the options.
3. **Determine integration method** — For EVM: Solidity (on-chain), ethers.js (off-chain), or viem (off-chain). For other chains: use chain-specific patterns.
4. **Write the consumer contract/code immediately** — Generate the complete integration code from knowledge. Do not fetch first. Mark specific uncertainties inline (e.g. `// NEED: exact AggregatorV3Interface import path`, `// NEED: feed address for BTC/USD on Arbitrum`).
5. **Present and iterate** — Give the user the code. Ask them to compile/test. Then loop:
   - Compilation error -> fetch exactly what the error names -> fix -> ask user to re-test
   - Missing feed address -> fetch the address list page for that chain -> fill in -> continue
   - No error -> done
   - One fetch per gap. Never fetch speculatively.
6. **Always include validation** — Consumer contracts MUST check: answer freshness (updatedAt timestamp), answer bounds (reasonable min/max), and round completeness. Remind users of developer responsibilities.

## Debugging Checklist

Follow these steps when **diagnosing errors or fixing broken Data Feed integrations**:

1. **Identify the feed type and chain** — Determine which feed type (Price, MVR, SVR, etc.) and chain (EVM, Solana, etc.) is involved.
2. **Fetch the relevant doc page** — Look up the feed type in the appropriate reference file and web-fetch the doc page. Read the full content — pay attention to interface signatures, import paths, and chain-specific requirements.
3. **Check example code** — Consult the `repo-documentation.md` reference file for a working implementation. Fetch and read the example code.
4. **Check common issues** — Common Data Feeds issues include: wrong feed address, missing decimals conversion, stale price checks, wrong interface version (AggregatorV3Interface vs AggregatorV2V3Interface), L2 sequencer not checked, and deprecated feeds.
5. **Only then propose a fix** — Do not guess. Data Feeds have chain-specific and feed-type-specific requirements. Different chains use different contract interfaces and address formats.
6. **If a fix fails, re-consult docs** — Do not iterate by guessing alternatives. Go back to step 2 and re-read the docs more carefully, or fetch additional related pages.

## Doc Reference Files

These files contain URLs + enriched descriptions for each topic area. Read the matching file to find the right URLs to fetch.

| Reference file | Topics covered |
|---|---|
| `references/getting-started.md` | Getting started with Chainlink Data Feeds |
| `references/price-feeds.md` | Price feed overview and address lists |
| `references/using-data-feeds.md` | Reading feeds (Solidity, ethers.js, viem), selecting feeds, historical data |
| `references/feed-types.md` | Feed types overview, tokenized equity feeds, SmartData (RWA), rates feeds |
| `references/mvr-feeds.md` | Multiple-Variable Response (MVR) bundle feeds and integration guides |
| `references/svr-feeds.md` | Smart Value Recapture (SVR) feeds and searcher onboarding |
| `references/multi-chain.md` | Solana, StarkNet, Aptos, and Tron feed integration |
| `references/operations.md` | Developer responsibilities, feed deprecation, L2 sequencer feeds, self-managed feeds, contract registry, data sources |
| `references/api-reference.md` | AggregatorV3Interface API reference and MVR API reference |
| `references/general.md` | Data Feeds overview, index, ENS integration, llms-full.txt dump, US government macroeconomic feeds |

## Repo Reference Files

These files contain GitHub URLs to source code in Chainlink repositories. Consult when the user asks for code examples, integration patterns, contract templates, or needs to inspect actual contract interfaces and implementations.

| Reference file | Contents |
|---|---|
| `references/repo-documentation.md` | Solidity consumer contracts (DataConsumerV3, MVR, SVR, sequencer check, ENS, historical data, reserves), JavaScript/Python off-chain readers, Solana on-chain/off-chain examples (Rust, JS, TS), SVR broadcaster/decoder/listener examples (Go, TS) |
| `references/repo-chainlink-evm.md` | On-chain contract source code: AggregatorProxy, EACAggregatorProxy, AggregatorV3Interface, AggregatorV2V3Interface (v0.6 legacy), BundleAggregatorProxy, IBundleAggregatorProxy, DataFeedsCache (v0.8 MVR). Use when debugging interface mismatches, verifying function signatures, or understanding proxy/aggregator internals. |

## Assets

| Asset | Purpose |
|---|---|
| `assets/data-feeds-docs-index.md` | Full docs index with all 45 Data Feeds URLs and LLM-generated summaries (source of truth for URL list) |
