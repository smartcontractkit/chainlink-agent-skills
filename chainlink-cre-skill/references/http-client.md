# HTTP Client

Use for outbound HTTP, node mode, report submission over HTTP, or Confidential HTTP. HTTP *triggers* are in [triggers.md](triggers.md); whole-handler TEE execution is in [confidential-workflows.md](confidential-workflows.md).

## Choose a pattern

| Pattern | Use | Execution |
|---|---|---|
| `HTTPClient.sendRequest` | one straightforward request | per-node request plus consensus aggregation |
| `runtime.runInNodeMode` | several requests or extra per-node work | callback per node, then aggregation |
| `ConfidentialHTTPClient` | protect one request's credentials/payload | enclave request with Vault DON templates |

Use the high-level `sendRequest` unless it cannot express the node work.

## Canonical TypeScript GET

```typescript
import {
  CronCapability, HTTPClient, Runner, consensusMedianAggregation, handler, json, ok,
  type HTTPSendRequester, type Runtime,
} from '@chainlink/cre-sdk'
import { z } from 'zod'

type Config = { schedule: string; apiUrl: string }
const schema = z.object({ price: z.number() })

const fetchPrice = (sender: HTTPSendRequester, url: string): number => {
  const response = sender.sendRequest({ url, method: 'GET' }).result()
  if (!ok(response)) throw new Error(`HTTP ${response.statusCode}`)
  return schema.parse(json(response)).price
}

const onCron = (runtime: Runtime<Config>): string => {
  const price = new HTTPClient()
    .sendRequest(runtime, fetchPrice, consensusMedianAggregation<number>())(
      runtime.config.apiUrl,
    ).result()
  return JSON.stringify({ price })
}

const initWorkflow = (config: Config) => [
  handler(new CronCapability().trigger({ schedule: config.schedule }), onCron),
]
export async function main() {
  const runner = await Runner.newRunner<Config>()
  await runner.run(initWorkflow)
}
main()
```

The callback's first argument is the SDK-supplied `HTTPSendRequester`; every remaining callback parameter must match the arguments passed to the function returned by `sendRequest`, one-for-one and in the same order. There is no workflow-global fetch. `.result()` returns a `Response`: `statusCode` is numeric, `body` is bytes; use `ok`, `json` (returns `unknown`), `text`, and `getHeader`.

Every handler callback declares and returns `string` — serialize a numeric or structured result with `JSON.stringify` as above rather than returning the raw aggregated value; a bare `number`/object return does not satisfy the trigger workflow's output contract.

## Aggregation and node mode

Whole-value aggregators are called: `consensusMedianAggregation<T>()`, `consensusIdenticalAggregation<T>()`, `consensusCommonPrefixAggregation<T>()`, `consensusCommonSuffixAggregation<T>()`, `consensusFrequencyListAggregation<T>()`. Median aggregation is only for numeric `number` or `bigint` observations; strings, booleans, addresses, and hashes use identical aggregation. Field maps call `ConsensusAggregationByFields<T>({ price: median, symbol: identical })`; values are bare function references, not calls or `{method: ...}` objects. Other fields: `commonPrefix`, `commonSuffix`, `frequencyList`, `ignore`. There is no `mode`.

Every node-mode or secret-backed HTTP call — including a quick "how do I use an API key" example — passes a consensus aggregator; there is no unaggregated shortcut, because each DON node runs the callback independently and the results must reach BFT agreement. `runInNodeMode` belongs to `Runtime`, not `HTTPClient`:

```typescript
const fetchWithAuth = (node: NodeRuntime<Config>, token: string): number => {
  const response = new HTTPClient().sendRequest(node, {
    url: node.config.apiUrl,
    method: 'GET',
    headers: { Authorization: `Bearer ${token}` },
  }).result()
  if (!ok(response)) throw new Error(`HTTP ${response.statusCode}`)
  return schema.parse(json(response)).price
}

const token = runtime.getSecret({ id: 'API_KEY' }).result().value
const price = runtime
  .runInNodeMode(fetchWithAuth, consensusMedianAggregation<number>())(token)
  .result()
```

`NodeRuntime` has no secrets API, and closing over DON runtime raises `DonModeError`; read secrets before entering node mode and pass them as arguments. The SDK supplies `node` to `fetchWithAuth`, while the invocation's `(token)` argument supplies its matching `token` parameter; the request URL remains `node.config.apiUrl`. The node-mode HTTP overload is `httpClient.sendRequest(nodeRuntime, request).result()`.

