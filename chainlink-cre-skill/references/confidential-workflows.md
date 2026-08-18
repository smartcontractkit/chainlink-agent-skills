# Confidential Workflows

Use for whole-handler execution inside a TEE/enclave (`handlerInTee`/`cre.HandlerInTee`, `TeeRuntime`). This is not Confidential HTTP; their APIs do not mix.

## Choose the boundary

| | Confidential HTTP | Confidential Workflow |
|---|---|---|
| Protects | One request's credentials/payload | Handler secrets, requests, and intermediate values |
| Registration/runtime | normal `handler`, `Runtime` | `handlerInTee`, `TeeRuntime` |
| Secrets | `{{.SECRET_NAME}}` plus `vaultDonSecrets` | `runtime.getSecret()`/`GetSecret()` at use time |
| Decision logic | DON-visible | enclave |
| Availability | capability-specific | private-beta deployment |

`ConfidentialHTTPClient` has no TypeScript `TeeRuntime` overload; Go `confidentialhttp.Client.SendRequest` accepts only `cre.Runtime`. Inside a TEE use the regular `HTTPClient` with `TeeRuntime`, or Go `http.Client.SendRequestInTee`.

## Availability and boundary

Deployment requires separate private-beta enrollment through `https://docs.chain.link/cre/account/confidential-workflows-access`; local development and simulation do not. Only AWS Nitro in `us-west-2` is registered—do not invent TEE names/regions.

Confidential: Vault DON secrets released into the attested enclave, capability request/response payloads issued inside it, and intermediate enclave memory. Not confidential: the workflow binary/logic (revealed to the DON), triggers, chain reads/writes, logs, or anything passed through `usingTheDons()`/`UsingTheDons()`. DON consensus verifies enclave attestations; it does not make exported data private. Multiple confidential workflows may currently share an enclave; dedicated per-workflow isolation is planned, not available.

Keep TEE logging for simulation only and remove it before production. Every shown TEE handler crosses back with `usingTheDons()`/`UsingTheDons()` and carries only derived non-sensitive conclusions—never secrets or raw confidential payloads; show both TypeScript and Go equivalents when explaining this boundary. Preserve per-item or per-position threshold cardinality inside the enclave and fail closed if any required threshold is missing. Chain writes happen after crossing back.

## Canonical TypeScript workflow

```typescript
import {
  CronCapability, HTTPClient, Runner, handlerInTee, hexToBase64, ok, text,
  type TeeRuntime,
} from '@chainlink/cre-sdk'
import { encodeAbiParameters, parseAbiParameters } from 'viem'
import { z } from 'zod'

export const configSchema = z.object({
  schedule: z.string(), url: z.string(), secretId: z.string(), threshold: z.number(),
})
type Config = z.infer<typeof configSchema>

const score = (s: string) => [...s].reduce((n, c) => (n + c.charCodeAt(0)) % 1000, 0)

const onCron = (runtime: TeeRuntime<Config>): string => {
  const token = runtime.getSecret({ id: runtime.config.secretId }).result().value
  const response = new HTTPClient().sendRequest(runtime, {
    url: runtime.config.url,
    method: 'GET',
    multiHeaders: { Authorization: { values: [`Bearer ${token}`] } },
  }).result()
  if (!ok(response)) throw new Error(`HTTP ${response.statusCode}`)

  const value = score(text(response))
  const verdict = value >= runtime.config.threshold ? 'APPROVE' : 'REJECT'
  const don = runtime.usingTheDons() // only derived values cross
  const encodedPayload = encodeAbiParameters(
    parseAbiParameters('string verdict, uint256 score'), [verdict, BigInt(value)],
  )
  don.report({
    encodedPayload: hexToBase64(encodedPayload), encoderName: 'evm',
    signingAlgo: 'ecdsa', hashingAlgo: 'keccak256',
  }).result()
  return verdict
}

export const initWorkflow = (config: Config) => [
  handlerInTee(new CronCapability().trigger({ schedule: config.schedule }), onCron, [
    { tee: 'nitro', regions: ['us-west-2'] },
  ]),
]

export async function main() {
  const runner = await Runner.newRunner({ configSchema })
  await runner.run(initWorkflow)
}
main()
```

The SDK also exports equivalent `cre.handlerInTee` and `cre.capabilities.*` names; match the repository style.

## Canonical Go workflow

