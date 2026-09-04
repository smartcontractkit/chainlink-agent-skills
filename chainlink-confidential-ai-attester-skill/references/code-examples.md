# Chainlink Confidential AI Attester — Code Examples

## curl: submit + poll

```bash
export BASE_URL="https://confidential-ai-dev-preview.cldev.cloud"
# `API_KEY` must already be supplied by the environment or an injected secret store.
: "${API_KEY:?API_KEY is required}"
auth_header() { printf 'Authorization: Bearer %s\n' "$API_KEY"; }

# Base64-encode your document
PDF_B64=$(base64 -i ./statement.pdf)

# Submit (success: 202 Accepted with {"id":"...","status":"queued"})
SUBMIT_RESPONSE=$(auth_header | curl -sS -X POST "$BASE_URL/v1/inference" \
  -H @- \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"gemma4\",
    \"system_prompt\": \"You are a helpful assistant. When documents are provided, base your answers on their content. If the documents do not contain enough information to answer, say so.\",
    \"prompt\": \"Extract monthly income, obligations, liquid assets, and risk flags for human review. Do not approve or deny the loan. Return ONLY JSON: {\\\"estimated_monthly_income_usd\\\": 0, \\\"estimated_monthly_obligations_usd\\\": 0, \\\"liquid_buffer_usd\\\": 0, \\\"risk_flags\\\": [], \\\"review_required\\\": true}\",
    \"resources\": [{
      \"filename\": \"statement.pdf\",
      \"content_type\": \"application/pdf\",
      \"content_base64\": \"$PDF_B64\"
    }]
  }")
echo "$SUBMIT_RESPONSE" | jq '{id, status}'
REQUEST_ID=$(echo "$SUBMIT_RESPONSE" | jq -r '.id')

# Poll until done
while true; do
  RESULT=$(auth_header | curl -sS "$BASE_URL/v1/inference/$REQUEST_ID" \
    -H @-)
  STATUS=$(echo "$RESULT" | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then break; fi
  sleep 3
done

echo "$RESULT" | jq '{status, output, error}'
```

The authorization header is piped to curl over standard input, so the expanded API key is never placed in curl's command-line arguments.

The same two HTTP calls—POST to submit and GET to poll—work from any language. Require the service URL through `BASE_URL` (or an equivalent environment variable), emit the complete request fields and `202` `{id,status}` shape, save the `id`, poll until `completed` or `failed`, and retrieve `output` or `error`; provide runnable code, not a completion summary.

## CRE callback to EVM

Set `cre_callback` to the live callback route for the CRE workflow. The callback remains a single best-effort POST with no retries, so return 2xx within 10 seconds and keep any tunnel running until the request reaches a terminal state.

In the workflow:

1. Require `status` to be `completed`.
2. Parse `output` and validate its required JSON schema. Treat prose, fenced JSON, malformed JSON, and `failed` status as failure; create no report or downstream action.
3. Encode the accepted result with the workflow's expected schema and use CRE-native report creation.
4. Deliver that report to EVM through the Chainlink Forwarder.

Do not use a wallet private key or generic EIP-712 signer for this route. The Attester response has no independently verifiable Chainlink or TEE signature, and hashing it produces neither one nor enclave proof. A CRE report provides the CRE-native delivery artifact; it does not retroactively attest the Attester API response.
