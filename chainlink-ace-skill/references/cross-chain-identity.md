# Cross-Chain Identity

Read for CCIDs; cross-chain identity; KYC/KYB/AML/accreditation; credentials, issuers, registries, sources, data/privacy, expiration/revocation; or `CredentialRegistryIdentityValidatorPolicy`.

## Model

Cross-Chain Identity links one or more EVM addresses to a CCID, then credentials to that identity. Policy Management governs registry administration so issuer authorization can change through policy rather than hardcoded ownership.

| Concept | Meaning |
| --- | --- |
| CCID | `bytes32` identity within an application domain, portable across addresses/EVM chains |
| `IdentityRegistry` | Local mapping; each wallet address maps to exactly one CCID |
| `CredentialRegistry` | CCID credentials and registration, removal/revocation, renewal, expiration, validation |
| Credential Issuer | Trusted offchain verifier that writes resulting credentials onchain |
| Credential Source | Credential type plus trusted IdentityRegistry, CredentialRegistry, and optional Credential Data Validator |
| Identity Validator | Onchain check that an account meets credential requirements |

One CCID may link multiple addresses across chains, avoiding repeated verification. This also creates correlation risk; privacy-sensitive systems can issue multiple CCIDs per actor and keep correlations offchain.

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

Credential data must not contain PII: store hashes, pointers, or minimal non-sensitive references. Data Validator contracts handle requirements beyond binary existence; design them defensively so one failed source does not unexpectedly break validation. Cross-Chain Identity validation-interface view functions should not revert for normal failures; return booleans instead of propagating unexpected external-call errors.

For sanctions screening, choose explicitly among a positive “not sanctioned” attestation, a deny credential with inverted/custom negative logic, or an external-list policy for onchain sanctions state.

## Lifecycle and Runtime

1. A user requests verification; a trusted issuer performs offchain checks.
2. The issuer generates a CCID and registers address-to-CCID mappings.
3. The issuer writes credentials to CredentialRegistry.
4. The application protects functions with `CredentialRegistryIdentityValidatorPolicy`.
5. At runtime, an extractor supplies address parameters; the policy resolves each through IdentityRegistry.
6. It checks required types across configured Credential Sources and invokes any configured Data Validator.
7. A failing address rejects; if all pass, return `Continue`.
8. Credentials may expire, renew, or be removed/revoked.

Keep real-world verification offchain. Treat issuer trust and revocation operations as security controls, and explain address correlation whenever privacy matters.
