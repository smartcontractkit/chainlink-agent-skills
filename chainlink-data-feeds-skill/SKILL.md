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

## Overview

Route Data Feed requests to the simplest valid path. Generate working code on first attempt when possible. Fetch documentation only when a specific gap blocks progress.

## Progressive Disclosure

1. Keep this file as the default guide.
2. Read [references/reading-price-feeds.md](references/reading-price-feeds.md) only when the user wants to read a price feed on EVM, write a consumer contract, read off-chain, look up AggregatorV3Interface, or debug a price feed integration.
3. Read [references/mvr-feeds.md](references/mvr-feeds.md) only when the user asks about Multiple-Variable Response feeds, bundle feeds, or BundleAggregatorProxy.
4. Read [references/svr-feeds.md](references/svr-feeds.md) only when the user asks about Smart Value Recapture, OEV recapture, or searcher onboarding.
5. Read [references/feed-types.md](references/feed-types.md) only when the user asks about feed categories, SmartData/RWA, rates/volatility, tokenized equity feeds, or needs help choosing a feed type.
6. Read [references/multi-chain.md](references/multi-chain.md) only when the user targets Solana, StarkNet, Aptos, or Tron.
7. Read [references/feed-operations.md](references/feed-operations.md) only when the user asks about L2 sequencer uptime checks, feed deprecation, contract registry, developer responsibilities, or data sources.
8. Read [references/official-sources.md](references/official-sources.md) only when the answer depends on live data that the reference files do not contain — feed addresses for a specific chain, current deprecation schedules, specific network parameters.
9. Read [references/source-code.md](references/source-code.md) only when debugging interface mismatches or the user needs to inspect contract source code on GitHub.
10. Do not load reference files speculatively.

## Routing

1. Use reading-price-feeds.md as the default for any EVM price feed request — this covers the vast majority of Data Feeds use cases.
2. Route to the chain-specific section of multi-chain.md for non-EVM chains (Solana, Aptos, StarkNet, Tron).
3. Route to mvr-feeds.md for bundle or multi-variable feed requests.
4. Route to svr-feeds.md for OEV or MEV recapture requests.
5. Route to feed-operations.md for operational concerns (L2 sequencer checks, deprecation, monitoring).
6. Ask one focused question if the chain, feed type, or integration method is unclear.
7. Proceed without asking for read-only work: explanations, code generation, debugging.

## Safety Defaults

These are non-negotiable in generated code. Every consumer contract or integration must include them.

1. Always validate freshness: check `updatedAt` against a staleness threshold based on the feed's heartbeat. Never skip this.
2. Always call `decimals()` on the feed: never hardcode decimal counts. Different feeds use different decimals.
3. On L2 chains (Arbitrum, Optimism, Base, Scroll, etc.): always include an L2 Sequencer Uptime Feed check with a grace period after recovery.
4. Never use `answeredInRound` for freshness validation — this field is deprecated.
5. Remind users that example code is unaudited and not for production use without a security review.
6. If the user is targeting mainnet, emphasize developer responsibilities and recommend a security audit.

## Documentation Access

This skill references official Data Feeds documentation URLs throughout its reference files. Whether the model can fetch those URLs depends on the host agent's capabilities.

1. If WebFetch, a browser tool, or an MCP server that can retrieve documentation is available, use it to fetch the referenced URL before answering.
2. If no documentation-fetching tool is available, do not silently improvise Data Feeds patterns from training data alone. Instead:
   - Use the embedded reference content in this skill's reference files as the floor for guidance.
   - Tell the user that live documentation could not be verified.
   - Provide the specific URL so the user can check it directly.
3. For contract-first workflows where correctness matters most, prefer the concrete examples in [references/reading-price-feeds.md](references/reading-price-feeds.md) over generating patterns from memory.

## Working Rules

1. Generate working code from knowledge and reference files first. Fetch only when a specific detail is missing.
2. Treat 0-1 fetches as normal, 2-3 as the ceiling. Most questions need no fetches because the reference files contain the implementation guidance.
3. When a fetch is needed, apply the cascade: WebFetch first; if it returns <1000 chars of useful content, fall back to `curl -s -L -A "Mozilla/5.0 ..." "<url>"`; if both fail, report the URL to the user.
4. Keep answers proportional — a simple "read a price feed" question gets a code block and brief explanation, not a full tutorial.
5. Generate code only when code is actually needed.
6. Keep unsupported or out-of-scope features out of the answer rather than speculating.
