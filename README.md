# Chainlink Agent Skills

Official Repo for Chainlink skills. Each skill follows the [Agent Skills specification](https://agentskills.io/specification).

## Spec

Skills follow the [Agent Skills format](https://agentskills.io/specification): YAML frontmatter (`name`, `description`) plus markdown instructions.

## Available Skills


| Skill                     | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| [cre-skills](cre-skills/) | CRE onboarding, workflow generation, CLI/SDK help, and runtime operations |


## Install

## [Easiest]

Use [vercel's CLI for the open skills ecosystem](https://github.com/vercel-labs/skills#readme). Project-level installation is the default. 

But if you want to install globally (at the user level) then add the `-g` flag.

Note the use of `--skill` to specify which specific skill to install. 

```
npx skills add https://github.com/smartcontractkit/chainlink-agent-skills --skill cre-skills -g
```

## [Manual] Get the skills

[Download the repo as ZIP](https://github.com/chainlink/chainlink-agent-skills/archive/refs/heads/main.zip) and extract it, or clone with `git clone https://github.com/chainlink/chainlink-agent-skills.git`. Then copy the skill folder(s) you need into your agent's skills directory.

### Add skills to your agent

**Note:** Cursor Composer-1.5 works really well with agent skills. This installation guide is for Cursor Composer, and Claude models. Installation instructions for Codex CLI and Gemini are different. Please look up their official CLI reference to find out how to install agent skills for those models.

**User-level** — Copy into `~/.claude/skills`:

```bash
mkdir -p ~/.claude/skills
cp -a /path/to/chainlink-agent-skills/cre-skills ~/.claude/skills/
```

**Project/ Repo level** — Copy into the project or repo's `.claude/skills`:

```bash
mkdir -p .claude/skills
cp -a ###/path/to/chainlink-agent-skills/cre-skills### .claude/skills/
```

Replace `/path/to/chainlink-agent-skills` with your extracted or cloned repo path.

IDEs that support skills (eg Cursor) will automatically pick skills up when the skill is in `~/.claude/skills`.

## Use

When your agent supports Agent Skills, it will discover and activate these skills based on the task. **However** we recommend that you explicitly invoke the skill in your agent chat sessions as follows:

 `Use the /cre-skills skill and .....[insert detailed prompt]....`

## Best Used With

Cursor Composer-1.5, Claude Opus 4.6, Codex 5.2+, Gemini 3.