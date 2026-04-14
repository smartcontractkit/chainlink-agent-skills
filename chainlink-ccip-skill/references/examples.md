# Examples

Use this file when you need a concrete reference for what a good response looks like. These examples show the expected shape and tone, not the only valid answer.

## Example 1: Preflight Summary for a Testnet Token Bridge

User asks: "Bridge 1 CCIP-BnM from Ethereum Sepolia to Base Sepolia using CCIP."

Good response shape:

```text
Proposed on-chain action:
- Action: Token transfer via CCIP
- Network: Testnet
- Source chain: Ethereum Sepolia
- Destination chain: Base Sepolia
- Route/lane: Ethereum Sepolia → Base Sepolia
- Token/amount: 1 CCIP-BnM
- Payload: Tokens only (no data)
- Contracts: N/A (tool-first path, no custom contracts)
- Method: CCIP CLI `send` command
- Expected effect: 1 CCIP-BnM debited on Sepolia, credited on Base Sepolia after lane finality

Do you want me to execute this?
```

After the user approves, ask the second confirmation immediately before the actual send:

> "This will send 1 CCIP-BnM from Ethereum Sepolia to Base Sepolia. This is a testnet transaction. Confirm to proceed."

## Example 2: Monitoring Response with Lifecycle Explanation

User asks: "Show me the status of this CCIP message: 0x1234abcd..."

Good response shape:

> Your CCIP message `0x1234abcd...` is currently **in transit**.
>
> **Lifecycle stage:** Committed
>
> Here is what happened so far:
> 1. The message was sent on Ethereum Sepolia and the source transaction was finalized.
> 2. The Committing DON observed and committed the message on the destination chain.
> 3. Next step: the Executing DON will execute the message on Base Sepolia. This typically takes a few more minutes depending on current lane latency.
>
> Once executed, the status will move to **delivered**. If execution fails, the status will show **failed** and you can inspect the revert reason.
>
> Want me to check again in a minute, or look up the lane latency for this route?

Key elements: name the current state, explain what already happened, explain what happens next, offer a follow-up action.

## Example 3: Contract-Generation Response Shape

User asks: "Create a minimal CCIP sender and receiver in Solidity for arbitrary messaging on testnet."

Good response structure:

1. **Clarify the shape:** "I will generate a data-only sender and a data-only receiver. No token transfers. Let me know if you also need tokens."

2. **Sender contract** with:
   - Import paths (`@chainlink/contracts-ccip/...`)
   - Constructor taking router address and LINK token address
   - A `send` function that builds `Client.EVM2AnyMessage`, quotes fees via `IRouterClient.getFee`, and sends via `ccipSend`
   - Owner-only access control on send
   - Destination chain allowlisting

3. **Receiver contract** with:
   - Inheriting `CCIPReceiver`
   - `_ccipReceive` override with source chain and sender validation
   - Router address check (inherited from `CCIPReceiver`)
   - Simple payload handling (e.g., decode and store or emit)

4. **Setup instructions:**
   - Foundry install commands with version tags
   - Remappings for `@chainlink/contracts-ccip` and OpenZeppelin
   - Deployment steps (deploy receiver, deploy sender, allowlist destination chain on sender, allowlist source chain and sender on receiver)

5. **What to test first:** "Before deploying to testnet, add a Chainlink Local simulator test for the happy path. See the local testing reference."

For concrete Solidity code, see [ccip-solidity-examples.md](ccip-solidity-examples.md).
