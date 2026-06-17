# Official Sources

Use this file only when the answer depends on live data that the reference files do not contain: supported network lists, release notes, template repositories, SDK source code, or forwarder addresses for specific networks.

## Trigger Conditions

- "What networks does CRE support?"
- "Where is the CRE SDK source code?"
- "What are the latest CRE release notes?"
- "What's the forwarder address on [specific network]?"

Do not use for workflow code patterns, CLI usage, or conceptual questions that are covered in other reference files.

## Documentation

| Resource | URL |
|----------|-----|
| CRE documentation home | `https://docs.chain.link/cre.md` |
| Getting started overview | `https://docs.chain.link/cre/getting-started/overview.md` |
| CLI installation | `https://docs.chain.link/cre/getting-started/cli-installation.md` |
| Account setup | `https://docs.chain.link/cre/account.md` |
| Organization management | `https://docs.chain.link/cre/organization.md` |

## Guides

| Resource | URL |
|----------|-----|
| Using triggers (overview) | `https://docs.chain.link/cre/guides/workflow/using-triggers/overview.md` |
| Cron trigger (TS) | `https://docs.chain.link/cre/guides/workflow/using-triggers/cron-trigger-ts.md` |
| HTTP trigger (TS) | `https://docs.chain.link/cre/guides/workflow/using-triggers/http-trigger/overview-ts.md` |
| EVM log trigger (TS) | `https://docs.chain.link/cre/guides/workflow/using-triggers/evm-log-trigger-ts.md` |
| HTTP GET (TS) | `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-ts.md` |
| HTTP GET (Go) | `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-go.md` |
| HTTP POST (TS) | `https://docs.chain.link/cre/guides/workflow/using-http-client/post-request-ts.md` |
| Confidential HTTP (TS) | `https://docs.chain.link/cre/capabilities/confidential-http-ts.md` |
| Onchain read (TS) | `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-ts.md` |
| Onchain read (Go) | `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-go.md` |
| Onchain write | `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/writing-data-onchain.md` |
| Consumer contracts | `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/building-consumer-contracts.md` |
| Secrets | `https://docs.chain.link/cre/guides/workflow/secrets.md` |
| Time in workflows (TS) | `https://docs.chain.link/cre/guides/workflow/time-in-workflows-ts.md` |
| Randomness | `https://docs.chain.link/cre/guides/workflow/using-randomness.md` |
| Deploying workflows | `https://docs.chain.link/cre/guides/operations/deploying-workflows.md` |

## Reference

| Resource | URL |
|----------|-----|
| Supported networks | `https://docs.chain.link/cre/supported-networks-ts.md` |
| Forwarder addresses | `https://docs.chain.link/cre/guides/workflow/using-evm-client/forwarder-directory-ts.md` |
| Service quotas | `https://docs.chain.link/cre/service-quotas.md` |
| Project configuration (TS) | `https://docs.chain.link/cre/reference/project-configuration-ts.md` |
| Project configuration (Go) | `https://docs.chain.link/cre/reference/project-configuration-go.md` |
| CRE CLI reference | `https://docs.chain.link/cre/reference/cli.md` |

## Concepts

| Resource | URL |
|----------|-----|
| Consensus computing | `https://docs.chain.link/cre/concepts/consensus-computing.md` |
| Finality | `https://docs.chain.link/cre/concepts/finality.md` |
| Non-determinism | `https://docs.chain.link/cre/concepts/non-determinism.md` |

## GitHub Repositories

| Repository | URL | Description |
|------------|-----|-------------|
| CRE Templates | `https://github.com/smartcontractkit/cre-templates` | Starter templates for CRE workflows |
| CRE SDK TypeScript | `https://github.com/smartcontractkit/cre-sdk-typescript` | TypeScript SDK source |
| CRE SDK Go | `https://github.com/smartcontractkit/cre-sdk-go` | Go SDK source |
| CRE CLI | `https://github.com/smartcontractkit/cre-cli` | CLI source and releases |
| Prediction Market Demo | `https://github.com/smartcontractkit/cre-gcp-prediction-market-demo` | Example prediction market workflow |

## Release Notes and Migration

| Resource | URL |
|----------|-----|
| Release notes | `https://docs.chain.link/cre/release-notes.md` |

## Full-Text Documentation Dumps

For comprehensive content when reference files are insufficient:

| Resource | URL |
|----------|-----|
| CRE docs index | Check `assets/cre-docs-index.md` in the skill directory |

## Freshness Policy

CRE is evolving rapidly. When a user reports that information seems outdated or incorrect:

1. Check the official documentation URL for the specific topic
2. Fetch the latest content if WebFetch is available
3. Compare with the embedded reference content
4. Update guidance based on the latest official content
5. Note any discrepancies to the user

## Live Values Policy

Use official sources for values that may change or are easy to misremember:

- supported networks
- chain selector names or numeric selectors
- forwarder addresses
- feed proxy addresses
- CLI flags introduced in recent releases
- SDK API signatures from source or generated docs

When including one of these values in an answer or generated artifact, cite the official source if available. If live verification is not possible, mark the value as `NEED: verify against official Chainlink docs before deployment` rather than presenting it as current fact.
