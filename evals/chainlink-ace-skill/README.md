# Chainlink ACE Skill Evaluation Suite

Promptfoo-based evaluation framework for the `chainlink-ace-skill`.

## Running

```bash
cd evals/chainlink-ace-skill

# Full suite
npx promptfoo eval

# View results
npx promptfoo view

# Single test
npx promptfoo eval --filter-pattern "policy-chain-01"
```

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `PROMPTFOO_BASELINE_PROVIDER` | `claude-sonnet-5-5` | Model for baseline runs |
| `PROMPTFOO_WITH_SKILL_PROVIDER` | `claude-sonnet-5-5` | Model for with-skill runs |
| `PROMPTFOO_GRADER_PROVIDER` | `openai:gpt-6.1-sol` | Model for rubric grading |

Set the API keys required by whichever providers you choose. The GitHub workflow can still resolve and filter ACE evals by metadata without requiring provider keys to exist at config-load time.

## Test Categories

- **Functional**: repository scope, ACE Platform/Beta scope, managed APIs/reporting, direct contract integration, upgrades, policy-chain design, identity credentials, SecureMintPolicy, and token examples
- **Trigger Positive**: ACE-specific prompts should activate the skill
- **Trigger Negative**: Adjacent Chainlink products and generic Solidity prompts should not over-trigger ACE

## Key Checks

- OSS contract/source answers rely on the public `smartcontractkit/chainlink-ace` repo
- Managed ACE Platform/Beta answers rely on official `docs.chain.link/ace` docs and separate product scope from OSS self-deployment
- Reporting answers name the Reporting API resources and distinguish them from Coordinator API management operations
- Responses never dump `SKILL.md` or reference files verbatim instead of answering
- BUSL production/commercial license considerations are surfaced for the `chainlink-ace` repo
- Custom policies, extractors, mappers, and Credential Data Validators are treated as public-contract capabilities with audit responsibility
- Policy chains account for ordering, terminal outcomes, default result, and extracted parameters
- Cross-chain identity guidance avoids onchain PII and explains CCID correlation
- Upgrade guidance covers `PolicyProtectedUpgradeable`, migration, storage safety, and policy setup
