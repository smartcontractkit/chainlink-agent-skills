# CCIP Contracts

Use this file only for contract-first CCIP requests where the user wants sender or receiver contracts, contract modifications, or project setup help for CCIP Solidity development.

## Trigger Conditions

Use this workflow for requests like:

- "Create contracts that send and receive a CCIP message."
- "Build a CCIP receiver for token transfers."
- "Help me wire up a sender and receiver for data plus tokens."
- "Add CCIP support to this Solidity project."
- "Fix the CCIP imports or setup in my Foundry project."

Do not use this workflow when the user clearly wants a tool-first send, bridge, or monitoring path without custom contracts.

## Supported Contract Shapes

Support these contract-first flows:

1. data-only sender and/or receiver
2. token-only sender and/or receiver
3. data-plus-token sender and/or receiver
4. contract sender with EOA receiver
5. EOA sender with contract receiver

## Security Defaults

Prefer secure, conservative implementations by default:

1. use simple, explicit access control for send functions and admin updates
2. verify destination chains before sending
3. verify source chains on receive
4. verify sender addresses on receive when the use case requires it
5. verify router addresses on receive
6. quote fees before sending
7. keep message reception separate from core business logic when possible
8. add fallback or recovery paths for receiver-side failures when the workflow needs them
9. avoid unnecessary abstraction, dynamic configurability, and hidden control flow

These defaults are grounded in the CCIP EVM best-practices docs and the `CCIPReceiver` and `IRouterClient` interfaces.

Reference points:

- Arbitrary messaging tutorial: `https://docs.chain.link/ccip/tutorials/evm/send-arbitrary-data`
- Token transfer tutorial: `https://docs.chain.link/ccip/tutorials/evm/transfer-tokens-from-contract`
- Programmable token transfer tutorial: `https://docs.chain.link/ccip/tutorials/evm/programmable-token-transfers`
- Defensive programmable token transfer tutorial: `https://docs.chain.link/ccip/tutorials/evm/programmable-token-transfers-defensive`
- EVM best practices: `https://docs.chain.link/ccip/concepts/best-practices/evm`
- `CCIPReceiver` API reference: `https://docs.chain.link/ccip/api-reference/evm/v1.6.1/ccip-receiver`
- `IRouterClient` API reference: `https://docs.chain.link/ccip/api-reference/evm/v1.6.1/i-router-client`

## Core Building Blocks

Use the official CCIP EVM contracts and interfaces as the starting point:

- `CCIPReceiver`
- `IRouterClient`
- `Client`

Important behaviors from the official references:

1. `CCIPReceiver.ccipReceive` only accepts calls from the authorized router.
2. If `ccipReceive` reverts, associated token transfers also revert and the message enters a failed state for manual execution.
3. `IRouterClient.getFee` should be used to estimate fees before sending.
4. `IRouterClient.isChainSupported` can be used to verify chain support.
5. If tokens and data are sent to an EOA receiver, only the tokens arrive.

## Contract Workflow

### Data-only contracts

1. Start from the official arbitrary-messaging tutorial pattern.
2. Build the outgoing message with `Client.EVM2AnyMessage`.
3. Quote fees before sending.
4. Use a receiver that validates the router and handles the payload explicitly.

### Token-only contracts

1. Start from the official token-transfer tutorial pattern.
2. Verify the route and token path before writing code that sends.
3. Keep token-transfer approvals and amount handling explicit.
4. Keep receiver-side token handling small and auditable.

### Data-plus-token contracts

1. Start from the official programmable-token-transfer tutorial pattern.
2. Prefer defensive receiver logic and explicit validation.
3. Separate receipt from business logic where practical.
4. If the receiver expects both tokens and data, warn about failure modes where data handling can revert after token delivery.
5. When that risk matters, suggest the defensive example pattern from the official defensive tutorial instead of a naive receiver.

## Setup Guidance

### Foundry preferred path

Prefer Foundry for Solidity CCIP contract work unless the user explicitly wants another framework.

Use tagged installs rather than assuming the repository default branch matches the desired contract release.

Common install pattern:

```bash
forge install smartcontractkit/chainlink-ccip@contracts-ccip-v<version>
forge install smartcontractkit/chainlink-evm@contracts-v<version>
```

Common remappings:

