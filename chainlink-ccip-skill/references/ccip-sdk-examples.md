# CCIP SDK Examples

Single owner for `@chainlink/ccip-sdk` EVM/Solana/Aptos construction and `generateUnsignedSendMessage`. Verify exports/signatures at `https://docs.chain.link/ccip/tools/llms.txt` or `https://docs.chain.link/ccip/tools/sdk/`; signing and broadcasting stay outside agent tools.

## Package and guide map

`npm install @chainlink/ccip-sdk`; Node 20+ required, 24+ recommended. The SDK uses ethers v6 and optionally peers with viem.

Guides: `docs.chain.link/ccip/tools/sdk/guides/<slug>`:

| Slug | Subject |
|---|---|
| `fee-estimation`, `gas-estimation` | Fees, fee tokens, receiver gas/margins |
| `sending-messages`, `tracking-messages`, `searching-messages` | Send/unsigned, lifecycle, API search/pagination |
| `querying-data`, `token-pools` | Lanes/ramps/registries, pools/remotes/rate limits |
| `manual-execution` | `calculateManualExecProof`, `execute`, `generateUnsignedExecute` |
| `multi-chain`, `ftf` | Family classes, faster-than-finality/CCTP finality |
| `error-handling`, `error-reference`, `cancellation` | Typed errors/recovery, `isTransientError`, `AbortSignal` |
| `browser-setup`, `viem-integration` | Bundlers/wallets, viem |

## Construction and unsigned send

The classes share the `Chain` base interface. This is the canonical construction plus fee/unsigned-send example; parameterize the family row instead of copying the workflow.

```typescript
import {
  EVMChain,
  SolanaChain,
  AptosChain,
  networkInfo,
} from "@chainlink/ccip-sdk";

const families = {
  evm: {
    Chain: EVMChain,
    rpc: "https://ethereum-sepolia-rpc.publicnode.com",
    sender: "0xYourWalletAddress",
    router: "0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59",
    receiver: "0xYourReceiverAddress",
    token: "0xTokenAddress",
  },
  solana: {
    Chain: SolanaChain,
    rpc: "https://api.devnet.solana.com",
    sender: "<user-solana-wallet-address>",
    router: "<solana-router-address>",
    receiver: "0xYourEVMReceiverAddress",
    token: "<solana-token-address>",
  },
  aptos: {
    Chain: AptosChain,
    rpc: "https://api.testnet.aptoslabs.com/v1",
    sender: "<user-aptos-account-address>",
    router: "<aptos-router-address>",
    receiver: "0xYourEVMReceiverAddress",
    token: "<aptos-token-address>",
  },
} as const;

const { Chain, rpc, sender, router, receiver, token } = families.solana;
const chain = await Chain.fromUrl(rpc);
const destChainSelector = networkInfo("ethereum-testnet-sepolia-base-1").chainSelector;
const body = {
  receiver,
  data: "0x48656c6c6f",
  tokenAmounts: [{ token, amount: 1_000_000n }],
  extraArgs: { gasLimit: 200_000n, allowOutOfOrderExecution: true },
};
const fee = await chain.getFee({ router, destChainSelector, message: body });
const unsignedTx = await chain.generateUnsignedSendMessage({
  sender,
  router,
  destChainSelector,
  message: { ...body, fee },
});
console.log({ fee: fee.toString(), unsignedTx });
```

Family deltas are only RPC, router, address/token formats, and output: EVM/Aptos expose `transactions` (Aptos BCS-encoded), Solana `instructions`, TON `body`; Sui does not support unsigned generation. For token-only set `data: "0x"`, `gasLimit: 0n`; for data-only use `tokenAmounts: []`. To pay fees in LINK rather than native, set `feeToken: "0xLinkTokenAddress"` in the message. Chain selectors—not chain IDs—go in `destChainSelector`; the Base Sepolia example resolves to `10344971235874465080n`.

Shared methods include `getFee`, `sendMessage`, `generateUnsignedSendMessage`, `getMessagesInTx`, `getTokenInfo`, `getBalance`, `getSupportedTokens`, `getTokenAdminRegistryFor`, and `execute`; signing methods are user-runtime-only. Family support/architecture and CLI belong to [ccip-non-evm.md](ccip-non-evm.md).

