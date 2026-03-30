# Chainlink CCIP Skill Evals

This directory contains the Promptfoo eval suite for `chainlink-ccip-skill`.

The shipped skill lives in `chainlink-ccip-skill/`.

This directory supports both:

1. automated Promptfoo evaluation
2. lightweight manual testing via the runbook

## Quick Start

```bash
npm install -g promptfoo
cd evals/chainlink-ccip-skill
promptfoo eval
promptfoo view
```

The skill itself is agent-agnostic. However, Promptfoo still needs an execution provider. That provider is configurable through environment variables.

Defaults:

- baseline provider: `anthropic:messages:claude-sonnet-4-20250514` unless overridden
- with-skill provider: `anthropic:messages:claude-sonnet-4-20250514` unless overridden
- grader provider: `anthropic:messages:claude-sonnet-4-20250514` unless overridden

Examples:

Anthropic:

```bash
export ANTHROPIC_API_KEY=sk-...
promptfoo eval
```

OpenAI:

```bash
export PROMPTFOO_BASELINE_PROVIDER='openai:gpt-5-mini'
export PROMPTFOO_WITH_SKILL_PROVIDER='openai:gpt-5-mini'
export PROMPTFOO_GRADER_PROVIDER='openai:gpt-5-mini'
export OPENAI_API_KEY=sk-...
promptfoo eval
```

Google:

```bash
export PROMPTFOO_BASELINE_PROVIDER='google:gemini-2.5-pro'
export PROMPTFOO_WITH_SKILL_PROVIDER='google:gemini-2.5-pro'
export PROMPTFOO_GRADER_PROVIDER='google:gemini-2.5-pro'
export GOOGLE_API_KEY=...
promptfoo eval
```

Run a subset:

```bash
promptfoo eval --filter-pattern "tool-first"
```

## What Gets Evaluated

The suite covers:

1. trigger behavior
2. functional workflow behavior
3. must-pass safety checks
4. output completeness and usefulness
5. freshness and source selection

Workflow coverage:

1. tool-first sends and bridging
2. contract-first sender and receiver generation
3. Chainlink Local simulation and testing
4. monitoring and status workflows
5. route and token discovery
6. CCT workflows

## Files

- `promptfooconfig.yaml`: root Promptfoo configuration
- `cases/`: prompt case files
- `rubrics/`: LLM-as-judge rubric files
- `eval-rubric.md`: human-readable scoring and must-pass reference for reviewers
- `autoresearch-playbook.md`: maintainer improvement loop
- `feedback-log.md`: maintainer failure log used with the playbook
- `usage-runbook.md`: local install and manual test guide

## Reading Results

After `promptfoo eval`, run:

```bash
promptfoo view
```

Use the web viewer to compare:

1. baseline vs with-skill outputs
2. pass/fail assertions
3. rubric scores
4. failure reasons

For the human-readable scoring contract behind the suite, see [eval-rubric.md](eval-rubric.md).

## Cost Estimate

A curated subset of about 30 cases across 2 providers at roughly 10K tokens per case is about `$1.50-$3.00` with Sonnet.

The current full suite is larger than that subset, so expect a higher cost for a full run.

## Manual Testing

For manual A/B testing and local install instructions, see [usage-runbook.md](usage-runbook.md).

## Improvement Loop

For maintainer follow-up after failures:

1. record the issue in `feedback-log.md`
2. follow the small-loop process in [autoresearch-playbook.md](autoresearch-playbook.md)
