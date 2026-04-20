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
  HTTPClientCapability,
  CronCapability,
  handler,
  Runner,
  type Runtime,
  ConsensusAggregationByFields,
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

const fetchData = (url: string): ApiResponse => {
  const response = fetch(url)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  const data = response.json()
  return responseSchema.parse(data)
}

const onCronTrigger = (runtime: Runtime<Config>): string => {
  const httpClient = new HTTPClientCapability()

  const aggregation: ConsensusAggregationByFields<ApiResponse> = {
    method: "byFields",
    fields: {
      price: { method: "median" },
      symbol: { method: "identical" },
    },
  }

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

| Method | Description | Use Case |
|--------|-------------|----------|
| `median` | Median of numeric values | Prices, quantities |
| `identical` | All nodes must return the same value | Strings, booleans, addresses |
| `mode` | Most common value | Categorical data |

## GET Request with runInNodeMode (TypeScript)

```typescript
const onCronTrigger = (runtime: Runtime<Config>): string => {
  const httpClient = new HTTPClientCapability()

  const aggregation: ConsensusAggregationByFields<ApiResponse> = {
    method: "byFields",
    fields: {
      price: { method: "median" },
      symbol: { method: "identical" },
    },
  }

  const fetchWithAuth = (): ApiResponse => {
    const apiKey = runtime.getSecret("API_KEY")
    const response = fetch(runtime.config.apiUrl, {
      headers: { Authorization: `Bearer ${apiKey}` },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return responseSchema.parse(response.json())
  }

  const result = httpClient
    .runInNodeMode(runtime, fetchWithAuth, aggregation)()
    .result()

  runtime.log(`Price: ${result.price}`)
  return JSON.stringify(result)
}
```

### Key Difference from sendRequest

- `runInNodeMode` does not take a URL parameter; the fetch URL is inside the closure
- The closure has access to `runtime.getSecret()` for API keys
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

```typescript
const postData = (): ApiResponse => {
  const response = fetch("https://api.example.com/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: "ETH/USD" }),
  })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  return responseSchema.parse(response.json())
}

const result = httpClient
  .runInNodeMode(runtime, postData, aggregation)()
  .result()
```

## Cache Settings for Non-Idempotent Requests

By default, identical HTTP requests within a short window may be cached. For non-idempotent requests (POST, PUT, DELETE), disable caching:

```typescript
const result = httpClient
  .runInNodeMode(runtime, postData, aggregation, { cache: false })()
  .result()
```

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

const result = httpClient
  .runInNodeMode(runtime, submitReport, {
    method: "byFields",
    fields: { status: { method: "identical" } },
  })()
  .result()
```

## Confidential HTTP Client

The Confidential HTTP client provides privacy-preserving HTTP requests via enclave execution. Secrets are injected into the request inside the enclave using template syntax, never exposed to DON nodes.

### Key Differences from Standard HTTP

| Aspect | Standard HTTP | Confidential HTTP |
|--------|--------------|-------------------|
| Class | `HTTPClientCapability` | `ConfidentialHTTPClient` |
| Secrets | `runtime.getSecret()` | `{{.secretName}}` template in headers/body |
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

- HTTP GET (TypeScript): `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-ts`
- HTTP GET (Go): `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-go`
- HTTP POST (TypeScript): `https://docs.chain.link/cre/guides/workflow/using-http-client/post-request-ts`
- Confidential HTTP: `https://docs.chain.link/cre/guides/workflow/using-http-client/confidential-http-ts`
