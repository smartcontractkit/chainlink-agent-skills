# Chainlink VRF Skill Evals

Evaluation suite for `chainlink-vrf-skill`. 10 cases total; 9 are smoke-tagged and run in CI.

## Running Evals

### Agent-powered (no API keys needed)

Follow the protocol in [evals/run-agent-eval.md](../run-agent-eval.md):

```
Run agent evals for chainlink-vrf-skill
```

### With API keys (promptfoo)

```bash
source ../../.env
npx promptfoo eval --filter-metadata "smoke=true"   # smoke tier (9 cases)
npx promptfoo eval                                    # full suite (10 cases)
npx promptfoo view
```

## Case Summary

| Case | Type | What it validates |
|---|---|---|
| `functional/subscription-01.txt` | functional | v2.5 subscription consumer on Sepolia, native payment |
| `functional/subscription-02.txt` | functional | Add LINK-paid path to existing subscription consumer |
| `functional/direct-funding-01.txt` | functional | Direct funding consumer on Arbitrum, native payment |
| `functional/migration-01.txt` | functional | V2 → v2.5 migration, all breaking changes applied |
| `functional/starter-kit-01.txt` | functional | Scaffolds the v2.5 Foundry starter-kit project (build + test locally) |
| `functional/starter-kit-02.txt` | functional | Scaffolds the starter kit for Sepolia with deploy script and tests |
| `trigger-positive/subscription-01.txt` | trigger+ | Generic randomness question triggers VRF skill |
| `trigger-positive/legacy-trap-01.txt` | trigger+ | V2 code triggers skill + migration warning |
| `trigger-positive/starter-kit-01.txt` | trigger+ | Runnable Foundry project request triggers VRF skill |
| `trigger-negative/data-feeds-01.txt` | trigger- | Price feed question does NOT trigger VRF skill |

## Key Assertions (must-pass.txt)

The must-pass rubric fails if any response:
- Uses V1/V2 base contracts instead of the correct v2.5 base for the workflow
- Uses positional subscription `requestRandomWords` instead of the struct
- Omits `extraArgs` from subscription or direct-funding requests
- Uses `uint64` subscription IDs
- Uses `VRFV2WrapperConsumerBase` (V2)
- Uses the wrong `fulfillRandomWords` data location (`calldata` for subscription consumers, `memory` for direct-funding wrapper consumers)
- Invents coordinator/wrapper/LINK addresses
- Recommends `block.*` as a randomness fallback
