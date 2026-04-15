# Triggers

Use this file when the user wants to set up cron triggers, HTTP triggers, or EVM log triggers.

## Trigger Conditions

- "How do I set up a cron trigger?"
- "How do I use an HTTP trigger?"
- "How do I listen for onchain events?"
- "How do I trigger a workflow on a schedule?"

Do not use for HTTP client operations (see http-client.md), EVM client reads/writes (see evm-client.md), or general workflow structure (see workflow-patterns.md).

## Trigger Types

CRE supports three trigger types:

| Trigger | Description | Use Case |
|---------|-------------|----------|
| Cron | Time-based scheduling | Periodic data fetching, scheduled onchain writes |
| HTTP | External HTTP request | Webhook endpoints, API-driven workflows |
| EVM Log | Onchain event emission | React to smart contract events |

## Cron Trigger

### TypeScript

```typescript
import { CronCapability, handler, Runner, type Runtime } from "@chainlink/cre-sdk"

type Config = {
  schedule: string
}

const onCronTrigger = (runtime: Runtime<Config>): string => {
  runtime.log(`Cron triggered at ${runtime.now().toISOString()}`)
  return "done"
}

const initWorkflow = (config: Config) => {
  const cron = new CronCapability()
  return [handler(cron.trigger({ schedule: config.schedule }), onCronTrigger)]
}

export async function main() {
  const runner = await Runner.newRunner<Config>()
  await runner.run(initWorkflow)
}
```

### Go

```go
package main

import (
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
)

type Config struct {
    Schedule string `json:"schedule"`
}

func onCronTrigger(config *Config, runtime cre.Runtime, trigger *cron.Payload) (*string, error) {
    runtime.Logger().Info("Cron triggered")
    result := "done"
    return &result, nil
}

func InitWorkflow(config *Config) []cre.HandlerDefinition {
    return []cre.HandlerDefinition{
        cre.Handler(cron.Trigger(cron.Config{Schedule: config.Schedule}), onCronTrigger),
    }
}
```

### Cron Expression Format

Standard 5-field cron expressions with an optional 6th field for seconds:

```
┌──────────── second (optional, 0-59)
│ ┌────────── minute (0-59)
│ │ ┌──────── hour (0-23)
│ │ │ ┌────── day of month (1-31)
│ │ │ │ ┌──── month (1-12)
│ │ │ │ │ ┌── day of week (0-6, Sunday=0)
│ │ │ │ │ │
* * * * * *
```

Examples:
- `*/30 * * * * *` = every 30 seconds
- `0 */5 * * * *` = every 5 minutes
- `0 0 * * * *` = every hour
- `0 0 12 * * *` = daily at noon UTC

### CronPayload

The trigger callback receives a `CronPayload` with:
- `scheduledTime`: The scheduled trigger time (use for time-based logic instead of `runtime.now()`)

### Timezone Support

Cron expressions run in UTC by default. Time-zone aware scheduling is available with the `TZ` prefix:

```json
{
  "schedule": "CRON_TZ=America/New_York 0 9 * * *"
}
```

## HTTP Trigger

### TypeScript

```typescript
import { HTTPCapability, handler, Runner, type Runtime, type HTTPTriggerPayload } from "@chainlink/cre-sdk"

type Config = {
  authorizedKeys: string[]
}

const onHttpTrigger = (runtime: Runtime<Config>, triggerEvent: HTTPTriggerPayload): string => {
  runtime.log(`HTTP trigger received: ${JSON.stringify(triggerEvent.body)}`)
  return JSON.stringify({ status: "ok", received: triggerEvent.body })
}

const initWorkflow = (config: Config) => {
  const http = new HTTPCapability()
  return [handler(http.trigger({ authorizedKeys: config.authorizedKeys }), onHttpTrigger)]
}

export async function main() {
  const runner = await Runner.newRunner<Config>()
  await runner.run(initWorkflow)
}
```

### Go

