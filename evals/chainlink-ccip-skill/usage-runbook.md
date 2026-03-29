# Usage Runbook

Use this runbook to install, validate, smoke-test, and locally experiment with `chainlink-ccip-skill`.

## Local Install From This Repository

From the repository root:

```bash
npx skills add . --list
npx skills add . --skill chainlink-ccip-skill -a <agent> -y
```

Examples:

```bash
npx skills add . --skill chainlink-ccip-skill -a claude-code -y
npx skills add . --skill chainlink-ccip-skill -a codex -y
npx skills add . --skill chainlink-ccip-skill -a cursor -y
```

## Local Install From Another Workspace

Use a path to this repository:

```bash
npx skills add /absolute/path/to/chainlink-agent-skills --skill chainlink-ccip-skill -a <agent> -y
```

## GitHub Install

```bash
npx skills add https://github.com/smartcontractkit/chainlink-agent-skills --skill chainlink-ccip-skill -a <agent> -y
```

## Validation Checks

Use these before testing:

```bash
npx skills add . --list
npx skills list -a <agent>
```

Check that:

1. `chainlink-ccip-skill` appears in `--list`
2. the target agent shows the skill as installed
3. you start each test in a fresh session

## Smoke Test

Pick prompts from `ab-prompts.md` and score the results with `eval-rubric.md`.

Recommended first smoke tests:

1. tool-first send or bridge
2. contract-first generation
3. monitoring or discovery

Use fresh sessions for each prompt.

## Cleanup

Remove the installed skill when needed:

```bash
npx skills remove chainlink-ccip-skill -a <agent> -y
```

## Private Local `feedback.log` Variant

This is for your own testing only. Do not commit it.

1. Make a local-only change to the skill instructions so your agent reads a `feedback.log` file before starting work.
2. Create a local-only `feedback.log` inside `chainlink-ccip-skill/`.
3. Install the skill locally from `.` so the installed version picks up your local edits.
4. Use fresh sessions while testing.
5. After each correction or stable preference, append only reusable preferences to `feedback.log`.
6. When you are done testing, remove or discard those local-only changes before opening the PR.

Recommended reusable feedback entries:

1. routing preference
2. tone or brevity preference
3. guardrail preference
4. preferred framework bias
5. documentation or citation preference

Do not log task-specific facts that will not generalize to future sessions.

## Automated Evals

For automated evaluation using Promptfoo, see the main [README.md](README.md) in this directory.
