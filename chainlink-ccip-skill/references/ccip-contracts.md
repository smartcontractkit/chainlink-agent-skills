# CCIP Contracts

Use for EVM contract-first sender/receiver work, modifications, and Solidity project setup. For tool-first send/bridge/monitoring use [tools](ccip-tools.md); for Solana programs, Aptos/Sui Move, TON, or Canton use [non-EVM](ccip-non-evm.md).

## Shapes and invariants

Supported shapes: data-only, token-only, small programmable data-plus-token, defensive data-plus-token, contract→EOA, and EOA→contract. When a sender/receiver or generic sender is requested, emit the actual complete CCIP contracts immediately—not a plan, outline, file list, or completion summary—if constructor-injected router/LINK addresses suffice; do not wait for testnet names or runtime values. Emit exactly one final, internally consistent version of each contract: never present a broken draft followed by a replacement function, and resolve fee-token selection and Solidity mutability before output. A diagnosis request whose contracts were not pasted still gets the most likely causes from the described symptoms, and any specific requested replacement is emitted as actual code in the same response. A source-only request gets no prepared-action block, selected route/network, or deployment/send commands; it gets the command-free checklist below and exact wallet footer. Match the requested shape exactly: no token branches in data-only artifacts and no callbacks in explicitly token-only/no-callback artifacts. A receiver requested with secure/secured defaults, defensive handling, or a callback uses the active `DefensiveTokenReceiver`, never the passive vault. If the shape is otherwise ambiguous, recommend data-only as the simpler security-first default. Start code from [ccip-solidity-examples.md](ccip-solidity-examples.md) using only the selected shape's required imports.

For a source-only answer, follow the contracts with a concise, command-free checklist: configure verified router/LINK/selector values; fund the sender with the chosen testnet fee and transfer tokens; allowlist the destination on the sender and the exact source-selector/sender pair plus every accepted token on the receiver. Do not invent deployment commands, addresses, routes, or repository paths. Close with the exact wallet footer from the main boundary.

Conservative defaults:

- explicit send/admin access control; reject zero router/LINK constructor inputs and zero token/recipient/amount recovery inputs; validate destination before send;
- receiver validates the source-selector-and-sender pair together (a single pair-bound allowlist, never an independent global sender list) when required; inherited `CCIPReceiver.ccipReceive` admits only its router;
- a data-only pair validates the router through `CCIPReceiver`, then the source-selector-and-sender pair; deployment and setup remain user-run;
- every sender, including a generic sender, calls `IRouterClient.isChainSupported(destinationSelector)` and rejects an unsupported selector before `getFee` or `ccipSend`; a nonzero selector or owner allowlist alone is insufficient;
- every token-plus-data receiver requires at least one token entry, rejects zero amounts and non-allowlisted tokens, and accounts for every entry; never silently read only `destTokenAmounts[0]`;
- a small/auditable programmable receiver stays direct — no self-call, try/catch, or recovery — but its pair-bound sender allowlist, token allowlist, nonzero amounts, and accounting of every token entry are mandatory safety controls, not optional complexity; briefly explain that distinction. Keep receipt separate from business logic and add try/catch, failed-message storage, and recovery for a defensive receiver whose business logic may itself revert;
- if `ccipReceive` reverts, associated token transfer reverts and the message enters failed/manual-execution state;
- tokens plus data sent to an EOA deliver only the tokens;
- token-only delivery uses empty data, `gasLimit: 0`, zero-address/zero-amount checks, correct allowance when the transfer token is also the fee token, and an EOA or passive token-holding contract with no `CCIPReceiver`, `_ccipReceive`, callback allowlists, or callback claims; use this passive shape only when the user explicitly requests token-only/no-callback delivery;
- an explicit data, programmable-transfer, secure/secured receiver, defensive receiver, or callback request must retain its payload, nonzero destination gas, and active `CCIPReceiver` callback path;
- avoid dynamic configuration, hidden control flow, and unnecessary abstraction.

For testnet transfers, default to faucet/tutorial **CCIP-BnM** (burn-and-mint) unless the user chooses another token. Verify the route and token first.

| Shape | Required construction |
|---|---|
| Data | `Client.EVM2AnyMessage`, fee quote, router-supported destination check, explicit payload, validated receiver |
| Token only | route/token verification; router-supported destination check; explicit amount and router approvals with no allowance collision when the transfer token is also the fee token; zero-address/zero-amount checks; empty data, `gasLimit: 0`, and no callback receiver |
| Data + token, small/auditable | programmable-transfer pattern with payload, nonzero destination gas, router-supported destination check, and a pair-bound source-selector-and-sender receiver that validates and accounts for every allowed nonzero token entry, with no self-call, try/catch, or recovery |
| Data + token, defensive | same programmable-transfer pattern plus an active defensive callback receiver — pair-bound source authorization, allowed-token validation and complete amount accounting, concrete try/catch, failed-message storage, and recovery — whenever secure/secured defaults or callback handling are requested or payload handling could revert after token delivery |

