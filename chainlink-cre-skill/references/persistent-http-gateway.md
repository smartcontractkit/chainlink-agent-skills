# Persistent HTTP Gateway Pattern

Use a persistent HTTP gateway when a CRE workflow needs authenticated external claim or authorization state that must survive process restarts.

## Responsibilities

A gateway may provide:

- authenticated claim ingress;
- persistent claim storage;
- deterministic retrieval by claim ID;
- read-only authorization verification; and
- explicit terminal states.

The gateway should not silently become the authorization authority.

## Claim ingress

Claims requiring independent authorization should enter in a pristine state.

For example:

```text
authorizationState = UNAUTHORIZED
verifiedAmount     = 0
authorizedAmount   = 0
settledAmount      = 0
fundingSource      = null
```

Reject claims that arrive already asserting authorization or settlement unless the application has a separately defined trusted path for that transition.

## Authentication

For authenticated HTTP gateways:

- obtain credentials from secrets or runtime configuration;
- never commit real credentials;
- do not log them;
- reject missing or invalid credentials; and
- compare authentication material defensively.

## Persistence

Persist claim records outside process memory when restart durability matters.

After restart, recover the same claim state rather than implicitly resetting or promoting it.

Terminal states should remain terminal unless an explicit supported transition exists.

## Read-only authorization verification

A useful separation is:

```text
POST /v1/authorization/verify
```

The endpoint may:

1. load the referenced claim;
2. validate the authorization artifact;
3. verify the configured trusted signer;
4. verify the cryptographic signature; and
5. return a verification result.

It should not automatically mutate claim state or perform settlement.

## CRE integration

A confidential CRE workflow may call the gateway from inside a TEE when credentials or request data must remain hidden from node operators.

Only expose the minimum non-sensitive result outside the confidential handler, such as:

```text
claimId
decision
```

Keep credentials, authorization artifacts, and private application state inside the appropriate confidential boundary.
