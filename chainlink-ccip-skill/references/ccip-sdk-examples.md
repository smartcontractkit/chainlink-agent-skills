# CCIP SDK Examples

Use this file for tool-first workflows that involve the CCIP TypeScript SDK (`@chainlink/ccip-sdk`). These examples are based on the official SDK documentation and the [ccip-sdk-examples](https://github.com/smartcontractkit/ccip-sdk-examples) repo.

When documentation-fetching tools are available, verify these patterns against the latest SDK docs at `https://docs.chain.link/ccip/tools/sdk/`. When they are not, use these as the authoritative starting point.

## Package

```bash
npm install @chainlink/ccip-sdk
```

Node.js v20+ required. v24+ recommended. The SDK uses [ethers.js v6](https://docs.ethers.org/v6/) internally, with optional [viem](https://viem.sh/) peer dependency.

## Chain Classes

The SDK provides a unified `Chain` base class. Create chain instances with `fromUrl`:

```typescript
import { EVMChain, SolanaChain, AptosChain } from "@chainlink/ccip-sdk";

const evmChain = await EVMChain.fromUrl("https://ethereum-sepolia-rpc.publicnode.com");
const solanaChain = await SolanaChain.fromUrl("https://api.devnet.solana.com");
const aptosChain = await AptosChain.fromUrl("https://api.testnet.aptoslabs.com/v1");
```

All chain classes share the same interface for `getFee`, `sendMessage`, `getMessagesInTx`, `getSupportedTokens`, `getTokenInfo`, `getBalance`, and more. Code written against the `Chain` base class works with any supported chain family.

## Chain Selectors

CCIP uses chain selectors, not chain IDs. Use `networkInfo` to convert:

```typescript
import { networkInfo } from "@chainlink/ccip-sdk";

const destSelector = networkInfo("ethereum-testnet-sepolia-base-1").chainSelector;
// Returns: 10344971235874465080n
```

Always use chain selectors for `destChainSelector` in messages, lane configuration, and fee estimation.

## Get Fee Estimate

Estimate the fee for a cross-chain transfer before execution. No on-chain side effects.

```typescript
import { EVMChain, networkInfo } from "@chainlink/ccip-sdk";

const source = await EVMChain.fromUrl("https://ethereum-sepolia-rpc.publicnode.com");
const router = "0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59";
const destChainSelector = networkInfo("ethereum-testnet-sepolia-base-1").chainSelector;

const fee = await source.getFee({
  router,
  destChainSelector,
  message: {
    receiver: "0xYourReceiverAddress",
    data: "0x48656c6c6f", // "Hello" in hex
    extraArgs: { gasLimit: 200_000n },
  },
});

console.log("Fee in native token:", fee.toString());
```

For token transfers, include `tokenAmounts` in the message:

```typescript
const fee = await source.getFee({
  router,
  destChainSelector,
  message: {
    receiver: "0xYourReceiverAddress",
    tokenAmounts: [{ token: "0xTokenAddress", amount: 1000000000000000000n }],
    extraArgs: { gasLimit: 0n },
  },
});
```

To pay fees in LINK instead of native gas, add `feeToken` to the message:

```typescript
const fee = await source.getFee({
  router,
  destChainSelector,
  message: {
    receiver: "0xYourReceiverAddress",
    data: "0x48656c6c6f",
    extraArgs: { gasLimit: 200_000n },
    feeToken: "0xLinkTokenAddress",
  },
});
```

## Send a Cross-Chain Message

Send a message with optional token transfers. Requires a wallet.

```typescript
import { EVMChain, networkInfo } from "@chainlink/ccip-sdk";
import { Wallet } from "ethers";

const source = await EVMChain.fromUrl("https://ethereum-sepolia-rpc.publicnode.com");
const wallet = new Wallet("YOUR_PRIVATE_KEY", source.provider);

const router = "0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59";
const destChainSelector = networkInfo("ethereum-testnet-sepolia-base-1").chainSelector;

const fee = await source.getFee({
  router,
  destChainSelector,
  message: {
    receiver: "0xYourReceiverAddress",
    data: "0x48656c6c6f",
    extraArgs: { gasLimit: 200_000n, allowOutOfOrderExecution: true },
  },
});

const request = await source.sendMessage({
  router,
  destChainSelector,
  message: {
    receiver: "0xYourReceiverAddress",
    data: "0x48656c6c6f",
    extraArgs: { gasLimit: 200_000n, allowOutOfOrderExecution: true },
    fee,
  },
  wallet,
});

console.log("Transaction hash:", request.tx.hash);
console.log("Message ID:", request.message.messageId);
```

## Track a Message from a Transaction

Extract CCIP message details from an existing transaction:

```typescript
import { EVMChain } from "@chainlink/ccip-sdk";

const source = await EVMChain.fromUrl("https://ethereum-sepolia-rpc.publicnode.com");

const requests = await source.getMessagesInTx("0xYourTransactionHash");
const req = requests[0];

console.log("Message ID:", req.message.messageId);
console.log("Sender:", req.message.sender);
console.log("Destination chain:", req.lane.destChainSelector);
```

## Check Message Status via API

The CCIP API is a centralized index. One call locates any message regardless of source chain.

```typescript
import { CCIPAPIClient, getCCIPExplorerUrl } from "@chainlink/ccip-sdk";

const apiClient = new CCIPAPIClient();
const result = await apiClient.getMessageById("0xYourMessageId");

console.log("Status:", result.metadata.status);
console.log("Source:", result.metadata.sourceNetworkInfo.name);
console.log("Destination:", result.metadata.destNetworkInfo.name);

if (result.metadata.receiptTransactionHash) {
  console.log("Dest TX:", result.metadata.receiptTransactionHash);
}

console.log("Explorer:", getCCIPExplorerUrl("msg", "0xYourMessageId"));
```

Message lifecycle depends on lane version:

| Stage | V1 Lanes | V2 Lanes |
|-------|----------|----------|
| 1 | SENT | SENT |
| 2 | SOURCE_FINALIZED | SOURCE_FINALIZED |
| 3 | COMMITTED | VERIFYING |
| 4 | BLESSED | VERIFIED |
| 5 | SUCCESS or FAILED | SUCCESS or FAILED |

A message will never have both COMMITTED/BLESSED and VERIFIED states. The lifecycle depends on the lane version deployed.

## Discover Supported Tokens

Query on-chain registries for tokens supported on a lane:

```typescript
import { EVMChain, networkInfo } from "@chainlink/ccip-sdk";

const source = await EVMChain.fromUrl("https://ethereum-sepolia-rpc.publicnode.com");
const router = "0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59";

const registryAddress = await source.getTokenAdminRegistryFor(router);
const tokens = await source.getSupportedTokens(registryAddress);

for (const tokenAddress of tokens) {
  const info = await source.getTokenInfo(tokenAddress);
  console.log(`${info.symbol} (${info.decimals} decimals): ${tokenAddress}`);
}
```

## Check Token Pool Remote Config

Verify a token is supported for a specific destination and inspect rate limits:

```typescript
const destSelector = networkInfo("ethereum-testnet-sepolia-base-1").chainSelector;
const tokenConfig = await source.getRegistryTokenConfig(registryAddress, tokenAddress);

if (tokenConfig.tokenPool) {
  const remote = await source.getTokenPoolRemote(tokenConfig.tokenPool, destSelector);
  console.log("Remote token:", remote.remoteToken);

  if (remote.outboundRateLimiterState) {
    const { tokens: available, capacity, rate } = remote.outboundRateLimiterState;
    console.log(`Rate limit: ${available}/${capacity} (${rate}/sec refill)`);
  }
}
```

## Wallets by Chain Family

| Chain | Wallet Type | Example |
|-------|-------------|---------|
| EVM | `ethers.Signer` | `new Wallet(privateKey, provider)` |
| Solana | `anchor.Wallet` | `new Wallet(Keypair.fromSecretKey(...))` |
| Aptos | `aptos.Account` | `Account.fromPrivateKey(...)` |

## Unsigned Transactions

For browser wallets or hardware wallets, generate unsigned transaction data:

```typescript
const unsignedTx = await source.generateUnsignedSendMessage({
  sender: walletAddress,
  router,
  destChainSelector,
  message,
});

// EVM: iterate unsignedTx.transactions
// Solana: iterate unsignedTx.instructions
// Aptos: iterate unsignedTx.transactions (BCS-encoded)
for (const tx of unsignedTx.transactions) {
  const signed = await customSigner.sign(tx);
  await customSender.broadcast(signed);
}
```

For EVM in browsers, get a signer from the connected wallet:

```typescript
const signer = await source.provider.getSigner(0);
```

## Error Handling

The SDK throws typed errors:

```typescript
import {
  EVMChain,
  CCIPError,
  CCIPMessageNotFoundInTxError,
  CCIPMessageIdNotFoundError,
} from "@chainlink/ccip-sdk";

try {
  const requests = await chain.getMessagesInTx(txHash);
} catch (error) {
  if (error instanceof CCIPMessageNotFoundInTxError) {
    console.log("No CCIP messages in transaction:", error.context.txHash);
  } else if (CCIPError.isCCIPError(error)) {
    console.error(`CCIP Error: ${error.message}`);
    if (error.recovery) console.error(`Recovery: ${error.recovery}`);
    if (error.isTransient) console.error("Transient error — retry later.");
  } else {
    throw error;
  }
}
```

## Retry for Recent Messages

Recently sent messages may not be indexed immediately. Use the SDK's built-in retry:

```typescript
import { CCIPAPIClient, withRetry, CCIPMessageIdNotFoundError } from "@chainlink/ccip-sdk";

const apiClient = new CCIPAPIClient();
const result = await withRetry(() => apiClient.getMessageById(messageId), {
  maxRetries: 10,
  initialDelayMs: 5000,
  maxDelayMs: 30000,
  backoffMultiplier: 1.5,
  respectRetryAfterHint: true,
});
```

## Workflow: Complete Token Transfer

Full sequence from fee check through send and status verification:

1. `chain.getFee(...)` -- estimate cost and present to user
2. `chain.sendMessage(...)` -- execute the transfer (SDK handles token approval internally)
3. `chain.getMessagesInTx(tx.hash)` -- extract message ID from the transaction
4. `CCIPAPIClient.getMessageById(messageId)` -- poll destination for delivery status

Each step should complete before starting the next. Present the fee to the user before proceeding to execution.

## Quick Reference

| Task | Method |
|------|--------|
| Connect to chain | `EVMChain.fromUrl(rpcUrl)` |
| Get chain selector | `networkInfo(networkId).chainSelector` |
| Estimate fee | `chain.getFee({ router, destChainSelector, message })` |
| Send message | `chain.sendMessage({ router, destChainSelector, message, wallet })` |
| Track from tx | `chain.getMessagesInTx(txHash)` |
| Check status | `new CCIPAPIClient().getMessageById(messageId)` |
| Manual execution | `dest.execute({ messageId, wallet })` |
| Lane features | `chain.getLaneFeatures({ router, destChainSelector })` |
| List tokens | `chain.getSupportedTokens(registryAddress)` |
| Token info | `chain.getTokenInfo(tokenAddress)` |
| Token balance | `chain.getBalance(address, tokenAddress?)` |

## Starter Projects

Official working examples covering EVM, Solana, and Aptos:

- Repository: `https://github.com/smartcontractkit/ccip-sdk-examples`
- 01-getting-started: Node.js scripts for chains, fees, tokens, pools, transfers, status
- 02-evm-simple-bridge: EVM-to-EVM browser bridge app
- 03-multichain-bridge-dapp: EVM + Solana + Aptos browser bridge app
- 04-hardhat-ccip: Hardhat v3 + custom contracts + SDK-assisted operations
