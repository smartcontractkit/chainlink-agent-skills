# VRF v2.5 Subscription Method

Use subscriptions for recurring requests: fund one account with LINK or native coin, authorize consumer contracts, and pay the measured gas cost after each fulfillment. For a complete compiling consumer, deploy script, and mock test, use [`templates/starter-kit`](../templates/starter-kit/README.md); do not rebuild that project from this excerpt.

Official guide: https://docs.chain.link/vrf/v2-5/subscription/get-a-random-number.md

## Setup

1. Create a subscription at https://vrf.chain.link or with the coordinator methods below; record its `uint256` ID.
2. Fund it with the token selected by each request.
3. Deploy the consumer and add its address as an authorized consumer.
4. Call the consumer's request function from the owner/application path.

The agent prepares code or user-run instructions only; the user performs these writes in their wallet-controlled environment.

## Request and Callback Excerpt

This excerpt deliberately matches the runnable starter's `onlyOwner` request policy and request bookkeeping. It assumes the surrounding contract inherits `VRFConsumerBaseV2Plus`, imports `VRFV2PlusClient`, and defines `s_subscriptionId`, `keyHash`, `requestConfirmations`, `callbackGasLimit`, and `numWords`.

```solidity
struct RequestStatus {
    bool fulfilled;
    bool exists;
    uint256[] randomWords;
}

mapping(uint256 => RequestStatus) public s_requests;
uint256[] public requestIds;
uint256 public lastRequestId;

function requestRandomWords(bool enableNativePayment)
    external
    onlyOwner
    returns (uint256 requestId)
{
    requestId = s_vrfCoordinator.requestRandomWords(
        VRFV2PlusClient.RandomWordsRequest({
            keyHash: keyHash,
            subId: s_subscriptionId,
            requestConfirmations: requestConfirmations,
            callbackGasLimit: callbackGasLimit,
            numWords: numWords,
            extraArgs: VRFV2PlusClient._argsToBytes(
                VRFV2PlusClient.ExtraArgsV1({nativePayment: enableNativePayment})
            )
        })
    );
    s_requests[requestId] = RequestStatus({
        randomWords: new uint256[](0),
        exists: true,
        fulfilled: false
    });
    requestIds.push(requestId);
    lastRequestId = requestId;
}

function fulfillRandomWords(uint256 requestId, uint256[] calldata randomWords)
    internal
    override
{
    RequestStatus storage request = s_requests[requestId];
    if (!request.exists || request.fulfilled || randomWords.length == 0) return;
    request.fulfilled = true;
    request.randomWords = randomWords;
}
```

`VRFConsumerBaseV2Plus` provides `onlyOwner` and authenticates coordinator callbacks. Do not redeclare a coordinator variable or override the raw fulfillment entry point. A use case may replace the illustrative bookkeeping, but generated code must implement the requested application end to end, not a helper-only stub.

For a fair ERC-721 mint, mint before requesting randomness so the recipient and token ID are fixed before the result exists. Replace the generic request and callback above with this application flow in the surrounding ERC-721 consumer:

```solidity
struct TraitRequest {
    address recipient;
    uint256 tokenId;
    bool exists;
    bool fulfilled;
}

uint256 public constant TRAIT_COUNT = 8;
uint256 public nextTokenId = 1;
mapping(address => bool) public hasPendingTrait;
mapping(uint256 => TraitRequest) public traitRequests;
mapping(uint256 => uint256) public traitOf;

event TraitRequested(uint256 indexed requestId, uint256 indexed tokenId, address recipient);
event TraitAssigned(uint256 indexed requestId, uint256 indexed tokenId, uint256 trait);

error TraitRequestPending();

function mint(bool enableNativePayment)
    external
    returns (uint256 tokenId, uint256 requestId)
{
    if (hasPendingTrait[msg.sender]) revert TraitRequestPending();
    hasPendingTrait[msg.sender] = true;
    tokenId = nextTokenId++;

    _safeMint(msg.sender, tokenId);
    requestId = s_vrfCoordinator.requestRandomWords(
        VRFV2PlusClient.RandomWordsRequest({
            keyHash: keyHash,
            subId: s_subscriptionId,
            requestConfirmations: requestConfirmations,
            callbackGasLimit: callbackGasLimit,
            numWords: 1,
            extraArgs: VRFV2PlusClient._argsToBytes(
                VRFV2PlusClient.ExtraArgsV1({nativePayment: enableNativePayment})
            )
        })
    );
    traitRequests[requestId] = TraitRequest({
        recipient: msg.sender,
        tokenId: tokenId,
        exists: true,
        fulfilled: false
    });
    emit TraitRequested(requestId, tokenId, msg.sender);
}

function fulfillRandomWords(uint256 requestId, uint256[] calldata randomWords)
    internal
    override
{
    TraitRequest storage request = traitRequests[requestId];
    if (!request.exists || request.fulfilled || randomWords.length == 0) return;

    uint256 trait = randomWords[0] % TRAIT_COUNT;
    request.fulfilled = true;
    traitOf[request.tokenId] = trait;
    hasPendingTrait[request.recipient] = false;
    emit TraitAssigned(requestId, request.tokenId, trait);
}
```

