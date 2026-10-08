# Skill routing

This suite picks a skill from `name` and `description` only. It does not load a `SKILL.md` body.

The case table in tracking issue 57 lists ten ids. The VRF price-feed rejection is the `reject` list on `feeds-latest-round`. The issue text also says "eleven rows". There is no eleventh prompt in that table.

`ace-on-ccip-pool` passes only when both names are present.

## File check

No model key is required. CI does not run this suite.

```sh
python3 -m venv /tmp/skills-ref-venv
/tmp/skills-ref-venv/bin/pip install "skills-ref @ git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref"
PATH="/tmp/skills-ref-venv/bin:$PATH" python3 evals/skill-routing/check.py self-test
```

`self-test` builds the prompt with `skills-ref to-prompt` on all nine `chainlink-*-skill` directories. It fails when that prompt contains a skill heading or a body line. It accepts a fixture that names the expected skill. It rejects a fixture that names the wrong skill. One ACE fixture names only one of the two expected skills, and that fixture must fail.

## One model reply

```sh
PATH="/tmp/skills-ref-venv/bin:$PATH" python3 evals/skill-routing/check.py prompt > /tmp/routing-prompt.xml
```

Give the model that file and one `prompt` from `cases.yaml`. Ask it to reply with skill directory names only. Then grade the reply:

```sh
PATH="/tmp/skills-ref-venv/bin:$PATH" python3 evals/skill-routing/check.py grade --case cre-enclave-no-document --reply-file reply.txt
```

These rows are not part of the per-skill promptfoo suites. When no model key is set, use the agent path in `evals/README.md`.
