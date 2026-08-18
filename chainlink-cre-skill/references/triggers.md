# Triggers

CRE supports cron, HTTP, and EVM-log triggers. [workflow-patterns.md](workflow-patterns.md) owns Runner/handler scaffolding; this file supplies trigger-specific registration, payloads, and constraints.

## Cron

TypeScript:

```typescript
const cron = new CronCapability()
const trigger = cron.trigger({ schedule: config.schedule })
// handler(trigger, (runtime: Runtime<Config>) => output)
```

Go: `cron.Trigger(&cron.Config{Schedule: config.Schedule})`; callback payload is `*cron.Payload`.

Cron accepts five fields with an optional leading seconds field:

```text
second? minute hour day-of-month month day-of-week
```

Examples: `*/30 * * * * *` every 30 seconds; `0 */5 * * * *` every five minutes; `0 0 * * * *` hourly; `0 0 12 * * *` noon UTC. Default timezone is UTC; timezone-aware schedules use `CRON_TZ=America/New_York 0 9 * * *`. Cron callbacks obtain consensus time from `runtime.now()`/`runtime.Now()`; do not require or invent a `scheduledTime` payload field.

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

Go uses `webhooktrigger.Trigger(webhooktrigger.Config{AuthorizedSenders: config.AuthorizedKeys})`; callback payload is `*webhooktrigger.Payload`.

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

Go uses generated binding helpers when possible. Low-level registration uses the EVM log trigger/filter request types from the installed SDK; legacy project templates may expose:

```go
evmlogtrigger.Trigger(evmlogtrigger.Config{
    ContractAddress: config.ContractAddress,
    ChainSelectorName: config.ChainSelectorName,
    EventSignature: "Transfer(address,address,uint256)",
})
```

Event signatures omit names/spaces: `Transfer(address,address,uint256)`, `Approval(address,address,uint256)`, `OwnershipTransferred(address,address)`. Only indexed parameters can be topic-filtered. Use finalized confidence unless the product explicitly accepts reorg risk; constants are in [concepts.md](concepts.md).

## Composition

Register several trigger/callback pairs in one workflow when they share config, secrets, and consumers; instantiate each capability once. Separate workflows only for distinct chains, lifecycles, namespaces, or ownership. For non-interactive simulation, run each handler independently with `--trigger-index` and matching HTTP/EVM inputs.

## Sources

- https://docs.chain.link/cre/guides/workflow/using-triggers/cron-trigger-ts.md
- https://docs.chain.link/cre/guides/workflow/using-triggers/http-trigger/configuration-ts.md
- https://docs.chain.link/cre/guides/workflow/using-triggers/evm-log-trigger-ts.md
- https://docs.chain.link/cre/reference/sdk/triggers/overview-go.md
