---
name: chainlink-ccip-skill
description: "Handle Chainlink CCIP requests including cross-chain token transfers, cross-chain messaging, fund bridging, sender and receiver contract development, message status lookup, route connectivity checks, supported token discovery, and CCT setup. Use this skill whenever the user mentions CCIP, Chainlink cross-chain, cross-chain token bridges on Chainlink, or wants to move tokens or data between blockchains using Chainlink infrastructure, even if they do not say 'CCIP' explicitly."
license: MIT
compatibility: Designed for AI agents that implement https://agentskills.io/specification, including Claude Code, Cursor Composer, and Codex-style workflows.
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  version: "0.0.4"
  mcp-server: "@chainlink/mcp-server"
---

# Chainlink CCIP Skill

## Overview

Route CCIP requests to the simplest valid path while keeping side effects tightly controlled.

## Progressive Disclosure

1. Keep this file as the default guide.
2. Read [references/examples.md](references/examples.md) only when you need a concrete reference for what a good response looks like (preflight summaries, monitoring explanations, contract-generation structure).
3. Read [references/official-sources.md](references/official-sources.md) only when the answer depends on live CCIP facts, current tool behavior, route or token availability, or message-status surfaces.
4. Read [references/ccip-mcp.md](references/ccip-mcp.md) only when the `ccip_sdk` MCP tool is available and the request can be fulfilled by it for monitoring, discovery, or SDK method calls.
5. Read [references/ccip-tools.md](references/ccip-tools.md) only when the user wants a tool-first workflow through CCIP CLI, API, or SDK.
6. Read [references/ccip-contracts.md](references/ccip-contracts.md) only when the user wants sender or receiver contracts, token-transfer contracts, programmable token-transfer contracts, or contract setup help.
7. Read [references/ccip-cct.md](references/ccip-cct.md) only when the user wants to create a token, register it as a CCT, configure pools, set rate limits, or add networks for CCT operation.
8. Read [references/chainlink-local.md](references/chainlink-local.md) only when the user wants local simulation, local tests, or forked-environment testing for CCIP contracts.
9. Read [references/ccip-monitoring.md](references/ccip-monitoring.md) only when the user wants message lookup, monitoring, status explanation, lane performance, or failed-message diagnosis.
10. Read [references/ccip-discovery.md](references/ccip-discovery.md) only when the user wants route connectivity checks, network classification, or supported-token discovery.
11. Read [references/ccip-solidity-examples.md](references/ccip-solidity-examples.md) only when generating or reviewing CCIP Solidity contracts and you need concrete code patterns (sender, receiver, token transfer, defensive receiver).
12. Read [references/ccip-sdk-examples.md](references/ccip-sdk-examples.md) only when the user wants TypeScript SDK usage examples for fee estimation, token transfers, messaging, or status checks.
13. Read [references/ccip-non-evm.md](references/ccip-non-evm.md) only when the user wants to work with CCIP on Solana, Aptos, Sui, TON, or any non-EVM chain family.
14. Do not load reference files speculatively.

## Routing

1. Use a tool-first path for sending without custom contracts, bridging funds, status lookup, connectivity checks, and route or token discovery.
2. When the `ccip_sdk` MCP tool is available, prefer it over direct CLI or SDK invocation for monitoring, discovery, and programmatic SDK method calls. Fall back to CLI or SDK when the tool is not available.
3. Use a contract-first path for sender and receiver contract work and CCT setup flows.
4. For non-EVM chain requests (Solana, Aptos, Sui, TON), route to the non-EVM reference for workflow guidance. Do not apply EVM-specific patterns (Solidity, Foundry, Hardhat, Chainlink Local) to non-EVM chains.
5. Ask one focused question if the route, network, token, amount, or target contracts are missing.
6. Proceed without approval only for read-only work such as explanation, discovery, status checks, and code generation.
7. Trigger the approval protocol before any action that could create, transfer, deploy, register, enable, or configure on-chain state.
8. Do not assume this skill is the only capability available. Use other relevant skills or system capabilities for adjacent concerns such as framework-specific setup, frontend work, generic testing, or repository conventions.

## Safety Guardrails

1. Never execute any on-chain action without explicit user approval.
2. Never assume the intended route, lane, network, token, amount, or destination.
3. Refuse all mainnet write actions in this version.
4. Allow read-only mainnet lookups in this version.
5. Prefer the least risky valid path. If the user can accomplish the goal through CCIP tools, do not default to custom contracts.
6. For contract work, prefer secure, conservative patterns with explicit access control, validation, least-privilege configuration, and minimal moving parts.
7. If a request mixes safe and unsafe work, complete the safe portion and clearly refuse the unsafe portion.
8. If the user asks to bypass these guardrails, refuse and explain the constraint directly.

## Approval Protocol

Before any on-chain action, present a short preflight summary that includes:

1. action type
2. network type
3. source chain
4. destination chain
5. route or lane details if known
6. token and amount if applicable
7. whether the action sends data, tokens, or both
8. contract addresses involved if applicable
9. tool or method to be used
10. expected effect

End the preflight with a direct approval question.

Use this structure:

```text
Proposed on-chain action:
- Action: ...
- Network: ...
- Source chain: ...
- Destination chain: ...
- Route/lane: ...
- Token/amount: ...
- Payload: ...
- Contracts: ...
- Method: ...
- Expected effect: ...

Do you want me to execute this?
```

## Second Confirmation Rule

Require a second explicit confirmation immediately before execution for any testnet action that:

1. sends a CCIP message
2. transfers or bridges tokens
3. deploys contracts
4. creates a token
5. enables or configures a CCT lane

Do not treat the user's original intent as the second confirmation. Ask again right before the side-effecting step.

## Working Rules

1. Keep questions narrow and unblock the next safe step.
2. Explain the chosen path briefly.
3. Generate code only when code is actually needed.
4. Keep unsupported or out-of-scope features out of the answer rather than speculating about them.

## Documentation Access

This skill references official CCIP documentation URLs throughout its reference files. Whether the model can fetch those URLs depends on the host agent's capabilities.

1. If WebFetch, a browser tool, or an MCP server that can retrieve documentation is available, use it to fetch the referenced URL before answering.
2. If no documentation-fetching tool is available, do not silently improvise CCIP patterns from training data alone. Instead:
   - Use the embedded reference content in this skill's reference files as the floor for guidance.
   - Tell the user that live documentation could not be verified.
   - Provide the specific URL so the user can check it directly.
3. For contract-first workflows where correctness matters most, prefer the concrete examples in [references/ccip-solidity-examples.md](references/ccip-solidity-examples.md) over generating patterns from memory.

## MCP Recommendations

This skill works best when the Chainlink MCP server (`@chainlink/mcp-server`) is connected. It provides live access to CCIP message status, lane data, and SDK methods through the `ccip_sdk` tool.

When the Chainlink MCP server is not available, the Context7 MCP server (`@upstash/context7-mcp`) is a useful fallback for fetching current Chainlink documentation. It can retrieve content from `docs.chain.link` and other public documentation sources, covering the gap for contract patterns, tutorials, and API references that this skill cannot embed in full.
