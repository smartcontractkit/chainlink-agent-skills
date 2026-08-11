# HTTP Client

Use this file when the user wants to make HTTP GET/POST requests, use sendRequest or runInNodeMode, submit reports via HTTP, or use the Confidential HTTP client.

## Trigger Conditions

- "How do I make an HTTP request from a CRE workflow?"
- "How do I fetch data from an API?"
- "What is the difference between sendRequest and runInNodeMode?"
- "How do I use the Confidential HTTP client?"

Do not use for HTTP triggers (see triggers.md), EVM operations (see evm-client.md), or general workflow patterns (see workflow-patterns.md).

## HTTP Request Patterns

CRE provides two patterns for HTTP requests:

| Pattern | Use Case | Execution |
|---------|----------|-----------|
| `sendRequest` | Simple GET/POST with consensus | DON mode: all nodes make the same request, results are aggregated |
| `runInNodeMode` | Complex request logic, custom headers, secrets | Node mode: each node runs independently, results are aggregated |

### Recommendation

Use `sendRequest` for most cases. It is simpler, more efficient, and runs entirely in DON mode. Use `runInNodeMode` when you need:
- Custom headers (e.g., authorization)
- Request bodies with dynamic data
- Secret injection (API keys)
- Complex request logic

## GET Request with sendRequest (TypeScript)

```typescript
import {
  HTTPClient,
  CronCapability,
  handler,
  Runner,
  json,
  ok,
  type HTTPSendRequester,
  type Runtime,
  ConsensusAggregationByFields,
  median,
  identical,
} from "@chainlink/cre-sdk"
import { z } from "zod"

type Config = {
  schedule: string
  apiUrl: string
}

const responseSchema = z.object({
  price: z.number(),
  symbol: z.string(),
})

type ApiResponse = z.infer<typeof responseSchema>

// The fetch function's FIRST parameter is always an HTTPSendRequester supplied by
// the SDK. Your own arguments come after it, and are passed to the returned function.
// Do not use the global `fetch` here — HTTP goes through the send requester.
const fetchData = (sendRequester: HTTPSendRequester, url: string): ApiResponse => {
  const response = sendRequester.sendRequest({ url, method: "GET" }).result()
  if (!ok(response)) {
    throw new Error(`HTTP ${response.statusCode}`)
  }
  return responseSchema.parse(json(response))
}

const onCronTrigger = (runtime: Runtime<Config>): string => {
  const httpClient = new HTTPClient()

  // ConsensusAggregationByFields is a function call, not a type annotation.
  // Field values are bare aggregator references: `median`, not `median()`.
  const aggregation = ConsensusAggregationByFields<ApiResponse>({
    price: median,
    symbol: identical,
  })

  const result = httpClient
    .sendRequest(runtime, fetchData, aggregation)(runtime.config.apiUrl)
    .result()

  runtime.log(`Price: ${result.price}, Symbol: ${result.symbol}`)
  return JSON.stringify(result)
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

### How sendRequest Works

1. The function you pass (`fetchData`) runs on each DON node independently
2. Each node's result is aggregated using the specified consensus method
3. The aggregated result is returned to the caller

### Aggregation Methods

Aggregation is expressed by passing SDK **function references** into `ConsensusAggregationByFields`, or by calling a whole-value aggregator such as `consensusMedianAggregation()`. There are no `{ method: "..." }` object literals in this SDK. See `sdk-reference.md` for the full list.

| Field aggregator | Description | Use Case |
|------------------|-------------|----------|
| `median` | Median of numeric values | Prices, quantities |
| `identical` | All nodes must return the same value | Strings, booleans, addresses |
| `commonPrefix` / `commonSuffix` | Longest shared prefix/suffix of arrays | Append-only lists, log batches |
| `frequencyList` | Each observed value with its count | Categorical data |
| `ignore` | Drop the field from the consensus result | Per-node noise (timings, node ids) |

There is no `mode` aggregator; use `frequencyList` when you need observation counts.

## Per-node Execution with runInNodeMode (TypeScript)

`runInNodeMode` is a method on **`Runtime`**, not on the HTTP client. `httpClient.sendRequest` already wraps it, so reach for `runtime.runInNodeMode` directly only when a node has to do something `sendRequest` cannot express — several requests, or extra computation per node.

The callback receives a `NodeRuntime<Config>` as its first argument. Inside it, HTTP goes through the HTTP client's two-argument overload, `httpClient.sendRequest(nodeRuntime, request).result()`.

**Secrets are not available in node mode.** `NodeRuntime` extends only `BaseRuntime`, so it has no `getSecret`/`getSecrets` — and closing over the outer DON runtime does not work either, because entering node mode arms a `DonModeError` on it. Read secrets in DON mode *before* the call and pass the values in as arguments:

```typescript
import {
  HTTPClient,
  ConsensusAggregationByFields,
  median,
  identical,
  json,
  ok,
  type NodeRuntime,
  type Runtime,
} from "@chainlink/cre-sdk"

