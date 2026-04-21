# Chainlink Agent Skills - Development Guide

## Project Structure

This is a monorepo of Chainlink agent skills. Each skill lives in its own top-level directory (e.g., `chainlink-ccip-skill/`, `chainlink-cre-skill/`, `chainlink-data-feeds-skill/`).

Each skill directory contains:
- `SKILL.md` - The skill definition with YAML frontmatter (name, description, version) and markdown instructions
- `references/` - Supporting reference docs the skill reads at runtime
- `agents/` (optional) - Platform-specific agent configs (e.g., `openai.yaml`)
- `assets/` (optional) - Supplementary assets like doc indexes

Evals live in `evals/<skill-name>/` with test cases, rubrics, and promptfoo configs.

## Versioning

Each skill tracks its own version in its `SKILL.md` frontmatter under `metadata.version` using semver (e.g., `"0.0.3"`).

**When you modify any file within a skill directory, bump that skill's patch version** (the `0.0.x` component) in its `SKILL.md` frontmatter. Only bump the skill that was actually changed. Do not bump versions for other skills that were not touched.

## Skill Format

Skills follow the [Agent Skills specification](https://agentskills.io/specification). The `SKILL.md` frontmatter must include:
- `name` - Skill identifier (matches directory name)
- `description` - Trigger description used by agents to decide when to activate the skill
- `license`
- `compatibility`
- `allowed-tools`
- `metadata.version` - Semver string

## Running Evals

Each skill has an eval suite in `evals/<skill-name>/` containing test cases, grading rubrics, and a promptfoo config. Evals are organized into tiers:

| Tier | Cases | Method | When to use |
|------|-------|--------|-------------|
| Smoke | ~20 | Agent-powered or promptfoo | Quick feedback during development, PR CI gate |
| Full | All 95 | Promptfoo | Before releases, after major refactors, scheduled CI |

Cases included in the smoke tier are tagged with `smoke: true` in their `metadata` block in the promptfoo configs.

### Agent-powered (no API keys needed)

Read and follow the protocol in `evals/run-agent-eval.md`. This runs generation and grading entirely through Cursor subagents. Smoke tier is the default:

```
Run agent evals for chainlink-ccip-skill
Run agent evals for chainlink-ccip-skill, full suite
Run agent evals for chainlink-data-feeds-skill, functional cases only
```

### With API keys (promptfoo)

If `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are set in `.env`:

```
source .env
cd evals/<skill-name>
npx promptfoo eval --filter-metadata "smoke=true"   # smoke tier
npx promptfoo eval                                    # full suite
npx promptfoo view
```

### CI (GitHub Actions)

The `eval.yml` workflow runs the smoke tier automatically on PRs that touch skill or eval files. It uses `CI_ANTHROPIC_API_KEY` and `CI_OPENAI_API_KEY` secrets (separate from dev keys to avoid contention). Full suite can be triggered manually via workflow dispatch.

### When to run evals

- **Smoke**: After any change to a skill's `SKILL.md` or `references/`, before bumping patch version, when adding new eval cases
- **Full**: Before releases, after major refactors, or when smoke passes but you want full confidence

## Conventions

- Do not commit `.env` or secret files.
- Reference docs in `references/` should be kept factual and up to date with the latest Chainlink documentation.
- Eval cases go in `evals/<skill-name>/cases/` organized by category (`functional/`, `trigger-positive/`, `trigger-negative/`).
