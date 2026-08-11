# SDK Reference

Use this file when the user needs SDK API details: core types, consensus/aggregation functions, EVM Client methods, HTTP Client methods, or trigger type definitions.

## Trigger Conditions

- "What types does the CRE SDK expose?"
- "How do I use the Runtime type?"
- "What aggregation methods are available?"
- "What's the API for the EVM client?"

Do not use for workflow structure (see workflow-patterns.md), specific usage examples (see evm-client.md, http-client.md, triggers.md), or CLI commands (see cli-reference.md).

## TypeScript SDK

Package: `@chainlink/cre-sdk`

### Core Types

#### `Runtime<Config>`

The main runtime object passed to handler callbacks. Provides access to configuration, logging, time, secrets, and report generation.

| Property/Method | Return Type | Description |
|-----------------|-------------|-------------|
| `config` | `Config` | Parsed configuration from config.json |
| `log(message: string)` | `void` | Log a message (visible in simulation and monitoring) |
| `now()` | `Date` | Consensus-derived timestamp (DON mode) |
| `getSecret(request)` | `{ result(): Secret }` | Fetch one secret. Takes an object (`{ id, namespace? }`), not a string |
| `getSecrets(requests)` | `{ result(): Record<string, Secret> }` | Fetch several secrets in one call, keyed by `id` |
| `runInNodeMode(fn, aggregation, unwrapOptions?)` | `(...args) => { result(): TOutput }` | Run `fn` on each node and reach consensus on the results |
| `report(input)` | `{ result(): Report }` | Generate a signed report; build `input` with `prepareReportRequest(encodedData)` |

#### Secrets: `getSecret` / `getSecrets`

`getSecret` is **synchronous** and returns a lazy handle, not a `Promise` and not `string | undefined`. Resolve it with `.result()`, then read `.value`:

```typescript
const apiKey = runtime.getSecret({ id: "API_KEY" }).result().value
```

Batch form — the result is keyed by secret `id`:

```typescript
const requests = [{ id: "KEY_A" }, { id: "KEY_B" }]
const secrets = runtime.getSecrets(requests).result()
const keyA = secrets.KEY_A.value
```

Rules that trip people up:

- Never `await` it. There is no `Promise` anywhere in this API; `.result()` blocks until the value is available.
- Never pass a bare string. `runtime.getSecret("API_KEY")` does not type-check — the argument is `{ id, namespace? }`. `namespace` defaults to `main` when omitted.
- A missing or unauthorized secret **throws** (`SecretsError`, or `SecretsBatchError` from `getSecrets`) when `.result()` is called. It does not return `undefined`, so do not write `?? fallback` guards against it — use try/catch if you need a fallback.
- `TeeRuntime` exposes the identical `getSecret`/`getSecrets` shape, because both `Runtime` and `TeeRuntime` extend the same `SecretsProvider` type. Confidential Workflows code and normal DON code read secrets exactly the same way.
- **Secrets are unavailable in node mode.** `NodeRuntime` extends `BaseRuntime` only — not `SecretsProvider` — so `nodeRuntime.getSecret(...)` does not compile. Closing over the outer DON runtime inside a `runInNodeMode` callback fails too: entering node mode sets a `DonModeError` on it, which is thrown from `.result()`. Read secrets in DON mode and pass the values into the node function as arguments.

#### `handler(trigger, callback)`

Creates a handler definition binding a trigger to a callback function.

```typescript
handler(trigger: TriggerDefinition, callback: HandlerCallback): HandlerDefinition
```

#### `handlerInTee(trigger, fn, tees, hooks?)` and `TeeRuntime<Config>`

Confidential Workflows equivalent of `handler`: the callback runs inside a TEE and receives a `TeeRuntime<Config>` instead of a `Runtime<Config>`.

```typescript
handlerInTee(
  trigger: Trigger,
  fn: (runtime: TeeRuntime<Config>, triggerOutput) => TResult,
  tees: TeeConstraint,
  hooks?: Hooks,
): HandlerEntry
```

`TeeRuntime<Config>` extends the base runtime and the secrets provider, adding:

| Method | Return Type | Description |
|--------|-------------|-------------|
| `getSecret(request)` | `{ result(): Secret }` | Fetch a secret, decrypted only inside the enclave |
| `usingTheDons()` | `Runtime<Config>` | Cross back to the Workflow DON; values passed onward are no longer confidential |
| `reportFromDon(input)` | `{ result(): Report }` | Generate a report from the DON without a full crossover |

