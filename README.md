# Chainlink Agent Skills

Official Repo for Chainlink skills. Each skill follows the [Agent Skills specification](https://agentskills.io/specification).

## Available Skills


| Skill                     | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| [chainlink-cre-skill](chainlink-cre-skill/) | CRE onboarding, workflow generation, CLI/SDK help, and runtime operations |
| [chainlink-ccip-skill](chainlink-ccip-skill/) | CCIP sends, contracts, local testing, monitoring, discovery, and CCT workflows |
| [chainlink-data-feeds-skill](chainlink-data-feeds-skill/) | Data Feeds contracts, multi-chain Data Feeds integration |


## Install

Use [vercel's CLI for the open skills ecosystem](https://github.com/vercel-labs/skills#readme). Project-level installation is the default. 

```bash
npx skills add smartcontractkit/chainlink-agent-skills
```

<p align="center">
<img width="75%" alt="npx skills add" src="https://github.com/user-attachments/assets/4edcf29c-f34a-4e56-90de-ec5e92deee1a" />
</p>


But if you want to install globally (at the user level) then add the `-g` flag.

Note the use of `--skill` to specify which specific skill to install. 

```bash
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-cre-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-ccip-skill -g
npx skills add smartcontractkit/chainlink-agent-skills --skill chainlink-data-feeds-skill -g
```

## Use

When your agent supports Agent Skills, it will discover and activate these skills based on the task. **However** we recommend that you explicitly invoke the skill in your agent chat sessions as follows:

```text
Using the /chainlink-data-feeds-skill, develop a Solidity contract that:

- reads the ETH/USD Chainlink price feed on Ethereum mainnet
- is structured as a Foundry project
- handles required package installation and project setup
- includes proper validation
- follows security best practices

Any questions before you start?
```
