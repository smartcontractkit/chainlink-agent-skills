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

Use `viem` for ABI encoding/decoding. Solidity integers are `bigint`, never `number`. `LAST_FINALIZED_BLOCK_NUMBER` is the SDK's exported opaque finalized sentinel; import and use it directly rather than replacing it with a numeric literal. `-1n` is latest, `-2n` safe, `-3n` pending, and a positive value selects an exact block. The Ethereum Sepolia selector name is `ethereum-testnet-sepolia`; resolve other named chains through [chain-selectors.md](chain-selectors.md). See [concepts.md](concepts.md) for Go's distinct generated/low-level constants.

### Multi-output reads: tuple-to-object decoding

`viem`'s `decodeFunctionResult` returns a **readonly positional tuple** for a function with multiple named outputs, never a named object — destructure it in ABI order and map it into a domain type yourself. `AggregatorV3Interface.latestRoundData()` is the canonical example:

```typescript
const priceFeedAbi = parseAbi([
  'function latestRoundData() view returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)',
])

type RoundData = {
  roundId: bigint; answer: bigint; startedAt: bigint; updatedAt: bigint; answeredInRound: bigint
}

const readLatestRoundData = (runtime: Runtime<Config>): RoundData => {
  const network = getNetwork({
    chainFamily: 'evm', chainSelectorName: runtime.config.chainSelectorName,
  })
  if (!network) throw new Error(`Unknown selector: ${runtime.config.chainSelectorName}`)
  const client = new EVMClient(network.chainSelector.selector)
  const reply = client.callContract(runtime, {
    call: encodeCallMsg({
      from: zeroAddress, to: runtime.config.feedAddress as Address,
      data: encodeFunctionData({ abi: priceFeedAbi, functionName: 'latestRoundData' }),
    }),
    blockNumber: LAST_FINALIZED_BLOCK_NUMBER,
  }).result()
  // decodeFunctionResult is a readonly tuple in declared-output order; destructure positionally,
  // then build the named object — never declare/return the tuple as an object directly.
  const [roundId, answer, startedAt, updatedAt, answeredInRound] = decodeFunctionResult({
    abi: priceFeedAbi, functionName: 'latestRoundData', data: bytesToHex(reply.data),
  })
  if (roundId === 0n || answeredInRound < roundId) throw new Error('round not yet answered')
  return { roundId, answer, startedAt, updatedAt, answeredInRound }
}
```

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

Every consumer must enforce the generic onchain trust boundary: authenticate the configured forwarder, decode the report with the exact ABI types and order emitted by the workflow, and provide a complete compiling receiver implementation. These requirements apply regardless of business policy.

```solidity
interface IReceiver {
    function onReport(bytes calldata metadata, bytes calldata report) external;
}

contract ResourceConsumer is IReceiver {
    address public immutable forwarder;
    uint256 public lastObservedValue;
    error UnauthorizedForwarder(address caller);

    constructor(address forwarder_) {
        forwarder = forwarder_;
    }

    function onReport(bytes calldata, bytes calldata report) external override {
        if (msg.sender != forwarder) revert UnauthorizedForwarder(msg.sender);
        lastObservedValue = abi.decode(report, (uint256));
    }
}
```

`metadata` carries workflow/DON/execution metadata; `report` is the exact ABI payload. Prefer the documented `ReceiverTemplate`/`onlyForwarder`, or enforce the same sender check directly as above.

Match `abi.decode` types exactly to workflow encoding and keep `onReport` within configured gas. Always declare `function onReport(bytes calldata, bytes calldata report) external override`, whether the contract implements `IReceiver` directly, as above, or extends `ReceiverTemplate` — every generated consumer must compile as a complete unit, and `override` is required on `ReceiverTemplate` (its base already declares the function virtual) and on a direct `IReceiver` implementation. `ReceiverTemplate` also supplies forwarder validation and ERC165/IReceiver support. CRE receiver interfaces are not Forge/npm packages: copy `IReceiver.sol`, `IERC165.sol`, and `ReceiverTemplate.sol` from the official consumer-contract page, then use the local import; `ReceiverTemplate` depends on OpenZeppelin `Ownable`.

Do not invent owner-controlled thresholds, interval gates, actions, events, setters, or similar business policy for a generic workflow. Add them only when the user's requested behavior needs them, and emit indexing/audit events only where needed.

If the requested behavior gates an action by a threshold, limit, or eligibility value, never trust a value carried by the report as authoritative — a compromised or buggy workflow could report anything. Keep that policy owner-controlled onchain and gate the action in `onReport` against the stored value.

For requested interval-gated actions, the consumer—not only the workflow—must enforce the minimum interval, reject a report whose `requestedAt` is in the future, and update the last-execution timestamp only after successful validation. Use DON time in the report, but compare against `block.timestamp` at the onchain trust boundary.

Simulation consumers trust `MockKeystoneForwarder`; deployed consumers trust `KeystoneForwarder`. They are different addresses. Pass the correct address to the constructor and change it when moving environments. All address rows are in [chain-selectors.md](chain-selectors.md); do not duplicate or guess them here — verify a forwarder address against the official forwarder-directory page in [official-sources.md](official-sources.md) before a live deployment. Deploying this consumer and the workflow that writes to it also requires the [operations.md](operations.md) prerequisites — CRE Early Access, a funded linked wallet, and a passing simulation — state these explicitly whenever giving deploy guidance, not only the forwarder address.

## Type mapping

| Solidity | TypeScript |
|---|---|
| `uint*`, `int*` | `bigint` |
| `address`, `bytes`, `bytes32` | `` `0x${string}` `` |
| `bool`, `string` | `boolean`, `string` |
| tuple | object matching fields/order |
| array | typed array |

Use `viem` `parseUnits`/`formatUnits` for decimal scaling.

This includes narrow metadata integers such as a decoded `uint8 decimals()`: keep them as `bigint` and never wrap `decodeFunctionResult` in `Number(...)`. JSON configuration cannot contain a bigint, so represent the counterpart as a decimal string and convert that string to `BigInt` for comparison.

## Sources

- https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-ts.md
- https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/writing-data-onchain.md
- https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/building-consumer-contracts.md
- https://docs.chain.link/cre/guides/workflow/using-evm-client/generating-bindings.md
- https://docs.chain.link/cre/reference/sdk/evm-client-go.md
