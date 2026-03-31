# Chainlink Local

Use this file only for CCIP local simulation, local contract tests, or forked-environment testing.

## Trigger Conditions

Use this workflow for requests like:

- "Add local CCIP tests for these contracts."
- "Simulate this CCIP flow locally before testnet."
- "Use Chainlink Local in this Foundry project."
- "This is a Hardhat repo. Add CCIP local simulator tests."
- "Run this in a forked environment first."

Do not use this workflow for live-network execution, message monitoring, or basic contract generation without a local-testing goal.

## Default Path

1. Prefer Chainlink Local for local simulation and local contract tests.
2. Prefer the no-fork local simulator first.
3. Use the current repo framework when it is already clearly Foundry or Hardhat.
4. If the repo is not already committed to a framework and the user does not ask for one, default to Foundry.
5. Use forked environments only when the user needs higher realism or specifically asks for a forked-network workflow.

## Official References

Start from these official docs:

- Overview: `https://docs.chain.link/chainlink-local`
- Foundry local simulator: `https://docs.chain.link/chainlink-local/build/ccip/foundry/local-simulator`
- Foundry forked environments: `https://docs.chain.link/chainlink-local/build/ccip/foundry/local-simulator-fork`
- Hardhat local simulator: `https://docs.chain.link/chainlink-local/build/ccip/hardhat/local-simulator`
- Hardhat forked environments: `https://docs.chain.link/chainlink-local/build/ccip/hardhat/local-simulator-fork`

Core simulator types:

- `CCIPLocalSimulator`
- `CCIPLocalSimulatorFork`
- `CCIPLocalSimulatorFork JS` - for Hardhat users who want a JavaScript interface to the forked simulator

## Setup Guidance

### Common package

Use the official local package:

- npm or yarn: `@chainlink/local`

### Foundry

Use the official Foundry install path:

```bash
forge install smartcontractkit/chainlink-local
```

Add the remapping:

```text
@chainlink/local/=lib/chainlink-local/
```

Import the simulator from the local package:

```solidity
import {CCIPLocalSimulator} from "@chainlink/local/src/ccip/CCIPLocalSimulator.sol";
```

### Hardhat

Use the existing Hardhat repo if the project is already Hardhat or the user explicitly wants Hardhat.

Install the package:

```bash
npm install @chainlink/local
```

Prefer the starter-kit structure from the official docs when the user wants the quickest working path.

## Local Testing Workflow

### No-fork local simulator

This is the default path.

1. Start with the official local simulator guide for the current framework.
2. Use the simulator to obtain local router, LINK, token, and chain-selector configuration.
3. Write or update tests for the specific CCIP path the user cares about.
4. Keep the first test small and reproducible.
5. Move to forked environments only after the no-fork path is working or when the user explicitly needs the fork.

### Forked environments

Use forked environments only when the user needs to test against realistic chain state or current deployed contracts.

1. Confirm that the user actually needs a fork.
2. Keep the fork scope narrow.
3. Use the official forked-environment guide for the current framework.
4. Compare config details from `ccipLocalSimulatorFork.getNetworkDetails(block.chainid);` against the CCIP Directory.
5. If the simulator details differ from the CCIP Directory, treat the CCIP Directory as the source of truth.
6. When fork-network details are missing or need correction, configure them explicitly with `setNetworkDetails(...)` using CCIP Directory values.
7. Do not introduce fork complexity when the no-fork simulator already answers the question.

## What To Test First

Prioritize:

1. sender and receiver happy path
2. token-only transfer path
3. data-only message path
4. receiver validation and revert behavior
5. defensive receiver behavior when token-plus-data flows can fail
6. forked-network detail alignment against the CCIP Directory when forks are used

## Security and Design Rules

1. Local simulation is not a reason to relax security defaults in generated contracts.
2. Preserve the same router, chain, sender, and access-control checks the contract should have outside local tests.
3. If the local test exposes a risky receiver pattern, suggest the defensive programmable-token-transfer example.
4. Keep test setup simple enough that a developer can rerun it quickly.
5. In fork tests, prefer verified CCIP Directory values over simulator defaults when they differ.

## Triggering Tests

These prompts should trigger this story pack:

- "Add Chainlink Local tests for this CCIP sender and receiver."
- "This repo is Foundry. Add a local simulator test before I try testnet."
- "This is a Hardhat project. Use Chainlink Local instead of changing frameworks."
- "Create a forked-environment CCIP test only if the basic local simulator is not enough."

These prompts should not trigger this story pack:

- "Bridge funds using the CLI."
- "Show me the status of this message."
- "Create a CCIP contract but do not add tests."

## Functional Tests

1. If the user asks for local testing, choose Chainlink Local instead of live-network execution.
2. If the repo is already Hardhat, stay in Hardhat.
3. If the repo is already Foundry, stay in Foundry.
4. If no framework is established, default to Foundry.
5. If a no-fork test can satisfy the goal, do not jump to forked environments.
6. If a fork is requested, use the official forked-environment guide for the chosen framework.
7. In fork tests, compare `getNetworkDetails(...)` output against the CCIP Directory and correct mismatches with explicit config.
8. Preserve security checks in the tested contracts.

## Eval Checks

The workflow passes if it:

1. routes local-testing requests into Chainlink Local instead of live-network workflows
2. keeps the repo in its existing framework when that choice is already made
3. defaults to the simplest reproducible local simulator path
4. escalates to forked environments only when justified
5. uses the CCIP Directory as the source of truth for fork-network details
6. preserves security checks in local tests
7. helps the user validate the contract before testnet

## A/B Prompt Pack

Use these prompts with and without the skill installed:

1. "Add a local CCIP simulator test for this Foundry sender/receiver pair before we touch testnet."
2. "This is a Hardhat repo. Add Chainlink Local coverage for the CCIP receiver without switching frameworks."
3. "Use the simplest local simulator setup for this token-transfer contract, and only suggest a fork if it is truly needed."
4. "My receiver handles tokens and data. Add a local test that covers the failure case and point me to the defensive pattern if needed."