```go
package main

import (
    "encoding/json"
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/triggers/webhooktrigger"
)

type Config struct {
    AuthorizedKeys []string `json:"authorizedKeys"`
}

type Result struct {
    Status string `json:"status"`
}

func onHTTPTrigger(config *Config, runtime cre.Runtime, trigger *webhooktrigger.Payload) (*Result, error) {
    runtime.Logger().Info("HTTP trigger received")
    return &Result{Status: "ok"}, nil
}

func InitWorkflow(config *Config) []cre.HandlerDefinition {
    return []cre.HandlerDefinition{
        cre.Handler(
            webhooktrigger.Trigger(webhooktrigger.Config{AuthorizedSenders: config.AuthorizedKeys}),
            onHTTPTrigger,
        ),
    }
}
```

### HTTPTriggerPayload Fields

| Field | Type | Description |
|-------|------|-------------|
| `body` | `object` | Parsed JSON body of the request |
| `headers` | `Record<string, string>` | Request headers |
| `url` | `string` | Request URL path |

### Authorization

For deployed workflows, HTTP triggers require authorized sender keys to prevent unauthorized invocations. Set the `authorizedKeys` field in the config to a list of approved Ethereum addresses:

```json
{
  "authorizedKeys": ["0xABC123..."]
}
```

For simulation, leave the array empty to accept any request.

### Testing HTTP Triggers in Simulation

```bash
cre workflow simulate my-workflow --target staging-settings
```

In a separate terminal, send a test request:

```bash
curl -X POST http://localhost:8080/trigger \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

## EVM Log Trigger

### TypeScript

```typescript
import { EVMLogCapability, handler, Runner, type Runtime, type EVMLogPayload } from "@chainlink/cre-sdk"

type Config = {
  contractAddress: string
  chainSelectorName: string
}

const onLogTrigger = (runtime: Runtime<Config>, triggerEvent: EVMLogPayload): string => {
  runtime.log(`Event received from ${triggerEvent.address}`)
  runtime.log(`Topics: ${JSON.stringify(triggerEvent.topics)}`)
  return "processed"
}

const initWorkflow = (config: Config) => {
  const evmLog = new EVMLogCapability()
  return [
    handler(
      evmLog.trigger({
        contractAddress: config.contractAddress,
        chainSelectorName: config.chainSelectorName,
        eventSignature: "Transfer(address,address,uint256)",
      }),
      onLogTrigger,
    ),
  ]
}

export async function main() {
  const runner = await Runner.newRunner<Config>()
  await runner.run(initWorkflow)
}
```

### Go

```go
package main

import (
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/triggers/evmlogtrigger"
)

type Config struct {
    ContractAddress   string `json:"contractAddress"`
    ChainSelectorName string `json:"chainSelectorName"`
}

func onLogTrigger(config *Config, runtime cre.Runtime, trigger *evmlogtrigger.Payload) (*string, error) {
    runtime.Logger().Info("Event received", "address", trigger.Address)
    result := "processed"
    return &result, nil
}

func InitWorkflow(config *Config) []cre.HandlerDefinition {
    return []cre.HandlerDefinition{
        cre.Handler(
            evmlogtrigger.Trigger(evmlogtrigger.Config{
                ContractAddress:   config.ContractAddress,
                ChainSelectorName: config.ChainSelectorName,
                EventSignature:    "Transfer(address,address,uint256)",
            }),
            onLogTrigger,
        ),
    }
}
```

### EVMLogPayload Fields

| Field | Type | Description |
|-------|------|-------------|
| `address` | `string` | Contract address that emitted the event |
| `topics` | `string[]` | Indexed event parameters |
| `data` | `string` | ABI-encoded non-indexed parameters |
| `blockNumber` | `bigint` | Block number where the event was emitted |
| `transactionHash` | `string` | Hash of the transaction |

### Event Signature Format

Use the Solidity event signature string format:

```
Transfer(address,address,uint256)
Approval(address,address,uint256)
OwnershipTransferred(address,address)
```

Topic filtering can be used to narrow the events received. Check the SDK reference for advanced topic filter configuration.

## Official Documentation

- Cron trigger: `https://docs.chain.link/cre/guides/workflow/using-triggers/cron-trigger-ts`
- HTTP trigger: `https://docs.chain.link/cre/guides/workflow/using-triggers/http-trigger-ts`
- EVM log trigger: `https://docs.chain.link/cre/guides/workflow/using-triggers/evm-log-trigger-ts`
