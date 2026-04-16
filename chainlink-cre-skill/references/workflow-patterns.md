# Workflow Patterns

Use this file for questions about the CRE trigger+callback model, project configuration files, secrets management, DON Time, or randomness.

## Trigger Conditions

- "How does the CRE workflow model work?"
- "How do I configure secrets in my CRE workflow?"
- "How do I use time in a CRE workflow?"
- "How does consensus work for my data?"
- "What files do I need in a CRE project?"

Do not use for specific trigger setup (see triggers.md), specific capability usage (see evm-client.md, http-client.md), or deployment operations (see operations.md).

## The Trigger+Callback Model

Every CRE workflow consists of one or more **handlers**, each pairing a **trigger** with a **callback function**.

### TypeScript Pattern

```typescript
import { CronCapability, handler, Runner, type Runtime } from "@chainlink/cre-sdk"

type Config = {
  schedule: string
  apiUrl: string
}

const onCronTrigger = (runtime: Runtime<Config>): string => {
  runtime.log("Triggered!")
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

### Go Pattern

```go
package main

import (
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
)

type Config struct {
    Schedule string `json:"schedule"`
    ApiUrl   string `json:"apiUrl"`
}

func onCronTrigger(config *Config, runtime cre.Runtime, trigger *cron.Payload) (*string, error) {
    runtime.Logger().Info("Triggered!")
    result := "done"
    return &result, nil
}

func InitWorkflow(config *Config) []cre.HandlerDefinition {
    return []cre.HandlerDefinition{
        cre.Handler(cron.Trigger(cron.Config{Schedule: config.Schedule}), onCronTrigger),
    }
}
```

### Multiple Handlers

A single workflow can register multiple handlers for different triggers:

```typescript
const initWorkflow = (config: Config) => {
  const cron = new CronCapability()
  const http = new HTTPCapability()

  return [
    handler(cron.trigger({ schedule: config.schedule }), onCronTrigger),
    handler(http.trigger({ authorizedKeys: [] }), onHttpTrigger),
  ]
}
```

## Configuration Files

### project.yaml

Global settings shared across all workflows. Contains RPC endpoints for EVM capabilities organized by target:

```yaml
staging-settings:
  evms:
    - chain-selector: "16015286601757825753"
      rpc-url: "https://ethereum-sepolia-rpc.publicnode.com"

production-settings:
  evms:
    - chain-selector: "5009297550715157269"
      rpc-url: "wss://ethereum-mainnet-rpc.example.com"
```

### workflow.yaml

Per-workflow settings: workflow name, entry point path, config file path, and secrets file path for each target:

```yaml
staging-settings:
  user-workflow:
    workflow-name: "my-workflow-staging"
  workflow-artifacts:
    workflow-path: "./main.ts"
    config-path: "./config.staging.json"
    secrets-path: "../secrets.yaml"
```

### config.json

Runtime parameters injected into your workflow. Accessible via `runtime.config` (TypeScript) or the `config` parameter (Go):

```json
{
  "schedule": "*/30 * * * * *",
  "apiUrl": "https://api.example.com/data",
  "chainSelectorName": "ethereum-testnet-sepolia",
  "consumerAddress": "0x1234..."
}
```

### secrets.yaml

Declares secret names that the workflow needs. Values come from environment variables or `.env` file during simulation, and from the Vault DON when deployed:

```yaml
secretsNames:
  MY_API_KEY: "MY_API_KEY_VAR"
```

The key (`MY_API_KEY`) is the secret name used in code. The value (`MY_API_KEY_VAR`) is the environment variable that provides the actual secret value.

## Secrets Management

### In Simulation

1. Declare secrets in `secrets.yaml`
2. Provide values via `.env` file or environment variables
3. Reference `secrets.yaml` in `workflow.yaml` via `secrets-path`
4. Access in code with the SDK's secret API

### TypeScript

```typescript
const apiKey = runtime.getSecret("MY_API_KEY")
if (!apiKey) {
  throw new Error("MY_API_KEY secret not found")
}
```

### Go

```go
apiKey, err := runtime.GetSecret("MY_API_KEY")
if err != nil {
    return nil, fmt.Errorf("failed to get secret: %w", err)
}
```

### In Deployed Workflows

Secrets are stored in the Vault DON. Upload secrets via CLI:

```bash
cre secrets create my-workflow --target production-settings
```

Other secret lifecycle commands:

```bash
cre secrets update my-workflow --target production-settings
cre secrets delete my-workflow --target production-settings
cre secrets list --target production-settings
```

Default timeout for secrets operations is 48 hours. Secrets are organized into namespaces (default: `main`).

### 1Password Integration

For secure secret management, use the 1Password CLI to inject secrets at runtime:

```bash
# .env file with 1Password references
MY_API_KEY_VAR=op://my-vault/my-item/api-key

