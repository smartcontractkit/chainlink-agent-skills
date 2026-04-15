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

## Conventions

- Do not commit `.env` or secret files.
- Reference docs in `references/` should be kept factual and up to date with the latest Chainlink documentation.
- Eval cases go in `evals/<skill-name>/cases/` organized by category (`functional/`, `trigger-positive/`, `trigger-negative/`).
