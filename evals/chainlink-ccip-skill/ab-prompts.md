# A/B Prompts

Use the same prompt with and without the skill installed.

## Tool-First Sends and Bridging

1. "Bridge 0.01 test USDC from Ethereum Sepolia to Base Sepolia using CCIP. Tell me the fee first and do not write contracts."
2. "Send a CCIP message with payload `hello world` to this receiver on testnet, but ask me before executing anything."
3. "Check whether this route supports USDC and, if it does, prepare the transfer flow without deploying contracts."
4. "I want to use CCIP tools, not Solidity, to move funds across chains. Walk me through the safest path."

## Contract-First Sender and Receiver Generation

1. "Create a minimal CCIP sender and receiver in Solidity for arbitrary messaging on testnet, with secure defaults."
2. "Build a programmable token-transfer CCIP receiver and keep the receive-side business logic small and auditable."
3. "My Foundry project cannot resolve `@chainlink/contracts-ccip` imports. Fix the install and remappings using the safest path."
4. "I need a token-only CCIP sender/receiver pair. Prefer a boring, security-first implementation over abstraction."
5. "I want a contract sender but an EOA receiver. If I send both data and tokens, what actually arrives and how should I design around that?"
6. "My receiver handles both tokens and data. If the data path can revert, show me the defensive CCIP receiver pattern that avoids unsafe retry behavior."

## Chainlink Local Simulation and Testing

1. "Add a local CCIP simulator test for this Foundry sender/receiver pair before we touch testnet."
2. "This is a Hardhat repo. Add Chainlink Local coverage for the CCIP receiver without switching frameworks."
3. "Use the simplest local simulator setup for this token-transfer contract, and only suggest a fork if it is truly needed."
4. "My receiver handles tokens and data. Add a local test that covers the failure case and point me to the defensive pattern if needed."
5. "In this fork test, compare `ccipLocalSimulatorFork.getNetworkDetails(block.chainid)` with the CCIP Directory and fix any mismatch using explicit network config."

## Monitoring and Status

1. "Show me the status of this CCIP tx hash and explain the lifecycle in plain English."
2. "Search CCIP messages for this sender and summarize what happened."
3. "Help me diagnose this failed CCIP message, but do not execute anything yet."
4. "Check lane latency for this route and tell me whether I should treat it as a route problem or just current performance."

## Route and Token Discovery

1. "Are Ethereum Sepolia and Base Sepolia connected by CCIP, and is that route testnet or mainnet?"
2. "Which tokens are supported on the Arbitrum Sepolia to Base Sepolia route?"
3. "Can I move USDC on this CCIP route, or is the route available but the token unsupported?"
4. "Tell me whether this is a route-availability problem or just a lane-performance problem."

## CCT Workflows

1. "Create a token and enable it as a CCT on testnet, but break the work into explicit approved steps."
2. "Use the simplest path to register this existing token as a burn-and-mint CCT."
3. "Set token pool rate limits for this CCT and explain each admin step before doing anything."
4. "Add another network to this CCT setup, but verify the route first and ask me before every write."
