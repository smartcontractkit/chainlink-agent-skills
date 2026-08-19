# Chainlink Confidential AI Attester — Code Examples

## curl: submit + poll

```bash
export BASE_URL="https://confidential-ai-dev-preview.cldev.cloud"
export API_KEY="your-api-key"

# Base64-encode your document
PDF_B64=$(base64 -i ./statement.pdf)

# Submit
REQUEST_ID=$(curl -s -X POST $BASE_URL/v1/inference \
  -H "Authorization: Bearer $API_KEY" \
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
  }" | jq -r '.id')

echo "Request ID: $REQUEST_ID"

# Poll until done
while true; do
  RESULT=$(curl -s $BASE_URL/v1/inference/$REQUEST_ID \
    -H "Authorization: Bearer $API_KEY")
  STATUS=$(echo "$RESULT" | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then break; fi
  sleep 3
done

echo "$RESULT" | jq '{status, output, error}'
```

The same two HTTP calls—POST to submit and GET to poll—work from any language. Use the language's standard base64 encoder and put its result in `content_base64`; build the JSON body, save the `id`, and poll until `completed`.
