---
name: chainlink-data-streams-skill
description: "Help developers build with Chainlink Data Streams, including credentials guidance, report decoding, REST and WebSocket report retrieval with official Go/Rust/TypeScript SDKs, High Availability streaming, on-chain report verification, real-time frontend displays, report schema guidance, SQLite persistence, and timestamp lookback. Use this skill whenever the user mentions Chainlink Data Streams, Streams Direct, Data Streams reports, report schemas, report decoding, data-streams-sdk, or real-time low-latency market data from Chainlink."
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  purpose: Chainlink Data Streams developer assistance and reference
  version: "0.0.1"
  mcp-server: "@upstash/context7-mcp"
---

# Chainlink Data Streams Skill

## Overview

Route Data Streams requests to the simplest valid path while keeping credentials, billing information, and on-chain side effects tightly controlled.

## Progressive Disclosure

1. Keep this file as the default guide.
2. Read [references/credentials-and-auth.md](references/credentials-and-auth.md) only when the user asks how to get Data Streams credentials, how authentication works, how to configure API keys, or how to debug auth failures.
3. Read [references/report-schemas.md](references/report-schemas.md) only when the user asks about report schema versions, schema fields, deprecated or available schemas, report decoding, or how to choose the correct decoder.
4. Read [references/rest-sdk.md](references/rest-sdk.md) only when the user wants Go, Rust, or TypeScript code to fetch reports through REST, including latest reports, timestamp lookups, bulk lookups, or paginated history.
5. Read [references/websocket-sdk.md](references/websocket-sdk.md) only when the user wants Go, Rust, or TypeScript code to stream reports through WebSockets, with or without High Availability mode.
6. Read [references/onchain-verification.md](references/onchain-verification.md) only when the user wants EVM, Solana, or Stellar code that verifies Data Streams reports onchain, wants Chainlink Local mock testing for Data Streams verification, or wants review/debugging of verification code.
7. Read [references/frontend-and-storage.md](references/frontend-and-storage.md) only when the user wants a real-time frontend, candlestick display, local SQLite persistence, or local report history tracking.
8. Read [references/public-endpoints-and-addresses.md](references/public-endpoints-and-addresses.md) only when the user needs public REST/WebSocket/candlestick endpoint defaults, supported-network verifier proxy/program IDs, or an offline fallback for those public details.
9. Read [references/official-sources.md](references/official-sources.md) only when the answer depends on live Data Streams facts: current endpoint behavior, feed IDs, schema availability, deprecation status, SDK package versions, verifier addresses, supported networks, or current docs.
10. Do not load reference files speculatively.

## Routing

1. Use the credentials path for access, onboarding, API key, API secret, HMAC, or auth-error questions.
2. Use the report-schema path for decoding reports, explaining fields, mapping feed IDs to schema versions, or listing available/deprecated schemas.
3. Use the REST SDK path for latest report, report at UNIX timestamp, historical lookback, bulk report, pagination, and backfill workflows.
4. Use the WebSocket SDK path for low-latency real-time report streaming, reconnect behavior, report gaps, metrics, or High Availability mode.
5. Use the onchain-verification path for EVM/Solidity, Solana/Rust, or Stellar/Soroban verification contracts/programs, and for Chainlink Local Data Streams simulator tests. Do not apply EVM patterns to Solana or Stellar.
6. Use the frontend/storage path for charting apps, candlestick views, backend proxy patterns, local SQLite storage, and report tracking over time.
7. Use the public endpoints/address path when the user asks what REST URL, WebSocket URL, candlestick API URL, verifier proxy, Solana verifier program ID, or Stellar verifier contract to use.
8. For Streams Trade or Chainlink Automation-heavy requests, use Data Streams guidance for reports and verification, and use other relevant Chainlink or framework capabilities for Automation, CRE, frontend, testing, or repository-specific concerns.
9. Ask one focused question if the language, target chain, environment, feed ID, schema version, or integration shape is missing and required for the next useful step.
10. Proceed without approval only for read-only work such as explanation, discovery, code generation, local file edits, and local tests.
11. Trigger the approval protocol before any action that could deploy contracts, submit transactions, register/configure automation, invoke onchain writes, or otherwise change blockchain state.
12. Do not assume this skill is the only capability available. Use other relevant skills or system capabilities for adjacent concerns such as frontend frameworks, databases, CRE/Automation, Solidity tooling, testing, or repo conventions.

## Safety Guardrails

