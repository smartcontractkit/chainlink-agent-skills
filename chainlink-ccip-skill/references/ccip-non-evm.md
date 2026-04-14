# CCIP Non-EVM Chains

Use this file when the user wants to work with CCIP on Solana, Aptos, Sui, TON, or any non-EVM chain family. This covers SDK usage, CLI operations, wallet setup, architectural differences, and official tutorial links.

Do not apply EVM-specific patterns (Solidity contracts, Foundry/Hardhat setup, Chainlink Local, OpenZeppelin imports) to non-EVM chains. Contract development on non-EVM chains uses chain-native languages and tooling.

## Trigger Conditions

Use this reference for requests like:

- "Send tokens from Solana to Ethereum using CCIP."
- "How do I use the CCIP SDK with Aptos?"
- "Transfer tokens cross-chain from Solana devnet."
- "Build a CCIP receiver on Solana."
- "How does CCIP work on non-EVM chains?"
- "Set up a cross-chain token on Solana."

## Supported Chain Families

| Chain Family | SDK Class | CLI Support | Status |
|-------------|-----------|-------------|--------|
| EVM | `EVMChain` | Full | Full support |
| Solana (SVM) | `SolanaChain` | Full | Full support |
| Aptos | `AptosChain` | Full | Full support |
| Sui | `SuiChain` | Partial | Manual execution only |
| TON | `TONChain` | Partial | No token pool/registry queries |

## SDK Chain Classes

All chain classes share the same `Chain` base interface. Code written against the base class works across all families.

```typescript
import { EVMChain, SolanaChain, AptosChain } from "@chainlink/ccip-sdk";

const evmChain = await EVMChain.fromUrl("https://ethereum-sepolia-rpc.publicnode.com");
const solanaChain = await SolanaChain.fromUrl("https://api.devnet.solana.com");
const aptosChain = await AptosChain.fromUrl("https://api.testnet.aptoslabs.com/v1");
```

Common methods available on all chain classes:

| Method | Description |
|--------|-------------|
| `chain.getFee(...)` | Estimate transfer fee |
| `chain.sendMessage(...)` | Send cross-chain message |
| `chain.getMessagesInTx(...)` | Extract CCIP messages from a transaction |
| `chain.getTokenInfo(...)` | Get token metadata (symbol, decimals) |
| `chain.getBalance(...)` | Get native or token balance |
| `chain.getSupportedTokens(...)` | List registered tokens |
| `chain.getTokenAdminRegistryFor(...)` | Get token registry address |
| `chain.execute(...)` | Manually execute a message |

## Wallet Setup by Chain Family

| Chain | Wallet Type | Source | Example |
|-------|-------------|--------|---------|
| EVM | `ethers.Signer` | ethers.js v6 | `new Wallet(privateKey, provider)` |
| Solana | `anchor.Wallet` | @coral-xyz/anchor | `new Wallet(Keypair.fromSecretKey(...))` |
| Aptos | `aptos.Account` | @aptos-labs/ts-sdk | `Account.fromPrivateKey(...)` |

Private key formats:

- **EVM**: `0x`-prefixed hex private key, or encrypted JSON keystore file.
- **Solana**: Keypair JSON file path (e.g. `~/.config/solana/devnet.json`), base58-encoded secret key, or `0x`-hex secret key.
- **Aptos**: AIP-80 format (`ed25519-priv-0x...`) or raw `0x`-hex private key.

## Fee Estimation (Cross-Family)

Fee estimation works identically across chain families:

```typescript
import { SolanaChain, networkInfo } from "@chainlink/ccip-sdk";

const source = await SolanaChain.fromUrl("https://api.devnet.solana.com");
const destSelector = networkInfo("ethereum-testnet-sepolia").chainSelector;

const fee = await source.getFee({
  router: "<solana-router-address>",
  destChainSelector: destSelector,
  message: {
    receiver: "0xYourEVMReceiverAddress",
    tokenAmounts: [{ token: "<solana-token-address>", amount: 1000000n }],
    extraArgs: { gasLimit: 0n },
  },
});
```

## Sending Cross-Chain Messages

### Solana to EVM

