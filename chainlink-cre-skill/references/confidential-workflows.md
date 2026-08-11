# Confidential Workflows

Use this file when the user wants a workflow handler to execute inside a Trusted Execution Environment (TEE / enclave) so that node operators cannot see the data it computes over.

## Trigger Conditions

- "Make my CRE workflow confidential"
- "Run this handler inside an enclave / TEE"
- "How do I use `handlerInTee` / `cre.HandlerInTee`?"
- "Keep my API keys and risk thresholds hidden from node operators"
- "How do I get access to Confidential Workflows?"

Do not use for the Confidential HTTP client (see `http-client.md`) — that is a different capability. The table below decides between them.

## Confidential HTTP vs Confidential Workflows

Both hide data from node operators, but they protect different scopes, and their APIs do not mix. Choosing wrong produces code that does not compile.

| | Confidential HTTP | Confidential Workflows |
|---|---|---|
| Protects | The credentials and payload of one HTTP request | The whole handler: secrets, HTTP payloads, and the decision logic's intermediate values |
| Handler registration | Normal `handler` / `cre.Handler` | `handlerInTee` / `cre.HandlerInTee` |
| Runtime type | `Runtime` | `TeeRuntime` |
| Secrets | `{{.SECRET_NAME}}` template placeholders, declared upfront via `vaultDonSecrets` | `runtime.getSecret()` / `runtime.GetSecret()` at the point of use, nothing declared upfront |
| Where decision logic runs | On Workflow DON nodes (visible to operators) | Inside the enclave |
| Availability | Generally available | Private beta (see below) |

The two clients are not interchangeable inside a TEE handler:

- TypeScript: `ConfidentialHTTPClient` has no `TeeRuntime` overload. Use the regular `HTTPClient`, passing the `TeeRuntime`.
- Go: `confidentialhttp.Client.SendRequest` only accepts `cre.Runtime`. Use `http.Client.SendRequestInTee(runtime, req)`.

## Access and Availability