The user owns the token before the words arrive. Fulfillment only records the deterministic trait and cannot offer a mint, cancel, retry, or rejection path after inspection.

## Required Imports and Constructor Shape

```solidity
import {VRFConsumerBaseV2Plus} from "@chainlink/contracts/src/v0.8/vrf/dev/VRFConsumerBaseV2Plus.sol";
import {VRFV2PlusClient} from "@chainlink/contracts/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol";

constructor(address coordinatorAddress, uint256 subscriptionId, bytes32 _keyHash)
    VRFConsumerBaseV2Plus(coordinatorAddress)
{
    s_subscriptionId = subscriptionId;
    keyHash = _keyHash;
}
```

## Dependencies

```bash
npm install @chainlink/contracts
# Foundry: use a tagged chainlink-evm contracts release
forge install smartcontractkit/chainlink-evm@contracts-v1.5.0
```

```toml
remappings = ['@chainlink/contracts/=lib/chainlink-evm/contracts/']
```

Available tags: https://github.com/smartcontractkit/chainlink-evm/releases

## Request Parameters

| Field | Meaning and constraint |
|---|---|
| `keyHash` | Gas lane and maximum fulfillment gas price. Copy a network value from [`supported-networks.md`](supported-networks.md); a higher lane tolerates more congestion at potentially higher cost. |
| `callbackGasLimit` | Maximum callback gas. Simple storage is commonly 40,000–100,000; complex logic 200,000–500,000; absolute maximum 2,500,000. Under-sizing makes the callback revert, so measure and buffer it. |
| `requestConfirmations` | Blocks waited before fulfillment; minimum 3. Higher values trade latency for reorg resistance. 3–20 is common; use 20+ when justified by high value at risk. |
| `numWords` | Independent `uint256` values per request; maximum 500. Request only what the application consumes. |
| `extraArgs` | Required v2.5 bytes encoding of `ExtraArgsV1`. `nativePayment: false` selects LINK; `true` selects the native coin. The subscription must hold the matching asset. |

## Subscription Methods

The UI at https://vrf.chain.link is the usual management path. Contract integrations use `IVRFCoordinatorV2Plus`:

```solidity
IVRFCoordinatorV2Plus coordinator = IVRFCoordinatorV2Plus(coordinatorAddress);
uint256 subId = coordinator.createSubscription();
LINK.transferAndCall(address(coordinator), amount, abi.encode(subId)); // ERC-677 LINK
coordinator.addConsumer(subId, consumerAddress);
coordinator.cancelSubscription(subId, receivingAddress);
```

Native funding uses `coordinator.fundSubscriptionWithNative{value: amount}(subId)`. See [`billing.md`](billing.md) for token compatibility and cost details.

## Lifecycle and Security

1. The consumer requests and receives a `requestId`.
2. A VRF node derives randomness off-chain and submits values plus proof.
3. The coordinator verifies the proof and invokes `fulfillRandomWords` after the requested confirmations.
4. The consumer matches by `requestId`, stores the result, and emits any application event.

Fulfillment latency depends on confirmations and network conditions. Never assume FIFO order, allow request-specific re-request/cancellation, accept outcome-changing inputs after requesting, put revert-prone application logic in the callback, or expose request IDs in a way that lets callers predict which request maps to their action. See [`security-and-best-practices.md`](security-and-best-practices.md).
