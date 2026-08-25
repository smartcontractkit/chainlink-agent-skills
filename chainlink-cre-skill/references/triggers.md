# Triggers

CRE supports cron, HTTP, and EVM-log triggers. [workflow-patterns.md](workflow-patterns.md) owns Runner/handler scaffolding; this file supplies trigger-specific registration, payloads, and constraints.

| Category | TypeScript trigger/config | Callback shape |
|---|---|---|
| Schedule | `new CronCapability().trigger({ schedule })` | TS `(runtime: Runtime<C>) => O`; Go `func(*C, cre.Runtime, *cron.Payload) (O, error)` |
| Webhook | `new HTTPCapability().trigger({ authorizedKeys })` | TS `(runtime: Runtime<C>, event: HTTPTriggerPayload) => O`; Go `func(*C, cre.Runtime, *http.Payload) (O, error)` |
| Contract event | `new EVMClient(selector).logTrigger({ addresses, topics, confidence })` | TS `(runtime: Runtime<C>, event: Log) => O`; Go uses the generated binding or installed SDK payload type |

Register every trigger/callback pair with `handler(trigger, callback)` (Go: `cre.Handler(trigger, callback)`). Return each registration from the local `initWorkflow`; never discard handler definitions or import/call an SDK `initWorkflow`. Every complete TypeScript example must include an executable `main` that creates `Runner` and runs that local `initWorkflow`; [workflow-patterns.md](workflow-patterns.md) supplies the canonical scaffolding. If the user asks for cron and HTTP/webhook behavior together — even as a question about which triggers the workflow supports — answer with one complete dual-handler path: imports, config and payload types, defined callbacks, both handler registrations, local `initWorkflow`, and `Runner`/`main`. Use `runtime.now()`/`runtime.Now()` for time and return serialized strings from TypeScript handlers; never replace this path with trigger names or registration fragments.

## Cron

TypeScript:

```typescript
const cron = new CronCapability()
const trigger = cron.trigger({ schedule: config.schedule })
// handler(trigger, (runtime: Runtime<Config>) => output)
```

Go: `cron.Trigger(&cron.Config{Schedule: config.Schedule})`; callback payload is `*cron.Payload`.

CRE cron schedules have exactly six fields:

```text
second minute hour day-of-month month day-of-week
```

Emit six fields everywhere a schedule appears, including source, target config JSON, workflow records, docs, and commands. Use `0 */5 * * * *` for every five minutes. If the user supplies a five-field schedule, preserve its meaning by prepending the seconds field `0`, or reject it clearly when normalization is unsafe; never emit the five-field form. Other examples: `*/30 * * * * *` every 30 seconds; `0 0 * * * *` hourly; `0 0 12 * * *` noon UTC. Default timezone is UTC; timezone-aware schedules use `CRON_TZ=America/New_York 0 0 9 * * *` (the timezone prefix is not a cron field). Cron callbacks obtain consensus time from `runtime.now()`/`runtime.Now()`; do not require or invent a `scheduledTime` payload field.

## HTTP trigger

TypeScript:

```typescript
const http = new HTTPCapability()
const trigger = http.trigger({ authorizedKeys: config.authorizedKeys })
const onHTTP = (
  runtime: Runtime<Config>,
  event: HTTPTriggerPayload,
): string => JSON.stringify({ status: 'ok', received: event.body })
```

Go uses the same `github.com/smartcontractkit/cre-sdk-go/capabilities/networking/http` package as the HTTP client — there is no separate `webhooktrigger` package:

```go
authorizedKeys := []*http.AuthorizedKey{
    {Type: http.KeyType_KEY_TYPE_ECDSA_EVM, PublicKey: config.AuthorizedEVMAddress},
}
httpTrigger := http.Trigger(&http.Config{AuthorizedKeys: authorizedKeys})
```

The callback payload is `*http.Payload`: `Input []byte` is the raw JSON request body (`json.Unmarshal` it), `Key` is the authorized signer that triggered the run.

