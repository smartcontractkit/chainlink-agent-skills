# Confidential External Authorization Patterns

Use this pattern when a CRE-connected application records a claim or request that requires independent authorization before state mutation or settlement.

## Core rule

Cryptographic verification and authorization are separate decisions.

A valid signature proves that a signer signed an artifact. It does not prove that the signer is trusted to authorize the requested action.

## Safe flow

1. Record the claim in an unauthorized state.
2. Obtain authorization from an independently established trusted signer.
3. Bind the authorization to the exact claim and intended action.
4. Validate structure, scope, timestamps, and expected signer.
5. Verify the cryptographic signature.
6. Apply authorization policy only after verification succeeds.
7. Keep verification read-only unless a separate transition explicitly authorizes mutation.
8. Perform settlement through a distinct authorized path.

## Fail closed

If the trusted signer is missing, malformed, unknown, or mismatched, stop.

Never substitute the claimant, a claimant-controlled key, or an address supplied only by the authorization artifact for the independently configured trusted signer.

## Signed commitment

Bind fields needed to prevent replay or substitution, including:

- authorization ID;
- claim ID;
- canonical claim digest;
- asset;
- amount;
- recipient;
- funding source or authority context;
- authorization scope;
- signer identity;
- signing scheme;
- issued-at timestamp; and
- expiry timestamp.

`issuedAt` and `expiresAt` must be part of the signed commitment.

## Verification ordering

Prefer:

1. artifact version;
2. claim binding;
3. asset, amount, and recipient binding;
4. authorization scope;
5. issued-at and expiry bounds;
6. trusted signer;
7. signing scheme;
8. cryptographic signature;
9. application authorization policy.

## Verification is not settlement

Successful verification must not automatically:

- mark a claim settled;
- move tokens;
- mint assets;
- perform an EVM write;
- change authorization state; or
- create a funding source.

Use a separate authorized state-transition or settlement mechanism.

## Secrets

Trusted signer configuration, bearer tokens, API credentials, and other secrets must not be hardcoded or logged.

Use CRE secrets or deployment-time configuration appropriate to the environment.
