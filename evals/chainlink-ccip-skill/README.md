# Chainlink CCIP Skill Evals

This directory contains the committed eval harness for `chainlink-ccip-skill`.

The shipped skill lives in `chainlink-ccip-skill/`.

This directory is for:

1. trigger checks
2. functional checks
3. scoring and comparison
4. teammate-friendly A/B testing

## Files

- `trigger-tests.md`: positive and negative trigger cases
- `functional-tests.md`: behavior checks by workflow
- `eval-rubric.md`: shared scoring rubric and must-pass conditions
- `ab-prompts.md`: reusable prompts for with-skill vs without-skill comparisons
- `results-template.md`: markdown template for logging outcomes

## Suggested Workflow

1. Run the selected prompt without the skill.
2. Run the same prompt with the skill installed.
3. Score both runs with `eval-rubric.md`.
4. Record the comparison in `results-template.md`.
5. If the skill underperforms, capture the failure mode before editing the skill.

## Coverage Areas

The eval harness currently covers:

1. tool-first sends and bridging
2. contract-first sender and receiver generation
3. Chainlink Local simulation and testing
4. monitoring and status workflows
5. route and token discovery
6. CCT workflows
