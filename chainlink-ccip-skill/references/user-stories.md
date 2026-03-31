# User Stories

## Status

This document freezes the current story inventory for `chainlink-ccip-skill`.

## Story 1: Send a CCIP Message or Bridge Funds Without Writing Contracts

### User intent

- "Bridge USDC from one chain to another using CCIP."
- "Send a CCIP message for me."
- "I do not want to build sender and receiver contracts. I just want to move funds."

### Expected route

Tool-first.

### Target behavior

1. Ask which route the user wants instead of assuming one
2. Use CCIP CLI, API, or SDK when contracts are unnecessary
3. Explain the proposed action before any on-chain execution
4. Ask for approval before execution

## Story 2: Build CCIP Sender and Receiver Contracts

### User intent

- "Create contracts that send and receive a CCIP message."
- "Build a CCIP receiver for token transfers."
- "Help me wire up a sender and receiver for data plus tokens."

### Expected route

Contract-first.

### Target behavior

1. Support data-only, token-only, and data-plus-token flows
2. Prefer secure, boring and maintainable contract patterns
3. Incorporate project setup guidance when imports or dependencies are a blocker

## Story 3: Monitor, Inspect, and Explain Message Status

### User intent

- "Check whether my CCIP message landed."
- "Show me the status of the message I sent."
- "Help me inspect a stuck or failed message."

### Expected route

Tool-first.

### Target behavior

1. Prefer CLI, API, or explorer-style workflows over custom code
2. Explain the current state clearly
3. Surface the next diagnostic step when status is incomplete or unexpected

## Story 4: Discover Routes and Supported Tokens

### User intent

- "Are these two chains connected by CCIP?"
- "Is this route testnet or mainnet?"
- "Which tokens can I move on this route?"

### Expected route

Tool-first.

### Target behavior

1. Use freshness-aware sources for route and token data
2. Distinguish clearly between testnet and mainnet
3. Avoid guessing about supported lanes or assets

## Story 5: Create a Token and Enable It as a CCT

### User intent

- "Create a token and make it available as a CCT."
- "Help me enable this token on a CCIP lane."

### Expected route

Contract-first with guarded execution steps.

### Target behavior

1. Break the workflow into explicit steps
2. Explain prerequisites and partial completion states
3. Ask for approval before every on-chain action
4. Refuse mainnet execution in this version

## Story 6: Add Chainlink Local Simulation and Testing

### User intent

- "Add Chainlink Local tests for this CCIP sender and receiver."
- "Set up local CCIP simulation before we touch testnet."
- "Use Chainlink Local in this Foundry or Hardhat repo."

### Expected route

Contract-first with local-testing workflow guidance.

### Target behavior

1. Prefer Chainlink Local before live-network testing
2. Stay in the repository's existing framework unless the user asks to switch
3. Distinguish clearly between local simulation and forked-environment testing
4. Verify fork-network details against the CCIP Directory when fork tests are used

## Cross-Story Testing Requirement

Every story must eventually include:

1. Triggering tests
2. Functional tests
3. Eval tests
4. A/B prompts for with-skill and without-skill comparisons