Every `getSecret`/`GetSecret` call must be paired with the matching root `secrets.yaml` mapping, or the referenced ID cannot resolve at simulation or deploy time — retrieval code without it is incomplete:

```yaml
secretsNames:
  API_KEY: API_KEY_VAR
```

Go's high-level client is `creHttp.NewHTTPClient()` and resolves `RunInNodeMode(runtime, fetchFn, aggregation).Await()`. Node callbacks receive `cre.NodeRuntime`, whose `Fetch(*http.Request)` performs the request; use Go consensus/field aggregation types from the installed SDK. Capability completion is always `.Await()`.

## POST, bytes, and caching

Standard TypeScript `Request.body` is protobuf bytes encoded as base64, not a raw JSON string. `bodyString` exists only on Confidential HTTP requests.

```typescript
sender.sendRequest({
  url,
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: bytesToBase64(new TextEncoder().encode(JSON.stringify(payload))),
  cacheSettings: { store: false },
}).result()
```

`cacheSettings` belongs on the request, not as a fourth client argument; there is no `{cache:false}`. Disable storage for non-idempotent POST/PUT/DELETE. `cacheSettings.maxAge` accepts a `Duration`.

For alerts, prefer a user-owned relay that holds the real webhook URL, authenticates, rate-limits, and deduplicates by stable fields such as workflow ID, condition, round ID, and bucket timestamp. Direct Slack/Discord webhooks are for simulation/prototypes only and remain secret references.

For node-mode side effects, aggregate a stable semantic acknowledgement, never raw HTTP status codes. The relay must return the same acknowledgement for the first accepted submission and a deduplicated replay, or the callback must normalize every accepted response to the same small value before identical consensus.

## Reports over HTTP

The flow is ABI encode → `runtime.report(...).result()` (Go `GenerateReport(...).Await()`) → node-mode HTTP submission → consensus on a small response. The destination must deduplicate because node signatures/request attempts may differ. Do not pass a lazy report handle as raw request bytes; transform the resolved report into the endpoint's documented format. Official request/report sender signatures are version-sensitive—use [sdk-reference.md](sdk-reference.md) and the focused source page.

## Confidential HTTP

Confidential HTTP protects one request while decision logic stays visible on the DON. It is not a Confidential Workflow and cannot be called from a `TeeRuntime` handler. Secrets use Vault DON `{{.SECRET_NAME}}` placeholders and must be declared in `vaultDonSecrets`; regular runtime secrets use `runtime.getSecret` instead.

```typescript
import {
  ConfidentialHTTPClient, ConsensusAggregationByFields, identical,
  type ConfidentialHTTPSendRequester, type Runtime,
} from '@chainlink/cre-sdk'

type Answer = { answer: string }

const result = new ConfidentialHTTPClient().sendRequest(
  runtime,
  (sender: ConfidentialHTTPSendRequester): Answer => {
    const response = sender.sendRequest({
      request: {
        url: runtime.config.url,
        method: 'POST',
        bodyString: JSON.stringify({ question: runtime.config.question }),
        multiHeaders: {
          'Content-Type': { values: ['application/json'] },
          Authorization: { values: ['Bearer {{.API_TOKEN}}'] },
        },
      },
      vaultDonSecrets: [{ key: 'API_TOKEN', owner: runtime.config.secretOwner }],
      encryptOutput: false,
    }).result()
    return { answer: String(JSON.parse(new TextDecoder().decode(response.body)).answer) }
  },
  ConsensusAggregationByFields<Answer>({ answer: identical }),
).result()
```

Request fields:

| Field | Type/meaning |
|---|---|
| `request.url`, `request.method` | strings |
| `request.bodyString` | string body |
| `request.multiHeaders` | `Record<string,{values:string[]}>` |
| `vaultDonSecrets` | `{key, owner}[]`; owner is the secret creator address |
| `encryptOutput` | encrypt returned response |

The `key` must match the Vault DON secret; placeholders may appear in headers/body. Setup: map IDs in `secrets.yaml`, upload opaquely with `cre secrets create <dir> --target <target>` under operations approvals, declare each key/owner, then reference `{{.KEY}}`. Go uses the confidential HTTP client/signatures in the SDK reference; it accepts `cre.Runtime`, not `cre.TeeRuntime`.

## Sources

- https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-ts.md
- https://docs.chain.link/cre/guides/workflow/using-http-client/post-request-ts.md
- https://docs.chain.link/cre/guides/workflow/using-http-client/submitting-reports-http-ts.md
- https://docs.chain.link/cre/capabilities/confidential-http-ts.md
