# Agent A/B Test Protocol

This runbook lets an agent compare a skill-enabled response against a baseline response using local subagents instead of API-key-backed promptfoo runs. It is designed for Cursor, Codex, Gemini CLI, and similar host agents that can delegate work to subagents or parallel agent sessions.

Use this when you want to answer: "Did the skill make the response better than the same model without the skill?"

## Quick Start

Ask the agent:

```text
Run an agent A/B test for chainlink-cre-skill using mixed-chainlink
Run an agent A/B test for chainlink-cre-skill using mixed-chainlink, then propose improvements
Run an agent A/B test for chainlink-ccip-skill, smoke tier
```

`mixed-chainlink` is a curated CRE scenario set from manual A/B testing in `evals/chainlink-cre-skill/ab-scenarios/mixed-chainlink/`.

## How It Works

The parent agent coordinates four roles:

1. **Baseline generator**: answers the prompt without reading or using the skill.
2. **Skill generator**: answers the same prompt with `<skill>/SKILL.md` as system context and any necessary references loaded according to that skill.
3. **Evaluator**: compares the two outputs against the original prompt, applicable rubrics, and the A/B comparison rubric.
4. **Aggregator**: summarizes winners, failure patterns, proposed skill changes, and retest targets.

No API keys are required because the host agent's own subagent capacity performs generation and grading.

## Host Adapter

Use the best available delegation primitive in the host environment:

| Host | Generation workers | Evaluation worker |
|---|---|---|
| Cursor | General-purpose subagents | A separate general-purpose subagent, preferably a fast model if available |
| Codex | Spawned worker agents when available; otherwise parallel local tasks | A separate worker agent or a fresh local evaluation pass |
| Gemini CLI | Parallel agent sessions if available; otherwise sequential baseline/skill turns | A fresh evaluator session with no prior generation context |
| Other agents | Any isolated worker/chat that can receive a prompt and return text | Any isolated worker/chat that can compare outputs against rubrics |

Keep the generator and evaluator contexts separate. The evaluator must see the prompt and final outputs, not the generator's private reasoning.

## Inputs

Resolve these inputs before running:

- **skill**: The skill directory name, such as `chainlink-cre-skill`.
- **case source**: One of:
  - A named A/B scenario directory under `evals/<skill>/ab-scenarios/<name>/`.
  - The promptfoo smoke tier from `evals/<skill>/promptfooconfig.yaml`.
  - A specific case file or directory.
- **run tag**: Optional short identifier. If omitted, use `YYYYMMDD-HHMM-<skill>-ab`.
- **mode**: `compare` by default. Use `improve` only if the user asks to propose or implement changes after the comparison.

Create an untracked run directory:

```text
evals/runs/<skill>/<run-tag>/
```

Write artifacts there so results can be reviewed later without committing generated responses.

## Case Selection

### Named A/B Scenario Sets

If the case source names a directory under `evals/<skill>/ab-scenarios/`, collect every `*.txt` file in lexical order. The file content is the user prompt.

### Promptfoo Cases

If the case source is `smoke`, `full`, or a promptfoo category/filter:

1. Run `node evals/lib/preflight.cjs --skill <skill> --tier smoke --json` from the repo root (use `--tier full` and any category/workflow/case filters as requested). Print counts and stop on an empty selection before any workers start.
2. Select cases using the same rules as `evals/run-agent-eval.md`.
3. Read each `vars.case_file` prompt from `evals/<skill>/`.
4. Record `metadata.category`, `vars.workflow`, and applicable rubric files.

## Generation Protocol

For each case, create two generation jobs. Run up to 4 cases in parallel unless the host is already resource-constrained.

### Baseline Generator Prompt

Give the baseline generator:

```text
You are answering an eval prompt as the base agent with no Chainlink skill installed.

Do not read or use <skill>/SKILL.md.
Do not read or use files under <skill>/references/.
Answer the user's prompt directly and naturally.

User prompt:
<case prompt>
```

Save the response to:

