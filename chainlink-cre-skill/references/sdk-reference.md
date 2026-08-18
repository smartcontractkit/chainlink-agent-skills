# SDK Reference

Exact API map for `@chainlink/cre-sdk` and `github.com/smartcontractkit/cre-sdk-go`. Use capability guides for examples. Match installed versions when a live declaration differs.

## TypeScript core

`Runtime<Config>`:

| Member | Contract |
|---|---|
| `config: Config` | parsed target config |
| `log(message): void` | workflow log |
| `now(): Date` | consensus time |
| `getSecret({id,namespace?})` | lazy `Secret`; `.result().value` |
| `getSecrets(requests)` | lazy map keyed by ID |
| `runInNodeMode(fn,aggregation,unwrapOptions?)` | returns an argument-taking function whose result is lazy |
| `report(input)` | lazy signed `Report`; use `prepareReportRequest(encoded)` |

`getSecret` never takes a string or returns `undefined`; `.result()` throws `SecretsError`/`SecretsBatchError`. `namespace` defaults to `main`. `NodeRuntime` lacks secrets; closing over DON runtime while in node mode yields `DonModeError`. `TeeRuntime` shares the secrets provider.

```typescript
handler(trigger: TriggerDefinition, callback: HandlerCallback): HandlerDefinition
const runner = await Runner.newRunner<Config>({ configSchema? })
await runner.run(initWorkflow)
```

Every capability returns a synchronous lazy handle resolved by `.result()`, not a JavaScript `Promise`.

### Confidential Workflow core

```typescript
handlerInTee(
  trigger: Trigger,
  fn: (runtime: TeeRuntime<Config>, output) => TResult,
  tees: TeeConstraint,
  hooks?: Hooks,
): HandlerEntry
```

`TeeRuntime`: `getSecret`, `getSecrets`, `usingTheDons(): Runtime<Config>`, `reportFromDon(input)`, base `config`/`now`/`log`. Constraints accept `{}`, `{regions:[...]}`, or `[{tee:'nitro',regions:[...]}]`. See [confidential-workflows.md](confidential-workflows.md) for the security boundary.

## TypeScript consensus

Whole-value functions are called:

| Function | Input/result |
|---|---|
| `consensusMedianAggregation<T>()` | numeric (`number`, `bigint`, `Date`, `Decimal`, `Int64`, `UInt64`) → median |
| `consensusIdenticalAggregation<T>()` | any serializable value → identical |
| `consensusCommonPrefixAggregation<T>()` | arrays → common prefix |
| `consensusCommonSuffixAggregation<T>()` | arrays → common suffix |
| `consensusFrequencyListAggregation<T>()` | values → `FrequencyListEntry<T>[]` |

Each supports `.withDefault(value)`. Field aggregation is a function call with bare aggregator references:

```typescript
ConsensusAggregationByFields<Input, Output?>({
  price: median, symbol: identical, observations: frequencyList, noise: ignore,
})
```

Other reference: `commonPrefix`, `commonSuffix`. Never use `ConsensusAggregationByFields` as a type, call field functions, or invent `{method:'median'}`/`method:'byFields'`. There is no `mode`.

## TypeScript capabilities

Top-level and `cre.capabilities.*` exports are the same class objects; top-level `handler`/`handlerInTee` equal `cre.handler`/`cre.handlerInTee`.

| Capability | Constructor |
|---|---|
| `EVMClient` | `new EVMClient(chainSelector: bigint)` |
| `SolanaClient` | `new SolanaClient(chainSelector: bigint)` |
| `HTTPClient` | `new HTTPClient()` |
| `ConfidentialHTTPClient` | `new ConfidentialHTTPClient()` |
| `HTTPCapability` | `new HTTPCapability()` |
| `CronCapability` | `new CronCapability()` |

There are no `EVMClientCapability`, `HTTPClientCapability`, or `EVMLogCapability` exports.

### EVM

```typescript
client.callContract(runtime, {
  call: encodeCallMsg({from,to,data}),
  blockNumber?: bigint,
}): { result(): CallContractReply }
```

`CallContractReply.data` is `Uint8Array`; convert with `bytesToHex` before `viem.decodeFunctionResult`. The chain is fixed by the client constructor.

```typescript
client.writeReport(runtime, {
  receiver: string,
  report: Report,
  gasConfig?: { gasLimit: string },
}): { result(): WriteReportReply }
```

Reply: `txStatus: TxStatus`, optional `txHash: Uint8Array`, optional `errorMessage`. Compare the enum, not strings. Report: `runtime.report(prepareReportRequest(encoded)).result()`.

### HTTP and node mode

```typescript
http.sendRequest<TArgs extends unknown[], TIn, TOut = TIn>(
  runtime: Runtime<unknown>,
  fn: (sender: HTTPSendRequester, ...args: TArgs) => TIn,
  aggregation: ConsensusAggregation<TIn,TOut,true>,
  unwrapOptions?: UnwrapOptions<TIn>,
): (...args: TArgs) => { result(): TOut }
```

Inside node/TEE mode:

```typescript
http.sendRequest(
  runtime: NodeRuntime<unknown> | TeeRuntime<unknown>, request: Request,
): { result(): Response }
```

