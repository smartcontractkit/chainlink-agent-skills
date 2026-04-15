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

## Confidential HTTP Client (Experimental)

The Confidential HTTP client provides privacy-preserving HTTP requests via enclave execution. Currently available in simulation only.

### Features

- Secret injection into request headers/body without exposing to the DON
- Optional response encryption
- Enclave-based execution for privacy

### TypeScript

```typescript
import { ConfidentialHTTPClientCapability } from "@chainlink/cre-sdk"

const confidentialClient = new ConfidentialHTTPClientCapability()

const result = confidentialClient
  .sendRequest(runtime, {
    url: "https://api.example.com/sensitive",
    method: "GET",
    headers: {
      Authorization: `Bearer ${runtime.getSecret("API_KEY")}`,
    },
  })
  .result()
```

### Limitations

- Simulation only (not yet supported in deployed workflows)
- Limited consensus options
- Experimental API subject to change

## Official Documentation

- HTTP GET (TypeScript): `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-ts`
- HTTP GET (Go): `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-go`
- HTTP POST (TypeScript): `https://docs.chain.link/cre/guides/workflow/using-http-client/post-request-ts`
- Confidential HTTP: `https://docs.chain.link/cre/guides/workflow/using-http-client/confidential-http-ts`