```typescript
import { SolanaChain, networkInfo } from "@chainlink/ccip-sdk";

const source = await SolanaChain.fromUrl("https://api.devnet.solana.com");
const destSelector = networkInfo("ethereum-testnet-sepolia").chainSelector;

const request = await source.sendMessage({
  router: "<solana-router-address>",
  destChainSelector: destSelector,
  message: {
    receiver: "0xYourEVMReceiverAddress",
    tokenAmounts: [{ token: "<ccip-bnm-token>", amount: 1000000n }],
    extraArgs: { gasLimit: 0n },
    fee,
  },
  wallet: solanaWallet,
});

console.log("Message ID:", request.message.messageId);
```

### Aptos to EVM

```typescript
import { AptosChain, networkInfo } from "@chainlink/ccip-sdk";

const source = await AptosChain.fromUrl("https://api.testnet.aptoslabs.com/v1");
const destSelector = networkInfo("ethereum-testnet-sepolia").chainSelector;

const request = await source.sendMessage({
  router: "<aptos-router-address>",
  destChainSelector: destSelector,
  message: {
    receiver: "0xYourEVMReceiverAddress",
    tokenAmounts: [{ token: "<aptos-token-address>", amount: 1000000n }],
    extraArgs: { gasLimit: 0n },
    fee,
  },
  wallet: aptosAccount,
});
```

## Unsigned Transactions

For custom signing workflows (browser wallets, hardware wallets), generate unsigned transactions:

```typescript
const unsignedTx = await source.generateUnsignedSendMessage({
  sender: walletAddress,
  router,
  destChainSelector,
  message,
});

// Chain-specific transaction format:
// EVM: unsignedTx.transactions
// Solana: unsignedTx.instructions
// Aptos: unsignedTx.transactions (BCS-encoded)
// TON: unsignedTx.body
// Sui does not support unsigned transaction generation
```

## CLI Usage with Non-EVM Chains

The CCIP CLI (`@chainlink/ccip-cli`) supports non-EVM chains natively. Chain names and selectors work the same way.

### Send from Solana

```bash
ccip-cli send \
  --source solana-devnet \
  --dest ethereum-testnet-sepolia \
  --router <solana-router> \
  --receiver 0xYourEVMAddress \
  --transfer-tokens <token>=0.001
```

### Send from Aptos

```bash
ccip-cli send \
  --source aptos-testnet \
  --dest ethereum-testnet-sepolia \
  --router <aptos-router> \
  --receiver 0xYourEVMAddress \
  --transfer-tokens <token>=0.001
```

### Track any message (chain-agnostic)

```bash
ccip-cli show <tx-hash-or-message-id>
ccip-cli show <tx-hash-or-message-id> --wait
```

### CLI wallet options per chain family

- **EVM**: `0x`-hex private key, encrypted JSON file, `--wallet foundry:<name>`, `--wallet hardhat:<name>`, `--wallet ledger`
- **Solana**: base58 private key, path to `id.json` keypair file (default `~/.config/solana/id.json`), `--wallet ledger`
- **Aptos**: `0x`-hex private key, path to text file containing it

### CLI RPC configuration

Non-EVM RPCs are configured the same way as EVM RPCs -- pass via `--rpc` flag or list in an `.env` file:

```text
https://ethereum-sepolia-rpc.publicnode.com
https://api.devnet.solana.com
https://api.testnet.aptoslabs.com/v1
```

### Solana-specific CLI options

- `--token-receiver`: Solana token receiver if different from program
- `--account`: Solana accounts (append `=rw` for writable)
- `--force-buffer`: Force buffer for large messages
- `--force-lookup-table`: Create lookup table for account-heavy transactions
- `--clear-leftover-accounts`: Clean up temporary accounts after execution

## Architectural Differences from EVM

### Solana (SVM)

- **Account model**: Programs are stateless; all data is stored in accounts.
- **PDAs**: Program Derived Addresses provide deterministic storage.
- **Token accounts**: Each token requires a separate Associated Token Account (ATA).
- **Explicit access**: Programs can only access accounts explicitly provided to them.
- **Contract development**: Uses Rust with the Anchor framework. Not Solidity.

### Aptos

