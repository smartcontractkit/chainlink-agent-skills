# Getting Started

Use for CLI installation, account/login setup, organizations, or tutorial orientation. Project creation is in [project-scaffolding.md](project-scaffolding.md); simulation is in [simulation.md](simulation.md).

## Install

macOS/Linux:

```bash
curl -sSfL https://cre.chain.link/install.sh | bash
cre version
```

Manual installs must use a release for the correct architecture, verify its SHA-256 checksum, extract it, and add it to `PATH`. If macOS Gatekeeper blocks a verified binary: `xattr -d com.apple.quarantine /path/to/cre`.

Windows PowerShell:

```powershell
irm https://cre.chain.link/install.ps1 | iex
```

Update with `cre update`.

## Account and login boundary

The user alone creates an account at `https://app.chain.link/cre/discover`: choose/create an organization, verify the emailed six-digit code, set a password, enable 2FA (authenticator or biometric), and save the recovery code. Do not automate or request these credentials.

An agent may run:

```bash
cre whoami
cre login
```

Run `cre whoami` first. If it fails authentication, ask the user whether to export `CRE_API_KEY` (below) or complete `cre login`; do not run `cre login` unprompted. `cre login` opens a browser where the user enters password and 2FA. Continue only after it returns or `cre whoami` confirms the session. `cre whoami` reports email, organization ID, and linked keys. End with `cre logout`.

Deployment requires Early Access. After login, `cre account access` checks status and, when unavailable, interactively submits a use-case description. For unattended use, the user creates an API key in the CRE app (requires deploy access) and exports `CRE_API_KEY` in the environment that launches the agent; it replaces `cre login` for every command except `cre secrets`, which does not support API keys and requires an interactive `cre login`; the agent cannot perform `cre secrets` operations with `CRE_API_KEY` alone. The agent never reads, prints, or requests it. Keys are permissioned ([cli-reference.md](cli-reference.md)); on a permission error, name the missing permission instead of retrying or running `cre login`.

## Tutorial path

1. Initialize/configure a project and simulate it — read [project-scaffolding.md](project-scaffolding.md) for this step; it owns the Bun/Go prerequisite versions, non-interactive `cre init` flags, and the target-derivation command, so do not restate or re-derive them here.
2. Fetch offchain data through HTTP consensus.
3. Read a contract through the EVM client.
4. Generate a report and write through a consumer contract.

Every CLI getting-started answer that initializes a project must also show the first simulation, using [project-scaffolding.md](project-scaffolding.md)'s programmatic target derivation (never a `<placeholder>` or a manual copy step) substituted into:

```bash
cre workflow simulate "$workflow_name" --target "$target_name" --non-interactive --trigger-index 0
```

The complete loop is trigger → offchain/onchain reads → consensus → deterministic compute → report/write. Use the capability references rather than copying tutorial scaffolding.

## Organizations and keys

Organizations support a single owner or multiple members. The owner invites members from whitelisted email domains in the platform settings. Current constraints: at most two linked wallet keys per organization; a wallet address belongs to only one organization.

```bash
cre account link-key --target <target>
cre account list-key
cre account unlink-key --target <target>
```

Linking requires login, a funded wallet, and `CRE_ETH_PRIVATE_KEY` available to the CLI in a user-controlled environment. The agent must not read it. Unlinking is destructive and deletes workflows associated with that key; apply [operations.md](operations.md)'s approval protocol.

## Sources

- https://docs.chain.link/cre/getting-started/cli-installation.md
- https://docs.chain.link/cre/account.md
- https://docs.chain.link/cre/organization.md
- https://docs.chain.link/cre/getting-started/overview.md
