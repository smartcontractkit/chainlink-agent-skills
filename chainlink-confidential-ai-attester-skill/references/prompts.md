# Chainlink Confidential AI — Prompt Templates

Two layers of enforcement are always required:

1. **System prompt** — domain role
2. **User prompt** — binary question + exact JSON schema

---

## Undercollateralized DeFi Lending

**System prompt:**
```
You are a helpful assistant. When documents are provided, base your answers on their content. If the documents do not contain enough information to answer, say so.
```

**User prompt:**
```
Based on the financial documents provided, is this individual suitable for an
undercollateralized DeFi loan of [AMOUNT] USDC?

- Sum all credit transactions to estimate monthly income
- Sum all debit transactions to estimate monthly obligations
- Note total liquid assets as a repayment buffer
- Assess based on available evidence only — do not refuse due to missing documents

Respond with ONLY a valid JSON object:
{
  "approved": true,
  "confidence": "high|medium|low",
  "reason": "one sentence citing specific figures",
  "estimated_monthly_income_usd": 0,
  "estimated_monthly_obligations_usd": 0,
  "liquid_buffer_usd": 0,
  "risk_level": "low|medium|high"
}
```

---

## Accredited Investor (SEC Rule 501)

**System prompt:**
```
You are a helpful assistant. When documents are provided, base your answers on their content. If the documents do not contain enough information to answer, say so.
```

**User prompt:**
```
Based solely on the provided financial documents, does this individual qualify as
an accredited investor under SEC Rule 501?
Assess based on available evidence only — do not refuse due to missing documents.

Respond with ONLY a valid JSON object:
{
  "qualified": true,
  "confidence": "high|medium|low",
  "reason": "one sentence",
  "key_figure_usd": 0
}
```

---

## KYC/AML Check

**System prompt:**
```
You are a helpful assistant. When documents are provided, base your answers on their content. If the documents do not contain enough information to answer, say so.
```

**User prompt:**
```
Based on the provided documents, does this individual pass a basic KYC/AML check?
Look for identity verification, suspicious transaction patterns, and sanctions indicators.
Assess based on available evidence only.

Respond with ONLY a valid JSON object:
{
  "pass": true,
  "confidence": "high|medium|low",
  "reason": "one sentence",
  "flags": []
}
```

`flags` is an array of strings — include specific concerns (e.g. `"large unexplained cash deposits"`). Empty if none.

---

## Proof of Reserves

**System prompt:**
```
You are a helpful assistant. When documents are provided, base your answers on their content. If the documents do not contain enough information to answer, say so.
```

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