`TeeConstraint` accepts `{}` (any TEE, any region), `{ regions: [...] }`, or `[{ tee: 'nitro', regions: [...] }]`. See `confidential-workflows.md` for patterns, the confidentiality boundary, and the Go equivalents.

#### `Runner`

Manages workflow lifecycle.

```typescript
const runner = await Runner.newRunner<Config>(options?)
await runner.run(initWorkflow)
```

Options:
- `configSchema?: StandardSchema` - Optional schema for runtime config validation (Zod, ArkType)

#### `Promise<T>` / `.result()`

All capability calls return an object with `.result()` which blocks execution synchronously until the consensus-verified result is available.

```typescript
const response = httpClient.sendRequest(runtime, fetchFn, agg)(url).result()
const contractData = evmClient.callContract(runtime, opts).result()
```

### Consensus/Aggregation

Aggregation is always expressed by **calling SDK functions**. There are no aggregation object literals in this SDK: `{ method: "median" }`, `{ method: "byFields", fields: {...} }`, and any `method:` string tag are invented shapes and will not type-check.

#### Whole-value aggregators

Call these with no arguments; each returns a `ConsensusAggregation` value to hand to `sendRequest` or `runInNodeMode`.

| Function | Applies to | Result |
|----------|-----------|--------|
| `consensusMedianAggregation<T>()` | numeric `T` (`number`, `bigint`, `Date`) | Median across nodes |
| `consensusIdenticalAggregation<T>()` | any `T` | Requires every node to return the same value |
| `consensusCommonPrefixAggregation<T>()` | `T[]` | Longest shared prefix of the arrays |
| `consensusCommonSuffixAggregation<T>()` | `T[]` | Longest shared suffix of the arrays |
| `consensusFrequencyListAggregation<T>()` | `T[]` | `FrequencyListEntry<T>[]` — each value with its observation count |

```typescript
import { consensusIdenticalAggregation } from "@chainlink/cre-sdk"

const answer = httpClient
  .sendRequest(runtime, fetchAnswer, consensusIdenticalAggregation<string>())(url)
  .result()
```

Every aggregation value also has `.withDefault(value)`, which supplies a fallback when a node's execution fails instead of failing the whole aggregation:

```typescript
consensusMedianAggregation<number>().withDefault(0)
```

#### `ConsensusAggregationByFields<T>(fields)`

`ConsensusAggregationByFields` is a **function, not a type**. Never write it as a type annotation on an object literal. Call it with a type parameter for the object being aggregated, and pass a map from field name to a **field aggregator function reference**:

```typescript
import { ConsensusAggregationByFields, median, identical } from "@chainlink/cre-sdk"

type ReserveInfo = {
  totalReserve: number
  lastUpdated: number
  symbol: string
}

const aggregation = ConsensusAggregationByFields<ReserveInfo>({
  totalReserve: median,
  lastUpdated: median,
  symbol: identical,
})
```

The values are the functions themselves — bare `median`, not `median()` and not `{ method: "median" }`. `ConsensusAggregationByFields` invokes them internally.

Field aggregators, imported from `@chainlink/cre-sdk`:

| Aggregator | Applies to | Result |
|------------|-----------|--------|
| `median` | numeric field | Median across nodes |
| `identical` | any field | Requires every node to agree |
| `commonPrefix` | array field | Longest shared prefix |
| `commonSuffix` | array field | Longest shared suffix |
| `frequencyList` | any field | Each observed value with its count |
| `ignore` | any field | Field is dropped from the consensus result |

There is no `mode` aggregator. Use `frequencyList` if you need observation counts.

If a field aggregator reshapes the field type — `frequencyList` turns a field of type `F` into `FrequencyListEntry<F>[]` — pass the result type as the second type parameter so `.result()` is typed correctly:

```typescript
ConsensusAggregationByFields<Observed, Aggregated>({ votes: frequencyList })
```

#### Common mistakes

```typescript
// WRONG — used as a type annotation on an object literal
const agg: ConsensusAggregationByFields<T> = { method: "byFields", fields: { ... } }

// WRONG — field values as objects with a method tag
ConsensusAggregationByFields<T>({ valueScaled: { method: "median" } })

// WRONG — field aggregators called
ConsensusAggregationByFields<T>({ valueScaled: median() })

// RIGHT
ConsensusAggregationByFields<T>({ valueScaled: median })
```

