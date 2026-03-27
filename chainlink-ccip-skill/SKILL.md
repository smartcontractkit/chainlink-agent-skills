---
name: chainlink-ccip-skill
description: "Handle Chainlink CCIP requests with a safety-first workflow. Use for CCIP message sends, fund bridging through CCIP tools, sender and receiver contract development, message status lookup, route connectivity checks, supported token discovery, or CCT setup. Ask for missing route details, require explicit approval before any on-chain action, refuse mainnet writes in v1, and prefer secure, conservative contract patterns."
---

# Chainlink CCIP Skill

## Overview

Route CCIP requests to the simplest valid path while keeping side effects tightly controlled.

## Progressive Disclosure

1. Keep this file as the default guide.
2. Read [references/product-definition.md](references/product-definition.md) only when you need to confirm scope or safety constraints.
3. Read [references/user-stories.md](references/user-stories.md) only when the request is ambiguous or you need routing examples.
4. Do not load reference files speculatively.

## Routing

1. Use a tool-first path for sending without custom contracts, bridging funds, status lookup, connectivity checks, and route or token discovery.
2. Use a contract-first path for sender and receiver contract work and CCT setup flows.
3. Ask one focused question if the route, network, token, amount, or target contracts are missing.
4. Proceed without approval only for read-only work such as explanation, discovery, status checks, and code generation.
5. Trigger the approval protocol before any action that could create, transfer, deploy, register, enable, or configure on-chain state.
6. Do not assume this skill is the only capability available. Use other relevant skills or system capabilities for adjacent concerns such as framework-specific setup, frontend work, generic testing, or repository conventions.

## Safety Guardrails

1. Never execute any on-chain action without explicit user approval.
2. Never assume the intended route, lane, network, token, amount, or destination.
3. Refuse all mainnet write actions in v1.
4. Allow read-only mainnet lookups in v1.
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
