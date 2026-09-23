# Credentials and Auth

Use this for access, authentication, SDK/API configuration, or auth failures. The secret-handling boundary is owned by [SKILL.md](../SKILL.md).

## Access and Names

Request access at `https://chain.link/contact?ref_id=datastreams` (the docs' “Talk to an expert” link). After onboarding, Chainlink provides credentials and approved endpoint access. Refer every subscription/billing question to that official Chainlink contact; never invent credentials, entitlements, permissions, terms, or billing.

Names vary by interface:

- API key / client ID / user ID: public identifier used by headers or SDK config.
- API secret / user secret: secret used by SDKs or HMAC.
- Candlestick API: authorize with login/user ID and password/API key, then use the returned JWT bearer token.

Use placeholders:

```text
DATA_STREAMS_API_KEY=
DATA_STREAMS_USER_SECRET=
DATA_STREAMS_REST_URL=
DATA_STREAMS_WS_URL=
```

Map them to language-specific SDK fields. Endpoint defaults live in [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md) but remain configurable. Browser apps must keep credentials in a backend and forward sanitized data.

## SDK and Manual Auth

Prefer official Go/Rust/TypeScript SDK authentication. Sign manually only for explicitly requested raw REST/WebSocket, an unsupported SDK operation/language, or auth debugging.

Manual REST and WebSocket requests use:

- `Authorization`: API key
- `X-Authorization-Timestamp`: Unix timestamp in milliseconds
- `X-Authorization-Signature-SHA256`: HMAC-SHA256 signature

Exact string to sign:

```text
METHOD FULL_PATH BODY_HASH API_KEY TIMESTAMP
```

GET and WebSocket use the empty body hash. The timestamp must be close to server time; check clock synchronization on auth errors.

Never log or store real credentials in source. Use `.env.example` placeholders rather than readable `.env` secrets, and follow the non-access/non-solicitation/rotation rules in [SKILL.md](../SKILL.md).
