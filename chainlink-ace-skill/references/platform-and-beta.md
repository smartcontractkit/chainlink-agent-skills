# ACE Platform and Beta Scope

Read for ACE Platform/private Beta, product UI or managed API, Policy/Identity/Reporting Manager, Coordinator/Reporting API, auditors, audit trails, networks/mainnet readiness, managed registration/indexing, externally deployed contract visibility, custom managed capabilities, credentials, or product limitations.

## Authority and Boundary

Current product sources:
- Overview: `https://docs.chain.link/ace.md`
- Beta: `https://docs.chain.link/ace/beta-scope.md`
- Networks: `https://docs.chain.link/ace/supported-networks.md`
- Coordinator: `https://docs.chain.link/ace/reference/api/coordinator.md`
- Reporting API/concept: `https://docs.chain.link/ace/reference/api/reporting.md`, `https://docs.chain.link/ace/concepts/reporting.md`

Before answering, fetch and cite the exact live official page for every current managed claim—including resources, `as_of`, availability, networks, mainnet, and Beta limits—and state when it was verified. Make network feasibility conditional on the current supported-network list and ask for the target chain when it changes the answer.

| Surface | Authority and scope |
| --- | --- |
| OSS/self-deployed contracts | `smartcontractkit/chainlink-ace`; users deploy/extend under BUSL/commercial licensing, security review, and their own infrastructure |
| Managed ACE Platform | `docs.chain.link/ace`; managed UI/APIs subject to access, provisioning, supported networks, private-Beta scope, and product limitations |

Never infer managed support from a repository capability, or infer that a managed Beta limitation prevents OSS evaluation/self-deployment.

## Beta Defaults

As verified against the official Beta scope, August 24, 2026:
- The Platform is a provisioned private Beta for selected mainnet and testnet networks; confirm the requested chain against the live supported-network list.
- Users can register custom policies. Custom extractors and mappers are unavailable through the Platform, so the full managed experience is limited to the documented ERC-20 and ERC-3643 function signatures.
- Contracts deployed outside the Platform can function onchain but do not appear in its UI, API responses, reporting, or monitoring; do not propose registration or indexing unless current official docs explicitly add it.
- Credential Data Validators come from Chainlink's curated catalog; do not promise a user-deployed validator. Re-fetch the Beta page because all product scope can change.
- For production, distinguish managed availability from self-deployed OSS, which still needs current license review, audits, operational ownership, deployment approval, and legal/compliance review.

## Managed Surfaces

- **Policy Manager (UI + API):** configure/deploy compliance rules.
- **Identity Manager (UI + API):** manage CCIDs, identities, credential registries/types, issuers, and credentials.
- **Reporting Manager (API):** query policy-run history, transactions, and onchain compliance state.

### Coordinator API

Privileged write/control-plane API for the management operations currently listed at `https://docs.chain.link/ace/reference/api/coordinator`; cite that page rather than extrapolating a resource from the UI or OSS contracts:
- delegated signing-wallet creation where supported;
- PolicyEngine deployment/configuration on supported networks;
- policy-library instance creation and parameters;
- target registration and function-selector protection attachment;
- extractor management;
- identity/credential registry creation;
- CCID and wallet mapping registration;
- credential-type definition, credential issuance/management, and trusted-issuer management.

It changes ACE resources and is not the auditor evidence API.

### Reporting API

Read-only audit/monitoring plane for the resources currently listed at `https://docs.chain.link/ace/reference/api/reporting`. As verified August 24, 2026, these are **Transactions, Policies, Targets, Identities, and Permits**; `as_of` point-in-time queries are documented for Policies, Targets, and Identities, not every resource. Cite and re-check the page before repeating either list. Reporting data is indexed evidence, not a substitute for chain state: reconcile it with onchain logs, deployed addresses, policy wiring/snapshots, credential-issuer records, and governance/admin history.

Do not invent exact event names: identify the deployed contract and verify its ABI or pinned source before naming logs. Do not equate a managed Reporting `Identities` record with an OSS CCID registry record; state the boundary and reconcile each against its actual onchain registry.

## External Deployments

Current Beta docs say Foundry/self-deployed contracts do not appear in Platform UI, API responses, reporting, or monitoring because the Platform tracks contracts it deploys. Cite the live Beta page and do not claim an external registration/indexing path unless that page explicitly documents one.

## Managed-Answer Guardrails

Every managed workflow must state the applicable private-Beta/access and feature limits. Require authorized access and explicit human or governance approval before Coordinator operations or onchain writes; keep PII and raw identity evidence offchain; apply least-privilege access and documented retention to reports; and include legal/compliance review where the design governs regulated activity. Always include the onchain reconciliation step for audit or reporting guidance and review policy order because an earlier `Allowed` result can skip later controls.

## Credential Modes

OSS Cross-Chain Identity supports credential registries and Credential Data Validator patterns. Managed credentials are product-scoped: cite the current official ACE Beta docs at `https://docs.chain.link/ace/beta-scope` before stating attestation-only or any other Beta limit, and do not promise custom data-validator behavior through UI/API. When contrasting the modes, require production OSS BUSL/commercial-license and counsel review, trusted-issuer controls, and credential expiry/revocation handling; separate what OSS contracts can implement from what managed Beta exposes.
