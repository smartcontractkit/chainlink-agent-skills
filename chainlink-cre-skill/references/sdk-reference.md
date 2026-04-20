# SDK Reference

Use this file when the user needs SDK API details: core types, consensus/aggregation functions, EVM Client methods, HTTP Client methods, or trigger type definitions.

## Trigger Conditions

- "What types does the CRE SDK expose?"
- "How do I use the Runtime type?"
- "What aggregation methods are available?"
- "What's the API for EVMClientCapability?"

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
| `getSecret(name: string)` | `string \| undefined` | Retrieve a secret by name |
| `report(data: `0x${string}`)` | `SignedReport` | Generate a signed report from ABI-encoded data |

#### `handler(trigger, callback)`

Creates a handler definition binding a trigger to a callback function.

```typescript
handler(trigger: TriggerDefinition, callback: HandlerCallback): HandlerDefinition
```

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

### Consensus/Aggregation Types

#### `ConsensusAggregationByFields<T>`

Per-field aggregation configuration:

```typescript
type ConsensusAggregationByFields<T> = {
  method: "byFields"
  fields: {
    [K in keyof T]: { method: "median" | "identical" | "mode" }
  }
}
```

#### `ConsensusAggregationIdentical`

Requires all nodes to return the identical result:

```typescript
type ConsensusAggregationIdentical = {
  method: "identical"
}
```

### EVM Client API

#### `EVMClientCapability`

```typescript
const evmClient = new EVMClientCapability()
```

#### `callContract(runtime, options)`

Read from a smart contract.

```typescript
evmClient.callContract(runtime, {
  toAddress: string,
  chainSelectorName: string,
  callMsg: {
    data: `0x${string}`,
    blockNumber?: bigint,
  },
}): { result(): CallContractResult }
```

`CallContractResult`:
- `data: string` - ABI-encoded return data

#### `writeReport(runtime, options)`

Write a signed report onchain.

```typescript
evmClient.writeReport(runtime, {
  toAddress: string,
  chainSelectorName: string,
  report: SignedReport,
  gasLimit?: bigint,
}): { result(): WriteReportResult }
```

`WriteReportResult`:
- `txHash: string` - Transaction hash
- `txStatus: "Success" | "Reverted" | "Pending" | "FatalError"` - Transaction status

### HTTP Client API

#### `HTTPClientCapability`

```typescript
const httpClient = new HTTPClientCapability()
```

#### `sendRequest(runtime, fetchFn, aggregation)`

Execute a fetch function in DON mode with consensus aggregation.

```typescript
httpClient.sendRequest<Args extends any[], R>(
  runtime: Runtime,
  fetchFn: (...args: Args) => R,
  aggregation: ConsensusAggregation<R>,
): (...args: Args) => { result(): R }
```

#### `runInNodeMode(runtime, fetchFn, aggregation, options?)`

Execute a fetch function in node mode with consensus aggregation.

```typescript
httpClient.runInNodeMode<Args extends any[], R>(
  runtime: Runtime,
  fetchFn: (...args: Args) => R,
  aggregation: ConsensusAggregation<R>,
  options?: { cache?: boolean },
): (...args: Args) => { result(): R }
```

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

#### `EVMLogCapability`

```typescript
const evmLog = new EVMLogCapability()
evmLog.trigger({
  contractAddress: string,
  chainSelectorName: string,
  eventSignature: string,
}): TriggerDefinition
```

Callback receives: `(runtime: Runtime<Config>, event: EVMLogPayload) => T`

`EVMLogPayload`:
- `address: string`
- `topics: string[]`
- `data: string`
- `blockNumber: bigint`
- `transactionHash: string`

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