- **Account model**: Code (modules) and data (resources) are stored within accounts.
- **Resource model**: Move language provides strong ownership and access control.
- **Fungible Assets**: Tokens use the Fungible Asset standard, stored as resources within an owner's account.
- **Contract development**: Uses Move language. Not Solidity.

### Sui

- **Object model**: Data is stored as objects with unique IDs.
- **Move variant**: Uses Sui Move, a modified version of the Move language.
- **CCIP status**: Manual execution only -- limited support.

### TON

- **Actor model**: Smart contracts are actors communicating via messages.
- **CCIP status**: Partial -- no token pool or registry queries.

## Message Types (All Non-EVM Families)

All non-EVM chain families support the same CCIP message types:

1. **Token transfers**: Send tokens across chains without program execution on the destination.
2. **Arbitrary messaging**: Send data to trigger program execution on the destination chain.
3. **Programmable token transfers**: Send both tokens and data in a single message.

## Cross-Chain Tokens (CCT) on Solana

Solana supports CCT registration with different governance models:

- Direct mint authority transfer (development/testing)
- SPL Token multisig (educational)
- Production multisig governance (enterprise-grade dual-layer governance)

Tutorial: `https://docs.chain.link/ccip/tutorials/svm/cross-chain-tokens`

## Official Tutorials

### Solana

- Getting started: `https://docs.chain.link/ccip/getting-started/svm`
- All SVM tutorials: `https://docs.chain.link/ccip/tutorials/svm`
- SVM to EVM: `https://docs.chain.link/ccip/tutorials/svm/source`
- EVM to SVM: `https://docs.chain.link/ccip/tutorials/svm/destination`
- Token transfers (SVM source): `https://docs.chain.link/ccip/tutorials/svm/source/token-transfers`
- Token transfers (SVM dest): `https://docs.chain.link/ccip/tutorials/svm/destination/token-transfers`
- Arbitrary messaging (EVM to SVM): `https://docs.chain.link/ccip/tutorials/svm/destination/arbitrary-messaging`
- Implementing CCIP receivers: `https://docs.chain.link/ccip/tutorials/svm/receivers`

### Aptos

- Getting started: `https://docs.chain.link/ccip/getting-started/aptos`
- All Aptos tutorials: `https://docs.chain.link/ccip/tutorials/aptos`
- Aptos to EVM: `https://docs.chain.link/ccip/tutorials/aptos/source`
- EVM to Aptos: `https://docs.chain.link/ccip/tutorials/aptos/destination`
- Token transfers (Aptos source): `https://docs.chain.link/ccip/tutorials/aptos/source/token-transfers`
- Token transfers (Aptos dest): `https://docs.chain.link/ccip/tutorials/aptos/destination/token-transfers`

### SDK Examples (Multi-Chain)

- Repository: `https://github.com/smartcontractkit/ccip-sdk-examples`
- 01-getting-started: Node.js scripts for EVM, Solana, Aptos (chains, fees, tokens, transfers, status)
- 03-multichain-bridge-dapp: Browser app supporting EVM + Solana + Aptos

## Testnet Networks

| Network | Family | Example Chain Selector |
|---------|--------|----------------------|
| Ethereum Sepolia | EVM | 16015286601757825753 |
| Base Sepolia | EVM | 10344971235874465080 |
| Avalanche Fuji | EVM | 14767482510784806043 |
| Solana Devnet | Solana | 16423721717087811551 |
| Aptos Testnet | Aptos | 4741433654826277614 |

Faucets: [Chainlink Faucets](https://faucets.chain.link/), [Solana Faucet](https://faucet.solana.com/), [Aptos Faucet](https://aptos.dev/en/network/faucet).

## Limitations

1. Chainlink Local simulator is EVM-only. There is no local simulation for Solana, Aptos, Sui, or TON.
2. Solidity contract patterns (sender, receiver, CCIPReceiver, IRouterClient) are EVM-only. Non-EVM chains use chain-native languages and frameworks.
3. Foundry and Hardhat tooling applies only to EVM. Non-EVM chains use their own build tools (Anchor/Cargo for Solana, Aptos CLI for Aptos).
4. Sui support is partial -- manual execution only.
5. TON support is partial -- no token pool or registry queries.
6. The CCIP Explorer, CCIP API, and CLI `show`/`status` commands work for all chain families.
