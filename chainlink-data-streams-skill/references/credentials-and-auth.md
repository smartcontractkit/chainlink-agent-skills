# Credentials and Auth

Use this file when the user asks how to get Data Streams credentials, how auth works, or how to configure SDK/API clients.

## Official Access Process

1. Explain that Data Streams access is requested through official Chainlink channels.
2. Point users to `https://chain.link/contact?ref_id=datastreams` or the "Talk to an expert" link in the Data Streams docs.
3. Explain that after onboarding, Chainlink provides API credentials and endpoint access for the environments they are approved to use.
4. Do not invent credentials, feed entitlements, endpoint permissions, subscription terms, or billing details.

## Credential Names

The docs and SDK examples use slightly different labels depending on language and interface:

- API key / client ID / user ID: public identifier used in auth headers or SDK config.
- API secret / user secret: secret used by SDKs or HMAC signing.
- Candlestick API: authorize with login/user ID and password/API key, then use the returned JWT bearer token.

When generating project code, prefer environment variables such as:

```text
DATA_STREAMS_API_KEY=
DATA_STREAMS_USER_SECRET=
DATA_STREAMS_REST_URL=
DATA_STREAMS_WS_URL=
```

Map these to SDK-specific fields in the generated code. Never commit real secrets.

For public endpoint defaults, read [public-endpoints-and-addresses.md](public-endpoints-and-addresses.md). Keep endpoint values configurable through environment variables even when using documented defaults.

## SDK Auth Defaults

Prefer official SDKs for Go, Rust, and TypeScript. The SDKs handle REST and WebSocket authentication automatically, so generated code usually should not hand-roll HMAC signing.

Use manual auth only when:

1. the user explicitly asks for raw REST or WebSocket calls without an SDK
2. the target language has no official SDK path for the requested operation
3. the user is debugging an authentication failure

## Manual REST/WebSocket Auth

Current official auth docs require these headers for REST and WebSocket API requests:

- `Authorization`: API key
- `X-Authorization-Timestamp`: Unix timestamp in milliseconds
- `X-Authorization-Signature-SHA256`: HMAC-SHA256 signature

The string-to-sign format is:

```text
METHOD FULL_PATH BODY_HASH API_KEY TIMESTAMP
```

For GET requests and WebSocket connections, use the empty body hash. The timestamp must be close to server time, so tell users to verify system clock synchronization when debugging auth errors.

## Secret Handling

1. Never print API secrets in logs.
2. Never store real credentials in generated source files.
3. Use `.env.example` placeholders, not `.env` with real values.
4. For browser apps, keep Data Streams credentials in a backend process and stream sanitized data to the frontend.
5. If the user pastes real credentials, avoid repeating them and recommend rotating them if they may have been exposed.
