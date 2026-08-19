# CCIP Non-EVM Chains

Owner for Solana/SVM, Aptos, Sui, TON, and Canton architecture, support limits, CLI, and tutorials. Never apply Solidity, Foundry/Hardhat, OpenZeppelin, or Chainlink Local. Chain-native contract tooling is Anchor/Rust for Solana and Move for Aptos/Sui.

## Support matrix

| Family | SDK class | CLI/status |
|---|---|---|
| EVM | `EVMChain` | Full |
| Solana | `SolanaChain` | Full |
| Aptos | `AptosChain` | Full |
| Sui | `SuiChain` | **Manual execution only** |
| TON | `TONChain` | **No token pool/registry queries** |
| Canton | `CantonChain` | Requires `--canton-config`; `--indexer` for CCV verifications |

Re-verify the matrix against `https://docs.chain.link/ccip/tools/llms.txt` or the applicable CLI page before declaring something unsupported. Explorer, API, and CLI `show`/status work across families.

## SDK ownership and family deltas

[ccip-sdk-examples.md](ccip-sdk-examples.md) is the single owner of:

- `import { EVMChain, SolanaChain, AptosChain }` and `fromUrl` construction;
- shared `Chain` methods including `getFee`, `generateUnsignedSendMessage`, `sendMessage`, `getMessagesInTx`, token/balance/registry reads, and `execute`;
- the canonical fee plus `generateUnsignedSendMessage` flow and family outputs.

Use that one example with these deltas: family RPC and router; source-address format; destination receiver format; token identifier; and unsigned output (`EVM`/Aptos `transactions`, Solana `instructions`, TON `body`; Sui has no unsigned generation). `sendMessage`/`execute` belong only in a user-controlled runtime; agent examples stop at unsigned output.

## Wallet boundary

EVM uses an ethers v6/browser/hardware/external signer; Solana uses wallet adapter/Anchor/hardware/external signer; Aptos uses its wallet adapter/hardware/external signer. Never ask for or inspect wallet JSON, credentials, signing strings, secret environment variables, keystores, or local credential files. Do not reproduce default wallet paths from docs. Prefer browser/hardware/external signing; if a CLI path is unavoidable, write `<path-to-user-managed-wallet>` for the user to fill outside the agent.

## CLI

The `@chainlink/ccip-cli` uses names/selectors across families. These signing commands are user-run templates only:

```bash
# Solana → EVM
ccip-cli send --source solana-devnet --dest ethereum-testnet-sepolia \
  --router <solana-router> --receiver 0xYourEVMAddress \
  --transfer-tokens <token>=0.001

# Aptos → EVM
ccip-cli send --source aptos-testnet --dest ethereum-testnet-sepolia \
  --router <aptos-router> --receiver 0xYourEVMAddress \
  --transfer-tokens <token>=0.001
```

Read-only tracking is chain-agnostic:

```bash
ccip-cli show <tx-hash-or-message-id>
ccip-cli show <tx-hash-or-message-id> --wait
```

RPCs use `--rpc` or `.env`; examples: `https://ethereum-sepolia-rpc.publicnode.com`, `https://api.devnet.solana.com`, `https://api.testnet.aptoslabs.com/v1`. Do not inspect `.env`.

Solana flags: `--token-receiver` (token receiver differs from program), repeat `--account` (`=rw` for writable), `--force-buffer`, `--force-lookup-table`, `--clear-leftover-accounts`.

Canton rules:

- `--canton-config <path>` is required for every operation and provides party ID/default `senderInstanceId`.
- `--indexer <url>` supplies CCIP v2 indexers for CCV verification when a lane includes Canton.
- Source `send --router` is a `CCIPSender` instance ID, defaulting to configured `senderInstanceId`, not a router address.
- Destination `manual-exec --receiver` accepts a `CCIPReceiver` contract ID, party ID (`hint::1220…`), or `keccak256(party)`.
- Optional wallet material is a 64-character hex Ed25519 seed; identity still comes from config. Keep it outside the agent runtime.

## Family architecture

### Solana (SVM)

Programs are stateless; data lives in accounts. PDAs provide deterministic storage, each token uses an Associated Token Account, and programs access only explicitly supplied accounts. Contracts are Anchor/Rust programs.

### Aptos

Accounts store Move modules and resource data. Move resources enforce ownership/access; tokens use the Fungible Asset standard within owner accounts.

### Sui

Sui Move stores data as uniquely identified objects. Current CCIP support is manual-execution-only.

### TON

Actor-model contracts communicate by messages. CCIP has no token-pool or registry queries.

### Canton

Daml templates have contract IDs and parties are actors rather than addresses. Identity comes from `--canton-config`; signing yields `PartySignatures`. Fee tokens are instrument IDs (`parseCantonInstrumentId`, `DEFAULT_CANTON_LINK_INSTRUMENT_ID`), not ERC-20 addresses. Canton lanes use CCIP v2 verification and require `--indexer` for status/execution flows.

All families support token transfer, arbitrary data messaging, and programmable token-plus-data messaging subject to the matrix limits.

## Solana CCT and tutorials

Solana CCT governance choices: direct mint-authority transfer (development/testing), SPL Token multisig (educational), or production multisig dual-layer governance. Tutorial: `https://docs.chain.link/ccip/tutorials/svm/cross-chain-tokens.md`.

Solana: getting started `https://docs.chain.link/ccip/getting-started/svm.md`; index `https://docs.chain.link/ccip/tutorials/svm.md`; source `https://docs.chain.link/ccip/tutorials/svm/source.md`; destination `https://docs.chain.link/ccip/tutorials/svm/destination.md`; source/destination tokens under those paths at `token-transfers.md`; destination arbitrary data at `arbitrary-messaging.md`; receivers `https://docs.chain.link/ccip/tutorials/svm/receivers.md`.

Aptos: getting started `https://docs.chain.link/ccip/getting-started/aptos.md`; index `https://docs.chain.link/ccip/tutorials/aptos.md`; source `https://docs.chain.link/ccip/tutorials/aptos/source.md`; destination `https://docs.chain.link/ccip/tutorials/aptos/destination.md`; source/destination token guides at each path's `token-transfers.md`.

SDK examples: `https://github.com/smartcontractkit/ccip-sdk-examples` (`01-getting-started` scripts for EVM/Solana/Aptos; `03-multichain-bridge-dapp` browser app).

## Testnets and limits

| Network | Selector |
|---|---:|
| Ethereum Sepolia | `16015286601757825753` |
| Base Sepolia | `10344971235874465080` |
| Avalanche Fuji | `14767482510784806043` |
| Solana Devnet | `16423721717087811551` |
| Aptos Testnet | `4741433654826277614` |

Faucets: `https://faucets.chain.link/`, `https://faucet.solana.com/`, `https://aptos.dev/en/network/faucet`.

Chainlink Local is EVM-only; non-EVM testing goes to testnet with family build tools. Operational limits: Sui only manual execution; TON no pool/registry queries; Canton needs config plus indexer.