### Capability Class Names

Every capability class is exported twice, under one canonical name: as a top-level export and as a member of the `cre.capabilities` namespace object. `cre.capabilities.EVMClient` **is** the same class object as the top-level `EVMClient` — the namespace is built from the same imports, so the two forms are interchangeable and their constructors take identical arguments. Match whichever style the user's project already uses.

| Capability | Import name | Namespaced form | Constructor |
|------------|-------------|-----------------|-------------|
| EVM client | `EVMClient` | `cre.capabilities.EVMClient` | `new EVMClient(chainSelector: bigint)` |
| Solana client | `SolanaClient` | `cre.capabilities.SolanaClient` | `new SolanaClient(chainSelector: bigint)` |
| HTTP client | `HTTPClient` | `cre.capabilities.HTTPClient` | `new HTTPClient()` |
| Confidential HTTP client | `ConfidentialHTTPClient` | `cre.capabilities.ConfidentialHTTPClient` | `new ConfidentialHTTPClient()` |
| HTTP trigger | `HTTPCapability` | `cre.capabilities.HTTPCapability` | `new HTTPCapability()` |
| Cron trigger | `CronCapability` | `cre.capabilities.CronCapability` | `new CronCapability()` |

There are **no** `EVMClientCapability` or `HTTPClientCapability` exports. Those names do not exist in `@chainlink/cre-sdk` and will fail to import. The blockchain clients are named `EVMClient` / `SolanaClient`; only the trigger capabilities carry the `Capability` suffix (`CronCapability`, `HTTPCapability`).

`cre` also exposes `cre.handler` and `cre.handlerInTee`, which are the same functions as the top-level `handler` / `handlerInTee` exports.

### EVM Client API

#### `EVMClient`

The constructor takes the chain selector for the chain this client talks to, so you need one instance per chain:

```typescript
import { cre, getNetwork } from "@chainlink/cre-sdk"

const network = getNetwork({ chainFamily: "evm", chainSelectorName: "ethereum-testnet-sepolia", isTestnet: true })
const evmClient = new cre.capabilities.EVMClient(network.chainSelector.selector)

// identical to:
import { EVMClient } from "@chainlink/cre-sdk"
const sameThing = new EVMClient(network.chainSelector.selector)
```

#### `callContract(runtime, options)`

Read from a smart contract.

The target chain comes from the client's constructor, not from the call arguments — there is no `chainSelectorName` field here.

```typescript
evmClient.callContract(runtime, {
  call: CallMsg,          // build with encodeCallMsg({ from, to, data })
  blockNumber?: BigInt,   // e.g. LAST_FINALIZED_BLOCK_NUMBER
}): { result(): CallContractReply }
```

`CallContractReply`:
- `data: Uint8Array` - ABI-encoded return data. Convert with `bytesToHex(reply.data)` before passing to viem's `decodeFunctionResult`.

#### `writeReport(runtime, options)`

Write a signed report onchain.

```typescript
evmClient.writeReport(runtime, {
  receiver: string,                      // consumer contract address
  report: Report,                        // from runtime.report(...).result()
  gasConfig?: { gasLimit: string },      // uint64 as a decimal string
}): { result(): WriteReportReply }
```

`WriteReportReply`:
- `txStatus: TxStatus` - compare against the `TxStatus` enum, not string literals
- `txHash?: Uint8Array` - transaction hash; convert with `bytesToHex`
- `errorMessage?: string` - populated on failure

`runtime.report` also returns a lazy handle: `runtime.report(prepareReportRequest(encodedData)).result()`.

### HTTP Client API

#### `HTTPClient`

```typescript
const httpClient = new HTTPClient()
// or: new cre.capabilities.HTTPClient()
```

#### `sendRequest(runtime, fetchFn, aggregation)`

Execute a fetch function in DON mode with consensus aggregation. `fetchFn`'s **first parameter is always an `HTTPSendRequester`** supplied by the SDK; your own arguments follow it and are passed to the returned function.

