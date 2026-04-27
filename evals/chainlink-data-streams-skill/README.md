# Chainlink Data Streams Skill Evals

Minimal Promptfoo smoke suite for `chainlink-data-streams-skill`.

## Quick Start

```bash
cd evals/chainlink-data-streams-skill
promptfoo eval
promptfoo view
```

Provider defaults can be overridden:

- `PROMPTFOO_BASELINE_PROVIDER`
- `PROMPTFOO_WITH_SKILL_PROVIDER`
- `PROMPTFOO_GRADER_PROVIDER`

## Coverage

This suite is intentionally small:

1. credentials/process explanation
2. REST and WebSocket SDK code generation
3. on-chain verification with safety guardrails
4. positive triggering for report decoding
5. positive triggering for WebSocket High Availability streaming
6. negative triggering for Chainlink Data Feeds
7. negative triggering for CCIP bridging

Keep this as smoke coverage until the eval approach is more mature.