Confidential Workflows is in **private beta**. Deployment requires enrollment through the Chainlink account team via the [access request form](https://docs.chain.link/cre/account/confidential-workflows-access); enrollment is separate from standard CRE deploy access.

Enrollment gates *deployment only*. Local development and `cre workflow simulate` work today without approval, so the right advice to a user who is not yet enrolled is: build and simulate now, request access in parallel.

AWS Nitro in `us-west-2` is currently the only registered TEE type and region. Do not invent other TEE names or regions.

## What Is and Is Not Confidential

Understanding this boundary is the whole job — most mistakes are leaks, not compile errors.

Confidential:

- Secrets the Vault DON releases into the enclave, decrypted only at the moment the code requests them
- Request and response payloads of capability calls made from inside the enclave
- Intermediate values and enclave memory, for as long as the computation runs inside it

Not confidential:

- **The workflow logic itself.** The handler is part of the binary the Workflow DON hands to the enclave, so the code is revealed. What the enclave protects is the *data* that code computes over. Tell users this plainly — it is the most common misconception.
- **Triggers, chain reads, and chain writes.** These always execute on Workflow DON nodes, never inside the enclave.
- Anything crossed back out through `usingTheDons()` / `UsingTheDons()`.
- Anything logged.

Execution completes only after DON consensus verifies the enclave's attestations, which is what proves the executed logic's integrity. Trust for the in-enclave leg comes from attestation rather than DON consensus over the data.

Multiple confidential workflows may currently execute within the same enclave; dedicated per-workflow enclave isolation is planned but not available. If a user asks about tenant isolation, say so rather than implying stronger guarantees.

## TypeScript Pattern

```typescript
import {
  CronCapability,
  handlerInTee,
  HTTPClient,
  hexToBase64,
  ok,
  Runner,
  text,
  type TeeRuntime,
} from '@chainlink/cre-sdk'
import { encodeAbiParameters, parseAbiParameters } from 'viem'
import { z } from 'zod'

export const configSchema = z.object({
  schedule: z.string(),
  url: z.string(),
  secretId: z.string(),
  scoreThreshold: z.number(),
})
type Config = z.infer<typeof configSchema>

// Deterministic logic over confidential data. The enclave result is attested and
// verified by DON consensus, so the same input must always produce the same output.
const scoreResponse = (body: string): number => {
  let score = 0
  for (let i = 0; i < body.length; i++) {
    score = (score + body.charCodeAt(i)) % 1000
  }
  return score
}

// Receives a TeeRuntime, not a Runtime. Everything here runs inside the enclave
// until we explicitly cross back.
export const onCronTrigger = (runtime: TeeRuntime<Config>): string => {
  const config = runtime.config

  // Released by the Vault DON into the attested enclave, decrypted here.
  const apiToken = runtime.getSecret({ id: config.secretId }).result().value

  // Passing the TeeRuntime to the regular HTTPClient executes the request from
  // inside the enclave, so request and response payloads stay confidential.
  const response = new HTTPClient()
    .sendRequest(runtime, {
      url: config.url,
      method: 'GET',
      multiHeaders: {
        Authorization: { values: [`Bearer ${apiToken}`] },
      },
    })
    .result()

  if (!ok(response)) {
    throw new Error(`Confidential request failed with status: ${response.statusCode}`)
  }

  const score = scoreResponse(text(response))
  const verdict = score >= config.scoreThreshold ? 'APPROVE' : 'REJECT'

  // Cross back for anything needing consensus. Only the verdict and score cross
  // out — never the secret or the raw response body.
  const donRuntime = runtime.usingTheDons()

  const encodedPayload = encodeAbiParameters(
    parseAbiParameters('string verdict, uint256 score'),
    [verdict, BigInt(score)],
  )

  donRuntime
    .report({
      encodedPayload: hexToBase64(encodedPayload),
      encoderName: 'evm',
      signingAlgo: 'ecdsa',
      hashingAlgo: 'keccak256',
    })
    .result()

  return `${verdict} (score: ${score})`
}

export function initWorkflow(config: Config) {
  const cron = new CronCapability()

  return [
    handlerInTee(cron.trigger({ schedule: config.schedule }), onCronTrigger, [
      { tee: 'nitro', regions: ['us-west-2'] },
    ]),
  ]
}
```

`main.ts` is unchanged from a normal workflow:

```typescript
import { Runner } from '@chainlink/cre-sdk'
import { configSchema, initWorkflow } from './workflow'

export async function main() {
  const runner = await Runner.newRunner({ configSchema })
  await runner.run(initWorkflow)
}

main()
```

Some templates write these symbols through the `cre` namespace instead — `cre.handlerInTee(...)`, `new cre.capabilities.HTTPClient()`, `new cre.capabilities.CronCapability()`. Both forms are exported by the SDK and behave identically; match whichever style the user's existing project already uses.

## Go Pattern

```go
package main

import (
	"fmt"
	"log/slog"
	"math/big"

	"github.com/ethereum/go-ethereum/accounts/abi"

	"github.com/smartcontractkit/cre-sdk-go/capabilities/networking/http"
	"github.com/smartcontractkit/cre-sdk-go/capabilities/scheduler/cron"
	"github.com/smartcontractkit/cre-sdk-go/cre"
)

type Config struct {
	Schedule       string `json:"schedule"`
	URL            string `json:"url"`
	SecretID       string `json:"secretId"`
	ScoreThreshold uint64 `json:"scoreThreshold"`
}

func scoreResponse(body string) uint64 {
	var score uint64
	for _, b := range []byte(body) {
		score = (score + uint64(b)) % 1000
	}
	return score
}

// Receives cre.TeeRuntime, not cre.Runtime. Config arrives as a parameter, as in
// any Go handler.
func onCronTrigger(config *Config, runtime cre.TeeRuntime, _ *cron.Payload) (string, error) {
	secret, err := runtime.GetSecret(&cre.SecretRequest{Id: config.SecretID}).Await()
	if err != nil {
		return "", fmt.Errorf("failed to fetch secret %q inside the enclave: %w", config.SecretID, err)
	}

	// SendRequestInTee takes the TeeRuntime, so the request executes from inside
	// the enclave. The confidentialhttp client cannot be used here.
	client := &http.Client{}
	response, err := client.SendRequestInTee(runtime, &http.Request{
		Url:    config.URL,
		Method: "GET",
		MultiHeaders: map[string]*http.HeaderValues{
			"Authorization": {Values: []string{"Bearer " + secret.Value}},
		},
	}).Await()
	if err != nil {
		return "", fmt.Errorf("confidential request failed: %w", err)
	}
	if response.StatusCode < 200 || response.StatusCode > 299 {
		return "", fmt.Errorf("confidential request failed with status: %d", response.StatusCode)
	}

	score := scoreResponse(string(response.Body))
	verdict := "REJECT"
	if score >= config.ScoreThreshold {
		verdict = "APPROVE"
	}

	// Only the verdict and score cross out.
	donRuntime := runtime.UsingTheDons()

	encodedPayload, err := encodeVerdict(verdict, score)
	if err != nil {
		return "", fmt.Errorf("failed to encode report payload: %w", err)
	}

	if _, err := donRuntime.GenerateReport(&cre.ReportRequest{
		EncodedPayload: encodedPayload,
		EncoderName:    "evm",
		SigningAlgo:    "ecdsa",
		HashingAlgo:    "keccak256",
	}).Await(); err != nil {
		return "", fmt.Errorf("failed to generate report on the DON: %w", err)
	}

	return fmt.Sprintf("%s (score: %d)", verdict, score), nil
}

func encodeVerdict(verdict string, score uint64) ([]byte, error) {
	stringType, err := abi.NewType("string", "", nil)
	if err != nil {
		return nil, err
	}
	uint256Type, err := abi.NewType("uint256", "", nil)
	if err != nil {
		return nil, err
	}
	args := abi.Arguments{{Type: stringType}, {Type: uint256Type}}
	return args.Pack(verdict, new(big.Int).SetUint64(score))
}

func InitWorkflow(config *Config, _ *slog.Logger, _ cre.SecretsProvider) (cre.Workflow[*Config], error) {
	return cre.Workflow[*Config]{
		cre.HandlerInTee(
			cron.Trigger(&cron.Config{Schedule: config.Schedule}),
			onCronTrigger,
			cre.OneOfTees{cre.Nitro{Regions: []cre.NitroRegion{cre.NitroUsWest2}}},
		),
	}, nil
}
```

`main.go` is unchanged from a normal Go workflow (`//go:build wasip1`, `wasm.NewRunner(cre.ParseJSON[Config]).Run(InitWorkflow)`).

## TeeConstraint

The third argument to the TEE handler declares which enclaves the workflow accepts. Narrower constraints are better when the user has a jurisdictional or compliance reason; otherwise the permissive form is fine.

| Intent | TypeScript | Go |
|---|---|---|
| Any registered TEE, any region | `{}` | `cre.AnyTee{}` |
| Any TEE, specific regions | `{ regions: ['us-west-2'] }` | `cre.AnyTeeInRegions{Regions: []cre.Region{cre.AwsUsWest2}}` |
| Specific TEE type and regions | `[{ tee: 'nitro', regions: ['us-west-2'] }]` | `cre.OneOfTees{cre.Nitro{Regions: []cre.NitroRegion{cre.NitroUsWest2}}}` |

In Go each TEE binding owns its own region enum (`cre.Nitro` pairs with `cre.NitroRegion`), so passing a region belonging to another TEE is a compile-time error.

## TeeRuntime API

| Purpose | TypeScript | Go |
|---|---|---|
| Register the handler | `handlerInTee(trigger, fn, tees, hooks?)` | `cre.HandlerInTee(trigger, callback, tees)` |
| Fetch one secret | `runtime.getSecret({ id }).result().value` | `runtime.GetSecret(&cre.SecretRequest{Id: id}).Await()` |
| Fetch several secrets | one call per secret | `runtime.GetSecrets([]*cre.SecretRequest{...}).Await()` |
| HTTP from inside the enclave | `new HTTPClient().sendRequest(runtime, req).result()` | `(&http.Client{}).SendRequestInTee(runtime, req).Await()` |
| Cross back to the DON | `runtime.usingTheDons()` returns `Runtime<C>` | `runtime.UsingTheDons()` returns `cre.Runtime` |
| Report without a full crossover | `runtime.reportFromDon({...}).result()` | `runtime.ReportFromDon(&cre.ReportRequest{...}).Await()` |
| Config, time, logging | `runtime.config`, `runtime.now()`, `runtime.log()` | config is a handler parameter; `runtime.Now()`, `runtime.Logger()` |

`TeeRuntime` extends the base runtime and the secrets provider, so triggers, config parsing, and the `Runner` setup are identical to a non-confidential workflow. The handler registration and the runtime type are the only structural differences.

## Crossing Back to the DON

Cross the *conclusion*, not the inputs. A workflow that computes a verdict over a private position and then reports the verdict is confidential; one that reports the position size is not, no matter that it ran in an enclave.

- Anything passed into a capability call on the runtime from `usingTheDons()` executes on Workflow DON nodes and is visible there.
- Chain writes are never in-enclave. Generate the report after crossing back, then pass it to `evmClient.writeReport(donRuntime, report)`.
- `reportFromDon()` / `ReportFromDon()` is a shortcut when a report is the only thing needed from the DON, avoiding a full crossover.

## Pitfalls

| Pitfall | Why it matters | Do instead |
|---|---|---|
| Logging inside the enclave | Log output leaves the enclave, so anything logged is no longer confidential | Keep logs for simulation only and remove them before deploying to production. Report booleans or derived verdicts, never raw values |
| Using `ConfidentialHTTPClient` in a TEE handler | It has no `TeeRuntime` overload (Go: `confidentialhttp` only accepts `cre.Runtime`) | Regular `HTTPClient` with the `TeeRuntime`, or Go's `SendRequestInTee` |
| Declaring `vaultDonSecrets` for a confidential workflow | That is Confidential HTTP's mechanism; nothing needs declaring upfront here | `runtime.getSecret()` / `GetSecret()` at the point of use |
| Passing a secret through `usingTheDons()` | Silently ends confidentiality — it compiles and runs | Cross over derived, non-sensitive values only |
| Expecting chain reads or triggers to be confidential | They always run on Workflow DON nodes | Read on-chain data before or after the enclave leg and treat it as public |
| Non-deterministic in-enclave logic | The enclave result is attested and consensus-verified | Same determinism rules as any handler; see `concepts.md` |
| Assuming the code is hidden | The binary, including handler logic, is revealed to the DON | Protect *data*; if the logic itself is the secret, Confidential Workflows is the wrong tool |

## Secrets

Secrets work as they do elsewhere in CRE (see `workflow-patterns.md`), with one difference: the Vault DON releases them directly into the attested enclave rather than into node memory. `secrets.yaml` maps the workflow-facing secret ID to an environment variable:

```yaml
secretsNames:
    API_TOKEN:
        - SECRET_API_TOKEN
```

The workflow then requests `API_TOKEN` by ID. For deployment, upload to the Vault DON with `cre secrets create` as usual (see `operations.md`).

## Simulation

Simulation needs no beta enrollment, which makes it the fastest way to validate a confidential workflow:

```bash
cre workflow simulate ./my-workflow --target staging-settings
```

Set the environment variables named in `secrets.yaml` first (typically via `.env`). Simulation is also the only place in-enclave logging is appropriate — see `simulation.md` for general behavior and failure modes.

## Starter Templates

Two of these are registered with the CLI; the other three are project-shaped examples that must be cloned. Verify with `cre templates list --json` before telling a user a template is `cre init`-able.

| Template | How to obtain | Languages | What it does | Confidential inputs |
|---|---|---|---|---|
| `hello-confidential-workflows` | `cre init -t hello-confidential-workflows-ts` (or `-go`) | TS, Go | Minimal four-step confidential workflow: TEE handler, in-enclave secret, in-enclave HTTP call, crossover for the report. Defaults to an echo endpoint so no real API key is needed | One API token |
| `ai-audit-firewall` | Clone only | TS, Go | Pre-execution security firewall: fetches contract source and ABI, runs model-based risk classification, then allows, blocks, or escalates the transaction. Ships Solidity consumers | Scanner and LLM API credentials |
| `automated-liquidation-protection` | Clone only | TS, Go | Monitors lending-position health and adds collateral or repays debt before liquidation, under policy constraints | Exchange and LLM credentials, health-factor and reserve thresholds, execution preferences |
| `automated-portfolio-rebalancing` | Clone only | TS, Go | Tracks allocation drift and rebalances toward target weights when thresholds are exceeded | Exchange and LLM credentials, target weights, drift and slippage limits, venue preferences |

The three clone-only templates are absent from `cre templates list` because they carry no `.cre/template.yaml` registration file in `cre-templates`. Obtain them directly:

```bash
git clone --depth 1 https://github.com/smartcontractkit/cre-templates.git
cd cre-templates/starter-templates/confidential-workflows/<template-name>
```

Each is a standalone CRE project with `project.yaml`, `secrets.yaml`, `.env.example`, parallel `-ts` and `-go` workflow directories, a `mock-server.js` giving deterministic local responses, and tests. The usual loop is `bun install`, `cp .env.example .env`, `bun run mock:server`, then `cre workflow simulate ./<workflow-dir> --target=staging-settings`.

Their model-reasoning stages are replaceable with deterministic rule-based logic, which is worth mentioning when a user wants a policy engine rather than an LLM in the loop.

## Official Sources

| Resource | URL |
|---|---|
| Concepts: Confidential Workflows | `https://docs.chain.link/cre/concepts/confidential-workflows` |
| Requesting access | `https://docs.chain.link/cre/account/confidential-workflows-access` |
| Guide: making a workflow confidential (TS) | `https://docs.chain.link/cre/guides/workflow/using-confidential-workflows/making-workflow-confidential-ts` |
| Guide: making a workflow confidential (Go) | `https://docs.chain.link/cre/guides/workflow/using-confidential-workflows/making-workflow-confidential-go` |
| SDK reference: client (TS) | `https://docs.chain.link/cre/reference/sdk/confidential-workflows-client-ts` |
| SDK reference: client (Go) | `https://docs.chain.link/cre/reference/sdk/confidential-workflows-client-go` |
| Templates: hello | `https://github.com/smartcontractkit/cre-templates/tree/main/starter-templates/hello-confidential-workflows` |
| Templates: advanced examples | `https://github.com/smartcontractkit/cre-templates/tree/main/starter-templates/confidential-workflows` |
