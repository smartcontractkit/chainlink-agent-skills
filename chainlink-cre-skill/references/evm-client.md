# EVM Client

Use for EVM reads/writes, Go bindings, reports, consumer contracts, or forwarders. [workflow-patterns.md](workflow-patterns.md) owns handler scaffolding: when the user asks for a workflow, include its complete trigger, handler, `initWorkflow`/`InitWorkflow`, and TS `main`/`Runner` or Go `main`/WASM runner. [chain-selectors.md](chain-selectors.md) is the sole embedded owner of selector names and forwarder addresses.

## TypeScript reads

Create one `EVMClient` per chain; the selector belongs in its constructor, not each call. Resolve a configured selector name and reject unknown values:

```typescript
import {
  EVMClient, LAST_FINALIZED_BLOCK_NUMBER, bytesToHex, encodeCallMsg, getNetwork,
  type Runtime,
} from '@chainlink/cre-sdk'
import {
  decodeFunctionResult, encodeFunctionData, parseAbi, zeroAddress, type Address,
} from 'viem'

const abi = parseAbi(['function balanceOf(address) view returns (uint256)'])

const readBalance = (runtime: Runtime<Config>, owner: Address): bigint => {
  const network = getNetwork({
    chainFamily: 'evm', chainSelectorName: runtime.config.chainSelectorName,
  })
  if (!network) throw new Error(`Unknown selector: ${runtime.config.chainSelectorName}`)
  const client = new EVMClient(network.chainSelector.selector)
  const reply = client.callContract(runtime, {
    call: encodeCallMsg({
      from: zeroAddress, to: runtime.config.tokenAddress as Address,
      data: encodeFunctionData({ abi, functionName: 'balanceOf', args: [owner] }),
    }),
    blockNumber: LAST_FINALIZED_BLOCK_NUMBER,
  }).result()
  return decodeFunctionResult({
    abi, functionName: 'balanceOf', data: bytesToHex(reply.data),
  })
}
```

Use `viem` for ABI encoding/decoding. Solidity integers are `bigint`, never `number`. `LAST_FINALIZED_BLOCK_NUMBER` is exactly the TypeScript `0n` finalized sentinel; `-1n` is latest, `-2n` safe, `-3n` pending, and a positive value selects an exact block. The Ethereum Sepolia selector name is `ethereum-testnet-sepolia`; resolve other named chains through [chain-selectors.md](chain-selectors.md). See [concepts.md](concepts.md) for Go's distinct generated/low-level constants.

## Write/report flow

The invariant is:

1. ABI-encode the exact consumer payload.
2. Generate a signed report with `runtime.report(...).result()` (Go `runtime.GenerateReport(...).Await()`).
3. Submit it with `evmClient.writeReport(...).result()` (Go binding helper or `WriteReport(...).Await()`).

```typescript
import {
  EVMClient, TxStatus, bytesToHex, getNetwork, prepareReportRequest, type Runtime,
} from '@chainlink/cre-sdk'
import { encodeAbiParameters, parseAbiParameters } from 'viem'

const writePrice = (runtime: Runtime<Config>, price: bigint): string => {
  const network = getNetwork({
    chainFamily: 'evm', chainSelectorName: runtime.config.chainSelectorName,
  })
  if (!network) throw new Error(`Unknown selector: ${runtime.config.chainSelectorName}`)
  const client = new EVMClient(network.chainSelector.selector)
  const timestamp = BigInt(runtime.now().getTime()) / 1000n
  const encoded = encodeAbiParameters(
    parseAbiParameters('(uint256 price,uint256 timestamp)'), [{ price, timestamp }],
  )
  const report = runtime.report(prepareReportRequest(encoded)).result()
  const result = client.writeReport(runtime, {
    receiver: runtime.config.consumerAddress,
    report,
    gasConfig: { gasLimit: runtime.config.gasLimit }, // uint64 decimal string
  }).result()
  if (result.txStatus !== TxStatus.SUCCESS) {
    throw new Error(result.errorMessage ?? `write status ${result.txStatus}`)
  }
  if (!result.txHash) throw new Error('write succeeded without a transaction hash')
  return bytesToHex(result.txHash)
}
```

Use DON time, never local time, in reports. Arrays use `encodeAbiParameters(parseAbiParameters('uint256[]'), [[1n,2n]])`; structs must exactly match Solidity order/types.

`TxStatus.SUCCESS`, `REVERTED`, and `FATAL` map to Go `evm.TxStatus_TX_STATUS_SUCCESS`, `_REVERTED`, and `_FATAL`. Per-write gas is TypeScript `{gasLimit: string}` or Go `&evm.GasConfig{GasLimit:uint64}`; Go `nil` accepts the default.