```typescript
httpClient.sendRequest<TArgs extends unknown[], TInput, TOutput = TInput>(
  runtime: Runtime<unknown>,
  fetchFn: (sendRequester: HTTPSendRequester, ...args: TArgs) => TInput,
  consensusAggregation: ConsensusAggregation<TInput, TOutput, true>,
  unwrapOptions?: UnwrapOptions<TInput>,
): (...args: TArgs) => { result(): TOutput }
```

There is a second, simpler overload for use **inside** a node-mode callback, which takes a request object directly instead of a function:

```typescript
httpClient.sendRequest(
  runtime: NodeRuntime<unknown> | TeeRuntime<unknown>,
  input: Request,
): { result(): Response }
```

Read the response with the exported helpers `ok(response)`, `json(response)`, `text(response)`, `getHeader(response, name)` — `response.body` is raw bytes.

#### `runtime.runInNodeMode(fn, aggregation, unwrapOptions?)`

Runs `fn` on each node and reaches consensus on the results. This is a **`Runtime` method, not an HTTP client method** — there is no `httpClient.runInNodeMode`. `HTTPClient.sendRequest` is itself a thin wrapper that calls `runtime.runInNodeMode` for you.

```typescript
runtime.runInNodeMode<TArgs extends unknown[], TInput, TOutput = TInput>(
  fn: (nodeRuntime: NodeRuntime<Config>, ...args: TArgs) => TInput,
  consensusAggregation: ConsensusAggregation<TInput, TOutput, true>,
  unwrapOptions?: UnwrapOptions<TInput>,
): (...args: TArgs) => { result(): TOutput }
```

The callback's first parameter is a `NodeRuntime<Config>`, supplied by the SDK. Reach for this directly only when `sendRequest` cannot express the work (several requests per node, or non-HTTP per-node computation).

### Trigger Types

#### `CronCapability`

```typescript
const cron = new CronCapability()
cron.trigger({ schedule: string }): TriggerDefinition
```

Callback receives: `(runtime: Runtime<Config>) => T`

#### `HTTPCapability`

```typescript
const http = new HTTPCapability()
http.trigger({ authorizedKeys: string[] }): TriggerDefinition
```

Callback receives: `(runtime: Runtime<Config>, event: HTTPTriggerPayload) => T`

`HTTPTriggerPayload`:
- `body: object`
- `headers: Record<string, string>`
- `url: string`

#### EVM log triggers

There is no `EVMLogCapability` export. Log triggers come off the EVM client itself, via `logTrigger`:

```typescript
const evmClient = new EVMClient(network.chainSelector.selector)

evmClient.logTrigger({
  addresses: string[],           // contract addresses to watch
  topics: TopicValues[],         // indexed topic filters
  confidence?: ConfidenceLevel,  // e.g. finalized
}): Trigger<Log, Log>
```

Callback receives: `(runtime: Runtime<Config>, log: EVMLog) => T`, where `EVMLog` is the SDK's exported log type (`address`, `topics`, `data`, `blockNumber`, `txHash`, all as protobuf-shaped values — byte fields are `Uint8Array`).

In practice, generated contract bindings wrap this. A binding produced from an ABI exposes a per-event helper, which is the form the starter templates use:

```typescript
const monitoredToken = new MonitoredToken(evmClient, config.contractAddress as Address)
cre.handler(monitoredToken.logTriggerLargeTransfer(), onLargeTransfer)
```

### ConfidentialHTTPClient

```typescript
import {
  ConfidentialHTTPClient,
  ConfidentialHTTPSendRequester,
  ConsensusAggregationByFields,
  identical,
} from "@chainlink/cre-sdk"

const confClient = new ConfidentialHTTPClient()

confClient.sendRequest<R>(
  runtime: Runtime,
  callback: (req: ConfidentialHTTPSendRequester) => R,
  aggregation: ConsensusAggregation<R>,
): { result(): R }
```

Inside the callback, use `req.sendRequest()`:

```typescript
req.sendRequest({
  request: {
    url: string,
    method: string,
    bodyString?: string,
    multiHeaders?: Record<string, { values: string[] }>,
  },
  vaultDonSecrets: Array<{ key: string, owner: string }>,
  encryptOutput?: boolean,
}): { result(): { body: ArrayBuffer } }
```

Secrets use `{{.SECRET_NAME}}` template syntax in headers/body. See http-client.md for full usage patterns.

## Go SDK

Package: `github.com/smartcontractkit/cre-sdk-go`

