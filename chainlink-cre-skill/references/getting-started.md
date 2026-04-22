# Getting Started

Use this file for CLI installation, account setup, or the getting-started tutorial overview.

## Trigger Conditions

- "How do I install the CRE CLI?"
- "How do I create a CRE account?"
- "How do I log in to the CRE CLI?"
- "Walk me through the CRE getting started tutorial"

For project creation and scaffolding, see project-scaffolding.md. For running simulations, see simulation.md. Do not use for workflow-specific code patterns (triggers, HTTP, EVM), SDK API details, or deployment operations.

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

## Tutorial Overview

The getting-started tutorial is a 4-part series:

1. **Part 1: Project Setup & Simulation** - Initialize project, explore structure, run first simulation
2. **Part 2: Fetching Offchain Data** - Add HTTP capability to fetch from an external API with consensus
3. **Part 3: Reading Onchain Value** - Read from a smart contract using the EVM client
4. **Part 4: Writing Onchain** - Write data to a consumer contract on the blockchain

Each part builds on the previous one, creating a complete workflow that fetches offchain data, reads onchain state, computes a result, and writes it back onchain.

For hands-on project setup, see project-scaffolding.md. For running simulations, see simulation.md.

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
