# Functional Tests

These are behavior checks for the currently shipped workflows.

## Tool-First Sends and Bridging

1. Choose the tool-first path instead of contract generation for direct send/bridge requests.
2. Ask for missing route, network, recipient, token, or amount before proposing execution.
3. Verify route and token support before proposing execution.
4. Estimate fees before any side-effecting action.
5. Require preflight approval and a second confirmation before testnet execution.
6. Refuse mainnet writes.
7. Hand off follow-up tracking to the monitoring workflow.

## Contract-First Sender and Receiver Generation

1. Choose the contract-first path instead of CLI/API workflows when the user asks for contracts.
2. Generate the correct shape for data-only, token-only, or data-plus-token requests.
3. Preserve router, chain, sender, and receive-side validation where relevant.
4. Prefer simple, security-first designs over abstraction-heavy scaffolding.
5. Default to Foundry unless the repo is already Hardhat or the user explicitly asks for Hardhat.
6. Surface EOA receiver behavior correctly when tokens and data are sent together.
7. Suggest the defensive programmable-token-transfer pattern when receiver-side failure modes matter.

## Chainlink Local Simulation and Testing

1. Choose Chainlink Local for local testing requests instead of live-network guidance.
2. Stay in the repo’s existing framework when it is clearly Foundry or Hardhat.
3. Default to the no-fork simulator first.
4. Escalate to forked environments only when justified.
5. In fork tests, compare simulator network details against the CCIP Directory and prefer the directory when they differ.
6. Preserve the same security checks in tests that the contracts should have outside local simulation.

## Monitoring and Status

1. Use API-first behavior for monitoring, querying, and search-style requests.
2. Use CLI lookup/debug paths when the user wants direct command-line interaction.
3. Keep diagnosis read-only by default.
4. Treat `manual-exec` as remediation, not normal monitoring.
5. Refuse mainnet side-effecting remediation.
6. Distinguish message lifecycle explanation from raw output dumping.
7. Distinguish route existence questions from lane-performance questions.

## Route and Token Discovery

1. Use the CCIP Directory as the primary source of truth.
2. Answer mainnet vs testnet classification explicitly.
3. Distinguish route-exists-but-token-unsupported from route-missing.
4. Use CLI `get-supported-tokens` only as a complementary check.
5. Redirect lane-performance questions to monitoring.
6. Keep the workflow read-only.

## CCT Workflows

1. Choose the dedicated CCT workflow instead of generic contract generation.
2. Offer Token Manager first when the user wants the simplest path.
3. Clarify burn-and-mint vs lock-and-mint before proposing execution.
4. Verify route/network support before any state-changing step.
5. Break registration, rate-limit updates, and additional-network configuration into separate approved steps.
6. Refuse mainnet writes.
7. Do not guess ownership, admin permissions, or token-control assumptions.
