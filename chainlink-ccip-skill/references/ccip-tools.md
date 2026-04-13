# CCIP Tools

Use this file only for tool-first CCIP requests where the user wants to use CCIP CLI, API, or SDK instead of building custom contracts.

## Trigger Conditions

Use this workflow for requests like:

- "Send a CCIP message for me."
- "Bridge USDC from one chain to another using CCIP."
- "Move funds with CCIP without writing contracts."
- "Estimate the fee and send the transfer."

Do not use this workflow when the user clearly wants custom sender or receiver contracts.

## Required Inputs

Collect only the missing inputs needed for the next safe step:

1. source chain
2. destination chain
3. network type
4. recipient address or receiving account
5. token and amount for fund transfers
6. payload for message sends

If the route or network is missing, ask for it. Do not assume a lane.

## Default Path

1. When the `ccip_sdk` MCP tool is available, prefer it for programmatic SDK and API operations such as fee estimation, message status, lane latency, and on-chain reads. See [ccip-mcp.md](ccip-mcp.md) for tool parameters and workflow patterns.
2. Prefer the CCIP CLI for side-effecting on-chain actions such as sending, token support checks, and manual execution when MCP is not connected or the action is not supported by the MCP tool.
3. Use the CCIP SDK directly only when the user asks for a programmatic integration, code sample, or MCP is not available.
4. Route read-only monitoring, querying, searching, lane-latency checks, and message-status workflows to [ccip-monitoring.md](ccip-monitoring.md).
5. Do not switch to contract generation unless the user asks for it or the tool-first path cannot satisfy the goal.

Reference points:
- Tools overview: `https://docs.chain.link/ccip/tools/`
- CLI docs: `https://docs.chain.link/ccip/tools/cli/`
- API docs: `https://docs.chain.link/ccip/tools/api/`
- SDK docs: `https://docs.chain.link/ccip/tools/sdk/`
- CLI package: `@chainlink/ccip-cli`
- SDK package: `@chainlink/ccip-sdk`
- SDK examples repo: `https://github.com/smartcontractkit/ccip-sdk-examples`

For TypeScript SDK code examples (fee estimation, token transfers, messaging, status checks), see [ccip-sdk-examples.md](ccip-sdk-examples.md).

## Multi-Chain Support

The SDK, CLI, and API support multiple blockchain families:

| Chain Family | SDK/CLI Status |
|-------------|---------------|
| EVM | Full support |
| Solana (SVM) | Full support |
| Aptos | Full support |
| Sui | Partial (manual execution only) |
| TON | Partial (no token pool/registry queries) |

For non-EVM-specific workflow guidance (SDK chain classes, CLI options, wallet setup, tutorials), see [ccip-non-evm.md](ccip-non-evm.md).

### Non-EVM CLI Examples

```bash
# Send from Solana to EVM
ccip-cli send \
  --source solana-devnet \
  --dest ethereum-testnet-sepolia \
  --router <solana-router> \
  --receiver 0xYourEVMAddress \
  --transfer-tokens <token>=0.001

# Send from Aptos to EVM
ccip-cli send \
  --source aptos-testnet \
  --dest ethereum-testnet-sepolia \
  --router <aptos-router> \
  --receiver 0xYourEVMAddress \
  --transfer-tokens <token>=0.001

# Track any message (works for all chain families)
ccip-cli show <tx-hash-or-message-id> --wait

# Check lane latency
ccip-cli lane-latency solana-devnet ethereum-testnet-sepolia
```

## Testnet Tokens

For testnet flows, the standard test token is **CCIP-BnM** (burn-and-mint). It is the token provided by the Chainlink faucet and used in official CCIP tutorials. When the user is working on a testnet and has not specified a token, suggest CCIP-BnM as the default. LINK and WETH are also available on some testnet routes but CCIP-BnM is the most common starting point.

## Send and Bridge Workflow

### For token transfers

1. Verify that the route exists and the token is supported on that route.
2. Estimate the fee before proposing execution.
3. Present the on-chain preflight summary.
4. Ask for explicit approval.
5. Ask for a second confirmation immediately before execution.
6. Execute the transfer only after both confirmations.
7. If the user wants follow-up tracking, route that request to [ccip-monitoring.md](ccip-monitoring.md).

### For data-only message sends

1. Verify that the route exists.
2. Estimate the fee before proposing execution.
3. Present the on-chain preflight summary.
4. Ask for explicit approval.
5. Ask for a second confirmation immediately before execution.
6. Execute the send only after both confirmations.
7. If the user wants follow-up tracking, route that request to [ccip-monitoring.md](ccip-monitoring.md).

## Freshness Rules

1. Read [official-sources.md](official-sources.md) before answering route or token questions.
2. Use the CCIP Directory for route and token availability.
3. Use CLI docs for side-effecting command behavior.
4. Use SDK docs for programmatic integration behavior.
5. Do not hardcode live routes, lane counts, router assumptions, or token support.

## Refusal Rules

1. Refuse all mainnet write actions in this version.
2. Refuse to execute if the route, network, recipient, or transfer details are still ambiguous.
3. Refuse to skip the fee-estimation and approval steps for side-effecting actions.
4. If the user asks for unsupported behavior, explain the limit and offer the closest safe alternative.

