# Trigger Tests

Use these to check whether the right workflow pack activates and whether nearby workflows stay dormant.

## Tool-First Sends and Bridging

Should trigger:

1. "Bridge USDC from Ethereum Sepolia to Base Sepolia using CCIP."
2. "Send a CCIP message for me, but tell me the fee first."
3. "Use CCIP tools to move funds without writing contracts."

Should not trigger:

1. "Create a CCIP sender contract in Solidity."
2. "Show me the status of this CCIP message."

## Contract-First Sender and Receiver Generation

Should trigger:

1. "Create a CCIP sender and receiver in Solidity."
2. "Build a token-transfer CCIP receiver with secure defaults."
3. "Fix my Foundry CCIP imports and remappings."

Should not trigger:

1. "Bridge funds using CCIP tools."
2. "Add Chainlink Local tests for this repo."

## Chainlink Local Simulation and Testing

Should trigger:

1. "Add Chainlink Local tests for this CCIP sender and receiver."
2. "This repo is Hardhat. Add a local simulator test."
3. "Create a forked-environment CCIP test only if the local simulator is not enough."

Should not trigger:

1. "Show me the status of this message."
2. "Register this token as a CCT."

## Monitoring and Status

Should trigger:

1. "Check whether my CCIP message landed."
2. "Search CCIP messages for this sender."
3. "Help me inspect this failed CCIP message."

Should not trigger:

1. "Bridge funds using CCIP."
2. "Which tokens are supported on this route?"

## Route and Token Discovery

Should trigger:

1. "Are Ethereum Sepolia and Base Sepolia connected by CCIP?"
2. "Is this route testnet or mainnet?"
3. "Which tokens are supported on this route?"

Should not trigger:

1. "What is the lane latency for this route?"
2. "Create a CCIP receiver contract."

## CCT Workflows

Should trigger:

1. "Create a token and enable it as a CCT."
2. "Register this token as a burn-and-mint CCT."
3. "Set token pool rate limits for this CCT."

Should not trigger:

1. "Create a generic CCIP sender contract."
2. "Show me the status of this message."
