# CCIP Monitoring

Use this file only for CCIP message lookup, monitoring, status explanation, lane performance checks, or failed-message diagnosis. Monitoring surfaces (CCIP API, CLI `show`/`search`, Explorer) work for messages on all chain families including Solana and Aptos -- message status lookup via the API is chain-agnostic.

## Trigger Conditions

Use this workflow for requests like:

- "Check whether my CCIP message landed."
- "Show me the status of this message."
- "Help me inspect a stuck or failed message."
- "List or search messages matching this sender or tx hash."
- "Check lane latency or lane performance."

Do not use this workflow for contract generation or direct send/bridge execution.

## Default Path

1. When the `ccip_sdk` MCP tool is available, prefer it with `target='api'` for message retrieval, lane latency, and query workflows. See [ccip-mcp.md](ccip-mcp.md) for tool parameters and workflow patterns.
2. Prefer the CCIP API docs for monitoring and query workflows when MCP is not connected.
3. Use the CCIP CLI when the user wants direct command-line tracking, search, lane latency, or failed-message debugging.
4. If the MCP tool, API, or CLI path does not return a result or returns an error, fall back to the CCIP Explorer (`https://ccip.chain.link/`). The Explorer is the most reliable interactive surface for message status today.
5. Do not switch to side-effecting remediation unless the user explicitly asks for it.

Reference points:

- API docs: `https://docs.chain.link/ccip/tools/api/`
- CLI docs: `https://docs.chain.link/ccip/tools/cli/`
- Explorer: `https://ccip.chain.link/`

## Core Monitoring Surfaces

### ccip_sdk MCP Tool

When the MCP server is connected, prefer the `ccip_sdk` tool with `target='api'` for:

1. retrieving a message by ID or transaction hash
2. lane latency queries (pass chain selectors as strings)
3. programmatic monitoring integrations that benefit from structured MCP responses

Use `listMethods=true` with `target='api'` to discover all available monitoring methods. Fall back to the CCIP API or CLI paths below when MCP is not connected.

### CCIP API

Prefer the API for:

1. retrieving a message
2. lane information and latency-style monitoring
3. searching or querying by identifiers
4. intent lookup by transaction hash or intent ID
5. programmatic monitoring integrations

The API docs describe these read-oriented surfaces as the primary monitoring entrypoints.

### CCIP CLI

Prefer the CLI for:

1. `show` or default tx-hash-or-id lookup
2. `search messages`
3. `lane-latency`
4. `parse` for error and revert decoding
5. failed-message debugging workflows

Treat `manual-exec` as a separate side-effecting operation, not as a default monitoring action.

## Monitoring Workflow

### Extracting a message ID from a transaction receipt

After a CCIP send (via `cast send`, a contract call, or any on-chain submission), the CCIP message ID is emitted in the transaction logs. It is not returned directly by the send call.

To extract it:

1. Get the transaction receipt (e.g. `cast receipt <tx-hash>`).
2. Look for the `CCIPSendRequested` event in the logs. For token transfers, also check the `TokensSent` event.
3. The message ID is in the event topics (typically `topics[1]` for `CCIPSendRequested`, or a field in the log data depending on the CCIP version).
4. If using `cast`, parse the relevant log entry from the receipt output. The message ID is a 32-byte hex value (`0x` followed by 64 hex characters).

If log parsing is not practical, the transaction hash itself can be used with the CCIP Explorer, CLI `show`, or MCP/API lookup to find the associated message.

### Message lookup

1. Identify what the user has: tx hash, message ID, sender, route, or wallet.
2. If the user has a tx hash or message ID and wants direct tracking, use the CLI or API retrieve-message path.
3. If the user wants search or listing, prefer the API and use CLI search as an additional path.
4. Explain the lifecycle state clearly instead of only returning raw data.

### Lane checks

1. Use API or CLI lane-latency surfaces for current lane performance checks.
2. Distinguish between route existence and current lane performance.
3. If the user is really asking whether a lane exists or what tokens it supports, route to the route/token discovery workflow instead.

### Failed-message diagnosis

1. Start with a read-only diagnosis path.
2. Use CLI `show` and `parse`, plus API retrieval, to explain the current failed or pending state.
3. If the user asks for remediation and the operation would be side-effecting, hand back to the approval protocol before any action.
4. Refuse mainnet remediation in this version.

## Freshness Rules

1. Read [official-sources.md](official-sources.md) before answering live status, lane, or current message questions.
2. Prefer the CCIP API docs for monitoring and query behavior.
3. Use the CCIP CLI docs for command behavior and debugging workflows.
4. Use the CCIP Explorer when the user wants an explorer-style view.
5. Do not hardcode message states, lane metrics, or current availability.

## Refusal Rules

1. Keep default monitoring flows read-only.
2. Refuse to treat `manual-exec` as a normal monitoring step.
3. Refuse mainnet side-effecting remediation in this version.
4. If the user wants write remediation, require the same approval and second-confirmation guardrails as other on-chain actions.

