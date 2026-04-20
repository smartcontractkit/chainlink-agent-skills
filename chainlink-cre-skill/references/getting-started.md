# Getting Started

Use this file for CLI installation, account setup, project initialization, or the getting-started tutorial walkthrough.

## Trigger Conditions

- "How do I install the CRE CLI?"
- "Set up a new CRE project"
- "Walk me through the CRE getting started tutorial"
- "How do I create a CRE account?"
- "How do I log in to the CRE CLI?"

Do not use for workflow-specific code patterns (triggers, HTTP, EVM), SDK API details, or deployment operations.

## CLI Installation

### macOS and Linux

Automatic installation:

```bash
curl -sSfL https://cre.chain.link/install.sh | bash
```

Manual installation: Download the binary from the GitHub releases page, verify the SHA-256 checksum, extract, and add to PATH.

On macOS, if Gatekeeper blocks the binary:

```bash
xattr -d com.apple.quarantine /path/to/cre
```

### Windows

Automatic installation via PowerShell:

```powershell
irm https://cre.chain.link/install.ps1 | iex
```

### Verify Installation

```bash
cre version
```

### Updating

```bash
cre update
```

## Account Setup

### Creating an Account

1. Go to `https://cre.chain.link` and click "Sign Up"
2. Choose "Create a new organization" or "Join an existing organization"
3. Enter your email and verify with the 6-digit code
4. Set a secure password
5. Enable two-factor authentication (authenticator app or biometric)
6. Save the recovery code securely

### CLI Login

```bash
cre login
```

This opens a browser window for authentication. Complete 2FA when prompted. On success:

```
Account details retrieved:
Email:           [email protected]
Organization ID: org_AbCdEfGhIjKlMnOp
```

Check authentication status:

```bash
cre whoami
```

### API Key Authentication (CI/CD)

For non-interactive environments (requires Early Access approval):

```bash
export CRE_API_KEY=your_api_key_here
```

### Logging Out

```bash
cre logout
```

## Project Initialization

### Creating a New Project

```bash
cre init
```

The interactive wizard asks for:
- **Project name** (e.g., `my-project`)
- **Language**: Go or TypeScript
- **Template**: Helloworld or other starter template
- **Workflow name** (e.g., `my-workflow`)

### Generated Project Structure (TypeScript)

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

### Generated Project Structure (Go)

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

### Key Configuration Files

**project.yaml**: Global project settings shared across all workflows. Contains RPC URLs and environment targets.

**workflow.yaml**: Per-workflow configuration defining the workflow name, entry point, config file path, and secrets file path for each target.

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

**config.staging.json / config.production.json**: Runtime parameters accessible in your workflow code via `runtime.config` (TypeScript) or the `config` parameter (Go).

**.env**: Private key and environment variables. Never commit this file.

```bash
CRE_ETH_PRIVATE_KEY=YOUR_64_CHARACTER_PRIVATE_KEY_HERE
```

### Install Dependencies (TypeScript)

```bash
cd my-project/my-workflow
bun install
cd ..
```

The `postinstall` script automatically runs `bunx cre-setup` to configure WASM compilation tools.

### Prerequisites

- **Go**: version 1.25.3 or higher
- **TypeScript**: Bun version 1.2.21 or higher
- **Funded Sepolia account**: for transaction gas fees (get testnet ETH at `faucets.chain.link`)

## First Simulation

Run from the project root directory:

```bash
cre workflow simulate my-workflow --target staging-settings
```

This compiles your code to WebAssembly, uses the staging-settings target configuration, and runs a local simulation.

### Minimal TypeScript Workflow (Hello World)

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

With `config.staging.json`:

```json
{
  "schedule": "*/30 * * * * *"
}
```

### Expected Simulation Output

```
Workflow compiled
[SIMULATION] Simulator Initialized
[SIMULATION] Running trigger trigger=cron-trigger@1.0.0
[USER LOG] Hello world! Workflow triggered.
Workflow Simulation Result:
 "Hello world!"
[SIMULATION] Execution finished signal received
```

## Tutorial Overview

The getting-started tutorial is a 4-part series:

1. **Part 1: Project Setup & Simulation** - Initialize project, explore structure, run first simulation
2. **Part 2: Fetching Offchain Data** - Add HTTP capability to fetch from an external API with consensus
3. **Part 3: Reading Onchain Value** - Read from a smart contract using the EVM client
4. **Part 4: Writing Onchain** - Write data to a consumer contract on the blockchain

Each part builds on the previous one, creating a complete workflow that fetches offchain data, reads onchain state, computes a result, and writes it back onchain.

## Organizations

### Understanding Organizations

CRE organizations allow teams to collaborate on workflow development and deployment.

- **Single Owner model**: One individual with full administrative control
- **Multiple Members model**: Collaborative workflow management
- Maximum of 2 linked wallet keys per organization
- Each wallet address can only be linked to one organization

### Inviting Members

The organization Owner can invite new members:
1. Navigate to organization settings at `cre.chain.link`
2. Go to the Members tab
3. Add member email (must be from a whitelisted domain)
4. Send invitation

### Linking Wallet Keys

Link a wallet address to your organization for deploying and managing workflows:

```bash
cre account link-key --target <target-name>
```

Prerequisites:
- Logged in via `cre login`
- `.env` file contains `CRE_ETH_PRIVATE_KEY`
- Wallet funded with ETH for gas fees

List linked keys:

```bash
cre account list-key
```

Unlink a key (destructive, deletes associated workflows):

```bash
cre account unlink-key --target <target-name>
```

## Official Documentation

- Account setup: `https://docs.chain.link/cre/account`
- CLI installation: `https://docs.chain.link/cre/getting-started/cli-installation`
- Getting started tutorial: `https://docs.chain.link/cre/getting-started/overview`
- Organization management: `https://docs.chain.link/cre/organization`
