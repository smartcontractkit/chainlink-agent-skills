# Autonomous Skill Improvement Protocol

This runbook drives an autonomous improvement loop for a skill. An agent modifies the skill's instructions and references, runs evals, keeps improvements, reverts regressions, and loops indefinitely until stopped. Inspired by [karpathy/autoresearch](https://github.com/karpathy/autoresearch).

## Quick Start

Ask the agent:

```
Improve chainlink-ccip-skill
Improve chainlink-data-feeds-skill, tag apr21
```

## Setup

When asked to improve a skill, follow these steps to initialize.

### Step 1: Agree on inputs

- **skill**: The skill directory name (e.g., `chainlink-ccip-skill`).
- **run tag**: A short identifier for this improvement run (e.g., `apr21`). Propose one based on today's date if the user doesn't provide one. The branch `autoimprove/<skill>/<tag>` must not already exist.

### Step 2: Create the branch

```
git checkout -b autoimprove/<skill>/<tag>
```

### Step 3: Read in-scope files

Read these files for full context:

- `<skill>/SKILL.md` (the skill instructions you will be modifying)
- All files in `<skill>/references/` (reference docs you may modify)
- All smoke-tagged eval cases in `evals/<skill>/cases/` (read the promptfoo config to identify which are smoke)
- All rubric files in `evals/<skill>/rubrics/`

### Step 4: Detect eval method

Check whether API keys are available:

```
echo "${ANTHROPIC_API_KEY:+set}" "${OPENAI_API_KEY:+set}"
```

- If both print `set`: use **promptfoo** for evals (faster, ~2-3 min per iteration).
- Otherwise: use **agent-powered** smoke evals via `evals/run-agent-eval.md` (slower, ~5-8 min per iteration).

### Step 5: Run baseline eval

Run the smoke eval to establish starting scores.

**Promptfoo path:**
```
cd evals/<skill>
npx promptfoo eval --filter-metadata "smoke=true" --no-cache > run.log 2>&1
npx promptfoo export -o results.json
```

Then extract the composite score (see Composite Metric below).

**Agent path:**
Follow `evals/run-agent-eval.md` for the skill, smoke tier. Record the pass rate from the summary table.

### Step 6: Initialize results.tsv

Create `results.tsv` (tab-separated) in the repo root with the header and baseline row:

```
commit	score	pass_rate	status	description
a1b2c3d	0.850	17/20	keep	baseline
```

Do NOT commit this file. Keep it untracked by git.

### Step 7: Confirm and go

Tell the user: the branch name, detected eval method, baseline score, and number of smoke cases. Then begin the experiment loop immediately.

## Composite Metric

Skill evals produce multiple rubric scores across multiple cases. The composite metric reduces these to a single number for comparison:

**composite score** = (number of fully-passing cases) / (total smoke cases)

A case "fully passes" when every applicable rubric scores at or above its pass threshold.

**Extracting the score (promptfoo path):**
```
jq '{pass: .results.stats.successes, total: (.results.stats.successes + .results.stats.failures), score: (.results.stats.successes / (.results.stats.successes + .results.stats.failures))}' results.json
```

**Comparison rules:**
- Higher composite score = better. Keep the change.
- Equal composite score: keep only if at least one individual rubric improved and none regressed (Pareto improvement). Otherwise discard.
- Lower composite score or any rubric regression = worse. Revert.

**Simplicity criterion:** All else equal, simpler is better. If a change removes text from SKILL.md or references without lowering the composite score, that is a keep.

## Scope Rules

**You CAN modify:**
- `<skill>/SKILL.md` (instructions, routing logic, progressive disclosure, examples)
- `<skill>/references/*.md` (reference doc content, corrections, examples, completeness)

**You CANNOT modify:**
- `evals/<skill>/` (cases, rubrics, promptfoo config are the fixed evaluation harness)
- Other skills' directories
- Any file outside the skill directory
- `results.tsv` format (only append rows)

## The Experiment Loop

Once setup is complete, run this loop. **Do not stop or ask the user for confirmation between iterations.** The user may be away from the computer. Continue until manually interrupted.