# Run simulation with 1Password injection
op run --env-file ../.env -- cre workflow simulate my-workflow --target staging-settings
```

## DON Time

In a decentralized environment, all nodes must agree on the current time. CRE provides consensus-derived timestamps through the runtime.

### TypeScript

```typescript
const now = runtime.now()
runtime.log(`Current DON time: ${now.toISOString()}`)
```

### Go

```go
now := runtime.Now()
logger.Info("Current DON time", "time", now)
```

### Execution Modes

- **DON mode** (default): `runtime.Now()` / `runtime.now()` returns the consensus-derived timestamp (median of all node observations). Deterministic across all nodes.
- **Node mode**: Within `runInNodeMode`, the node's local time is accessible but may differ across nodes. Use DON mode timestamps for any value that enters consensus.

### Rules

- Always use `runtime.now()` / `runtime.Now()` for time-dependent logic
- Never use `Date.now()`, `new Date()`, `time.Now()`, or system clocks in DON mode
- DON Time resolution is limited; avoid relying on sub-second precision

## Randomness (Go Only)

CRE provides consensus-safe random number generation through the runtime.

```go
randSource, err := runtime.Rand()
if err != nil {
    return nil, fmt.Errorf("failed to get random source: %w", err)
}

randomInt := randSource.Intn(100)

randomBig := new(big.Int).Rand(randSource, new(big.Int).SetUint64(1000000))
```

### Rules

- Always use `runtime.Rand()` for randomness
- Never use Go's `math/rand` global functions or `crypto/rand` in DON mode
- Random values are mode-aware: values generated in DON mode are deterministic across nodes; values in Node mode may differ
- Do not mix random values across execution modes

## Config Schema Validation (TypeScript)

The TypeScript SDK supports runtime validation via any Standard Schema library (Zod, ArkType):

```typescript
import { z } from "zod"

const configSchema = z.object({
  schedule: z.string(),
  apiUrl: z.string(),
  chainSelectorName: z.string(),
})

type Config = z.infer<typeof configSchema>

export async function main() {
  const runner = await Runner.newRunner<Config>({ configSchema })
  await runner.run(initWorkflow)
}
```

This provides both compile-time type checking and runtime validation of config values.

## The .result() Pattern (TypeScript)

All CRE capability calls in TypeScript return objects with a `.result()` method. Calling `.result()` blocks execution synchronously within the WASM environment and waits for the consensus-verified result:

```typescript
const response = httpClient.sendRequest(runtime, fetchFn, aggregation)(config).result()
const contractCall = evmClient.callContract(runtime, { ... }).result()
const secret = runtime.getSecret("KEY")
```

This pattern is consistent across all SDK capabilities and replaces the `await` pattern from standard async JavaScript.

## The .Await() Pattern (Go)

In Go, asynchronous capability calls return a `Promise` that resolves when `.Await()` is called:

```go
promise := evmBinding.Get(big.NewInt(-3))
result, err := promise.Await()
if err != nil {
    return nil, err
}
```

Execution is single-threaded. `.Await()` drives the event loop forward until the result is available.

## Official Documentation

- Secrets management: `https://docs.chain.link/cre/guides/workflow/secrets`
- Time in workflows: `https://docs.chain.link/cre/guides/workflow/time-in-workflows-ts`
- Randomness: `https://docs.chain.link/cre/guides/workflow/using-randomness`
- Project configuration: `https://docs.chain.link/cre/reference/project-configuration-ts`
