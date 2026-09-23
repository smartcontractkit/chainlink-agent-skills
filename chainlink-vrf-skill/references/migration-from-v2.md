# Migrating VRF V1/V2 to v2.5

V2 coordinators are being deprecated, V1/V2 contracts do not work with v2.5 coordinator addresses, and every detected legacy pattern must be converted before emitting code. Output v2.5 only.

Official guide: https://docs.chain.link/vrf/v2-5/migration-from-v2.md

## Before/After Matrix

| Area | Before: detect, do not emit | After: v2.5 output |
|---|---|---|
| Subscription base import | `@chainlink/contracts/src/v0.8/vrf/VRFConsumerBaseV2.sol` (`VRFConsumerBaseV2`) | `@chainlink/contracts/src/v0.8/vrf/dev/VRFConsumerBaseV2Plus.sol` (`VRFConsumerBaseV2Plus`) |
| Coordinator interface | `@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol`; typed `COORDINATOR` state | No separate interface/state variable; use inherited `s_vrfCoordinator` |
| V1 base import | `@chainlink/contracts/src/v0.8/VRFConsumerBase.sol` (`VRFConsumerBase`) | Subscription base above |
| Client | None | `@chainlink/contracts/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol` (`VRFV2PlusClient`) |
| Subscription ID | `uint64` | `uint256` everywhere, including constructor and coordinator methods |
| Subscription request | Positional `COORDINATOR.requestRandomWords(keyHash, subId, requestConfirmations, callbackGasLimit, numWords)` | `s_vrfCoordinator.requestRandomWords(VRFV2PlusClient.RandomWordsRequest({...}))`, including encoded `extraArgs` |
| Subscription callback | `uint256[] memory randomWords` | `uint256[] calldata randomWords` with `VRFConsumerBaseV2Plus` (`@chainlink/contracts` v1.1.1+) |
| Direct base import | `@chainlink/contracts/src/v0.8/vrf/VRFV2WrapperConsumerBase.sol` (`VRFV2WrapperConsumerBase`) | `@chainlink/contracts/src/v0.8/vrf/dev/VRFV2PlusWrapperConsumerBase.sol` (`VRFV2PlusWrapperConsumerBase`) |
| Direct constructor | `(linkAddress, wrapperAddress)` | Single argument: `VRFV2PlusWrapperConsumerBase(wrapperAddress)` |
| Direct callback | `uint256[] memory` | Still `uint256[] memory` for wrapper consumers |
| Direct LINK request | Three arguments; returns only `requestId` | Four arguments including `extraArgs`; returns `(requestId, reqPrice)` |
| Direct native request | Not supported by that V2 shape | `requestRandomnessPayInNative(..., extraArgs)`; returns `(requestId, reqPrice)` |

## Subscription Conversion

```solidity
import {VRFConsumerBaseV2Plus} from "@chainlink/contracts/src/v0.8/vrf/dev/VRFConsumerBaseV2Plus.sol";
import {VRFV2PlusClient} from "@chainlink/contracts/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol";

contract MyConsumer is VRFConsumerBaseV2Plus {
    uint256 public s_subscriptionId;
    mapping(uint256 => uint256) public randomWordByRequest;

    constructor(address coordinatorAddress, uint256 subscriptionId)
        VRFConsumerBaseV2Plus(coordinatorAddress)
    {
        s_subscriptionId = subscriptionId;
    }

    function request(
        bytes32 keyHash,
        uint16 requestConfirmations,
        uint32 callbackGasLimit,
        uint32 numWords
    ) internal returns (uint256 requestId) {
        return s_vrfCoordinator.requestRandomWords(
            VRFV2PlusClient.RandomWordsRequest({
                keyHash: keyHash,
                subId: s_subscriptionId,
                requestConfirmations: requestConfirmations,
                callbackGasLimit: callbackGasLimit,
                numWords: numWords,
                extraArgs: VRFV2PlusClient._argsToBytes(
                    VRFV2PlusClient.ExtraArgsV1({nativePayment: false})
                )
            })
        );
    }

    function fulfillRandomWords(uint256 requestId, uint256[] calldata randomWords)
        internal
        override
    {
        if (randomWords.length == 0) return;
        randomWordByRequest[requestId] = randomWords[0];
    }
}
```

Use `nativePayment: true` only for a subscription funded in the native coin.

## Direct-Funding Conversion

```solidity
import {VRFV2PlusWrapperConsumerBase} from "@chainlink/contracts/src/v0.8/vrf/dev/VRFV2PlusWrapperConsumerBase.sol";
import {VRFV2PlusClient} from "@chainlink/contracts/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol";

contract MyDirectConsumer is VRFV2PlusWrapperConsumerBase {
    mapping(uint256 => uint256) public randomWordByRequest;

    constructor(address wrapperAddress)
        VRFV2PlusWrapperConsumerBase(wrapperAddress)
    {}

    function request(
        bool nativePayment,
        uint32 callbackGasLimit,
        uint16 requestConfirmations,
        uint32 numWords
    ) internal returns (uint256 requestId, uint256 reqPrice) {
        bytes memory extraArgs = VRFV2PlusClient._argsToBytes(
            VRFV2PlusClient.ExtraArgsV1({nativePayment: nativePayment})
        );
        if (nativePayment) {
            return requestRandomnessPayInNative(
                callbackGasLimit, requestConfirmations, numWords, extraArgs
            );
        }
        return requestRandomness(
            callbackGasLimit, requestConfirmations, numWords, extraArgs
        );
    }

    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords)
        internal
        override
    {
        if (randomWords.length == 0) return;
        randomWordByRequest[requestId] = randomWords[0];
    }
}
```

## Address and State Migration

V2 and v2.5 coordinator addresses differ, and V2 subscriptions do not carry over. Replace the constructor address, create and fund a v2.5 subscription, and authorize the new consumer. Make every coordinator address, key hash, and other network-specific value in migrated code a constructor or function parameter. If a value must be hardcoded, explicitly state that it was verified and link https://docs.chain.link/vrf/v2-5/supported-networks.md; never hardcode one without that note and link.

## Compile-Error Map

| Error | Fix |
|---|---|
| `VRFConsumerBaseV2Plus: not found` | Use the `vrf/dev/` import shown above. |
| `requestRandomWords: too many arguments` | Replace the positional call with `RandomWordsRequest`. |
| `Expected identifier but got memory` | Subscription callback uses `calldata`; wrapper callback uses `memory`. |
| `uint64 to uint256 implicit conversion` | Convert every subscription ID declaration/argument to `uint256`. |
| Wrapper base reports too many arguments | Remove the LINK address; the v2.5 wrapper constructor takes one argument. |
