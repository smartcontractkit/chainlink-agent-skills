# Project Scaffolding

Use this file when the user wants to create a new CRE project, scaffold workflow files, or set up dependencies for Go or TypeScript.

## Trigger Conditions

- "Create a new CRE project"
- "Scaffold a CRE workflow"
- "Set up a CRE TypeScript/Go project"
- "Initialize a CRE project"
- "Start a new CRE workflow from scratch"

Do not use for CLI installation or account setup (see getting-started.md), simulation (see simulation.md), or workflow code patterns (see workflow-patterns.md).

## Project Creation

Prefer `cre init` with `--non-interactive` and explicit flags. This generates the correct project structure without requiring human input. Fall back to manual scaffolding from the templates below only if `cre init` is unavailable or fails.

### Using `cre init` (Preferred)

`cre init` supports non-interactive mode via the `--non-interactive` flag. Always use this mode when running as an agent.

| Flag | Description | Required with `--non-interactive` |
|------|-------------|-----------------------------------|
| `--non-interactive` | Fail instead of prompting | Yes (prevents interactive prompts) |
| `-p, --project-name` | Name for the new project | Yes (when creating a new project) |
| `-w, --workflow-name` | Name for the new workflow | No (defaults to template name) |
| `-t, --template` | Template name (e.g., `hello-world-ts`, `hello-world-go`) | No (but recommended) |
| `--rpc-url` | RPC endpoint, format: `chain-name=url` (repeatable) | Depends on template |
| `--refresh` | Bypass template cache and fetch from GitHub | No |

Built-in templates (available offline, no GitHub fetch needed):
- `hello-world-go` - Go hello world with cron trigger
- `hello-world-ts` - TypeScript hello world with cron trigger

Run `cre templates list` to see all available templates including those from GitHub.

#### TypeScript project:

```bash
cre init \
  --non-interactive \
  --project-name my-project \
  --workflow-name my-workflow \
  --template hello-world-ts
```

#### Go project:

```bash
cre init \
  --non-interactive \
  --project-name my-project \
  --workflow-name my-workflow \
  --template hello-world-go
```

#### With RPC URLs (required by some templates):

```bash
cre init \
  --non-interactive \
  --project-name my-project \
  --workflow-name my-workflow \
  --template hello-world-ts \
  --rpc-url sepolia=https://ethereum-sepolia-rpc.publicnode.com
```

After `cre init` completes, install TypeScript dependencies from inside the workflow directory. Do not leave that directory until WASM tooling is set up.

```bash
cd my-project/my-workflow
bun install
# postinstall may not always run `bunx cre-setup`; if install output does not show cre-setup, or you are unsure, run it explicitly:
bunx cre-setup
cd ../..
```

For Go projects, `cre init` handles `go.mod` creation. Run `go mod tidy` from the project root if needed.

### Manual Scaffolding (Fallback)

If `cre init` is unavailable or fails, create the project files directly from the templates below.

## Prerequisites

- **Go**: version 1.25.3 or higher
- **TypeScript**: Bun version 1.2.21 or higher
- **Funded Sepolia account**: for deployment gas fees (get testnet ETH at `faucets.chain.link`)

## TypeScript Project Template

Create the following directory structure. Replace `my-project` and `my-workflow` with the desired names.

```
my-project/
├── my-workflow/
│   ├── config.production.json
│   ├── config.staging.json
│   ├── main.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── workflow.yaml
├── .env
├── .gitignore
├── project.yaml
└── secrets.yaml
```

### my-workflow/main.ts

```typescript
import { CronCapability, handler, Runner, type Runtime } from "@chainlink/cre-sdk"

type Config = {
  schedule: string
}

const onCronTrigger = (runtime: Runtime<Config>): string => {
  runtime.log("Hello world! Workflow triggered.")
  return "Hello world!"
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

### my-workflow/package.json

```json
{
  "name": "my-workflow",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "postinstall": "bunx cre-setup"
  },
  "dependencies": {
    "@chainlink/cre-sdk": "latest"
  }
}
```

### my-workflow/tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "./dist",
    "rootDir": ".",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["./**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### my-workflow/workflow.yaml

```yaml
staging-settings:
  user-workflow:
    workflow-name: "my-workflow-staging"
  workflow-artifacts:
    workflow-path: "./main.ts"
    config-path: "./config.staging.json"
    secrets-path: ""
production-settings:
  user-workflow:
    workflow-name: "my-workflow-production"
  workflow-artifacts:
    workflow-path: "./main.ts"
    config-path: "./config.production.json"
    secrets-path: ""
```

### my-workflow/config.staging.json

```json
{
  "schedule": "*/30 * * * * *"
}
```

### my-workflow/config.production.json

```json
{
  "schedule": "0 */5 * * * *"
}
```

### project.yaml (project root)

```yaml
staging-settings:
  evms:
    - chain-selector: "16015286601757825753"
      rpc-url: "https://ethereum-sepolia-rpc.publicnode.com"
production-settings:
  evms:
    - chain-selector: "5009297550715157269"
      rpc-url: "https://ethereum-mainnet-rpc.example.com"
```

### secrets.yaml (project root)

```yaml
secretsNames: {}
```

### .env (project root)

```bash
CRE_ETH_PRIVATE_KEY=YOUR_64_CHARACTER_PRIVATE_KEY_HERE
```

### .gitignore (project root)

```
.env
node_modules/
dist/
*.wasm
```

### Install TypeScript Dependencies

Run from the project root:

```bash
cd my-workflow && bun install && cd ..
```

The `postinstall` script automatically runs `bunx cre-setup` to configure WASM compilation tools. If `bun install` fails, verify Bun is version 1.2.21 or higher with `bun --version`.

### Verify TypeScript Setup

```bash
cre workflow simulate my-workflow --target staging-settings
```

Expected output:

```
Workflow compiled
[SIMULATION] Simulator Initialized
[SIMULATION] Running trigger trigger=cron-trigger@1.0.0
[USER LOG] Hello world! Workflow triggered.
Workflow Simulation Result:
 "Hello world!"
