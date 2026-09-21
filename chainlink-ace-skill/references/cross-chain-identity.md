# Cross-Chain Identity

Read for CCIDs; cross-chain identity; KYC/KYB/AML/accreditation; credentials, issuers, registries, sources, data/privacy, expiration/revocation; or `CredentialRegistryIdentityValidatorPolicy`.

## Model

Cross-Chain Identity links one or more EVM addresses to a Cross-Chain Identifier (CCID), then credentials to that identifier. Policy Management governs registry administration so issuer authorization can change through policy rather than hardcoded ownership.

| Concept | Meaning |
| --- | --- |
| CCID | Cross-Chain Identifier: a `bytes32` identity within an application domain, portable across addresses/EVM chains |
| `IdentityRegistry` | Local mapping; each wallet address maps to exactly one CCID |
| `CredentialRegistry` | CCID credentials and registration, removal/revocation, renewal, expiration, validation |
| Credential Issuer | Trusted offchain verifier that writes resulting credentials onchain |
| Credential Source | Credential type plus trusted IdentityRegistry, CredentialRegistry, and optional Credential Data Validator |
| Identity Validator | Onchain check that an account meets credential requirements |

One CCID may link multiple addresses across chains, avoiding repeated verification. This also creates correlation risk; privacy-sensitive systems can issue multiple CCIDs per actor and keep correlations offchain. A CCID stored in public registries is public, not secret; never treat it as an authentication secret, and it must not contain PII.

## Types, Sources, and Data

Credential type IDs are `bytes32` hashes of namespaced strings:

```solidity
keccak256("namespace.requirement_name")
```

| String | Meaning |
| --- | --- |
| `common.kyc` | passed KYC |
| `common.kyb` | business passed KYB |
| `common.aml` | not flagged by AML requirements |
| `common.accredited` | accredited investor |

Custom types must not use `common.`; for example `keccak256("com.yourapp.level.gold")`.

Requirements select credential types, trusted sources, and optional data validation. Different types can use different sources; one type can require one or multiple independent providers. A simple KYC transfer can require `keccak256("common.kyc")` from a trusted IdentityRegistry/CredentialRegistry pair, optionally with a data validator.

Model KYC, AML, and accreditation as three separate conjunctive (AND) credential requirements, never one combined check: each has its own credential type, its own Credential Source, and its own authorized issuer.

Configure each Credential Source explicitly: credential type, trusted IdentityRegistry, trusted CredentialRegistry, and optional Credential Data Validator. Map the intended subject address from extractor output into the policy parameter; never assume it is the caller or target. Restrict identity mapping, credential issuance, renewal, and revocation to authorized registry writers/issuers with reviewed policy ordering and approval controls.

Credential data must not contain PII: store hashes, pointers, or minimal non-sensitive references. Data Validator contracts handle requirements beyond binary existence; design them defensively so one failed source does not unexpectedly break validation. Cross-Chain Identity validation-interface view functions should not revert for normal failures; return booleans instead of propagating unexpected external-call errors.

For sanctions screening, choose explicitly among a positive “not sanctioned” attestation, a deny credential with inverted/custom negative logic, or an external-list policy for onchain sanctions state.

## Lifecycle and Runtime

1. A user requests verification; a trusted issuer performs offchain checks.
2. An authorized identity-registry writer generates a CCID and registers address-to-CCID mappings.
3. An authorized Credential Issuer writes credentials to CredentialRegistry.
4. The application protects functions with `CredentialRegistryIdentityValidatorPolicy`.
5. At runtime, an extractor supplies address parameters; the policy resolves each through IdentityRegistry.
6. It checks required types across configured Credential Sources and invokes any configured Data Validator.
7. A failing address rejects; if all pass, return `Continue`.
8. Credentials may expire, renew, or be removed/revoked; prove that expiry or revocation immediately fails the protected path and audit issuer/revoker changes.

Keep real-world verification and PII offchain; store only minimal non-sensitive commitments or references. Treat issuer authorization, revocation, registry administration, parameter mapping, policy order, and address correlation as security controls.

Verify exact contract, interface, or API names against the public `smartcontractkit/chainlink-ace` repository (see Official Sources) before citing them.

OSS Cross-Chain Identity contracts are self-deployed and independently operated; they do not imply managed Platform visibility or capabilities. For managed use, cite the live ACE Beta scope and its curated Credential Data Validator boundary. For production OSS use, review the current repository license, obtain deployment/governance approval, and require legal/compliance review.