// Extra arguments follow the NodeRuntime, and are supplied by the returned function.
const fetchWithAuth = (nodeRuntime: NodeRuntime<Config>, apiKey: string): ApiResponse => {
  const httpClient = new HTTPClient()

  const response = httpClient
    .sendRequest(nodeRuntime, {
      url: nodeRuntime.config.apiUrl,
      method: "GET",
      headers: { Authorization: `Bearer ${apiKey}` },
    })
    .result()

  if (!ok(response)) {
    throw new Error(`HTTP ${response.statusCode}`)
  }
  return responseSchema.parse(json(response))
}

const onCronTrigger = (runtime: Runtime<Config>): string => {
  // DON mode: read the secret here, before entering node mode
  const apiKey = runtime.getSecret({ id: "API_KEY" }).result().value

  const aggregation = ConsensusAggregationByFields<ApiResponse>({
    price: median,
    symbol: identical,
  })

  const result = runtime.runInNodeMode(fetchWithAuth, aggregation)(apiKey).result()

  runtime.log(`Price: ${result.price}`)
  return JSON.stringify(result)
}
```

### Key Difference from sendRequest

- `runInNodeMode` lives on the runtime and takes no `runtime` argument of its own; `sendRequest` lives on the HTTP client and takes `runtime` first
- `runInNodeMode` does not take a URL parameter; the fetch URL is inside the closure
- Secrets must be read in DON mode and passed in as arguments — the node function cannot read them itself
- Each node runs the closure independently; results are aggregated afterward

## GET Request (Go)

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
    creHttp "github.com/smartcontractkit/cre-sdk-go/capabilities/http"
)

type Config struct {
    Schedule string `json:"schedule"`
    ApiUrl   string `json:"apiUrl"`
}

type ApiResponse struct {
    Price  float64 `json:"price"`
    Symbol string  `json:"symbol"`
}

func onCronTrigger(config *Config, runtime cre.Runtime, trigger *cron.Payload) (*ApiResponse, error) {
    httpClient := creHttp.NewHTTPClient()

    fetchFn := func(nodeRuntime cre.NodeRuntime) (*ApiResponse, error) {
        apiKey, err := runtime.GetSecret("API_KEY")
        if err != nil {
            return nil, err
        }

        req, err := http.NewRequest("GET", config.ApiUrl, nil)
        if err != nil {
            return nil, err
        }
        req.Header.Set("Authorization", "Bearer "+apiKey)

        resp, err := nodeRuntime.Fetch(req)
        if err != nil {
            return nil, err
        }
        defer resp.Body.Close()

        body, err := io.ReadAll(resp.Body)
        if err != nil {
            return nil, err
        }

        var result ApiResponse
        if err := json.Unmarshal(body, &result); err != nil {
            return nil, err
        }

        return &result, nil
    }

    aggregation := creHttp.AggregationConfig{
        Fields: map[string]creHttp.FieldAggregation{
            "price":  {Method: "median"},
            "symbol": {Method: "identical"},
        },
    }

    result, err := httpClient.RunInNodeMode(runtime, fetchFn, aggregation).Await()
    if err != nil {
        return nil, fmt.Errorf("HTTP request failed: %w", err)
    }

    return result, nil
}

func InitWorkflow(config *Config) []cre.HandlerDefinition {
    return []cre.HandlerDefinition{
        cre.Handler(cron.Trigger(cron.Config{Schedule: config.Schedule}), onCronTrigger),
    }
}
```

