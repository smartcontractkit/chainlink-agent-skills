# Chainlink Developer Agent Skills

Official Repo for Chainlink coding skills. Each skill follows the [Agent Skills specification](https://agentskills.io/specification).

## Available Skills

| Skill                                                         | Description                                                                                           |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [chainlink-cre-skill](chainlink-cre-skill/)                   | CRE onboarding, workflow generation, CLI/SDK help, and runtime operations                             |
| [chainlink-cre-connect-skill](chainlink-cre-connect-skill/)   | CRE Connect watchers, verifiable events, gas-less operations, Smart Accounts, and DTA                     |
| [chainlink-ccip-skill](chainlink-ccip-skill/)                 | CCIP sends, contracts, local testing, monitoring, discovery, and CCT workflows                        |
| [chainlink-data-feeds-skill](chainlink-data-feeds-skill/)     | Data Feeds contracts, multi-chain Data Feeds integration                                              |
| [chainlink-data-streams-skill](chainlink-data-streams-skill/) | Data Streams REST/WebSocket SDKs, report decoding, on-chain verification, and real-time frontend apps |
| [chainlink-ace-skill](chainlink-ace-skill/)                   | ACE core contracts, Policy Management, Cross-Chain Identity, and compliance token examples            |
| [chainlink-confidential-ai-attester-skill](chainlink-confidential-ai-attester-skill/) | Confidential AI Attester: TEE LLM inference over private documents with attested results |
| [chainlink-vrf-skill](chainlink-vrf-skill/)                   | VRF v2.5 subscription and direct-funding consumers, migration from V2, billing, and network addresses |

## Install

Use [vercel's CLI for the open skills ecosystem](https://github.com/vercel-labs/skills#readme). Project-level installation is the default.

```bash
npx skills add smartcontractkit/chainlink-agent-skills
```

<p align="center">
<img width="75%" alt="npx skills add smartcontractkit/chainlink-agent-skills" src="https://github.com/user-attachments/assets/2f4fbecb-be53-47d6-9f5a-7cb32979eb72" />
</p>

But if you want to install globally (at the user level) then add the `-g` flag.

Note the use of `--skill` to specify which specific skill to install.

```bash
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-cre-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-cre-connect-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-ccip-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-data-feeds-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-data-streams-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-ace-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-confidential-ai-attester-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-vrf-skill -g
```

## Use

When your agent supports Agent Skills, it will discover and activate these skills based on the task. **However** we recommend that you explicitly invoke the skill in your agent chat sessions as follows:


```text
Using /chainlink-data-feeds-skill, /chainlink-cre-skill, and /chainlink-ccip-skill, 
build a tokenized fund project that:

- delivers data (NAV, yields and ESG attestations) securely on-chain
- mints fund tokens representing shares in a tokenized investment fund
- uses Chainlink Proof of Reserve by CRE for real-time verification of reserved assets
- can be traded and settled seamlessly across multiple public and private chains
- has a clean, modern UI dashboard

Create a development plan. Include steps for testing on testnets. 
Make sure README has instructions on how to run local CRE simulations and 
how to monitor status of cross-chain transfers using the CCIP CLI.

Any questions before you start?
```

Disclaimer: Please note, this repo contains community examples only  — these are not Chainlink products or services and are not supported or maintained by Chainlink. This code represents an example of using a Chainlink product or service, and is intended for demonstration and educational purposes only. It is provided “AS IS” and “AS AVAILABLE” without warranties of any kind, may not have been audited, and may omit checks or error handling. Each party intending to use this example code does so entirely at their own risk and must perform its own audits, security and code review, key management, and testing before any production deployment and ensure the operation and performance of such code matches expectations. Neither Chainlink Labs nor the Chainlink Foundation deploys, operates, monitors, maintains or endorses any deployment of this code. Note that this is not a Chainlink product, feature or service, and there are no commitments made with respect to the code, including compatibility with future Chainlink releases. You should not rely on this code without first conducting your own technical, engineering, and security review. This code is also outside the scope of any Chainlink bug bounty programs. Neither Chainlink Labs, the Chainlink Foundation, nor Chainlink node operators are responsible for outcomes due to errors in this example or how it is deployed or operated, or liable for any resulting claims or damages. Use of the Chainlink Network is subject to the Chainlink Foundation [Terms of Service](https://chain.link/terms), which provides important information and disclosures. By using this code, you acknowledge and agree to these terms.
