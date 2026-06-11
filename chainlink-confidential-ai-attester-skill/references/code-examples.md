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
    \"prompt\": \"Is this individual suitable for an undercollateralized DeFi loan of 500,000 USDC? Assess based on available evidence only. Respond with ONLY a valid JSON object: {\\\"approved\\\": true, \\\"confidence\\\": \\\"high\\\", \\\"reason\\\": \\\"one sentence\\\", \\\"estimated_monthly_income_usd\\\": 0, \\\"liquid_buffer_usd\\\": 0, \\\"risk_level\\\": \\\"low\\\"}\",
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

The same two HTTP calls (POST to submit, GET to poll) work identically from any language — Python `requests`, Node.js `fetch`, Go `net/http`, Rust `reqwest`, etc. Base64-encode the file, build the JSON body, save the `id`, poll until `completed`.

## Base64 encoding by language

| Language | One-liner |
|----------|-----------|
| Bash | `base64 -i file.pdf` |
| Python | `base64.b64encode(open("file.pdf","rb").read()).decode()` |
| Node.js | `fs.readFileSync("file.pdf").toString("base64")` |
| Go | `base64.StdEncoding.EncodeToString(fileBytes)` |