## POST Request (TypeScript)

On the standard HTTP client, `body` is a protobuf `bytes` field, so it must be **base64-encoded** — you cannot assign a raw JSON string to it. (`bodyString` exists only on the *Confidential* HTTP client's request type; it is not a field here.)

```typescript
const postData = (sendRequester: HTTPSendRequester): ApiResponse => {
  const payload = JSON.stringify({ query: "ETH/USD" })

  const response = sendRequester
    .sendRequest({
      url: "https://api.example.com/submit",
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: bytesToBase64(new TextEncoder().encode(payload)), // base64, not the raw string
    })
    .result()

  if (!ok(response)) {
    throw new Error(`HTTP ${response.statusCode}`)
  }
  return responseSchema.parse(json(response))
}

const result = httpClient
  .sendRequest(runtime, postData, aggregation)()
  .result()
```

## Cache Settings for Non-Idempotent Requests

By default, identical HTTP requests within a short window may be cached. Caching is configured **on the request object** via `cacheSettings` — it is not a fourth argument to `sendRequest` or `runInNodeMode`, and there is no `{ cache: false }` option. For non-idempotent requests (POST, PUT, DELETE), disable the store:

```typescript
sendRequester.sendRequest({
  url: "https://api.example.com/submit",
  method: "POST",
  body: bytesToBase64(new TextEncoder().encode(payload)),
  cacheSettings: { store: false },
})
```

`cacheSettings` also accepts `maxAge` (a `Duration`) to bound how long a stored response stays usable.

## Webhooks And Alert Delivery

For production alerts, prefer posting to a user-owned relay service instead of calling Slack, Discord, or another webhook directly from each DON node. The relay should deduplicate alerts by a stable key, enforce rate limits, and hold the real webhook URL outside workflow config.

Use direct webhooks only for simulation, prototypes, or controlled tests, and keep the webhook URL in secrets rather than config or README examples.

Recommended alert flow:

1. Workflow evaluates the condition using scaled values.
2. Workflow sends a signed or authenticated alert payload to a relay endpoint.
3. Relay deduplicates by fields such as `workflowId`, `condition`, `roundId`, and `bucketTimestamp`.
4. Relay posts to Slack or another destination once.
5. Relay returns a small status object for consensus aggregation.

## Submitting Reports via HTTP

Instead of writing reports onchain, you can submit them to an external HTTP endpoint:

```typescript
const signedReport = runtime.report(encoded)

const submitReport = (): { status: string } => {
  const response = fetch("https://api.example.com/report", {
    method: "POST",
    headers: { "Content-Type": "application/octet-stream" },
    body: signedReport,
  })
  return { status: response.ok ? "success" : "failed" }
}

const result = runtime
  .runInNodeMode(
    submitReport,
    ConsensusAggregationByFields<{ status: string }>({ status: identical }),
  )()
  .result()
```

## Confidential HTTP Client

The Confidential HTTP client provides privacy-preserving HTTP requests via enclave execution. Secrets are injected into the request inside the enclave using template syntax, never exposed to DON nodes.

This is not the same feature as Confidential Workflows, which runs an entire handler inside an enclave — see `confidential-workflows.md`. Use Confidential HTTP when only one request's credentials and payload need protecting while the decision logic stays on the DON. The two do not compose: `ConfidentialHTTPClient` has no `TeeRuntime` overload, and Go's `confidentialhttp.Client.SendRequest` only accepts `cre.Runtime`, so neither can be called from a TEE handler. Inside a TEE handler, use the standard `HTTPClient` with the `TeeRuntime` (Go: `http.Client.SendRequestInTee`).

### Key Differences from Standard HTTP

| Aspect | Standard HTTP | Confidential HTTP |
|--------|--------------|-------------------|
| Class | `HTTPClient` | `ConfidentialHTTPClient` |
| Secrets | `runtime.getSecret({ id }).result().value` | `{{.secretName}}` template in headers/body |
| Secret storage | secrets.yaml + env vars | Vault DON (`vaultDonSecrets`) |
| Execution | DON/Node mode | Enclave execution |
| Response | Plain | Optional encryption via `encryptOutput` |

### How It Works

1. Declare secrets in `vaultDonSecrets` with the secret `key` and the `owner` address
2. Save the sensitive data (API keys, tokens) to the Vault DON using `cre secrets create`
3. Reference secrets in request headers or body using `{{.SECRET_NAME}}` template syntax
4. The enclave resolves templates, executes the request, and returns the result to the DON for consensus

### TypeScript: Minimal Example

```typescript
import {
  ConfidentialHTTPClient,
  ConfidentialHTTPSendRequester,
  CronCapability,
  handler,
  Runner,
  type Runtime,
  type CronPayload,
  ConsensusAggregationByFields,
  identical,
} from "@chainlink/cre-sdk"

type Config = {
  schedule: string
}

const onTrigger = (runtime: Runtime<Config>, _payload: CronPayload): string => {
  const confClient = new ConfidentialHTTPClient()

  const result = confClient.sendRequest(
    runtime,
    (req: ConfidentialHTTPSendRequester) => {
      const resp = req.sendRequest({
        request: {
          url: 'https://api.anthropic.com/v1/messages',
          method: 'POST',
          bodyString: JSON.stringify({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 300,
            messages: [{ role: 'user', content: 'Is this vault safe?' }],
          }),
          multiHeaders: {
            'Content-Type': { values: ['application/json'] },
            'x-api-key': { values: ['{{.ANTHROPIC_API_KEY}}'] },
            'anthropic-version': { values: ['2023-06-01'] },
          },
        },
        vaultDonSecrets: [
          { key: 'ANTHROPIC_API_KEY', owner: '0xYourOwnerAddress' },
        ],
        encryptOutput: false,
      }).result()

      const body = JSON.parse(new TextDecoder().decode(resp.body))
      return { answer: String(body.content?.[0]?.text ?? '') }
    },
    ConsensusAggregationByFields<{ answer: string }>({ answer: identical }),
  ).result()

  runtime.log(`AI says: ${result.answer}`)
  return JSON.stringify(result)
}

const initWorkflow = (config: Config) => {
  const cron = new CronCapability()
  return [handler(cron.trigger({ schedule: config.schedule }), onTrigger)]
}

export async function main() {
  const runner = await Runner.newRunner<Config>()
  await runner.run(initWorkflow)
}
```

### Request Format

The `sendRequest` callback receives a `ConfidentialHTTPSendRequester` and must call `req.sendRequest()` with:

| Field | Type | Description |
|-------|------|-------------|
| `request.url` | `string` | Target URL |
| `request.method` | `string` | HTTP method (`GET`, `POST`, etc.) |
| `request.bodyString` | `string` | Request body as a string |
| `request.multiHeaders` | `Record<string, { values: string[] }>` | Headers with multi-value support |
| `vaultDonSecrets` | `Array<{ key: string, owner: string }>` | Secrets to resolve from Vault DON |
| `encryptOutput` | `boolean` | Whether to encrypt the response |

### Secret Template Syntax

Use `{{.SECRET_NAME}}` anywhere in headers or body to inject a Vault DON secret:

```typescript
multiHeaders: {
  'Authorization': { values: ['Bearer {{.MY_API_TOKEN}}'] },
},
vaultDonSecrets: [
  { key: 'MY_API_TOKEN', owner: '0xYourOwnerAddress' },
],
```

The `key` must match the secret name stored in the Vault DON. The `owner` is the address that created the secret.

### Secrets Setup for Confidential HTTP

1. Define secrets in `secrets.yaml` as usual
2. Upload to Vault DON: `cre secrets create <workflow-dir> --target <target>`
3. In the workflow code, reference via `{{.SECRET_NAME}}` in the request (not `runtime.getSecret()`)
4. Declare each secret in `vaultDonSecrets` so the enclave knows which secrets to fetch

## Official Documentation

- HTTP GET (TypeScript): `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-ts.md`
- HTTP GET (Go): `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-go.md`
- HTTP POST (TypeScript): `https://docs.chain.link/cre/guides/workflow/using-http-client/post-request-ts.md`
- Confidential HTTP: `https://docs.chain.link/cre/capabilities/confidential-http-ts.md`