Response helpers: `ok`, `json`, `text`, `getHeader`; body is bytes. `Runtime.runInNodeMode` (not an HTTP-client method):

```typescript
runtime.runInNodeMode<TArgs extends unknown[],TIn,TOut = TIn>(
  fn: (node: NodeRuntime<Config>, ...args: TArgs) => TIn,
  aggregation: ConsensusAggregation<TIn,TOut,true>,
  unwrapOptions?: UnwrapOptions<TIn>,
): (...args: TArgs) => { result(): TOut }
```

### Triggers

| Trigger | Definition / callback |
|---|---|
| cron | `new CronCapability().trigger({schedule:string})`; `(Runtime<C>, CronPayload?)` |
| HTTP | `new HTTPCapability().trigger({authorizedKeys:string[]})`; `(Runtime<C>, HTTPTriggerPayload)` |
| EVM log | `new EVMClient(selector).logTrigger({addresses,topics,confidence?})`; `(Runtime<C>, Log)` |

`HTTPTriggerPayload`: `body`, `headers`, `url`. `Log` fields include address, topics, data, block number, transaction hash; protobuf byte fields are `Uint8Array`. Generated bindings expose typed event helpers.

### Confidential HTTP

```typescript
new ConfidentialHTTPClient().sendRequest<R>(
  runtime: Runtime,
  callback: (sender: ConfidentialHTTPSendRequester) => R,
  aggregation: ConsensusAggregation<R>,
): { result(): R }
```

Callback request:

```typescript
sender.sendRequest({
  request: { url, method, bodyString?, multiHeaders? },
  vaultDonSecrets: [{ key, owner }],
  encryptOutput?: boolean,
}).result()
```

Secrets use `{{.SECRET_NAME}}` in headers/body.

## Go core

`cre.Runtime`: `Logger()`, `Now() time.Time`, `Rand() (*rand.Rand,error)`, secret provider methods, and `GenerateReport(*cre.ReportRequest) cre.Promise[*cre.Report]`. `cre.NodeRuntime` supplies `Fetch(*http.Request)` and `Logger()`.

```go
cre.Handler[C any, M proto.Message, T any, O any](
    trigger Trigger[M,T],
    callback func(config C, runtime cre.Runtime, payload T) (O,error),
) ExecutionHandler[C,Runtime]
```

```go
cre.HandlerInTee[C any, M proto.Message, T any, O any](
    trigger Trigger[M,T],
    callback func(config C, runtime cre.TeeRuntime, payload T) (O,error),
    tees cre.TeeConstraint,
) ExecutionHandler[C,Runtime]
```

`cre.Promise[T].Await() (T,error)`. `cre.TeeRuntime`: `GetSecret(*cre.SecretRequest)`, `GetSecrets([]*cre.SecretRequest)`, `UsingTheDons() cre.Runtime`, `ReportFromDon(*cre.ReportRequest)`. Constraints: `cre.AnyTee{}`, `cre.AnyTeeInRegions{...}`, `cre.OneOfTees{cre.Nitro{...}}`. In-enclave HTTP: `http.Client.SendRequestInTee(runtime,req)`.

## Go EVM

```go
client := &evm.Client{ChainSelector: selector} // uint64
selector, err := evm.ChainSelectorFromName(name)
```

Generated binding calls: `binding.Method(runtime, Input{...}, blockNumber).Await()`; no-input methods omit `Input`. Generated writes use `WriteReportFrom<StructName>(runtime,data,gasConfig)`.

Low-level stable signature:

```go
WriteReport(runtime cre.Runtime, input *evm.WriteCreReportRequest) cre.Promise[*evm.WriteReportReply]
```

Request: `Receiver []byte`, `Report *cre.Report`, optional `GasConfig *evm.GasConfig` (`GasLimit uint64`). Reply: `TxStatus`, `ReceiverContractExecutionStatus`, `TxHash []byte`, `TransactionFee *pb.BigInt`, `ErrorMessage *string`. Statuses: `TX_STATUS_SUCCESS`, `TX_STATUS_REVERTED`, `TX_STATUS_FATAL`.

Report fields:

```go
&cre.ReportRequest{
  EncodedPayload: encoded, EncoderName: "evm",
  SigningAlgo: "ecdsa", HashingAlgo: "keccak256",
}
```

## Go HTTP and triggers

HTTP client: `creHttp.NewHTTPClient()`; `RunInNodeMode(runtime,fetchFn,aggregation).Await()`. Node HTTP is `cre.NodeRuntime.Fetch`.

| Trigger | API / payload |
|---|---|
| cron | `cron.Trigger(&cron.Config{Schedule: ...})`; `*cron.Payload` |
| HTTP | `webhooktrigger.Trigger(webhooktrigger.Config{AuthorizedSenders: ...})`; webhook payload |
| EVM log | generated helper preferred; low-level `evmlogtrigger` config/filter types |

## Sources

- https://github.com/smartcontractkit/cre-sdk-typescript
- https://github.com/smartcontractkit/cre-sdk-go
- https://docs.chain.link/cre/reference/sdk/overview-ts.md
- https://docs.chain.link/cre/reference/sdk/overview-go.md
