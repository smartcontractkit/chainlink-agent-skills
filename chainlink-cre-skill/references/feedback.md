# Feedback Loop: Filing Agent Issues Against This Repo

This reference governs how the CRE skill captures gaps in itself and routes them
back to `smartcontractkit/chainlink-agent-skills` as GitHub issues. Read this
file only when a trigger signal has fired (see below). Do not load it
speculatively.

The goal is a tight feedback loop: when the skill is wrong or incomplete, the
agent offers — once, with a fully drafted issue — to file a bug so the skill
can be improved. Confirmation is always required before filing.

## When to consider offering to file

Offer to file only when at least one of the signals below has clearly fired in
the current session. Be conservative — false positives are noise, and once you
have offered to file in a session, do not offer again.

### Signal A — Content gap (agent-detected)

- You read one or more CRE references and they did not contain the information
  needed to answer the user's request, so you had to `WebFetch` an official
  source or fall back to general knowledge.
- The user supplied or asked about a CRE CLI flag, SDK symbol, capability
  name, trigger type, chain selector, or forwarder address that is not
  mentioned in any reference under `chainlink-cre-skill/references/`.
- A reference disagrees with an authoritative live source (for example, a
  flag exists in `cre --help` output but is missing from
  `references/cli-reference.md`).
- You ran a CRE CLI command and it failed in a way the references do not
  describe.

### Signal B — User pain (user-voiced)

- The user explicitly tells you the skill got something wrong, e.g. "this
  didn't work", "the skill should know X", "you missed Y", "that flag doesn't
  exist anymore".
- The user manually corrects you on something the skill is responsible for
  (a CRE pattern, command, type, or capability) — not on adjacent territory
  like generic Solidity or frontend code.
- The user says they want this captured for the maintainers
  ("file an issue about this", "let's leave a note for the skill author").

## When NOT to offer

- The user asked a straightforward question and the skill answered it
  correctly. No offer.
- The gap is in upstream Chainlink (broken docs, broken SDK behavior, a bug
  in `cre` itself). That is not a skill bug; do not file it here. You may
  still mention it to the user.
- The user has already declined an offer this session.
- You have already filed (or offered to file) one issue this session.
- The user is mid-task and an offer would interrupt flow. Wait until the
  current task is complete, then offer at a natural pause.
- The signal is weak or speculative ("the skill probably could be clearer
  somewhere"). Wait for a concrete trigger.

## How to offer

Keep the offer short. Show a complete draft so the user can approve or edit
in one step. Use this shape, verbatim where reasonable:

```
I noticed the CRE skill <one-sentence problem>. Want me to file an issue
against smartcontractkit/chainlink-agent-skills so this gets fixed?

  Repo:   smartcontractkit/chainlink-agent-skills
  Title:  [CRE] <concise summary, <= 70 chars>
  Labels: agent-feedback, skill:cre, kind:gap   # or kind:pain
  Body:
    Skill: chainlink-cre-skill @ <version from SKILL.md frontmatter>
    Signal type: content-gap            # or user-pain
    Summary: <1–2 sentences>
    What the user asked for: <paraphrase, secrets redacted>
    What the skill said or did: <agent's actual behavior>
    What the skill should have said: <correct behavior, cite source if possible>
    Suggested fix: <where in references/ this lands, sketch the change>
    Reproduction: <minimal prompt that triggers the gap>
    Authoritative source: <URL if applicable>
    Session context: <short excerpt, redacted>
    Agent metadata: <model / surface, e.g. "Claude Code, Opus 4.7">

Reply "file it" to submit, "edit" to revise, or "skip" to discard.
```

Pick exactly one of `kind:gap` (missing or stale reference content) or
`kind:pain` (user-voiced complaint where the skill produced a bad outcome).
Always include `agent-feedback` and `skill:cre`.

## Drafting rules

- **Title**: prefix with `[CRE]`, keep under 70 characters, describe the
  thing missing, not the symptom. Good: `[CRE] cli-reference.md missing
  --target alias for cre workflow simulate`. Bad: `[CRE] something is wrong`.
- **Suggested fix**: be concrete about the destination file and the rough
  change. The maintainer should be able to act without re-deriving the
  problem.
- **Authoritative source**: include a URL only if you actually consulted
  it during the session. Do not invent citations.
- **Reproduction**: a single line is enough if the issue is obvious from
  the prompt. Do not paste long transcripts unless they are load-bearing.
- **Version**: read the `metadata.version` field from
  `chainlink-cre-skill/SKILL.md`. Do not guess.

## Redaction (mandatory before showing the draft)

Before showing the draft to the user, strip the following from every field:

- Private keys, mnemonics, seed phrases.
- Bearer tokens, API keys, webhook URLs containing secrets.
- Long hex strings (`0x[a-fA-F0-9]{40,}`) when they appear in contexts that
  suggest a private key or signed payload; replace with `<redacted>`.
- File paths that include a user's home directory (`/Users/<name>/...` →
  `~/...`).
- Any value the user has explicitly marked as confidential.

If you are unsure whether a field contains a secret, redact it and note
`<redacted; see local logs>`.

## Duplicate check

Before filing (after the user says "file it"), run a quick search to avoid
piling on:

```bash
gh issue list \
  --repo smartcontractkit/chainlink-agent-skills \
  --state open \
  --label agent-feedback \
  --search "<3–5 word fragment from your title>"
```

If a clear match appears, show the existing issue URL to the user and ask
whether they want to add a comment to it instead of opening a new one.

## Filing the issue

Prefer the local `gh` CLI. If it is not available or not authenticated,
fall back to a prefilled URL.

### Path 1 — `gh` available

First verify `gh` is set up:

```bash
gh auth status
```

Then file:

```bash
gh issue create \
  --repo smartcontractkit/chainlink-agent-skills \
  --title "[CRE] <title>" \
  --label agent-feedback \
  --label skill:cre \
  --label kind:gap \
  --body-file <(cat <<'EOF'
<body, exactly as shown in the approved draft>
EOF
)
```

Use `kind:pain` instead of `kind:gap` when the signal was user-voiced.
Do not pass `--assignee`; agent-filed issues are routed by label, not
person.

After filing, print the issue URL returned by `gh` to the user.

### Path 2 — `gh` unavailable, missing, or unauthenticated

If `gh auth status` exits non-zero, fall back to a prefilled GitHub URL
the user can open in a browser:

1. URL-encode the title and body. (In bash:
   `printf %s "$TITLE" | jq -sRr @uri`.)
2. Build the URL:

   ```
   https://github.com/smartcontractkit/chainlink-agent-skills/issues/new?template=agent-feedback.md&title=<encoded title>&labels=agent-feedback,skill:cre,kind:gap&body=<encoded body>
   ```

3. Print the URL and tell the user it will open the issue form with all
   fields pre-filled — they just need to click "Submit new issue".

Do not silently drop the feedback. Either `gh` succeeds, or the user gets
the URL.

## After filing

- Print the issue URL.
- Do not offer to file again in this session, even if a different signal
  fires later. One per session.
- Continue with the user's original task. Do not over-celebrate or write
  a postmortem.
