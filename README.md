# Chainlink Agent Skills

Official Repo for Chainlink skills. Each skill follows the [Agent Skills specification](https://agentskills.io/specification).

## Spec

Skills follow the [Agent Skills format](https://agentskills.io/specification): YAML frontmatter (`name`, `description`) plus markdown instructions.

## Available Skills

| Skill                     | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| [cre-skills](cre-skills/) | CRE onboarding, workflow generation, CLI/SDK help, and runtime operations |

## Install

### Get the skills

[Download the repo as ZIP](https://github.com/chainlink/chainlink-agent-skills/archive/refs/heads/main.zip) and extract it, or clone with `git clone https://github.com/chainlink/chainlink-agent-skills.git`. Then copy the skill folder(s) you need into your agent's skills directory.

### Add skills to your agent

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

` Use the /cre-skills skill and .....[insert detailed prompt]....`
