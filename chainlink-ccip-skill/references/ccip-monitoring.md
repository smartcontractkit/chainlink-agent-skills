# CCIP Monitoring

Use this file only for CCIP message lookup, monitoring, status explanation, lane performance checks, or failed-message diagnosis.

## Trigger Conditions

Use this workflow for requests like:

- "Check whether my CCIP message landed."
- "Show me the status of this message."
- "Help me inspect a stuck or failed message."
- "List or search messages matching this sender or tx hash."
- "Check lane latency or lane performance."

Do not use this workflow for contract generation or direct send/bridge execution.

## Default Path

1. Prefer the CCIP API for monitoring, querying, and message lookup workflows.
2. Use the CCIP CLI when the user wants direct command-line tracking, search, lane latency, or failed-message debugging.
3. Use explorer-style lookup only when the user explicitly wants an explorer view or the API/CLI path is less convenient.
4. Do not switch to side-effecting remediation unless the user explicitly asks for it.

Reference points:

- API docs: `https://docs.chain.link/ccip/tools/api/`
- CLI docs: `https://docs.chain.link/ccip/tools/cli/`
- Explorer: `https://ccip.chain.link/`

## Core Monitoring Surfaces

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

### Message lookup

1. Identify what the user has: tx hash, message ID, sender, route, or wallet.
2. If the user has a tx hash or message ID and wants direct tracking, use the CLI or API retrieve-message path.
3. If the user wants search or listing, prefer the API and use CLI search as a complementary path.
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

## Triggering Tests

These prompts should trigger this story pack:

- "Check whether my CCIP message landed."
- "Show me the status of this tx hash."
- "Search CCIP messages from this sender."
- "Help me inspect a failed CCIP message and explain what happened."
- "What is the lane latency for this route?"

These prompts should not trigger this story pack:

- "Bridge funds using CCIP."
- "Create a CCIP sender contract."
- "Add Chainlink Local tests for this receiver."

## Functional Tests

1. If the user asks for monitoring or message lookup, choose API-first or CLI lookup paths instead of contract generation.
2. If the user asks for query or search behavior, prefer the API first.
3. If the user asks for direct command-line lookup, use the CLI path.
4. If the user asks for failed-message diagnosis, start read-only.
5. If the user asks for side-effecting remediation, require approval and refuse mainnet writes.
6. If the request is actually route discovery, redirect to the route/token workflow instead of overusing monitoring.
7. Explain message state and next steps clearly.

## Eval Checks

The workflow passes if it:

1. routes monitoring requests away from contract generation and send flows
2. prefers API for monitoring and querying
3. uses CLI effectively for direct lookup and debugging
4. keeps default monitoring read-only
5. distinguishes lane performance from route existence
6. explains the message lifecycle clearly
7. preserves approval guardrails for any remediation step

## A/B Prompt Pack

Use these prompts with and without the skill installed:

1. "Show me the status of this CCIP tx hash and explain the lifecycle in plain English."
2. "Search CCIP messages for this sender and summarize what happened."
3. "Help me diagnose this failed CCIP message, but do not execute anything yet."
4. "Check lane latency for this route and tell me whether I should treat it as a route problem or just current performance."