### LOOP FOREVER:

**1. Review state.** Read `results.tsv` to see recent experiments. Look at the current git diff and the last few results. Identify patterns: which rubrics are failing, which cases, what has been tried.

**2. Propose a change.** Pick one focused idea (see Idea Generation below). One change per iteration. Do not batch unrelated modifications.

**3. Apply the change.** Edit `<skill>/SKILL.md` or files in `<skill>/references/`.

**4. Commit.**
```
git add <skill>/
git commit -m "<short description of change>"
```

**5. Run smoke eval.**

Promptfoo path:
```
cd evals/<skill>
npx promptfoo eval --filter-metadata "smoke=true" --no-cache > run.log 2>&1
npx promptfoo export -o results.json
```

Agent path: follow `evals/run-agent-eval.md`, smoke tier.

**6. Extract the composite score.** Parse the eval output to get the pass rate and composite score.

**7. Compare to the previous best.**

- **Improved**: Keep the commit. Record `keep` in results.tsv.
- **Equal (Pareto improvement)**: Keep the commit. Record `keep` in results.tsv.
- **Equal (no Pareto improvement) or worse**: Revert. Run `git reset --hard HEAD~1`. Record `discard` in results.tsv.
- **Eval crashed**: Run `tail -50 run.log` to diagnose. If it is a simple fix (typo, syntax), fix and re-run. If the idea is fundamentally broken, revert and record `crash` in results.tsv.

**8. Log the result.** Append a row to `results.tsv`:
```
<commit>	<score>	<pass>/<total>	<status>	<description>
```

Use commit hash `0000000` and score `0.000` for crashes. Use the reverted-to commit hash for discards.

**9. Go to step 1.**

### Timeout

Each eval iteration should complete in under 10 minutes. If a promptfoo run exceeds 10 minutes, kill it (use the PID from the background process) and treat it as a crash.

### Getting stuck

If three consecutive experiments are discarded with no improvement, shift strategy:
- Re-read all failing cases and their grader reasons carefully
- Try a more radical approach (restructure a section rather than tweak wording)
- Try a simplification pass (remove instructions and see if scores hold)
- Look at the rubric definitions again for hints about what "good" looks like

If five consecutive experiments are discarded, try reverting to an earlier successful commit and exploring a different direction.

## Idea Generation

Strategies to try, ordered from safest to most ambitious:

### Tier 1: Fix specific failures
Read the grader's reason for each failing case. Identify the exact gap in SKILL.md or references that caused the failure. Patch it directly.

### Tier 2: Clarify routing logic
If correctness failures show the wrong workflow being selected, sharpen the decision criteria in SKILL.md. Add distinguishing signals, reorder routing rules, or add disambiguation examples.

### Tier 3: Improve reference accuracy
Cross-check reference docs against the rubric expectations. Fix stale content, add missing examples, fill in incomplete sections that eval cases depend on.

### Tier 4: Strengthen safety guardrails
If safety or must-pass rubrics fail, add explicit warnings, refusal patterns, or approval-first language for dangerous operations.

### Tier 5: Simplify
Remove unnecessary instructions, collapse redundant sections, eliminate hedging language. If the score holds after removal, the skill is better (simpler = more robust).

### Tier 6: Restructure
Reorganize major sections of SKILL.md for clarity. Change the progressive disclosure order. Rewrite routing tables. This is high-risk/high-reward.

## Important Rules

- **Never stop.** Once the loop begins, do not pause to ask the human anything. Continue indefinitely until manually interrupted. The human might be asleep.
- **Never modify evals.** Cases and rubrics are ground truth. Changing them to improve scores defeats the purpose.
- **One change per iteration.** Multiple changes make it impossible to attribute improvement. Keep commits atomic.
- **Log everything.** Every experiment gets a results.tsv row, including crashes and discards.
- **Simplicity wins.** A change that removes 20 lines and maintains the score is better than a change that adds 20 lines for +0.05.
- **Do not bump versions.** The version bump happens when the human reviews and merges the branch, not during the improvement loop.
