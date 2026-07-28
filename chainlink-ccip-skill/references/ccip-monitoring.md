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

1. Call the CCIP API directly. It answers message retrieval, search, lane latency, and lane inventory with no RPC endpoint, wallet, or local tooling. Endpoint mechanics, parameters, response fields, status semantics, and error handling are in [ccip-api.md](ccip-api.md).
2. Use the CCIP CLI when the user wants command-line tracking, search, lane latency, or revert decoding. The CLI calls the same API, so prefer it only when the user asked for commands or already works in a shell.
3. Use the SDK when the user is building a monitoring integration rather than asking a question. See [ccip-sdk-examples.md](ccip-sdk-examples.md).
4. If the API and CLI paths return nothing or error, fall back to the CCIP Explorer (`https://ccip.chain.link/`). Remember that a message sent moments ago may not be indexed yet, so retry with backoff before treating an empty result as a problem.
5. Do not execute side-effecting remediation. If the user asks for remediation, prepare a user-run plan or command template instead.

Reference points:

- Machine-readable aggregate of endpoints, parameters, and CLI flags: `https://docs.chain.link/ccip/tools/llms.txt`
- API docs: `https://docs.chain.link/ccip/tools/api/`
- CLI docs: `https://docs.chain.link/ccip/tools/cli/`
- CLI debugging guide: `https://docs.chain.link/ccip/tools/cli/guides/debugging-workflow`
- Explorer: `https://ccip.chain.link/`

## Core Monitoring Surfaces

### CCIP API

Base URL `https://api.ccip.chain.link/v2`. The endpoints that carry monitoring:

| Endpoint | Use |
|---|---|
| `GET /v2/messages/{messageId}` | Status and full detail for one message |
| `GET /v2/messages` | Search by `sender`, `receiver`, chain selectors, `sourceTransactionHash`, `sourceTokenAddress`, `readyForManualExecOnly`, or `q` |
| `GET /v2/messages/{messageId}/execution-inputs` | Inputs a user needs to execute a stuck message |
| `GET /v2/lanes/latency` | Current trimmed-median delivery estimate, in `totalMs` |

Read [ccip-api.md](ccip-api.md) before constructing a call. It covers the required
`/v2` prefix, cursor and filter rules, the `status` lifecycle by lane version,
`readyForManualExecution`, error codes, and the retry window for messages that are
not indexed yet.

### CCIP CLI

Prefer the CLI for:

1. `show` or default tx-hash-or-id lookup
2. `search messages`
3. `lane-latency`
4. `parse` for error and revert decoding
5. failed-message debugging workflows
6. `--format json` on any of the above when the output will be parsed rather than read

Treat `manual-exec` as a separate side-effecting operation, not as a default monitoring action. The agent may explain or prepare a user-run template for it, but must not execute it.

## Monitoring Workflow

### Extracting a message ID from a transaction receipt

After a CCIP send (via `cast send`, a contract call, or any on-chain submission), the source OnRamp emits the CCIP message ID in the transaction logs. It is not returned directly by the send call.

To extract it:

1. Get the transaction receipt (e.g. `cast receipt <tx-hash>`).
2. Look for the `CCIPSendRequested` event in the logs. For token transfers, also check the `TokensSent` event.
3. The message ID is in the event topics (typically `topics[1]` for `CCIPSendRequested`, or a field in the log data depending on the CCIP version).
4. If using `cast`, parse the relevant log entry from the receipt output. The message ID is a 32-byte hex value (`0x` followed by 64 hex characters).

If log parsing is not practical, pass the transaction hash itself to `GET /v2/messages?sourceTransactionHash=<tx-hash>`, `ccip-cli show`, or the CCIP Explorer to find the associated message.

### Message lookup

1. Identify what the user has: tx hash, message ID, sender, route, or wallet.
2. If the user has a message ID, call `GET /v2/messages/{messageId}`. If they have a transaction hash, call `GET /v2/messages?sourceTransactionHash=<tx-hash>`, which also covers the case of several messages in one transaction.
3. If the user wants search or listing, use `GET /v2/messages` with the named filters and paginate by cursor. Offer CLI `search messages` when they want a command.
4. Explain the lifecycle state clearly instead of only returning raw data.

### Lane checks

1. Use `GET /v2/lanes/latency` for current lane performance, and `GET /v2/lanes` to confirm the lane exists at all. CLI `lane-latency` is the command-line equivalent.
2. Distinguish between route existence and current lane performance.
3. If the user is really asking whether a lane exists or what tokens it supports, route to the route/token discovery workflow instead.

### Failed-message diagnosis

1. Start with a read-only diagnosis path.
2. Read the message with `GET /v2/messages/{messageId}`, check `status` and `readyForManualExecution`, and use CLI `parse` to decode a revert reason. Explain the state before proposing any action.
3. If the user asks for remediation and the operation would be side-effecting, prepare a non-custodial user-run artifact instead of executing it.
4. Refuse mainnet remediation in this version.

## Freshness Rules

1. Read [official-sources.md](official-sources.md) before answering live status, lane, or current message questions.
2. Treat CCIP API responses as the current truth for message state and lane metrics.
3. Use the CCIP CLI docs for command behavior and debugging workflows.
4. Use the CCIP Explorer when the user wants an explorer-style view.
5. Do not hardcode message states, lane metrics, or current availability.

## Refusal Rules

1. Keep default monitoring flows read-only.
2. Refuse to treat `manual-exec` as a normal monitoring step.
3. Refuse mainnet side-effecting remediation in this version.
4. If the user wants write remediation, refuse agent-side execution and offer a command template, unsigned transaction data, or code for the user to run in their own wallet-controlled environment.
