# Chainlink CRE Skill Evaluation

Promptfoo-based evaluation suite for the `chainlink-cre-skill`.

## Running

```bash
cd evals/chainlink-cre-skill
npx promptfoo eval
npx promptfoo view
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMPTFOO_BASELINE_PROVIDER` | `claude-sonnet-4-20250514` | Model for baseline (no skill) runs |
| `PROMPTFOO_WITH_SKILL_PROVIDER` | `claude-sonnet-4-20250514` | Model for with-skill runs |
| `PROMPTFOO_GRADER_PROVIDER` | `openai:gpt-5-mini` | Model for rubric grading |

## Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| Functional | 12 | End-to-end CRE workflows: generation, HTTP, EVM, triggers, secrets, getting started, operations, concepts |
| Trigger Positive | 8 | Prompts that should activate the CRE skill |
| Trigger Negative | 6 | Prompts about other Chainlink products (CCIP, Data Feeds, VRF, Automation, Functions) or generic Solidity |

## Rubrics

| Rubric | Applied To | Description |
|--------|-----------|-------------|
| `must-pass` | All tests | Hard safety/correctness requirements (binary PASS/FAIL) |
| `correctness` | Functional | Routes to correct CRE workflow |
| `completeness` | Functional | Response is complete and proportional |
| `safety` | Functional | CRE-specific safe coding practices |
| `freshness` | Functional | Correct handling of live vs embedded data |
| `clarification` | Functional | Minimal, focused clarifying questions |
| `triggering-positive` | Trigger Positive | CRE skill clearly activates |
| `triggering-negative` | Trigger Negative | CRE skill does not over-trigger |
