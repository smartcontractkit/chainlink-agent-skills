# Chainlink Confidential AI — Prompt Templates

Prompts need two layers:

1. **System prompt** — domain role
2. **User prompt** — fact-extraction task + exact JSON schema

---

## Undercollateralized DeFi Lending

**Default system prompt (use for every template):**
```
You are a helpful assistant. When documents are provided, base your answers on their content. If the documents do not contain enough information to answer, say so.
```

**User prompt:**
```
Extract repayment-relevant facts from the supplied documents for a human reviewer.
Do not approve or deny the loan, score eligibility, or invent thresholds.
Use only provided evidence; represent unknowns as null.

Respond with ONLY a valid JSON object:
{
  "estimated_monthly_income_usd": 0,
  "estimated_monthly_obligations_usd": 0,
  "liquid_buffer_usd": 0,
  "risk_flags": [],
  "missing_information": [],
  "review_required": true
}
```

---

## Accredited Investor (SEC Rule 501)

**User prompt:**
```
Extract facts relevant to SEC Rule 501 for review by a qualified human.
Do not decide qualification or give legal advice. Use only provided evidence.

Respond with ONLY a valid JSON object:
{
  "evidence": ["specific document fact"],
  "key_figure_usd": 0,
  "missing_information": [],
  "review_required": true
}
```

---

## KYC/AML Check

**User prompt:**
```
Extract identity and transaction facts for human review.
Do not decide pass/fail or sanctions status; flag potential matches for verification.

Respond with ONLY a valid JSON object:
{
  "identity_evidence": [],
  "transaction_flags": [],
  "potential_sanctions_matches": [],
  "review_required": true
}
```

---

## Proof of Reserves

**User prompt:**
```
Do the provided financial documents substantiate the claimed reserves of $[AMOUNT]?
Assess based on available evidence only.

Respond with ONLY a valid JSON object:
{
  "verified": true,
  "confidence": "high|medium|low",
  "reason": "one sentence",
  "documented_reserves_usd": 0
}
```

---

## Handling LLM Refusals

If the model returns prose like "I cannot determine this without more information", the prompt is too open-ended. Add this line immediately before the JSON schema:

```
Assess based on available evidence only — do not refuse due to missing documents.
Make your best determination from what is provided and reflect uncertainty in the confidence field.
```

If the output is wrapped in markdown fences (` ```json ... ``` `), add:

```
Do not include markdown formatting, code fences, or any text outside the JSON object.
```