TypeScript `HTTPTriggerPayload` supplies the request body to the handler; consume `event.body` and return a serialized string rather than depending on an assumed `event.url` field. Deployed HTTP triggers require authorized Ethereum public-key addresses; an empty authorized-senders list is valid only for simulation, where approved senders may be omitted. Deployed requests use the documented JSON-RPC/JWT signature flow; never handle the caller's private signing key. For simulation inputs and `--http-payload`, see [simulation.md](simulation.md).

## EVM log trigger

There is no TypeScript `EVMLogCapability`. Resolve the selector with `getNetwork`, construct `new EVMClient(network.chainSelector.selector)`, then use:

```typescript
evmClient.logTrigger({
  addresses: string[],
  topics: TopicValues[],
  confidence?: ConfidenceLevel,
}): Trigger<Log, Log>
```

The SDK `Log`/`EVMLog` payload contains address, topics, data, block number, and transaction hash in protobuf-shaped fields; byte fields are `Uint8Array`. Low-level address/topic filters require the SDK's documented base64 encoding, and indexed values must be padded to 32 bytes; do not invent an encoder. Generated bindings are safer and expose per-event helpers such as `binding.logTriggerLargeTransfer()`.

Go prefers generated binding helpers for a single event on a single contract — resolve the chain selector by name (never invent one; look it up in [chain-selectors.md](chain-selectors.md)), bind the contract, and register the generated `LogTrigger<Event>Log` helper. The callback receives a decoded, type-safe payload, not a raw byte-oriented struct:

Save this complete minimal ABI as `contracts/evm/src/MyToken.abi`, then generate the binding:

```json
[
  {
    "anonymous": false,
    "inputs": [
      {"indexed": true, "name": "from", "type": "address"},
      {"indexed": true, "name": "to", "type": "address"},
      {"indexed": false, "name": "value", "type": "uint256"}
    ],
    "name": "Transfer",
    "type": "event"
  }
]
```

```bash
cre generate-bindings evm
```

The generated binding import must start with the exact `module` value from the generated project's root `go.mod`. The complete example below uses this explicit reversible sample module (sample only):

```go
module example.com/cre-transfer-sample
```

If the generated `go.mod` declares a different module, replace `example.com/cre-transfer-sample` in the import with that exact value; never leave an unresolved module placeholder.

```go
package main

import (
	"fmt"
	"log/slog"

	"github.com/ethereum/go-ethereum/common"
	"github.com/smartcontractkit/cre-sdk-go/capabilities/blockchain/evm"
	"github.com/smartcontractkit/cre-sdk-go/capabilities/blockchain/evm/bindings"
	"github.com/smartcontractkit/cre-sdk-go/cre"
	"github.com/smartcontractkit/cre-sdk-go/cre/wasm"
	"example.com/cre-transfer-sample/contracts/evm/src/generated/my_token" // generated by `cre generate-bindings evm`
)

type Config struct {
	ChainSelectorName string
	TokenAddress      string
}

type TransferLog struct {
	From, To string
	Amount   string
}

func onTransfer(config *Config, runtime cre.Runtime, payload *bindings.DecodedLog[my_token.TransferDecoded]) (*TransferLog, error) {
	logger := runtime.Logger()
	from, to, value := payload.Data.From, payload.Data.To, payload.Data.Value
	logger.Info("Transfer detected", "from", from.Hex(), "to", to.Hex(), "value", value.String())
	return &TransferLog{From: from.Hex(), To: to.Hex(), Amount: value.String()}, nil
}

func InitWorkflow(config *Config, _ *slog.Logger, _ cre.SecretsProvider) (cre.Workflow[*Config], error) {
	chainSelector, err := evm.ChainSelectorFromName(config.ChainSelectorName)
	if err != nil {
		return nil, fmt.Errorf("failed to resolve chain selector: %w", err)
	}
	client := &evm.Client{ChainSelector: chainSelector}
	tokenContract, err := my_token.NewMyToken(client, common.HexToAddress(config.TokenAddress), nil)
	if err != nil {
		return nil, fmt.Errorf("failed to bind contract: %w", err)
	}
	logTrigger, err := tokenContract.LogTriggerTransferLog(chainSelector, evm.ConfidenceLevel_CONFIDENCE_LEVEL_FINALIZED, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create log trigger: %w", err)
	}
	return cre.Workflow[*Config]{
		cre.Handler(logTrigger, onTransfer),
	}, nil
}

func main() {
	wasm.NewRunner(cre.ParseJSON[Config]).Run(InitWorkflow)
}
```

