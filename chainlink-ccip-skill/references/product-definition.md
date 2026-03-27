# Scope Reference

Use this file as the minimal public scope contract for `chainlink-ccip-skill`.

## Purpose

Route CCIP-related requests to the simplest valid path:

1. Tool-first when the user can accomplish the goal through CCIP CLI, API, or SDK
2. Contract-first when the user needs sender/receiver contracts or token setup work

## In Scope For v1

1. Intent-based CCIP message sending through CCIP CLI
2. Intent-based fund bridging through CCIP tools when contracts are unnecessary
3. Sender and receiver contract generation for CCIP
4. Data-only, token-only, and data-plus-token contract flows
5. Message monitoring and status lookup
6. Chain connectivity checks on testnet and mainnet
7. Route token availability lookup
8. CCT creation and lane enablement, if executable safely

## Out of Scope For v1

1. Automatic on-chain state changes without explicit user approval
2. Non-EVM chain family execution paths
3. MCP server integration

## Required Safety Behavior

1. Ask the user which route or network they want instead of assuming one
2. Before any on-chain action, explain the proposed action clearly enough for approval
3. Refuse all mainnet write actions in v1
4. Allow only read-only mainnet lookups in v1
5. Prefer official Chainlink sources for live CCIP facts that can change over time

## Testing Requirement

Every in-scope user story must eventually have:

1. Triggering tests
2. Functional tests
3. Eval tests
4. Example prompts for A/B testing with and without the skill installed