```text
evals/runs/<skill>/<run-tag>/generations/<case-id>.baseline.md
```

### Skill Generator Prompt

Give the skill generator:

```text
You are answering an eval prompt with <skill> activated.

Read <skill>/SKILL.md in full and follow its instructions.
Use reference files only as directed by the skill. Do not invent live data.
Answer the user's prompt directly and naturally.

User prompt:
<case prompt>
```

Save the response to:

```text
evals/runs/<skill>/<run-tag>/generations/<case-id>.with-skill.md
```

## Evaluation Protocol

Read `evals/<skill>/rubrics/ab-comparison.txt`. If the case came from promptfoo, also read the applicable category rubrics from `evals/<skill>/rubrics/`.

Evaluate in batches of up to 4 paired cases. For each case, give the evaluator:

- Case id and original prompt.
- Baseline response.
- Skill response.
- A/B comparison rubric.
- Applicable promptfoo rubrics, if any.

The evaluator must return strict JSON:

```json
{
  "case": "01-token-pool-rebalancing",
  "winner": "skill",
  "confidence": 0.84,
  "scores": {
    "baseline": {
      "task_satisfaction": 4,
      "correctness": 4,
      "chainlink_specificity": 3,
      "deliverable_completeness": 3,
      "safety": 4,
      "proportionality": 4
    },
    "with_skill": {
      "task_satisfaction": 5,
      "correctness": 5,
      "chainlink_specificity": 5,
      "deliverable_completeness": 5,
      "safety": 4,
      "proportionality": 4
    }
  },
  "skill_helped": ["Added deployable CRE workflow structure."],
  "skill_hurt": [],
  "recommended_skill_changes": [],
  "reason": "The skill response is more complete and gives concrete CRE implementation details without overfitting the prompt."
}
```

Allowed `winner` values are `skill`, `baseline`, `tie`, and `mixed`.

Save evaluator JSON to:

```text
evals/runs/<skill>/<run-tag>/grades/<case-id>.json
```

For promptfoo-derived cases, run `evals/check-response.cjs` on both baseline and skill responses as specified in Step 6 of `evals/run-agent-eval.md`. Use the same case vars and any trusted harness action evidence. Include deterministic failures in each arm's result; an LLM grade cannot override them. Named scenario sets do not have configured assertions: record guards as not run rather than claiming parity for those sets.

## Aggregation

Create:

```text
evals/runs/<skill>/<run-tag>/summary.md
evals/runs/<skill>/<run-tag>/summary.tsv
```

`summary.md` must include:

- Run metadata: skill, case source, run tag, date, host agent, number of cases.
- Verdict table with case id, topic, winner, confidence, and one-sentence reason.
- Totals: skill wins, baseline wins, ties, mixed.
- Average score deltas by criterion.
- Patterns where the skill helped.
- Patterns where the skill hurt or over-triggered.
- Recommended skill changes, grouped by expected impact.
- Suggested retest subset.

`summary.tsv` must use:

```text
case	winner	confidence	baseline_total	with_skill_total	delta	reason
```

## Improvement Mode

If the user asks the agent to propose or implement improvements:

1. Start from `summary.md` and `grades/*.json`.
2. Pick one focused skill change at a time.
3. Modify only files under `<skill>/`.
4. Re-run the smallest relevant A/B subset first.
5. Keep the change only if:
   - skill wins increase, or
   - score deltas improve without introducing new baseline wins, or
   - equal scores are achieved with simpler instructions.
6. Then run the broader smoke or named scenario set.

Do not modify eval prompts or rubrics to make the score better. They are the measuring stick.

## Reporting Back

End with a concise report:

```text
A/B run complete for chainlink-cre-skill using mixed-chainlink.

Skill wins: 5
Baseline wins: 0
Ties/mixed: 3
Most important pattern: deployable CRE workflows benefit most from the skill.
Artifacts: evals/runs/chainlink-cre-skill/<run-tag>/summary.md
Recommended next change: clarify when CRE is optional for architecture-only prompts.
```

Do not paste full generated responses unless the user asks for them.
