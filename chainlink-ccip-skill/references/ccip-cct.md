# CCT Workflow

Use this file only when the user wants to create a token, register it as a CCT, configure token pools, set rate limits, or add networks for a CCT lane.

## Trigger Conditions

Use this workflow for requests like:

- "Create a token and enable it as a CCT."
- "Register this token as a CCT using burn and mint."
- "Enable this token on a CCIP lane."
- "Set token pool rate limits for this CCT."
- "Add another network to this CCT setup."

Do not use this workflow for generic sender/receiver contracts, plain route discovery, or message-status monitoring.

## Default Path

1. Treat CCT work as a multi-step contract and administration workflow, not a one-shot action.
2. If the user wants the fastest no-code or low-code path, prefer Token Manager first.
3. If the user is already in a Hardhat or Foundry repo, stay in that framework and use the matching official tutorial path.
4. If no framework is established and the user wants a code path, default to the simplest official registration tutorial path.
5. Require explicit approval before every state-changing step.

Reference points:

- CCT overview: `https://docs.chain.link/ccip/concepts/cross-chain-token/overview`
- Registration and administration: `https://docs.chain.link/ccip/concepts/cross-chain-token/evm/registration-administration`
- Token Manager: `https://docs.chain.link/ccip/tutorials/evm/token-manager`
- Register from an EOA (Burn & Mint): `https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens/register-from-eoa-burn-mint-hardhat`
- Register from an EOA (Lock & Mint): `https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens/register-from-eoa-lock-mint-hardhat`
- Set token pool rate limits: `https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens/update-rate-limiters-hardhat`
- Configure additional networks: `https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens/configure-additional-networks-hardhat`

## Core Decisions

Clarify these before proposing execution:

1. Is the token new or existing?
2. Does the user want a no-code or low-code path through Token Manager, or a repo-based code path?
3. Which token handling mechanism fits the setup: burn and mint or lock and mint?
4. Which source and destination networks are in scope?
5. Does the user only want registration, or also rate limits and additional network configuration?

Ask only the missing questions needed for the next safe step.

## Workflow

### Step 1: Choose the path

1. If the user wants the simplest self-serve path, use Token Manager.
2. If the user wants repo-based execution, use the matching official Hardhat or Foundry registration tutorial path.
3. If the repo is already Hardhat, stay in Hardhat.
4. If the repo is already Foundry, stay in Foundry.

### Step 2: Choose the token handling mechanism

1. Use burn and mint when that matches the token control model.
2. Use lock and mint when that matches the token control model.
3. Do not guess the mechanism if ownership or mint/burn authority is unclear.

### Step 3: Verify networks and route

1. Use [ccip-discovery.md](ccip-discovery.md) to verify route and network support before proposing any state-changing step.
2. Confirm whether the user is working on testnet or mainnet.
3. Refuse mainnet writes in this version.

### Step 4: Register and configure

1. Break the workflow into separate user-approved steps.
2. Present one preflight summary per state-changing step.
3. After each step, verify the result before proposing the next step.
4. Treat rate-limit changes as a distinct administrative step, not as a silent default.
5. Treat additional-network configuration as a distinct step, not as a silent default.

## Security and Administration Rules

1. Keep ownership and administrative authority explicit.
2. Do not guess token ownership, mint authority, pool ownership, or admin permissions.
3. Prefer the official registration and administration flows over improvised custom admin scripts.
4. Use rate limits deliberately and explicitly.
5. Keep the step order small and auditable.
6. If a safer smaller scope can satisfy the user, do not push them into a broader CCT rollout.

## Freshness Rules

1. Read [official-sources.md](official-sources.md) before using live route or network facts.
2. Use [ccip-discovery.md](ccip-discovery.md) to confirm routes and token support before CCT steps that depend on them.
3. Do not hardcode current route availability or token support.

## Refusal Rules

1. Refuse all mainnet write actions in this version.
2. Refuse to collapse multiple CCT admin steps into a single implicit action.
3. Refuse to guess burn-and-mint vs lock-and-mint when the token control model is unclear.
4. Refuse to proceed when required ownership or admin permissions are not established.

