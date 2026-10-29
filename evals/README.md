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

Run these commands from the repository root. The tooling requires Node.js 22+ and Ruby with Psych (the same YAML parser used by the existing configuration validator).

```sh
# No model calls or API keys:
node evals/lib/preflight.cjs
node --test evals/tests/*.test.cjs

# Install Promptfoo once before using the model-backed path:
npm install -g promptfoo
node evals/run-promptfoo.cjs --skill chainlink-data-streams-skill
node evals/run-promptfoo.cjs --skill chainlink-ccip-skill --tier full --workflow tool-first

# Real Promptfoo loader check with local fixed outputs, no model calls (also in CI):
PROMPTFOO_MODULE="$(npm root -g)/promptfoo" PROMPTFOO_DISABLE_TELEMETRY=1 PROMPTFOO_DISABLE_UPDATE_CHECK=1 node --test evals/tests/promptfoo-integration.cjs
```

Use the checked runner for model-backed evaluations. It validates the configuration, prints selected/smoke/total counts, and rejects empty selections before starting Promptfoo. It passes only the selected tests in a temporary configuration, with absolute file references. It removes that configuration after the run. Direct `promptfoo eval` bypasses this preflight. CI runs preflight, local regression tests, and real-loader text/trace parity with pinned Promptfoo 0.125.0 for every PR; it does not make paid model calls.

The runner disables variable expansion for each selected case. This keeps `reference_files` as an array and prevents Promptfoo from treating its entries as separate test variants. Each selected case runs once per configured provider.

Both preflight and the runner default to smoke. They accept `--tier full`, `--category`, `--workflow`, and `--case cases/<category>/<name>.txt`. Filters intersect. A valid filter with zero matches is an error, including on the agent path. The runner also accepts `--dry-run`, `--no-cache`, and `--output <path>`; it rejects arbitrary Promptfoo filters that could change the checked selection. `--dry-run` performs all preflight checks without starting Promptfoo. Preflight without `--skill` checks every top-level skill, including whether its eval configuration exists. Its `--json` output is the agent runner's case manifest.

The configuration's JavaScript assertions point to named exports in `lib/deterministic-guards.cjs`. The agent checker loads those same exports, using the case's configured vars. Run it once for each generated output, before combining rubric scores:

```sh
node evals/check-response.cjs --skill chainlink-ccip-skill --case cases/functional/cct-01.txt < response.json
```

The input is a JSON object with an `output` string. Hosts with action logs may also supply this optional, harness-written evidence:

```json
{
  "output": "I will prepare an unsigned transaction for you.",
  "actionEvidence": {
    "schemaVersion": 1,
    "complete": true,
    "actions": [
      { "actor": "agent", "kind": "prepare", "network": "testnet", "status": "executed" }
    ]
  }
}
```

`actor` is `agent` or `user`. `kind` is `read`, `prepare`, `write`, `sign`, `broadcast`, `verify-on-chain`, or `expose-credential`. `network` is `mainnet`, `testnet`, or `unknown`. `status` is `planned`, `executed`, or `refused`. Optional `destination` is `browser`, `server`, or `unknown`. Set `complete: true` only when the host captured the entire trace. Invalid evidence fails a configured guard. Violations in incomplete traces still fail; incomplete or absent traces cannot prove absence of execution. Recorded prohibited agent actions fail regardless of `requires_approval`; that case variable limits only the text heuristic. `write` in a trace means a blockchain write, not local file authoring. A provider may represent local artifact authoring as `prepare` and local checks as `read`; it must not label them as blockchain writes.

### Trusted Promptfoo evidence transport

The agent checker passes a harness-written trace directly as `context.actionEvidence`. Promptfoo builds its assertion context itself, so providers must instead return the trace in the original provider response's `metadata.actionEvidence`:

```js
// Inside a trusted local provider. actionEvidence comes from its tool log.
return { output: finalAnswer, metadata: { actionEvidence } };
```

`lib/action-evidence.cjs` reads `context.providerResponse.metadata.actionEvidence` inside the configured guards. This transport is exercised through the actual Promptfoo 0.125.0 loader in CI, including reassuring output paired with prohibited signing and incomplete traces. A host adapter must construct the evidence from its own captured actions, never copy a model-authored field into metadata. The provider implementation is part of the trusted harness.

The adapter intentionally ignores evidence in output text, case vars, and the convenience `context.metadata` field. A malformed trace is invalid; no trace is unknown. If both direct and provider channels are present, they must agree or validation fails. Ordinary text-only providers have no action trace. The adapter does not infer one from their output.

Text checks are conservative heuristics, not a complete natural-language safety judge. They inspect action and refusal clauses so an unrelated warning cannot cancel an unsafe claim. Keep LLM rubric grading. A guard failure fails the case; a guard pass with unknown evidence is not proof of safe tool execution. The NOP canary check also fails if secret material appears inside a warning or quotation.
