# CCIP Contracts

Use for EVM contract-first sender/receiver work, modifications, and Solidity project setup. For tool-first send/bridge/monitoring use [tools](ccip-tools.md); for Solana programs, Aptos/Sui Move, TON, or Canton use [non-EVM](ccip-non-evm.md).

## Shapes and invariants

Supported shapes: data-only, token-only, data-plus-token, contract→EOA, and EOA→contract. When a sender/receiver or generic sender is requested, emit concrete CCIP contracts immediately if constructor-injected router/LINK addresses suffice; do not wait for testnet names or runtime values. If the shape is ambiguous, recommend data-only as the simpler security-first default before data plus tokens. Start code from [ccip-solidity-examples.md](ccip-solidity-examples.md) using `CCIPReceiver`, `IRouterClient`, and `Client`.

Conservative defaults:

- explicit send/admin access control; validate destination before send;
- receiver validates source selector and sender when required; inherited `CCIPReceiver.ccipReceive` admits only its router;
- a data-only pair validates the router through `CCIPReceiver`, then the source selector and sender contract; deployment and setup remain user-run;
- quote with `IRouterClient.getFee`; `isChainSupported` can verify chain support;
- keep receipt separate from business logic and add recovery when receiver logic may fail;
- if `ccipReceive` reverts, associated token transfer reverts and the message enters failed/manual-execution state;
- tokens plus data sent to an EOA deliver only the tokens;
- avoid dynamic configuration, hidden control flow, and unnecessary abstraction.

For testnet transfers, default to faucet/tutorial **CCIP-BnM** (burn-and-mint) unless the user chooses another token. Verify the route and token first.

| Shape | Required construction |
|---|---|
| Data | `Client.EVM2AnyMessage`, fee quote, explicit payload, validated receiver |
| Token | route/token verification; explicit amount and router approvals; `gasLimit: 0` when no callback |
| Data + token | programmable-transfer pattern; defensive receiver if payload handling could revert after token delivery |

## Local/testnet deployment order

These examples are for local use or testnets. Before deployment, verify the router, LINK address, and route in the [CCIP Directory](https://docs.chain.link/ccip/directory/testnet). Deployment and every configuration/send action are user-run:

1. Deploy the receiver on the destination testnet.
2. Deploy the sender on the source testnet.
3. Allow the destination selector on the sender.
4. Allow the source selector and sender contract on the receiver.
5. Fund the sender with testnet LINK.
6. The user calls `sendMessage`.

Tutorials: arbitrary data `https://docs.chain.link/ccip/tutorials/evm/send-arbitrary-data.md`; tokens `https://docs.chain.link/ccip/tutorials/evm/transfer-tokens-from-contract.md`; programmable `https://docs.chain.link/ccip/tutorials/evm/programmable-token-transfers.md`; defensive `https://docs.chain.link/ccip/tutorials/evm/programmable-token-transfers-defensive.md`; best practices `https://docs.chain.link/ccip/concepts/best-practices/evm.md`; `CCIPReceiver` `https://docs.chain.link/ccip/api-reference/evm/v1.6.1/ccip-receiver.md`; `IRouterClient` `https://docs.chain.link/ccip/api-reference/evm/v1.6.1/i-router-client.md`.

## Project setup

Prefer the established framework; otherwise Foundry. Install tagged releases rather than assuming default branches:

```bash
forge install smartcontractkit/chainlink-ccip@contracts-ccip-v<version>
forge install smartcontractkit/chainlink-evm@contracts-v<version>
```

```text
@chainlink/contracts/=lib/chainlink-evm/contracts/
@chainlink/contracts-ccip/=lib/chainlink-ccip/chains/evm/
@chainlink/contracts-ccip/contracts/=lib/chainlink-ccip/chains/evm/contracts/
```

Inspect installed CCIP imports before selecting OpenZeppelin versions: `CCIPReceiver` imports `IERC165`, and its version can differ from other dependencies. Common simultaneous remappings are:

```text
@openzeppelin/contracts@4.8.3/=lib/openzeppelin-contracts-4.8.3/contracts/
@openzeppelin/contracts@5.3.0/=lib/openzeppelin-contracts-5.3.0/contracts/
```

`CCIPReceiver` may instead require `5.0.2`; grep `lib/chainlink-ccip/` for `@openzeppelin`, install exact releases, and give each a separate remapping. ACE projects may also need:

```text
@chainlink/policy-management/=lib/chainlink-ace/packages/policy-management/src/
```

In existing/explicit Hardhat projects use npm with the same import-driven discipline. Aliases may be required:

```json
{"dependencies":{"@openzeppelin/contracts-4.8.3":"npm:@openzeppelin/contracts@4.8.3","@openzeppelin/contracts-5.3.0":"npm:@openzeppelin/contracts@5.3.0"}}
```

Use [Chainlink Local](chainlink-local.md) only for an actual local-testing request. Reusable Solidity with placeholders or constructor arguments may be mainnet-compatible and is not an onchain write. Verify current routes, tokens, routers, versions, and remappings before deployment.
