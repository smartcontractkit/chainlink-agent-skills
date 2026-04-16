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
| CRE documentation home | `https://docs.chain.link/cre` |
| Getting started overview | `https://docs.chain.link/cre/getting-started/overview` |
| CLI installation | `https://docs.chain.link/cre/getting-started/cli-installation` |
| Account setup | `https://docs.chain.link/cre/account` |
| Organization management | `https://docs.chain.link/cre/organization` |

## Guides

| Resource | URL |
|----------|-----|
| Using triggers (overview) | `https://docs.chain.link/cre/guides/workflow/using-triggers` |
| Cron trigger (TS) | `https://docs.chain.link/cre/guides/workflow/using-triggers/cron-trigger-ts` |
| HTTP trigger (TS) | `https://docs.chain.link/cre/guides/workflow/using-triggers/http-trigger-ts` |
| EVM log trigger (TS) | `https://docs.chain.link/cre/guides/workflow/using-triggers/evm-log-trigger-ts` |
| HTTP GET (TS) | `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-ts` |
| HTTP GET (Go) | `https://docs.chain.link/cre/guides/workflow/using-http-client/get-request-go` |
| HTTP POST (TS) | `https://docs.chain.link/cre/guides/workflow/using-http-client/post-request-ts` |
| Confidential HTTP (TS) | `https://docs.chain.link/cre/guides/workflow/using-http-client/confidential-http-ts` |
| Onchain read (TS) | `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-ts` |
| Onchain read (Go) | `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-read-go` |
| Onchain write | `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/writing-data-onchain` |
| Consumer contracts | `https://docs.chain.link/cre/guides/workflow/using-evm-client/onchain-write/consumer-contracts` |
| Secrets | `https://docs.chain.link/cre/guides/workflow/secrets` |
| Time in workflows (TS) | `https://docs.chain.link/cre/guides/workflow/time-in-workflows-ts` |
| Randomness | `https://docs.chain.link/cre/guides/workflow/using-randomness` |
| Deploying workflows | `https://docs.chain.link/cre/guides/workflow/deploying-a-workflow` |

## Reference

| Resource | URL |
|----------|-----|
| Supported networks | `https://docs.chain.link/cre/reference/supported-networks` |
| Forwarder addresses | `https://docs.chain.link/cre/reference/forwarder-addresses` |
| Service quotas | `https://docs.chain.link/cre/reference/service-quotas` |
| Project configuration (TS) | `https://docs.chain.link/cre/reference/project-configuration-ts` |
| Project configuration (Go) | `https://docs.chain.link/cre/reference/project-configuration-go` |
| CRE CLI reference | `https://docs.chain.link/cre/reference/cre-cli` |

## Concepts

| Resource | URL |
|----------|-----|
| Consensus computing | `https://docs.chain.link/cre/concepts/consensus-computing` |
| Finality | `https://docs.chain.link/cre/concepts/finality` |
| Non-determinism | `https://docs.chain.link/cre/concepts/non-determinism` |

## GitHub Repositories

| Repository | URL | Description |
|------------|-----|-------------|
| CRE Templates | `https://github.com/smartcontractkit/cre-templates` | Starter templates for CRE workflows |
| CRE SDK TypeScript | `https://github.com/smartcontractkit/cre-sdk-typescript` | TypeScript SDK source |
| CRE SDK Go | `https://github.com/smartcontractkit/cre-sdk-go` | Go SDK source |
| CRE CLI | `https://github.com/smartcontractkit/cre-cli` | CLI source and releases |
| Prediction Market Demo | `https://github.com/smartcontractkit/cre-prediction-market-demo` | Example prediction market workflow |

## Release Notes and Migration

| Resource | URL |
|----------|-----|
| Release notes | `https://docs.chain.link/cre/release-notes` |
| Migration guides | `https://docs.chain.link/cre/migration` |

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
