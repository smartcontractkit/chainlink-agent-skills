# Chainlink CRE Connect Skill Evaluation

Promptfoo evaluation suite for `chainlink-cre-connect-skill`, with baseline and with-skill providers.

## Promptfoo

Run from the repository root:

```bash
npx promptfoo validate config -c evals/chainlink-cre-connect-skill/promptfooconfig.yaml
npx promptfoo eval -c evals/chainlink-cre-connect-skill/promptfooconfig.yaml --filter-metadata "smoke=true"
npx promptfoo eval -c evals/chainlink-cre-connect-skill/promptfooconfig.yaml
```

## Agent Evaluation

For a no-key smoke evaluation, follow [`evals/run-agent-eval.md`](../run-agent-eval.md) and ask:

```text
Run agent evals for chainlink-cre-connect-skill
```

For baseline-vs-skill A/B evaluation, follow [`evals/run-agent-ab-test.md`](../run-agent-ab-test.md) and ask:

```text
Run an agent A/B test for chainlink-cre-connect-skill using mixed-cre-connect
```

## Coverage

- **Functional (4):** verified-event side effects, atomic gasless operations, DTA integration, and product boundaries.
- **Trigger positive (2):** signed events and gasless operations.
- **Trigger negative (2):** ordinary CRE workflows and generic ERC-4337 requests.
