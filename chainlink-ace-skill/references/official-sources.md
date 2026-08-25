# Official Sources

Use for current repository/product facts, exact source or interface locations, scripts, licensing, managed scope, Beta constraints, networks, APIs, and reporting. Repository root: `https://github.com/smartcontractkit/chainlink-ace`; package metadata names `@chainlink/ace` under `BUSL-1.1`.

## Freshness

Re-check repository source before exact signatures, schemas, scripts, remappings, imports, or license claims; re-check product docs before availability, supported networks, mainnet readiness, API resources, or Beta limitations. Every current managed-product claim must cite the exact live official URL and state the verification date. Before listing Coordinator or Reporting resources/capabilities or `as_of` support, fetch both API pages, report only what each currently documents, and say which resource types support `as_of`; never generalize it to every endpoint. Prefer live official source over a bundled reference and name any change from it.

## Product Docs

| Topic | URL |
| --- | --- |
| Overview | `https://docs.chain.link/ace.md` |
| Beta scope | `https://docs.chain.link/ace/beta-scope.md` |
| Supported networks | `https://docs.chain.link/ace/supported-networks.md` |
| Release notes | `https://docs.chain.link/ace/release-notes.md` |
| Architecture | `https://docs.chain.link/ace/concepts/architecture.md` |
| Reporting | `https://docs.chain.link/ace/concepts/reporting.md` |
| Coordinator API | `https://docs.chain.link/ace/reference/api/coordinator.md` |
| Reporting API | `https://docs.chain.link/ace/reference/api/reporting.md` |
| SecureMintPolicy | `https://docs.chain.link/ace/reference/policy-library/secure-mint-policy.md` |

## Repository Docs

Paths below are relative to `https://github.com/smartcontractkit/chainlink-ace/blob/main/`.

| Topic | Path |
| --- | --- |
| Main README | `README.md` |
| Getting Started | `getting_started/GETTING_STARTED.md` |
| Advanced Getting Started | `getting_started/advanced/GETTING_STARTED_ADVANCED.md` |
| Upgrade Guide | `UPGRADE_GUIDE.md` |
| Glossary | `Glossary.md` |
| License | `LICENSE` |
| Package metadata | `package.json` |
| Remappings | `remappings.txt` |
| Policy Management README | `packages/policy-management/README.md` |
| Policy concepts | `packages/policy-management/docs/CONCEPTS.md` |
| Policy API Guide | `packages/policy-management/docs/API_GUIDE.md` |
| Policy API Reference | `packages/policy-management/docs/API_REFERENCE.md` |
| Custom Policies Tutorial | `packages/policy-management/docs/CUSTOM_POLICIES_TUTORIAL.md` |
| Policy Ordering Guide | `packages/policy-management/docs/POLICY_ORDERING_GUIDE.md` |
| Policy Security | `packages/policy-management/docs/SECURITY.md` |
| Policies README | `packages/policy-management/src/policies/README.md` |
| Cross-Chain Identity README | `packages/cross-chain-identity/README.md` |
| Identity concepts | `packages/cross-chain-identity/docs/CONCEPTS.md` |
| Identity API Guide | `packages/cross-chain-identity/docs/API_GUIDE.md` |
| Identity API Reference | `packages/cross-chain-identity/docs/API_REFERENCE.md` |
| Credential Flow | `packages/cross-chain-identity/docs/CREDENTIAL_FLOW.md` |
| Identity Security | `packages/cross-chain-identity/docs/SECURITY.md` |

## Source Areas

Paths below are relative to the repository root. These rows are the canonical package/source map.

| Path | Purpose |
| --- | --- |
| `packages/policy-management/src/core` | `PolicyEngine`, `PolicyProtected`, `PolicyProtectedUpgradeable`, base `Policy` |
| `packages/policy-management/src/interfaces` | `IPolicyEngine`, `IPolicyProtected`, `IPolicy`, `IExtractor`, `IMapper` |
| `packages/policy-management/src/policies` | Pre-built policies |
| `packages/policy-management/src/extractors` | Calldata extractors |
| `packages/policy-management/src/libraries` | Shared libraries |
| `packages/policy-management/docs` | Concepts, API guide/reference, custom-policy tutorial, ordering, security |
| `packages/policy-management/test` | Foundry tests |
| `packages/cross-chain-identity/src` | Identity/credential registries, validator policy and implementation |
| `packages/cross-chain-identity/src/interfaces` | `IIdentityRegistry`, `ICredentialRegistry`, `ICredentialRequirements`, `IIdentityValidator`, `ICredentialValidator`, `ICredentialDataValidator`, `ITrustedIssuerRegistry` |
| `packages/cross-chain-identity/docs` | Concepts, API guide/reference, credential flow, security |
| `packages/cross-chain-identity/test` | Foundry tests |
| `packages/tokens` | ACE-integrated token examples |
| `scripts` | Deployment scripts |

## Token Implementations

| Token | Source | Distinction |
| --- | --- | --- |
| ERC-20 Compliance Token | `https://github.com/smartcontractkit/chainlink-ace/tree/main/packages/tokens/erc-20` | Policy-protected ERC-20; keeps frozen tokens frozen during burns/forced transfers and checks unfrozen balances |
| ERC-3643 Compliance Token | `https://github.com/smartcontractkit/chainlink-ace/tree/main/packages/tokens/erc-3643` | T-REX-style token using ACE identity and compliance; automatically unfreezes as needed during burns/forced transfers |

Tokens root: `https://github.com/smartcontractkit/chainlink-ace/tree/main/packages/tokens`; deployment scripts: `https://github.com/smartcontractkit/chainlink-ace/tree/main/scripts`.

Token examples are implementation references, not a compliance determination. Forced transfer, burn, freeze, recovery, and issuer powers require strict authorization, governance approval, auditability, and legal/compliance review; keep PII and raw identity evidence offchain. Never imply that using ERC-3643 or the T-REX example itself establishes regulatory or legal compliance.

## Selection

- Overview/start: README; new OSS integration: Getting Started plus package README; existing proxy: Upgrade Guide.
- Policy behavior: policies README, or the docs.chain.link policy page for product scope; exact signature/schema: corresponding Solidity interface/source.
- Identity/credentials: identity package docs for OSS, Beta Scope for managed credential limitations.
- Production licensing: `LICENSE`; tell the user to contact Chainlink and consult counsel.
- Managed Platform/Beta/mainnet/network: Beta Scope plus Supported Networks; auditor/reporting: Reporting concept plus Reporting API.
- Coordinator versus Reporting: fetch both; distinguish write/control-plane management from read-only evidence queries.
- Current scripts: fetch `package.json` rather than copying a potentially stale script block.
