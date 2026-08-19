# CCT Workflow

Use only to create or register a Cross-Chain Token (CCT), configure pools/rate limits, or add networks. Generic sender/receiver, discovery, and monitoring use their dedicated references.

## Decision and source map

Name this Chainlink CCIP CCT onboarding and check the current CCIP Directory. Before any write artifact, if source, destination, or mainnet/testnet is missing, ask one focused question that establishes those route facts.

At the token stage, establish whether the token is new or existing and who controls token ownership and mint/burn authority. Then choose Token Manager or the repository's framework and burn-and-mint or lock-and-mint from those facts. At the registration stage, establish pool ownership and administrator permissions. Never guess the control model or authority. Sources:

- overview: `https://docs.chain.link/ccip/concepts/cross-chain-token/overview.md`
- registration/admin: `https://docs.chain.link/ccip/concepts/cross-chain-token/evm/registration-administration.md`
- Token Manager: `https://docs.chain.link/ccip/tutorials/evm/token-manager.md`
- EOA burn/mint: `https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens/register-from-eoa-burn-mint-hardhat.md`
- EOA lock/mint: `https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens/register-from-eoa-lock-mint-hardhat.md`
- rate limits: `https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens/update-rate-limiters-hardhat.md`
- more networks: `https://docs.chain.link/ccip/tutorials/evm/cross-chain-tokens/configure-additional-networks-hardhat.md`

## Auditable sequence

1. Establish the source, destination, and testnet/mainnet environment, then verify the route and token support with [discovery](ccip-discovery.md).
2. At the current token or registration stage, establish only the authority facts it needs and choose the matching Token Manager or official Foundry/Hardhat flow.
3. Explain the whole sequence, but request approval only for the current stage.
4. After explicit approval, emit the [main preflight](../SKILL.md#boundary-and-preflight) for that step. The user runs it from their own wallet; this skill never signs or sends. Verify the result before preparing the next approved step.

CCT registration and pool configuration require their own user-run approval and execution.

Rate-limit changes require a separate user-run approval and execution.

Each additional-network configuration requires a separate user-run approval and execution.

Keep ownership/admin authority explicit; use rate limits deliberately; prefer official administration over improvised scripts and the smallest safe rollout. Never collapse admin operations into an implicit action or proceed without required permission. Prepare write artifacts only for testnets; refuse mainnet write artifacts.
