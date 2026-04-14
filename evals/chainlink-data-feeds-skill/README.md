# Chainlink Data Feeds Skill — Evaluation Suite

Promptfoo-based evaluation framework for the `chainlink-data-feeds-skill`.

## Running

```bash
cd evals/chainlink-data-feeds-skill

# Full suite
npx promptfoo eval

# View results
npx promptfoo view

# Single test
npx promptfoo eval --filter-pattern "reading-price-feeds-01"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Anthropic API key |
| `PROMPTFOO_BASELINE_PROVIDER` | `claude-sonnet-4-20250514` | Model for baseline runs |
| `PROMPTFOO_WITH_SKILL_PROVIDER` | `claude-sonnet-4-20250514` | Model for with-skill runs |
| `PROMPTFOO_GRADER_PROVIDER` | `openai:gpt-5-mini` | Model for rubric grading |

## Test Categories

- **Functional** (12 cases): End-to-end workflow tests covering reading-price-feeds, mvr-feeds, svr-feeds, feed-types, multi-chain, and feed-operations
- **Trigger Positive** (8 cases): Verify the skill activates for data-feeds-specific prompts
- **Trigger Negative** (6 cases): Verify the skill does not over-trigger for CCIP, VRF, Automation, Data Streams, Functions, or generic Solidity requests

## Rubrics

All rubrics use 3-point scales (1.0 pass / 0.5 borderline / 0.0 fail) except `must-pass` which is binary (1.0 / 0.0).

Key safety checks enforced by `must-pass`:
- Staleness validation present in all consumer contracts
- Decimals not hardcoded
- `answeredInRound` not used for freshness
- L2 sequencer check present for L2 chain targets
- MVR struct matches documented schema
- Correct interface used (AggregatorV2V3Interface for sequencer, IBundleAggregatorProxy for MVR)
