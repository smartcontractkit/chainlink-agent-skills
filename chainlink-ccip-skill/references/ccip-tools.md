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

1. Prefer the CCIP CLI for side-effecting on-chain actions such as fee estimation, sending, token support checks, and manual execution.
2. Use the CCIP SDK only when the user asks for a programmatic integration or code sample.
3. Route read-only monitoring, querying, searching, lane-latency checks, and message-status workflows to [ccip-monitoring.md](ccip-monitoring.md).
4. Do not switch to contract generation unless the user asks for it or the tool-first path cannot satisfy the goal.

Reference points:
- CLI docs: `https://docs.chain.link/ccip/tools/cli/`
- API docs: `https://docs.chain.link/ccip/tools/api/`
- SDK docs: `https://docs.chain.link/ccip/tools/sdk/`
- CLI package: `@chainlink/ccip-cli`
- SDK package: `@chainlink/ccip-sdk`

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

## Triggering Tests

These prompts should trigger this story pack:

- "Bridge USDC from Ethereum Sepolia to Base Sepolia using CCIP."
- "Send a CCIP test message to this receiver and tell me the fee first."
- "Use CCIP tools to move funds without writing contracts."
- "Check supported tokens on this CCIP route, then prepare a transfer."

These prompts should not trigger this story pack:

- "Write a CCIP sender contract in Solidity."
- "Add Foundry tests for my CCIP receiver."
- "Explain how CCIP works at a high level."

## Functional Tests

1. If the user asks to bridge funds without contracts, choose the tool-first path instead of generating contracts.
2. If the route is missing, ask for it before proposing execution.
3. If the token is unsupported on the route, stop and explain that constraint.
4. If the user wants a fee quote only, provide the non-executing path and do not ask for transaction approval.
5. If the user wants execution on mainnet, refuse the write action.
6. If execution proceeds on testnet, require both the preflight approval and the second confirmation.
7. After execution, direct read-only follow-up tracking to [ccip-monitoring.md](ccip-monitoring.md).

## Eval Checks

The workflow passes if it:

1. routes to tools instead of contracts for direct send and bridge requests
2. asks only for the missing inputs needed for the next safe step
3. verifies route and token support before proposing execution
4. estimates fees before execution
5. enforces approval and second-confirmation guardrails
6. refuses mainnet writes
7. hands off read-only follow-up tracking to the monitoring workflow

## A/B Prompt Pack

Use these prompts with and without the skill installed:

1. "Bridge 1 test USDC from Ethereum Sepolia to Base Sepolia using CCIP. Tell me the fee first and do not write contracts."
2. "Send a CCIP message with payload `hello world` to this receiver on testnet, but ask me before executing anything."
3. "Check whether this route supports USDC and, if it does, prepare the transfer flow without deploying contracts."
4. "I want to use CCIP tools, not Solidity, to move funds across chains. Walk me through the safest path."