```go
//go:build wasip1

package main

import (
    "fmt"
    "log/slog"
    "math/big"

    "github.com/ethereum/go-ethereum/accounts/abi"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/networking/http"
    "github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
    "github.com/smartcontractkit/cre-sdk-go/cre"
    "github.com/smartcontractkit/cre-sdk-go/cre/wasm"
)

type Config struct {
    Schedule string `json:"schedule"`
    URL string `json:"url"`
    SecretID string `json:"secretId"`
    Threshold uint64 `json:"threshold"`
}

func score(body []byte) uint64 {
    var result uint64
    for _, b := range body { result = (result + uint64(b)) % 1000 }
    return result
}

func encodeVerdict(verdict string, value uint64) ([]byte, error) {
    stringType, err := abi.NewType("string", "", nil)
    if err != nil { return nil, err }
    uintType, err := abi.NewType("uint256", "", nil)
    if err != nil { return nil, err }
    return (abi.Arguments{{Type: stringType}, {Type: uintType}}).
        Pack(verdict, new(big.Int).SetUint64(value))
}

func onCron(config *Config, runtime cre.TeeRuntime, _ *cron.Payload) (string, error) {
    secret, err := runtime.GetSecret(&cre.SecretRequest{Id: config.SecretID}).Await()
    if err != nil { return "", err }
    response, err := (&http.Client{}).SendRequestInTee(runtime, &http.Request{
        Url: config.URL, Method: "GET",
        MultiHeaders: map[string]*http.HeaderValues{
            "Authorization": {Values: []string{"Bearer " + secret.Value}},
        },
    }).Await()
    if err != nil { return "", err }
    if response.StatusCode < 200 || response.StatusCode > 299 {
        return "", fmt.Errorf("HTTP %d", response.StatusCode)
    }

    value := score(response.Body)
    verdict := "REJECT"
    if value >= config.Threshold { verdict = "APPROVE" }
    encoded, err := encodeVerdict(verdict, value)
    if err != nil { return "", err }
    _, err = runtime.UsingTheDons().GenerateReport(&cre.ReportRequest{
        EncodedPayload: encoded, EncoderName: "evm",
        SigningAlgo: "ecdsa", HashingAlgo: "keccak256",
    }).Await()
    return verdict, err
}

func InitWorkflow(config *Config, _ *slog.Logger, _ cre.SecretsProvider) (cre.Workflow[*Config], error) {
    return cre.Workflow[*Config]{cre.HandlerInTee(
        cron.Trigger(&cron.Config{Schedule: config.Schedule}), onCron,
        cre.OneOfTees{cre.Nitro{Regions: []cre.NitroRegion{cre.NitroUsWest2}}},
    )}, nil
}

func main() {
    wasm.NewRunner(cre.ParseJSON[Config]).Run(InitWorkflow)
}
```

## TEE API

| Purpose | TypeScript | Go |
|---|---|---|
| Register | `handlerInTee(trigger, fn, tees, hooks?)` | `cre.HandlerInTee(trigger, callback, tees)` |
| One secret | `getSecret({ id }).result().value` | `GetSecret(&cre.SecretRequest{Id: id}).Await()` |
| Several | one call each / `getSecrets` | `GetSecrets([]*cre.SecretRequest{...}).Await()` |
| In-enclave HTTP | `new HTTPClient().sendRequest(runtime, req).result()` | `(&http.Client{}).SendRequestInTee(runtime, req).Await()` |
| Cross back | `usingTheDons(): Runtime<C>` | `UsingTheDons(): cre.Runtime` |
| Report shortcut | `reportFromDon(req).result()` | `ReportFromDon(req).Await()` |
| Config/time/log | `config`, `now()`, `log()` | config parameter, `Now()`, `Logger()` |

TEE constraints:

| Intent | TypeScript | Go |
|---|---|---|
| Any TEE/region | `{}` | `cre.AnyTee{}` |
| Any TEE, regions | `{ regions: ['us-west-2'] }` | `cre.AnyTeeInRegions{Regions: []cre.Region{cre.AwsUsWest2}}` |
| Nitro/regions | `[{ tee: 'nitro', regions: ['us-west-2'] }]` | `cre.OneOfTees{cre.Nitro{Regions: []cre.NitroRegion{cre.NitroUsWest2}}}` |

Go TEE bindings own their region enum; mismatched enums fail compilation.

## Secrets and simulation

`secrets.yaml` maps workflow IDs to environment variables; it never contains values:

```yaml
secretsNames:
  API_TOKEN:
    - SECRET_API_TOKEN
```

The workflow requests `API_TOKEN`. Deployment uses `cre secrets create` under [operations.md](operations.md). For simulation, set the referenced environment through a user-controlled mechanism, then use the canonical command in [simulation.md](simulation.md). Simulation is the only appropriate place for enclave logs.

A runnable scaffold uses a real cron expression (not a placeholder), a `workflow.yaml` target whose `config-path` points to the shown `config.staging.json`, and a root `secrets.yaml` containing identifiers/environment references only. The user supplies the referenced environment through a user-controlled mechanism; deployed upload is the concrete `cre secrets create <workflow-dir> --target <target>` operation with [operations.md](operations.md)'s approvals. Do not invent secret error classes, expiry rules, or testnet-only limitations.

## Starter templates

Verify registered templates with `cre templates list --json`.

| Template | Obtain | Purpose | Confidential inputs/config |
|---|---|---|---|
| `hello-confidential-workflows` (TS, Go) | `cre init -t hello-confidential-workflows-ts` or `-go` | Four-step TEE handler: secret, in-enclave HTTP, report crossover; defaults to an echo endpoint, so no real key is needed | one API token |
| `ai-audit-firewall` (TS, Go) | clone only | Fetches contract source/ABI, classifies risk, then allows, blocks, or escalates; ships Solidity consumers | scanner and LLM credentials |
| `automated-liquidation-protection` (TS, Go) | clone only | Monitors lending health and adds collateral or repays debt under policy | exchange/LLM credentials, health-factor/reserve thresholds, execution preferences |
| `automated-portfolio-rebalancing` (TS, Go) | clone only | Tracks allocation drift and rebalances toward targets | exchange/LLM credentials, target weights, drift/slippage limits, venue preferences |

Clone-only examples live under `https://github.com/smartcontractkit/cre-templates/tree/main/starter-templates/confidential-workflows`; each includes project/config/secrets examples, TS and Go workflows, deterministic `mock-server.js`, and tests. Their model stages may be replaced with deterministic rules. The exact hello source path is `/starter-templates/hello-confidential-workflows`; initialize its registered variants with `cre init -t hello-confidential-workflows-ts` or `cre init -t hello-confidential-workflows-go`.

## Sources

- https://docs.chain.link/cre/concepts/confidential-workflows
- https://docs.chain.link/cre/reference/sdk/confidential-workflows-client-ts
- https://docs.chain.link/cre/reference/sdk/confidential-workflows-client-go
