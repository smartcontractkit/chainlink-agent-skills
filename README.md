# Chainlink Agent Skills

Official Repo for Chainlink coding skills. Each skill follows the [Agent Skills specification](https://agentskills.io/specification).

## Available Skills

| Skill                                                         | Description                                                                                           |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [chainlink-cre-skill](chainlink-cre-skill/)                   | CRE onboarding, workflow generation, CLI/SDK help, and runtime operations                             |
| [chainlink-ccip-skill](chainlink-ccip-skill/)                 | CCIP sends, contracts, local testing, monitoring, discovery, and CCT workflows                        |
| [chainlink-data-feeds-skill](chainlink-data-feeds-skill/)     | Data Feeds contracts, multi-chain Data Feeds integration                                              |
| [chainlink-data-streams-skill](chainlink-data-streams-skill/) | Data Streams REST/WebSocket SDKs, report decoding, on-chain verification, and real-time frontend apps |
| [chainlink-ace-skill](chainlink-ace-skill/)                   | ACE core contracts, Policy Management, Cross-Chain Identity, and compliance token examples            |
| [chainlink-vrf-skill](chainlink-vrf-skill/)                   | VRF v2.5 subscription and direct-funding consumers, migration from V2, billing, and network addresses |

## Install

Use [vercel's CLI for the open skills ecosystem](https://github.com/vercel-labs/skills#readme). Project-level installation is the default.

```bash
npx skills add smartcontractkit/chainlink-agent-skills
```

<p align="center">
<img width="75%" alt="npx skills add smartcontractkit/chainlink-agent-skills" src="https://github.com/user-attachments/assets/6345c13f-e0c1-43e9-a039-a188027f4746" />
</p>

But if you want to install globally (at the user level) then add the `-g` flag.

Note the use of `--skill` to specify which specific skill to install.

```bash
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-cre-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-ccip-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-data-feeds-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-data-streams-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-ace-skill -g
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
