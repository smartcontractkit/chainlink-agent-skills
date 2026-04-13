# CCIP SDK Examples

Use this file for tool-first workflows that involve the CCIP JavaScript/TypeScript SDK (`@chainlink/ccip-js`). These examples are based on the official SDK documentation.

When documentation-fetching tools are available, verify these patterns against the latest SDK docs. When they are not, use these as the authoritative starting point.

## Package

```bash
npm install @chainlink/ccip-js
```

The SDK uses [viem](https://viem.sh/) for client and type primitives.

## Initialize the CCIP Client

```typescript
import * as CCIP from "@chainlink/ccip-js";
import { createPublicClient, createWalletClient, http, custom } from "viem";
import { sepolia } from "viem/chains";

const ccipClient = CCIP.createClient();

const publicClient = createPublicClient({
  chain: sepolia,
  transport: http(),
});

const walletClient = createWalletClient({
  chain: sepolia,
  transport: custom(window.ethereum!),
});
```

## Get Fee Estimate

Calculates the fee for a cross-chain transfer before execution. No on-chain side effects.

```typescript
const fee = await ccipClient.getFee({
  client: publicClient,
  routerAddress: "0x<router-address>",
  tokenAddress: "0x<token-address>",
  amount: 1000000000000000000n, // 1 token in wei
  destinationAccount: "0x<receiver-address>",
  destinationChainSelector: "<destination-chain-selector>",
});

console.log(`Estimated fee: ${fee} wei`);
```

For data-only messages, use `message` instead of `tokenAddress`/`amount`:

```typescript
const fee = await ccipClient.getFee({
  client: publicClient,
  routerAddress: "0x<router-address>",
  destinationAccount: "0x<receiver-address>",
  destinationChainSelector: "<destination-chain-selector>",
  amount: 0n,
  tokenAddress: "0x0000000000000000000000000000000000000000",
  message: "Hello from source chain",
});
```

## Approve Router

Before transferring tokens, approve the router to spend on behalf of the sender.

```typescript
const { txHash, txReceipt } = await ccipClient.approveRouter({
  client: walletClient,
  routerAddress: "0x<router-address>",
  tokenAddress: "0x<token-address>",
  amount: 1000000000000000000n,
  waitForReceipt: true,
});
```

## Transfer Tokens

Send tokens cross-chain. Pay fees in native gas or a specified fee token.

```typescript
// Pay with native gas
const { txHash, messageId } = await ccipClient.transferTokens({
  client: walletClient,
  routerAddress: "0x<router-address>",
  tokenAddress: "0x<token-address>",
  amount: 1000000000000000000n,
  destinationAccount: "0x<receiver-address>",
  destinationChainSelector: "<destination-chain-selector>",
});

console.log(`Transfer sent. TX: ${txHash}, Message ID: ${messageId}`);
```

```typescript
// Pay with LINK token
const { txHash, messageId } = await ccipClient.transferTokens({
  client: walletClient,
  routerAddress: "0x<router-address>",
  tokenAddress: "0x<token-address>",
  amount: 1000000000000000000n,
  destinationAccount: "0x<receiver-address>",
  destinationChainSelector: "<destination-chain-selector>",
  feeTokenAddress: "0x<link-token-address>",
});
```

## Send Data-Only Message

Send an arbitrary string message cross-chain without tokens.

```typescript
const { txHash, messageId } = await ccipClient.sendCCIPMessage({
  client: walletClient,
  routerAddress: "0x<router-address>",
  destinationAccount: "0x<receiver-contract-address>",
  destinationChainSelector: "<destination-chain-selector>",
  message: "Hello from source chain",
});

console.log(`Message sent. TX: ${txHash}, Message ID: ${messageId}`);
```

## Check Transfer Status

Poll the destination chain for message delivery status.

```typescript
const status = await ccipClient.getTransferStatus({
  client: publicClient, // client connected to destination chain
  destinationRouterAddress: "0x<destination-router-address>",
  sourceChainSelector: "<source-chain-selector>",
  messageId: "0x<message-id>",
});

if (status) {
  console.log(`Status: ${status}`);
} else {
  console.log("Message not yet received on destination chain.");
}
```

## Workflow: Complete Token Transfer

Full sequence from fee check through send and status verification:

1. `getFee` -- estimate cost
2. `approveRouter` -- approve token spend
3. `transferTokens` -- execute the transfer
4. `getTransferStatus` -- poll destination for delivery

Each step should complete before starting the next. Present the fee to the user before proceeding to approval and execution.
