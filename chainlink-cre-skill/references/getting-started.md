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
cre login
cre whoami
```

`cre login` opens a browser where the user enters password and 2FA. Continue only after it returns or `cre whoami` confirms the session. `cre whoami` reports email, organization ID, and linked keys. End with `cre logout`.

Deployment requires Early Access. After login, `cre account access` checks status and, when unavailable, interactively submits a use-case description. CI API-key authentication also requires approval; the user-controlled environment may supply `CRE_API_KEY`, but the agent never reads it.

## Tutorial path

1. Initialize/configure a project and simulate it.
2. Fetch offchain data through HTTP consensus.
3. Read a contract through the EVM client.
4. Generate a report and write through a consumer contract.

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
