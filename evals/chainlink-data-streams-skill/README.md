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
8. Chainlink 24/7 US equities (`rwa-24-7`): lending field, market closed, perp mark price, 24/7 TWAP prediction market, `marketStatus = 0`, and a safety case, scored by the `must-pass-24-7` rubric (per-case hard requirements keyed by `vars.case_id`, all must pass at 100%)
9. positive triggering for weekend/off-hours pricing, and a negative trigger where a plain 24/5 US equities question must get no 24/7-only advice and no `lastTradedPrice` recommendation

10. Chainlink Data Streams Futures on the v14 schema (`rwa-futures`): decode, `marketStatus` (0/1/2), contract roll, staleness, a safety case, two positive triggers (oil/natural gas futures, Goldman Roll fields), and two neighboring-product negatives (a 24/7 perpetual-futures mark price and a v11 equities decode must get no v14 guidance), scored by the `must-pass-futures` rubric (per-case hard requirements keyed by `vars.case_id`; its general rules are scoped so they never fail a correct answer about a neighboring product)

Keep this as smoke coverage until the eval approach is more mature.