[SIMULATION] Execution finished signal received
```

## Go Project Template

Create the following directory structure:

```
my-project/
├── my-workflow/
│   ├── config.production.json
│   ├── config.staging.json
│   ├── main.go
│   └── workflow.yaml
├── contracts/
│   └── evm/
│       └── src/
│           └── abi/
├── .env
├── .gitignore
├── go.mod
├── project.yaml
└── secrets.yaml
```

### my-workflow/main.go

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
	runtime.Logger().Info("Hello world! Workflow triggered.")
	result := "Hello world!"
	return &result, nil
}

func InitWorkflow(config *Config) []cre.HandlerDefinition {
	return []cre.HandlerDefinition{
		cre.Handler(cron.Trigger(cron.Config{Schedule: config.Schedule}), onCronTrigger),
	}
}
```

### go.mod (project root)

```
module my-project

go 1.25.3

require github.com/smartcontractkit/cre-sdk-go v0.0.0
```

The `v0.0.0` placeholder is resolved by `go mod tidy`. See dependency installation below.

### my-workflow/workflow.yaml

```yaml
staging-settings:
  user-workflow:
    workflow-name: "my-workflow-staging"
  workflow-artifacts:
    workflow-path: "./main.go"
    config-path: "./config.staging.json"
    secrets-path: ""
production-settings:
  user-workflow:
    workflow-name: "my-workflow-production"
  workflow-artifacts:
    workflow-path: "./main.go"
    config-path: "./config.production.json"
    secrets-path: ""
```

### my-workflow/config.staging.json

```json
{
  "schedule": "*/30 * * * * *"
}
```

### my-workflow/config.production.json

```json
{
  "schedule": "0 */5 * * * *"
}
```

### project.yaml (project root)

Same as the TypeScript version:

```yaml
staging-settings:
  evms:
    - chain-selector: "16015286601757825753"
      rpc-url: "https://ethereum-sepolia-rpc.publicnode.com"
production-settings:
  evms:
    - chain-selector: "5009297550715157269"
      rpc-url: "https://ethereum-mainnet-rpc.example.com"
```

### secrets.yaml (project root)

```yaml
secretsNames: {}
```

### .env (project root)

```bash
CRE_ETH_PRIVATE_KEY=YOUR_64_CHARACTER_PRIVATE_KEY_HERE
```

### .gitignore (project root)

```
.env
*.wasm
```

### Install Go Dependencies

Run from the project root:

```bash
GOFLAGS=-mod=mod go mod tidy
```

If `go mod tidy` hangs or fails to resolve the CRE SDK, try:

1. Verify Go version: `go version` (must be 1.25.3+)
2. Ensure `GONOSUMCHECK` and `GONOSUMDB` are not blocking the module: `GONOSUMCHECK=github.com/smartcontractkit/* GONOSUMDB=github.com/smartcontractkit/* go mod tidy`
3. If the module proxy is slow, try direct mode: `GOPROXY=direct go mod tidy`
4. If it still hangs after 60 seconds, cancel and retry with verbose output: `go mod tidy -v`

### Verify Go Setup

```bash
cre workflow simulate my-workflow --target staging-settings
```

## WASM Runtime Restrictions (TypeScript)

CRE TypeScript workflows compile to WebAssembly via QuickJS. The following Node.js APIs are NOT available in the WASM runtime:

`fs`, `path`, `crypto`, `process`, `http`, `https`, `net`, `stream`, `child_process`, `os`, `worker_threads`, `cluster`, `dgram`, `dns`, `tls`, `vm`, `zlib`, `readline`, `events` (Node.js EventEmitter), `util` (Node.js `promisify`), `buffer` (Node.js Buffer)

### What This Means for Code Generation

- Never use `process.env` to read environment variables. Use `runtime.getSecret()` instead.
- Never use `Buffer`. Use `Uint8Array` or `ArrayBuffer` instead.
- Never use `crypto` from Node.js. Use `viem` utilities for hashing and encoding.
- Never use `setTimeout`, `setInterval`, or `setImmediate`. The WASM environment is synchronous.
- Never use `fetch` from `node-fetch`. The CRE runtime provides its own `fetch`.

### Safe npm Packages

| Package | Status | Notes |
|---------|--------|-------|
| `@chainlink/cre-sdk` | Required | Core SDK |
| `zod` | Safe | Schema validation |
| `viem` | Safe | ABI encoding, type utilities |

### Unsafe npm Packages

| Package | Status | Reason |
|---------|--------|--------|
| `ethers` | Incompatible | Depends on Node.js `crypto` |
| `axios` | Incompatible | Depends on Node.js `http`/`https` |
| `node-fetch` | Incompatible | Depends on Node.js `http`/`stream` |
| `ws` | Incompatible | Depends on Node.js `net`/`http` |
| `dotenv` | Incompatible | Depends on Node.js `fs`/`path` |

Any package requiring native/N-API modules is incompatible. When uncertain about a package, check its dependency tree for Node.js built-in imports or consult `https://sebastianwessel.github.io/quickjs/docs/module-resolution/node-compatibility.html`.

## Official Documentation

- Getting started tutorial: `https://docs.chain.link/cre/getting-started/overview`
- Project configuration (TS): `https://docs.chain.link/cre/reference/project-configuration-ts`
- Project configuration (Go): `https://docs.chain.link/cre/reference/project-configuration-go`
- CRE Templates repo: `https://github.com/smartcontractkit/cre-templates`
