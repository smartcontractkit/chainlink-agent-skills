# CCIP MCP

Use this file only when the `ccip_sdk` MCP tool is available and the request can be fulfilled by it.

## Trigger Conditions

Use this workflow for requests like:

- "Check the status of my CCIP message using the MCP server."
- "Use the SDK to get lane latency for this route."
- "What methods are available on the CCIP API client?"
- "Read my CCIP token balance on this chain."
- "Get the fee estimate for this transfer using the SDK."

Do not use this workflow when the MCP server is not connected. Fall back to direct CLI or SDK usage from [ccip-tools.md](ccip-tools.md) instead.

## MCP Server

- Package: `@chainlink/mcp-server`
- Transport: stdio
- The server name in the host configuration (Cursor, Claude Code, etc.) is set by the developer and may vary. The tool name `ccip_sdk` is stable regardless of what the server is named.

## ccip_sdk Tool

Unified CCIP SDK tool. Use `target='api'` for `CCIPAPIClient` calls (message status, lane latency) or `target='chain'` for on-chain reads via RPC (balances, fees). Provide method name and args array. For chain calls, include `family` and `rpcUrl`. Use strings for large integers (chain selectors) to avoid precision loss. Set `listMethods=true` to discover available methods.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target` | `"api"` or `"chain"` | Yes | `api` for CCIPAPIClient calls, `chain` for on-chain reads via RPC. |
| `method` | string | Yes, unless `listMethods` is true | SDK method name to invoke on the target. |
| `args` | array | No | Positional arguments for the method. Use strings for large integers. |
| `listMethods` | boolean | No | When true, returns available method names for the target instead of calling a method. |
| `family` | `"evm"`, `"solana"`, `"aptos"`, `"sui"`, or `"ton"` | Required for `chain` target | Chain family for on-chain calls. |
| `rpcUrl` | string (URL) | Required for `chain` target unless a default exists | RPC URL for the source chain. Defaults exist for `evm` (Sepolia), `solana` (devnet), and `aptos` (testnet). |
| `baseUrl` | string (URL) | No | Override for the CCIP API base URL. Defaults to `https://api.ccip.chain.link`. |

### Validation Rules

1. `method` is required unless `listMethods` is true.
2. For `target='chain'`, `family` is always required.
3. For `target='chain'`, `rpcUrl` must be provided unless the family has a built-in default (`evm`, `solana`, `aptos`).
4. Pass chain selectors as strings, not numbers, to avoid JavaScript precision loss.

## Workflow Patterns

### Discover available methods

Before calling a method, use `listMethods` to see what is available on the target.

For API methods:

```json
{
  "target": "api",
  "listMethods": true
}
```

For chain methods on a specific family:

```json
{
  "target": "chain",
  "family": "evm",
  "listMethods": true
}
```

### Message status lookup

Use `target='api'` with the appropriate retrieval method and the message ID or transaction hash.

```json
{
  "target": "api",
  "method": "getMessageById",
  "args": ["0x<64-hex-message-id>"]
}
```

### Lane latency

Pass chain selectors as strings to preserve precision.

```json
{
  "target": "api",
  "method": "getLaneLatency",
  "args": ["<source-chain-selector>", "<destination-chain-selector>"]
}
```

### On-chain reads

Use `target='chain'` with the chain family and an RPC URL. Discover methods first, then call the relevant one.

```json
{
  "target": "chain",
  "family": "evm",
  "rpcUrl": "https://ethereum-sepolia-rpc.publicnode.com",
  "method": "<method-name>",
  "args": []
}
```

## Default Path

1. Start with `listMethods` to discover available methods on the target before guessing method names.
2. Use `target='api'` for monitoring, message retrieval, lane latency, and other API-backed queries.
3. Use `target='chain'` for on-chain reads such as balances, fees, and contract state.
4. Pass chain selectors as strings to avoid precision loss on large integers.
5. If MCP is not connected or a call fails with a connection error, fall back to direct CLI or SDK invocation and follow [ccip-tools.md](ccip-tools.md).

## Error Handling

### MCP connection failure

If the `ccip_sdk` tool is not available or returns a connection error:
1. Confirm the MCP server providing the `ccip_sdk` tool is connected in the host environment.
2. Fall back to direct CLI or SDK usage from [ccip-tools.md](ccip-tools.md).

### Invalid parameters

If the tool returns a validation error:
1. Check that `method` is provided (or `listMethods` is true).
2. For `chain` target, check that `family` and `rpcUrl` are provided.
3. For `getLaneLatency`, check that chain selectors are passed as strings.

### Unknown method

If the tool returns "Unknown CCIP SDK method":
1. Call the tool with `listMethods=true` for the same target to get available method names.
2. Retry with the correct method name.

## Freshness Rules

1. The MCP server loads CCIP configuration at startup. Treat its responses as current.
2. For questions about live message status or current lane performance, prefer MCP over cached assumptions.
3. Read [official-sources.md](official-sources.md) when the answer depends on sources beyond what the MCP tool covers.

## Refusal Rules

1. All safety guardrails, approval protocols, and mainnet-write restrictions from the main skill file still apply when using MCP tools.
2. Do not treat MCP tool availability as a bypass for the approval or second-confirmation requirements.
3. If the MCP tool would execute a side-effecting action, require the same approval flow as direct CLI or SDK execution.

## Triggering Tests

These prompts should trigger this workflow when the `ccip_sdk` tool is available:

- "Use the CCIP SDK tool to check the status of this message."
- "List the available methods on the CCIP API client."
- "Get lane latency for Ethereum Sepolia to Base Sepolia using the MCP tool."
- "Read my token balance on this chain using the CCIP SDK."

These prompts should not trigger this workflow:

- "Write a CCIP sender contract in Solidity."
- "Explain how CCIP works at a high level."
- "Add Chainlink Local tests for this receiver."
- "Bridge funds using the CLI." (explicit CLI preference)

## Functional Tests

1. If the `ccip_sdk` tool is available and the user asks for message status, use `target='api'` instead of directing to CLI or API docs.
2. If the user asks to discover available methods, call with `listMethods=true` before attempting a method call.
3. If the user provides chain selectors as numbers, convert them to strings before calling `getLaneLatency`.
4. If the `ccip_sdk` tool returns an unknown method error, retry with `listMethods=true` to discover the correct name.
5. If the `ccip_sdk` tool is not available, fall back to CLI or SDK without error.
6. If the request involves a side-effecting action through MCP, require the same approval and second-confirmation flow.
7. If the user explicitly asks for CLI or direct SDK usage, do not override with MCP.

## Eval Checks

The workflow passes if it:

1. prefers the `ccip_sdk` MCP tool when available for supported operations
2. falls back gracefully to CLI or SDK when MCP is not available
3. uses `listMethods` for method discovery instead of guessing
4. passes chain selectors as strings for precision safety
5. preserves all safety guardrails and approval protocols when using MCP
6. does not override an explicit user preference for CLI or direct SDK

## A/B Prompt Pack

Use these prompts with and without the `ccip_sdk` MCP tool available:

1. "Check the status of this CCIP message ID and explain what state it is in."
2. "What methods can I call on the CCIP API client? List them for me."
3. "Get the lane latency between Ethereum Sepolia and Base Sepolia and tell me whether it looks healthy."
4. "Read my CCIP-related balance on Ethereum Sepolia using the SDK."