## Go clients and bindings

Client: `&evm.Client{ChainSelector: config.ChainSelector}` (`uint64`); resolve names with `evm.ChainSelectorFromName`. Put raw `*.abi` arrays or compiled `*.json` artifacts in the generated ABI directory and run:

```bash
cre generate-bindings evm
```

Generated packages live under `contracts/evm/src/generated`. A constructor returns `(binding, error)`; reads take runtime first, optional generated input, then block number, and resolve with `.Await()`:

```go
binding, err := storage.NewStorage(client, common.HexToAddress(config.Address), nil)
if err != nil { return nil, err }
value, err := binding.Get(runtime, big.NewInt(-3)).Await()
```

No-input ABI methods omit the input struct. Generated `WriteReportFrom<StructName>(runtime, data, gasConfig)` helpers are named for public/external ABI input structs and perform encoding, `GenerateReport`, and `WriteReport`.

Low-level Go report/write:

```go
report, err := runtime.GenerateReport(&cre.ReportRequest{
    EncodedPayload: encoded,
    EncoderName: "evm",
    SigningAlgo: "ecdsa",
    HashingAlgo: "keccak256",
}).Await()
if err != nil { return nil, err }
reply, err := client.WriteReport(runtime, &evm.WriteCreReportRequest{
    Receiver: consumer.Bytes(), Report: report,
    GasConfig: &evm.GasConfig{GasLimit: config.GasLimit},
}).Await()
```

Stable signature: `WriteReport(runtime cre.Runtime, input *evm.WriteCreReportRequest) cre.Promise[*evm.WriteReportReply]`. Request fields are `Receiver []byte`, `Report *cre.Report`, optional `GasConfig`; reply fields are `TxStatus`, `ReceiverContractExecutionStatus`, `TxHash []byte`, `TransactionFee *pb.BigInt`, and `ErrorMessage *string`.

## Consumer contract requirements

A consumer receives the report through `KeystoneForwarder` and implements:

```solidity
interface IReceiver {
    function onReport(bytes calldata metadata, bytes calldata report) external;
}
```

`metadata` carries workflow/DON/execution metadata; `report` is the exact ABI payload. Validate `msg.sender` against the immutable configured `KeystoneForwarder` on every call. Prefer the documented `ReceiverTemplate`/`onlyForwarder`, or enforce the same check directly:

```solidity
contract PriceConsumer is IReceiver {
    address public immutable forwarder;
    uint256 public price;
    error UnauthorizedForwarder(address caller);

    constructor(address forwarder_) { forwarder = forwarder_; }

    function onReport(bytes calldata, bytes calldata report) external {
        if (msg.sender != forwarder) revert UnauthorizedForwarder(msg.sender);
        price = abi.decode(report, (uint256));
    }
}
```

Match `abi.decode` types exactly to workflow encoding; keep `onReport` within configured gas; emit indexing/audit events where needed. `ReceiverTemplate` also supplies forwarder validation and ERC165/IReceiver support. CRE receiver interfaces are not Forge/npm packages: copy `IReceiver.sol`, `IERC165.sol`, and `ReceiverTemplate.sol` from the official consumer-contract page, then use the local import; `ReceiverTemplate` depends on OpenZeppelin `Ownable`.

For interval-gated actions, the consumer—not only the workflow—must enforce the minimum interval, reject a report whose `requestedAt` is in the future, and update the last-execution timestamp only after successful validation. Use DON time in the report, but compare against `block.timestamp` at the onchain trust boundary.

Simulation consumers trust `MockKeystoneForwarder`; deployed consumers trust `KeystoneForwarder`. They are different addresses. Pass the correct address to the constructor and change it when moving environments. All address rows are in [chain-selectors.md](chain-selectors.md); do not duplicate or guess them here.

## Type mapping

| Solidity | TypeScript |
|---|---|
| `uint*`, `int*` | `bigint` |
| `address`, `bytes`, `bytes32` | `` `0x${string}` `` |
| `bool`, `string` | `boolean`, `string` |
| tuple | object matching fields/order |
| array | typed array |

Use `viem` `parseUnits`/`formatUnits` for decimal scaling.

## Sources

- https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-ts.md
- https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/writing-data-onchain.md
- https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/building-consumer-contracts.md
- https://docs.chain.link/cre/guides/workflow/using-evm-client/generating-bindings.md
- https://docs.chain.link/cre/reference/sdk/evm-client-go.md