## Local/testnet deployment order
These examples are for local use or testnets. Before an explicitly requested deployment, configuration, approval, registration, or send artifact, verify the router, LINK address, and route in the [CCIP Directory](https://docs.chain.link/ccip/directory/testnet). Every CCT/admin/contract/deployment/send executable artifact is user-run and must close, after all code and steps, with exactly: “This skill never signs or sends. You must sign and broadcast from your own wallet.” Never put a private key, signing secret, or placeholder for either on a command line; keep signing inside the user's wallet-controlled environment without exposing signing material to the agent.
For any mainnet deployment, configuration, admin, approval, or send artifact, provide no write artifact and say exactly: “I refuse mainnet write artifacts; testnet only.”

1. Deploy the receiver on the destination testnet.
2. Deploy the sender on the source testnet.
3. Allow the destination selector on the sender.
4. Allow the source selector and sender contract on the receiver.
5. Fund the sender with testnet LINK.
6. The user calls `sendMessage`.

Tutorials: arbitrary data `https://docs.chain.link/ccip/tutorials/evm/send-arbitrary-data.md`; tokens `https://docs.chain.link/ccip/tutorials/evm/transfer-tokens-from-contract.md`; programmable `https://docs.chain.link/ccip/tutorials/evm/programmable-token-transfers.md`; defensive `https://docs.chain.link/ccip/tutorials/evm/programmable-token-transfers-defensive.md`; best practices `https://docs.chain.link/ccip/concepts/best-practices/evm.md`; `CCIPReceiver` `https://docs.chain.link/ccip/api-reference/evm/v1.6.1/ccip-receiver.md`; `IRouterClient` `https://docs.chain.link/ccip/api-reference/evm/v1.6.1/i-router-client.md`.

## Project setup

Use the repository's established or explicitly requested framework: Hardhat stays Hardhat and Foundry stays Foundry. Default to Foundry only when neither is established or requested. Install tagged releases rather than assuming default branches; resolve `<version>` to the exact release tag from each repository's GitHub Releases page before running the command — never leave the placeholder in a command to run:

```bash
forge install smartcontractkit/chainlink-ccip@contracts-ccip-v<version>
forge install smartcontractkit/chainlink-evm@contracts-v<version>
```

```text
@chainlink/contracts/=lib/chainlink-evm/contracts/
@chainlink/contracts-ccip/=lib/chainlink-ccip/chains/evm/
@chainlink/contracts-ccip/contracts/=lib/chainlink-ccip/chains/evm/contracts/
```

Inspect installed CCIP imports before selecting OpenZeppelin versions: `CCIPReceiver` imports `IERC165`, and its version can differ from other dependencies. `forge install` always targets the default `lib/openzeppelin-contracts/` directory, so installing two OpenZeppelin versions back to back silently overwrites the first at that same path; install and rename one version at a time so each remapping points at the path that actually exists on disk:

```bash
forge install OpenZeppelin/openzeppelin-contracts@v4.8.3 --no-commit
mv lib/openzeppelin-contracts lib/openzeppelin-contracts-4.8.3
forge install OpenZeppelin/openzeppelin-contracts@v5.3.0 --no-commit
mv lib/openzeppelin-contracts lib/openzeppelin-contracts-5.3.0
```

```text
@openzeppelin/contracts@4.8.3/=lib/openzeppelin-contracts-4.8.3/contracts/
@openzeppelin/contracts@5.3.0/=lib/openzeppelin-contracts-5.3.0/contracts/
```

`CCIPReceiver` may instead require `5.0.2`; grep `lib/chainlink-ccip/` for `@openzeppelin`, install and rename that exact release the same way, and give it its own remapping pointed at its own renamed directory. ACE projects may also need:

```text
@chainlink/policy-management/=lib/chainlink-ace/packages/policy-management/src/
```

In existing/explicit Hardhat projects use npm with the same import-driven discipline. Aliases may be required:

```json
{"dependencies":{"@openzeppelin/contracts-4.8.3":"npm:@openzeppelin/contracts@4.8.3","@openzeppelin/contracts-5.3.0":"npm:@openzeppelin/contracts@5.3.0"}}
```

Use [Chainlink Local](chainlink-local.md) only for an actual local-testing request. Reusable Solidity with placeholders or constructor arguments may be mainnet-compatible and is not an onchain write. Verify current routes, tokens, routers, versions, and remappings before deployment.

## Complete project requests

When the user asks for a full project, a working implementation, or to "build this" in an established or requested Foundry/Hardhat repository, assemble every piece in one response, not across follow-ups: the project configuration; dependency install/rename commands and remappings that match the requested contracts (above); the actual sender/receiver code from [Solidity examples](ccip-solidity-examples.md) for the requested shape; a runnable deployment script and the [deployment order](#localtestnet-deployment-order); current-[Directory](https://docs.chain.link/ccip/directory/testnet) verification of the route and token before any deployment step; and a runnable [Chainlink Local](chainlink-local.md) no-fork test that calls through the generated contracts. Close the complete artifact with the exact wallet footer.