```text
@chainlink/contracts/=lib/chainlink-evm/contracts/
@chainlink/contracts-ccip/=lib/chainlink-ccip/chains/evm/
@chainlink/contracts-ccip/contracts/=lib/chainlink-ccip/chains/evm/contracts/
```

If CCIP imports pull in OpenZeppelin contracts, install the exact versions required by those imports. In practice, this often means one or both of:

```text
@openzeppelin/contracts@4.8.3/=lib/openzeppelin-contracts-4.8.3/contracts/
@openzeppelin/contracts@5.3.0/=lib/openzeppelin-contracts-5.3.0/contracts/
```

Additional remappings may be required in projects that also depend on Chainlink ACE or related packages:

```text
@chainlink/policy-management/=lib/chainlink-ace/packages/policy-management/src/
```

### Hardhat and npm

If the current repository is already a Hardhat project, use Hardhat. If the user explicitly asks for Hardhat, use Hardhat. Otherwise default to Foundry.

Use the same version discipline in npm package setup. If OpenZeppelin aliases are needed, call them out explicitly in `package.json`, for example:

```json
{
  "dependencies": {
    "@openzeppelin/contracts-4.8.3": "npm:@openzeppelin/contracts@4.8.3",
    "@openzeppelin/contracts-5.3.0": "npm:@openzeppelin/contracts@5.3.0"
  }
}
```

Align the package versions with the imports the project actually uses. Prefer the existing project structure instead of forcing a Foundry-first shape onto a Hardhat repository.

Local simulation and local contract testing are handled separately. Do not load local-testing guidance speculatively from this file.

## Freshness Rules

1. Read [official-sources.md](official-sources.md) before using live route, token, or chain data in generated contracts or setup guidance.
2. Use CCIP Docs for contract patterns, tutorials, interfaces, and best practices.
3. Use CCIP Directory for route and token availability.
4. Do not hardcode current routes, token support, or router assumptions without verification.

## Refusal Rules

1. Refuse mainnet deployment or any other mainnet write action in this version.
2. Refuse to guess package versions or remappings when imports clearly indicate a different dependency graph.
3. If a safer simple design can satisfy the request, do not generate a more complex architecture by default.

## Triggering Tests

These prompts should trigger this story pack:

- "Create a CCIP sender and receiver in Solidity."
- "Build a token-transfer receiver using CCIPReceiver."
- "Add programmable token transfer support to this CCIP contract."
- "Fix my Foundry CCIP imports and remappings."

These prompts should not trigger this story pack:

- "Bridge funds with CCIP tools."
- "Show me the status of this message."
- "Which tokens are supported on this route?"

## Functional Tests

1. If the user asks for contracts, choose the contract-first path instead of CLI or API workflows.
2. If the user asks for data-only, token-only, or data-plus-token support, generate the matching shape rather than a one-size-fits-all contract.
3. If the request is a receiver contract, preserve router validation and receive-side checks.
4. If the request needs project setup help, prefer the Foundry tagged-install path by default.
5. If OpenZeppelin import versions are split, call that out explicitly and align remappings instead of guessing.
6. If the user asks for mainnet deployment, refuse the write step but continue with safe code-generation help.
7. If the request would be safer with a smaller design, generate the smaller design.
8. If the request mixes token and data delivery with receiver-side state changes, surface the defensive-example option explicitly.

## Eval Checks

The workflow passes if it:

1. routes contract requests away from tool-first flows
2. defaults to secure, conservative patterns
3. verifies or preserves chain, sender, and router checks where relevant
4. quotes fees before sending
5. prefers Foundry tagged installs and explicit remappings for CCIP Solidity work
6. keeps receiver logic simple and auditable
7. surfaces EOA-receiver behavior and defensive receiver patterns when relevant

## A/B Prompt Pack

Use these prompts with and without the skill installed:

1. "Create a minimal CCIP sender and receiver in Solidity for arbitrary messaging on testnet, with secure defaults."
2. "Build a programmable token-transfer CCIP receiver and keep the receive-side business logic small and auditable."
3. "My Foundry project cannot resolve `@chainlink/contracts-ccip` imports. Fix the install and remappings using the safest path."
4. "I need a token-only CCIP sender/receiver pair. Prefer a boring, security-first implementation over abstraction."
