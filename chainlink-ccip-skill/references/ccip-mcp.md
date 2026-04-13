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

Unified CCIP SDK tool. For message status lookups, use the `messageId` or `sourceTxHash` shortcut fields — these bypass `target`/`method` dispatch and always return a standardized response. For all other operations, use `target='api'` for `CCIPAPIClient` calls (lane latency, discovery) or `target='chain'` for on-chain reads via RPC (balances, fees). Provide method name and args array. For chain calls, include `family` and `rpcUrl`. Use strings for large integers (chain selectors) to avoid precision loss. Set `listMethods=true` to discover available methods.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `messageId` | string (hex) | No | Shortcut: directly fetch status for this message ID. Bypasses `target`/`method` dispatch. `target` is not required. |
| `sourceTxHash` | string (hex) | No | Shortcut: resolve message IDs from this transaction hash, then fetch status for each. Bypasses `target`/`method` dispatch. `target` is not required. |
| `target` | `"api"` or `"chain"` | Required unless using `messageId` or `sourceTxHash` | `api` for CCIPAPIClient calls, `chain` for on-chain reads via RPC. |
| `method` | string | Required unless `listMethods` is true or using a shortcut field | SDK method name to invoke on the target. |
| `args` | array | No | Positional arguments for the method. Use strings for large integers. |
| `listMethods` | boolean | No | When true, returns available method names for the target instead of calling a method. |
| `family` | `"evm"`, `"solana"`, `"aptos"`, `"sui"`, or `"ton"` | Required for `chain` target | Chain family for on-chain calls. |
| `rpcUrl` | string (URL) | Required for `chain` target unless a default exists | RPC URL for the source chain. Defaults exist for `evm` (Sepolia), `solana` (devnet), and `aptos` (testnet). |
| `baseUrl` | string (URL) | No | Override for the CCIP API base URL. Defaults to `https://api.ccip.chain.link`. |

### Validation Rules

1. `method` is required unless `listMethods` is true or a shortcut field (`messageId`, `sourceTxHash`) is provided.
2. `target` is not required when `messageId` or `sourceTxHash` is provided.
3. For `target='chain'`, `family` is always required.
4. For `target='chain'`, `rpcUrl` must be provided unless the family has a built-in default (`evm`, `solana`, `aptos`).
5. Pass chain selectors as strings, not numbers, to avoid JavaScript precision loss.

### Standardized Message Status Response

When using `messageId` or `sourceTxHash`, the tool always returns a normalized shape:

```typescript
{
  messageId: "0x...",
  status: "pending" | "in_transit" | "delivered" | "failed",
  lifecycleStage: "waiting_for_finality" | "committed" | "blessed" | "executed" | null,
  sourceChain: "...",
  destinationChain: "...",
  sourceTxHash: "0x...",
  destinationTxHash: "0x..." | null,  // populated when delivered, null otherwise
  timestamp: "2025-..."
}
```

`lifecycleStage` maps all SDK `MessageStatus` values to a named stage:

| SDK status | `status` | `lifecycleStage` |
|---|---|---|
| SENT | `pending` | `waiting_for_finality` |
| SOURCE_FINALIZED | `in_transit` | `waiting_for_finality` |
| VERIFYING / VERIFIED | `in_transit` | `committed` |
| COMMITTED | `in_transit` | `committed` |
| BLESSED | `in_transit` | `blessed` |
| SUCCESS | `delivered` | `executed` |
| FAILED | `failed` | `executed` |

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

### Message status by message ID

Use the `messageId` shortcut. `target` and `method` are not required.

```json
{
  "messageId": "0x<64-hex-message-id>"
}
```

### Message status by source transaction hash

Use the `sourceTxHash` shortcut. The tool resolves all message IDs in the transaction, then returns status for each.

```json
{
  "sourceTxHash": "0x<transaction-hash>"
}
```

Both shortcuts return the [standardized response schema](#standardized-message-status-response).

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

1. For message status lookups, use the `messageId` or `sourceTxHash` shortcut instead of constructing a `target`/`method` call manually.
2. Start with `listMethods` to discover available methods on the target before guessing method names for non-shortcut calls.
3. Use `target='api'` for lane latency, discovery, and other API-backed queries.
4. Use `target='chain'` for on-chain reads such as balances, fees, and contract state.
5. Pass chain selectors as strings to avoid precision loss on large integers.
6. If MCP is not connected or a call fails with a connection error, fall back to direct CLI or SDK invocation and follow [ccip-tools.md](ccip-tools.md).

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

## Non-EVM Chain Families

The `ccip_sdk` MCP tool accepts `family` values for `solana`, `aptos`, `sui`, and `ton` in addition to `evm`.

When a user asks about non-EVM CCIP operations through MCP:
1. Use the MCP tool with the appropriate `family` value to retrieve the requested data.
2. For workflow guidance beyond what the tool returns, read [ccip-non-evm.md](ccip-non-evm.md) for SDK chain classes, CLI usage, wallet setup, architectural differences, and official tutorial links.
3. Do not apply EVM-specific workflow patterns (Solidity contract generation, Foundry/Hardhat setup, Chainlink Local) to non-EVM chains.
4. For non-EVM `target='chain'` calls, set `family` to the appropriate value and provide `rpcUrl` (defaults exist for `evm` Sepolia, `solana` devnet, and `aptos` testnet).

## Refusal Rules

1. All safety guardrails, approval protocols, and mainnet-write restrictions from the main skill file still apply when using MCP tools.
2. Do not treat MCP tool availability as a bypass for the approval or second-confirmation requirements.
3. If the MCP tool would execute a side-effecting action, require the same approval flow as direct CLI or SDK execution.

