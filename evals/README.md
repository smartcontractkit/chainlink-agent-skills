# Evaluate And Improve Skills

This repo includes two local eval paths:

- `evals/run-agent-eval.md` runs smoke/full evals through agent subagents without API keys.
- `evals/run-agent-ab-test.md` compares baseline responses against skill-enabled responses using subagents, then aggregates wins, ties, regressions, and recommended skill changes.

For example:

```text
Run an agent A/B test for chainlink-cre-skill using mixed-chainlink
Improve chainlink-cre-skill using agent A/B tests
```

The A/B workflow is useful in Cursor, Codex, Gemini CLI, and similar tools because it spends local agent/subagent budget instead of external model API keys.

## Promptfoo model set

Baseline: Sonnet 5.5 (medium) · Oracle: GPT 6.1 Sol (medium)

| Role | Model | Setting | Where used |
|------|-------|---------|------------|
| Baseline | `claude-sonnet-5-5` | `effort: medium` | Promptfoo, both sessions (with and without skill) |
| Oracle | `gpt-6.1-sol` | `reasoning.effort: medium` | Promptfoo, rubric grading |
| Local | Whatever the developer runs | n/a | Agent-powered eval protocol, agent A/B protocol |

The model set is fixed so results stay comparable over time. Changing a model resets the baseline and requires a full-suite run.

Baseline reset: 2026-10-29 (previous model set replaced). The new baseline numbers are recorded in the PR that made the change.
