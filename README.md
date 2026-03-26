# Chainlink Agent Skills

Official Repo for Chainlink skills. Each skill follows the [Agent Skills specification](https://agentskills.io/specification).

## Spec

Skills follow the [Agent Skills format](https://agentskills.io/specification): YAML frontmatter (`name`, `description`) plus markdown instructions.

## Available Skills


| Skill                     | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| [cre-skills](cre-skills/) | CRE onboarding, workflow generation, CLI/SDK help, and runtime operations |


## Install Using Vercel's Skills Installer

Use [vercel's CLI for the open skills ecosystem](https://github.com/vercel-labs/skills#readme). Project-level installation is the default. 

But if you want to install globally (at the user level) then add the `-g` flag.

Note the use of `--skill` to specify which specific skill to install. 

```
npx skills add https://github.com/smartcontractkit/chainlink-agent-skills --skill cre-skills -g
```

## Use

When your agent supports Agent Skills, it will discover and activate these skills based on the task. **However** we recommend that you explicitly invoke the skill in your agent chat sessions as follows:

 `Use the /cre-skills skill and .....[insert detailed prompt]....`

## Best Used With

Cursor Composer-1.5, Claude Opus 4.6, Codex 5.2+, Gemini 3.