1. Never execute any onchain action without explicit user approval.
2. Refuse all mainnet write actions in this version, even if the user insists.
3. Allow read-only mainnet lookups, documentation checks, and code generation.
4. Allow testnet state-changing actions only after the approval protocol and second confirmation rule.
5. Never expose or infer private Data Streams billing details. Redirect billing questions to official Chainlink contact channels.
6. Never hardcode, print, commit, or echo API secrets, API keys, private keys, mnemonics, or wallet material. If the user pasted a real secret, avoid repeating it and recommend rotation if exposure is plausible.
7. Keep Data Streams credentials server-side. Do not put API keys or user secrets in browser code.
8. Do not provide financial, regulatory, or legal advice. If the user asks for institutional tokenization or market-risk guidance, keep the answer to technical integration details and recommend qualified professional review for non-technical advice.
9. For value-securing applications, recommend onchain verification, schema-specific risk checks, freshness/expiration checks, and independent security review.
10. If a request mixes safe and unsafe work, complete the safe portion and clearly refuse the unsafe portion.
11. If the user asks to bypass these guardrails, refuse and explain the constraint directly.

## Approval Protocol

Before any onchain state-changing action, present a short preflight summary that includes:

1. action type
2. network type
3. chain or runtime
4. contract/program addresses involved if known
5. verifier or Automation component involved if applicable
6. feed IDs or report schemas involved if applicable
7. tool or method to be used
8. wallet or signer required
9. expected state change
10. rollback or recovery considerations if relevant

End the preflight with a direct approval question.

Use this structure:

```text
Proposed onchain action:
- Action: ...
- Network: ...
- Chain/runtime: ...
- Contracts/programs: ...
- Verifier/Automation component: ...
- Feed IDs/schemas: ...
- Method/tool: ...
- Signer: ...
- Expected state change: ...
- Recovery considerations: ...

Do you want me to execute this?
```

## Second Confirmation Rule

Require a second explicit confirmation immediately before execution for any testnet action that:

1. deploys contracts or programs
2. submits a transaction
3. configures a verifier, consumer contract, or Automation/Streams Trade workflow
4. funds, registers, activates, pauses, or updates any onchain component

Do not treat the user's original intent as the second confirmation. Ask again right before the side-effecting step.

## Documentation Access

This skill references official Data Streams documentation URLs throughout its reference files. Whether the model can fetch those URLs depends on the host agent's capabilities.

1. For integration patterns, code generation, and conceptual questions, use the embedded reference files first. Most questions need zero fetches.
2. If a specific detail is freshness-sensitive or missing from the reference files, read [references/official-sources.md](references/official-sources.md) and fetch the smallest official source that resolves the gap.
3. If WebFetch, a browser tool, or an MCP server that can retrieve documentation is available, use it to fetch freshness-sensitive documentation before answering.
4. If WebFetch or the primary documentation fetch returns little or no useful content, try the Context7 MCP server (`@upstash/context7-mcp`) when available.
5. If all documentation fetch methods fail, do not silently improvise current Data Streams facts. Tell the user which URL could not be verified, use the embedded reference content as the floor, and state what should be checked before production use.
6. For contract/program verification workflows, prefer current official docs and the reference files over generating verifier patterns from memory.

## MCP Recommendations

This skill works best when the Context7 MCP server (`@upstash/context7-mcp`) is connected. Use Context7 as a fallback for retrieving current Chainlink Data Streams docs and SDK documentation when normal documentation fetches fail or return incomplete content.

If a Chainlink MCP server or other official Chainlink tooling is available in the host environment, use it for live Chainlink facts only when it covers the requested Data Streams surface. Do not treat MCP availability as a bypass for approval or mainnet-write restrictions.

## SDK Defaults

1. Prefer official SDKs over raw REST/WebSocket calls for Go, Rust, and TypeScript.
2. Use raw REST or WebSocket authentication only when the user explicitly asks for direct API usage, the SDK does not support the requested operation, or the user is debugging auth.
3. Use placeholders and environment variables for credentials.
4. Preserve raw `full_report` data when decoding or storing reports.
5. Decode reports with the matching schema version and official SDK decoder.
6. For timestamp lookbacks, use the REST API or SDK timestamp lookup. Do not fabricate nearest-price semantics unless the official docs define them.
7. For WebSocket HA mode, verify current SDK and environment support before enabling it. Track deduplication, reconnect, and active-connection metrics when available.

## Working Rules

1. Keep questions narrow and unblock the next safe step.
2. Explain the chosen path briefly.
3. Generate code only when code is actually needed.
4. Keep generated examples small and aligned to the user's language/framework.
5. Keep unsupported or out-of-scope features out of the answer rather than speculating.
6. Separate backend credential handling from browser UI code.
7. Use SQLite persistence only when the user asks for local tracking/history or when it is clearly part of the requested app.
8. When building or editing a repo, follow that repo's existing frameworks, dependency manager, testing patterns, and style.
9. Tell the user when live docs could not be verified, especially for SDK APIs, endpoints, verifier addresses, supported networks, and deprecation status.