Callback signatures always return a pointer output type (`(*TransferLog, error)`, never a bare `string`/struct), and `payload.Log` (not shown above) carries raw metadata — `BlockNumber *pb.BigInt`, `TxHash []byte`, `Index uint32` — for cases that need it. Without generated bindings, low-level registration uses the EVM log trigger/filter request types from the installed SDK (`evm.FilterLogTriggerRequest{Addresses: [][]byte{...}, Topics: []*evm.TopicValues{...}}`); the handler then receives a raw `*evm.Log` whose `Topics` are `[][]byte` — decode an indexed `address` with `common.BytesToAddress(log.Topics[n][12:])`. Legacy project templates may instead expose `evmlogtrigger.Trigger(evmlogtrigger.Config{...})`; match whichever payload type the installed SDK/template actually declares rather than assuming one shape.

Event signatures omit names/spaces: `Transfer(address,address,uint256)`, `Approval(address,address,uint256)`, `OwnershipTransferred(address,address)`. Only indexed parameters can be topic-filtered. Use finalized confidence unless the product explicitly accepts reorg risk; constants are in [concepts.md](concepts.md).

## Composition

Register several trigger/callback pairs in one workflow when they share config, secrets, and consumers; instantiate each capability once. Separate workflows only for distinct chains, lifecycles, namespaces, or ownership. For non-interactive simulation, run each handler independently with `--trigger-index` and matching HTTP/EVM inputs.

Canonical multi-trigger TypeScript example — schedule plus webhook, complete and runnable, not a fragment to finish with prose:

```typescript
import { CronCapability, HTTPCapability, Runner, handler, type HTTPTriggerPayload, type Runtime } from '@chainlink/cre-sdk'

type Config = { schedule: string; authorizedKeys: string[] }

const onCronTrigger = (runtime: Runtime<Config>): string =>
  JSON.stringify({ status: 'ok', triggeredAt: runtime.now().toISOString() })
const onHTTP = (runtime: Runtime<Config>, event: HTTPTriggerPayload): string =>
  JSON.stringify({ status: 'ok', received: event.body })

const initWorkflow = (config: Config) => [
  handler(new CronCapability().trigger({ schedule: config.schedule }), onCronTrigger),
  handler(new HTTPCapability().trigger({ authorizedKeys: config.authorizedKeys }), onHTTP),
]

export async function main() {
  const runner = await Runner.newRunner<Config>()
  await runner.run(initWorkflow)
}
```

## Sources

- https://docs.chain.link/cre/guides/workflow/using-triggers/cron-trigger-ts.md
- https://docs.chain.link/cre/guides/workflow/using-triggers/cron-trigger-go.md
- https://docs.chain.link/cre/guides/workflow/using-triggers/http-trigger/configuration-ts.md
- https://docs.chain.link/cre/guides/workflow/using-triggers/http-trigger/configuration-go.md
- https://docs.chain.link/cre/guides/workflow/using-triggers/evm-log-trigger-ts.md
- https://docs.chain.link/cre/guides/workflow/using-triggers/evm-log-trigger-go.md
- https://docs.chain.link/cre/reference/sdk/triggers/overview-go.md
