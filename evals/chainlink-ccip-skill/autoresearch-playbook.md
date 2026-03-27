# Autoresearch Playbook

Use this playbook to improve `chainlink-ccip-skill` in small, reviewable loops.

This is a maintainer workflow. The shipped skill must not self-modify.

## Goal

Turn raw feedback into small, testable improvements without making multiple unrelated edits at once.

## Loop

1. Capture the issue in `feedback-log.md`.
2. Classify the failure:
   - trigger problem
   - routing problem
   - safety problem
   - freshness problem
   - domain problem
   - usability problem
3. Identify the smallest likely fix.
4. Change only the files needed for that fix.
5. Rerun only the relevant eval prompts first.
6. If the fix passes the targeted evals, keep it.
7. If the fix regresses behavior or fails to improve the target case, revert or revise it.
8. Record the result back in `feedback-log.md`.

## Rules

1. One issue at a time.
2. One plausible fix at a time.
3. Do not bundle unrelated cleanup into the same loop.
4. Prefer edits to existing references before adding new files.
5. If the issue is about routing or trigger boundaries, rerun both positive and negative trigger tests.
6. If the issue is about safety, rerun the relevant must-pass eval checks before anything else.
7. If the issue depends on current CCIP facts, verify against official sources before changing the skill.

## Suggested Decision Path

### Trigger or routing problems

1. Check `trigger-tests.md`.
2. Check whether the wrong reference file is too broad.
3. Tighten the owning reference before adding new routing text in `SKILL.md`.

### Safety problems

1. Check `eval-rubric.md` must-pass failures first.
2. Fix the guardrail where the unsafe suggestion originated.
3. Rerun the specific prompt pair and at least one nearby negative case.

### Freshness problems

1. Check `official-sources.md`.
2. Confirm whether the wrong source was used or whether the question should have triggered a live check.
3. Fix source selection before touching domain instructions.

### Domain problems

1. Check the owning workflow reference.
2. Confirm whether the docs or interfaces support the requested behavior.
3. Patch the narrowest reference file that owns the behavior.

## Minimal Evidence To Keep A Change

Keep a change only if:

1. the target prompt improves
2. must-pass checks still pass
3. nearby negative cases do not regress

## Good Commit Shape

Prefer commit messages like:

- `fix: tighten monitoring vs discovery routing`
- `fix: require second confirmation before testnet send`
- `fix: prefer CCIP Directory over simulator defaults in fork tests`

Avoid commit messages that hide multiple behavioral changes in one patch.
