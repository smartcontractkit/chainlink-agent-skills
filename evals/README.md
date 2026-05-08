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