## Read integrations

### Transaction and status

```typescript
import {
  EVMChain,
  CCIPAPIClient,
  getCCIPExplorerUrl,
  withRetry,
} from "@chainlink/ccip-sdk";

const source = await EVMChain.fromUrl("https://ethereum-sepolia-rpc.publicnode.com");
const [request] = await source.getMessagesInTx("0xYourTransactionHash");
const api = new CCIPAPIClient();
const result = await withRetry(
  () => api.getMessageById(request.message.messageId),
  {
    maxRetries: 10,
    initialDelayMs: 5000,
    maxDelayMs: 30000,
    backoffMultiplier: 1.5,
    respectRetryAfterHint: true,
  },
);
console.log({
  messageId: request.message.messageId,
  sender: request.message.sender,
  destination: request.lane.destChainSelector,
  status: result.metadata.status,
  source: result.metadata.sourceNetworkInfo.name,
  dest: result.metadata.destNetworkInfo.name,
  destTx: result.metadata.receiptTransactionHash,
  explorer: getCCIPExplorerUrl("msg", request.message.messageId),
});
```

Status is `SENT → SOURCE_FINALIZED → COMMITTED → BLESSED → SUCCESS|FAILED` on v1 or `SENT → SOURCE_FINALIZED → VERIFYING → VERIFIED → SUCCESS|FAILED` on v2; never both v1 commit/bless and v2 verified states. See [API](ccip-api.md) for exact schemas.

### Token pool read

```typescript
import { EVMChain, networkInfo } from "@chainlink/ccip-sdk";

const source = await EVMChain.fromUrl("https://ethereum-sepolia-rpc.publicnode.com");
const router = "0x0BF3dE8c5D3e8A2B34D2BEeB17ABfCeBaf363A59";
const registry = await source.getTokenAdminRegistryFor(router);
for (const token of await source.getSupportedTokens(registry)) {
  const info = await source.getTokenInfo(token);
  console.log(`${info.symbol} (${info.decimals} decimals): ${token}`);
}
const tokenConfig = await source.getRegistryTokenConfig(registry, "0xTokenAddress");
if (tokenConfig.tokenPool) {
  const remote = await source.getTokenPoolRemote(
    tokenConfig.tokenPool,
    networkInfo("ethereum-testnet-sepolia-base-1").chainSelector,
  );
  console.log(remote.remoteToken, remote.outboundRateLimiterState);
  // state fields: tokens (available), capacity, rate (per-second refill)
}
```

## Errors and sequence

```typescript
import {
  CCIPError,
  CCIPMessageNotFoundInTxError,
  CCIPMessageIdNotFoundError,
} from "@chainlink/ccip-sdk";

try {
  await chain.getMessagesInTx(txHash);
} catch (error) {
  if (error instanceof CCIPMessageNotFoundInTxError) {
    console.log("No CCIP messages in", error.context.txHash);
  } else if (CCIPError.isCCIPError(error)) {
    console.error(error.message, error.recovery, error.isTransient);
  } else throw error;
}
```

`CCIPMessageIdNotFoundError` is the retryable recent-index case used with `withRetry`. Non-custodial order: `getFee` → `generateUnsignedSendMessage` → user signs/broadcasts externally → `getMessagesInTx(userTxHash)` → `CCIPAPIClient.getMessageById`. Do not advance before the prior result.

Quick methods: `networkInfo(id).chainSelector`; `getLaneFeatures({router,destChainSelector})`; `getBalance(address, tokenAddress?)`; `getTokenInfo`; `getSupportedTokens`; `getRegistryTokenConfig`; `getTokenPoolRemote`. Manual execution is instructions only.

## Starters

`https://github.com/smartcontractkit/ccip-sdk-examples`: `01-getting-started` scripts; `02-evm-simple-bridge`; `03-multichain-bridge-dapp` (EVM/Solana/Aptos); `04-hardhat-ccip` (Hardhat v3/custom contracts/SDK operations). Preserve these runnable upstream starters rather than reproducing them.
