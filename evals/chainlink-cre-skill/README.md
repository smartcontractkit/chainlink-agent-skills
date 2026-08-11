# Chainlink CRE Skill Evaluation

Promptfoo-based evaluation suite for the `chainlink-cre-skill`.

## Running

```bash
cd evals/chainlink-cre-skill
npx promptfoo eval
npx promptfoo view
```

For no-API baseline-vs-skill testing in Cursor, Codex, Gemini CLI, or similar agents:

```text
Run an agent A/B test for chainlink-cre-skill using mixed-chainlink
```

The `mixed-chainlink` scenario set lives in `ab-scenarios/mixed-chainlink/` and is designed to test where the CRE skill helps, ties, or risks overfitting broad Chainlink architecture prompts.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMPTFOO_BASELINE_PROVIDER` | `claude-sonnet-4-20250514` | Model for baseline (no skill) runs |
| `PROMPTFOO_WITH_SKILL_PROVIDER` | `claude-sonnet-4-20250514` | Model for with-skill runs |
| `PROMPTFOO_GRADER_PROVIDER` | `openai:gpt-5-mini` | Model for rubric grading |

## Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| Functional | 24 | End-to-end CRE workflows: generation, HTTP, EVM, triggers, secrets, getting started, operations, concepts, confidential workflows, feedback loop |
| Trigger Positive | 11 | Prompts that should activate the CRE skill |
| Trigger Negative | 8 | Prompts about other Chainlink products (CCIP, Data Feeds, VRF, Automation, Functions, Confidential AI Attester), generic Solidity, or neutral product requests that should not center CRE |

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