### Core Types

#### `cre.Runtime`

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Logger()` | `Logger` | Structured logger |
| `Now()` | `time.Time` | Consensus-derived timestamp |
| `Rand()` | `(*rand.Rand, error)` | Consensus-safe random source |
| `GetSecret(name string)` | `(string, error)` | Retrieve a secret |
| `Report(data []byte)` | `SignedReport` | Generate signed report |
| `EVMClient()` | `EVMClient` | Access the EVM client |

#### `cre.NodeRuntime`

Available inside `RunInNodeMode` callbacks:

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Fetch(req *http.Request)` | `(*http.Response, error)` | Execute HTTP request |
| `Logger()` | `Logger` | Structured logger |

#### `cre.Handler(trigger, callback)`

```go
cre.Handler(trigger TriggerDefinition, callback HandlerFunc) HandlerDefinition
```

#### `cre.HandlerInTee(trigger, callback, tees)` and `cre.TeeRuntime`

Confidential Workflows equivalent of `cre.Handler`: the callback receives a `cre.TeeRuntime`.

```go
cre.HandlerInTee[C any, M proto.Message, T any, O any](
    trigger Trigger[M, T],
    callback func(config C, runtime cre.TeeRuntime, payload T) (O, error),
    tees cre.TeeConstraint,
) ExecutionHandler[C, Runtime]
```

| Method | Return Type | Description |
|--------|-------------|-------------|
| `GetSecret(*cre.SecretRequest)` | `Promise[*Secret]` | Fetch one secret, decrypted only inside the enclave |
| `GetSecrets([]*cre.SecretRequest)` | `Promise[[]*Secret]` | Batch secret fetch |
| `UsingTheDons()` | `cre.Runtime` | Cross back to the Workflow DON; values passed onward are no longer confidential |
| `ReportFromDon(*cre.ReportRequest)` | `Promise[*Report]` | Generate a report from the DON without a full crossover |

`cre.TeeConstraint` implementations: `cre.AnyTee{}`, `cre.AnyTeeInRegions{Regions: []cre.Region{...}}`, `cre.OneOfTees{cre.Nitro{Regions: []cre.NitroRegion{...}}}`. HTTP from inside the enclave uses `http.Client.SendRequestInTee(runtime, req)`. See `confidential-workflows.md`.

#### `cre.Promise[T]`

Asynchronous result wrapper.

| Method | Return Type | Description |
|--------|-------------|-------------|
| `Await()` | `(T, error)` | Block until result is available |

### EVM Client API (Go)

```go
evmClient := runtime.EVMClient()
```

#### Generated Bindings

```go
binding := abi.NewMyContract(address, chainSelector, evmClient)
result, err := binding.MyMethod(args...).Await()
```

#### WriteReport

```go
txResult, err := evmClient.WriteReport(cre.WriteReportConfig{
    ToAddress:         string,
    ChainSelectorName: string,
    Report:            SignedReport,
    GasLimit:          *big.Int,
}).Await()
```

### HTTP Client API (Go)

```go
httpClient := creHttp.NewHTTPClient()
```

#### RunInNodeMode

```go
result, err := httpClient.RunInNodeMode(runtime, fetchFn, aggregation).Await()
```

### Trigger Types (Go)

#### Cron

```go
import "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"

cron.Trigger(cron.Config{Schedule: "*/30 * * * * *"})
```

Callback: `func(config *Config, runtime cre.Runtime, trigger *cron.Payload) (*Result, error)`

#### Webhook (HTTP)

```go
import "github.com/smartcontractkit/cre-sdk-go/capabilities/triggers/webhooktrigger"

webhooktrigger.Trigger(webhooktrigger.Config{AuthorizedSenders: []string{}})
```

#### EVM Log

```go
import "github.com/smartcontractkit/cre-sdk-go/capabilities/triggers/evmlogtrigger"

evmlogtrigger.Trigger(evmlogtrigger.Config{
    ContractAddress:   "0x...",
    ChainSelectorName: "ethereum-testnet-sepolia",
    EventSignature:    "Transfer(address,address,uint256)",
})
```

## Official Documentation

- TypeScript SDK source: `https://github.com/smartcontractkit/cre-sdk-typescript`
- Go SDK source: `https://github.com/smartcontractkit/cre-sdk-go`
