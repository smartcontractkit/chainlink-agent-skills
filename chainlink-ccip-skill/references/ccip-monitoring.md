# CCIP Monitoring

Use for message lookup/search, lifecycle explanation, lane performance, and failed-message diagnosis on every family including Solana/Aptos. Use [ccip-api.md](ccip-api.md) first: it owns parameters, response schemas, versioned status, cursor rules, errors, and retry behavior. CLI is for users asking for commands; SDK examples are for monitoring integrations; `https://ccip.chain.link/` is the interactive fallback.

Sources: tools aggregate `https://docs.chain.link/ccip/tools/llms.txt`; API `https://docs.chain.link/ccip/tools/api/`; CLI `https://docs.chain.link/ccip/tools/cli/`; debugging `https://docs.chain.link/ccip/tools/cli/guides/debugging-workflow`.

## Surfaces

| Surface | Use |
|---|---|
| `GET /v2/messages/{messageId}` | One full message |
| `GET /v2/messages` | Search by sender, receiver, selectors, source transaction/token, or `q`; manual-exec readiness filters are failure-remediation-only |
| `GET /v2/messages/{messageId}/execution-inputs` | Read user manual-execution inputs only for a confirmed failed/ready message |
| `GET /v2/lanes`, `/v2/lanes/latency` | Existence and trimmed-median `totalMs` estimate |
| CLI `show`, `search messages`, `lane-latency` | Command-line equivalents |
| CLI `parse` | Decode errors, reverts, calldata, or events |

Use `--format json` for parsed CLI output. Normal lookup and monitoring report status and failure details only: do not mention manual-execution readiness, execution inputs, or `manual-exec` as a routine next step. Manual execution is a separate write considered only after current message data shows an actual failed message that is ready for it, never an agent-executed remediation.

## Workflow

### Find the message

A source OnRamp emits the ID; a send call does not return it directly. In the receipt find `CCIPSendRequested` (and `TokensSent` for transfers). The 32-byte ID is commonly `topics[1]`, but location depends on CCIP version. If log decoding is impractical, search the source transaction hash through the API, CLI `show`, or Explorer.

- ID: `GET /messages/{messageId}`.
- Transaction: `GET /messages?sourceTransactionHash=<tx>`; this also handles several messages in one transaction.
- Sender/route/wallet listing: named `/messages` filters with cursor pagination; offer CLI search only when commands are wanted.
- Explain the state rather than echoing the enum. Fresh messages may be unindexed, so apply API backoff before declaring a problem.

### Lane and failure diagnosis

Use `/lanes` for existence and `/lanes/latency` for current performance; do not confuse either with token support, which [discovery](ccip-discovery.md) owns.

For an actual failure: read the message, check `status`, and decode the revert with CLI `parse`; explain the diagnosis before suggesting action. Check `readyForManualExecution` or execution inputs only after the current status confirms failure and the user is diagnosing remediation—never during ordinary status monitoring. Side-effecting remediation gets only a permitted user-run artifact after the main preflight, and mainnet remediation/artifacts are refused.

Treat API responses as current truth for state/metrics; use current CLI docs for commands and Explorer for explorer-style views. Never hardcode state, latency, or availability.
