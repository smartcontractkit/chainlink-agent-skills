---
name: "Agent feedback (auto-filed)"
about: "Structured feedback filed by an agent using a skill in this repo. Humans can use this too."
title: "[<skill>] <one-line summary>"
labels: agent-feedback
assignees: ''

---

<!--
This template is intended for issues filed by an AI agent that detected a
content gap in one of the skills in this repo, or that surfaced explicit
user pain about a skill. Humans filing the same kind of structured
feedback are also welcome to use it.

The agent should fill every section. Sections marked OPTIONAL may be
omitted only when genuinely not applicable.
-->

**Skill**
<!-- e.g. chainlink-cre-skill @ 0.0.9 -->

**Signal type**
<!-- one of: content-gap | user-pain -->

**Summary**
<!-- one or two sentences -->

**What the user asked for**
<!-- paraphrase the user's actual request; redact any secrets/private values -->

**What the skill said or did**
<!-- the agent's behavior that prompted this issue: missing info, wrong answer, missing flag, contradiction with live source, etc. -->

**What the skill should have said**
<!-- correct/expected behavior, with reference to an authoritative source if available -->

**Suggested fix**
<!-- where in references/ or SKILL.md this should land, plus a sketch of the change. "Add `--new-flag` row to references/cli-reference.md under `cre workflow simulate`." -->

**Reproduction (OPTIONAL)**
<!-- exact user prompt or minimal repro, with secrets redacted -->

**Authoritative source (OPTIONAL)**
<!-- URL or doc location backing the suggested fix -->

**Session context (OPTIONAL)**
<!-- short transcript excerpt, secrets redacted; omit if not informative -->

**Agent metadata**
<!-- model / tool surface, e.g. "Claude Code, Opus 4.7" -->
