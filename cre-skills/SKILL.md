---
name: cre-skills
description: Enable developers to learn and use Chainlink Runtime Environment (CRE) quickly by referencing filtered CRE docs. Trigger when user wants onboarding, CRE workflow generation (in TypeScript or Golang or other supported languages), workflow guidance, CRE CLI and/or SDK help, runtime operations advice, or capability selection
license: MIT
compatibility: Designed for Claude Code and AI agents that implement https://agentskills.io/specification
allowed-tools: Read WebFetch Write Edit Bash
metadata:
  purpose: CRE developer onboarding, assistance and reference
  version: "0.1"
---

# CRE Skills

Assist developers working with the Chainlink Runtime Environment (CRE) by looking up the latest documentation at runtime.

## Runtime Pattern

When a user asks a CRE-related question:

1. **Match user intent to a reference file** — Identify which topic best fits the query from the reference files listed below.
2. **Read the matching reference file** — Load `references/<file>.md` to find relevant URLs.
3. **Web-fetch 3-5 URLs** — Fetch the latest doc content from the URLs in the reference file. Prefer URLs whose one-line labels most closely match the user's question.
4. **Synthesize a response** — Answer using the fetched content. Cite source URLs so the user can read further.

Do NOT embed or rely on cached doc content. Always web-fetch to get the latest information.

## Reference Files

| File | Topic | When to use |
|------|-------|-------------|
| [account-setup.md](references/account-setup.md) | Account setup | Creating accounts, CLI login, managing authentication |
| [getting-started.md](references/getting-started.md) | Getting started | CLI installation, project setup, tutorial walkthrough (Go & TypeScript) |
| [capabilities.md](references/capabilities.md) | Capabilities | EVM read/write, HTTP capability, triggers overview |
| [workflow-building.md](references/workflow-building.md) | Workflow building | Secrets, time, randomness, triggers (cron/HTTP/EVM log), HTTP client, EVM client, onchain read/write, report generation |
| [cli-reference.md](references/cli-reference.md) | CLI reference | CLI commands for accounts, auth, project setup, secrets, workflows, utilities |
| [sdk-reference.md](references/sdk-reference.md) | SDK reference | SDK core, consensus/aggregation, EVM client, HTTP client, trigger APIs (Go & TypeScript) |
| [operations.md](references/operations.md) | Operations | Deploying, simulating, monitoring, activating, pausing, updating, deleting workflows, multi-sig wallets |
| [concepts.md](references/concepts.md) | Concepts | Consensus computing, finality, non-determinism, TypeScript WASM runtime |
| [organization.md](references/organization.md) | Organization | Org management, inviting members, linking wallet keys |
| [general.md](references/general.md) | General | CRE overview, key terms, demos, templates, project configuration, supported networks, release notes, service quotas, support |

## Tips

- Many topics have separate Go and TypeScript pages. Ask the user which language they're using if unclear, or fetch both.
- For workflow generation tasks, start with `workflow-building.md` and supplement with `sdk-reference.md` for API details.
- For onboarding, start with `getting-started.md` then `account-setup.md`.
- The full docs index is available at `assets/cre-docs-index.md` if you need to search across all URLs.
