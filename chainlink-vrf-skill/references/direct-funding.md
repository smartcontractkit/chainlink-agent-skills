# VRF v2.5 Direct Funding

Use direct funding for one-off or infrequent requests that should not share a subscription. The consumer holds LINK or native coin and pays an estimated cost upfront when it requests; an underfunded call reverts. Prefer [`subscription.md`](subscription.md) for recurring requests.
For a one-off or single-request consumer, permanently block a second request after the first succeeds: check `lastRequestId != 0` (or a dedicated used flag) before calling the wrapper and revert with `RequestAlreadyMade`. Omit that guard only when the user asks for recurring requests.

Official guide: https://docs.chain.link/vrf/v2-5/direct-funding/get-a-random-number.md

## Consumer

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {VRFV2PlusWrapperConsumerBase} from "@chainlink/contracts/src/v0.8/vrf/dev/VRFV2PlusWrapperConsumerBase.sol";
import {VRFV2PlusClient} from "@chainlink/contracts/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol";
import {ConfirmedOwner} from "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";

contract VRFDirectFundingConsumer is VRFV2PlusWrapperConsumerBase, ConfirmedOwner {
    event RequestSent(uint256 requestId, uint32 numWords);
    event RequestFulfilled(uint256 requestId, uint256[] randomWords, uint256 payment);

    error RequestNotFound(uint256 requestId);
    error WithdrawFailed();

    struct RequestStatus {
        uint256 paid; // juels for LINK, wei for native
        bool fulfilled;
        uint256[] randomWords;
        bool native;
    }

    mapping(uint256 => RequestStatus) public s_requests;
    uint256[] public requestIds;
    uint256 public lastRequestId;

    uint32 public callbackGasLimit = 100_000;
    uint16 public requestConfirmations = 3;
    uint32 public numWords = 2;

    // v2.5 takes only the wrapper address; V2 also took a LINK address.
    constructor(address wrapperAddress)
        ConfirmedOwner(msg.sender)
        VRFV2PlusWrapperConsumerBase(wrapperAddress)
    {}

    function requestRandomWords(bool enableNativePayment)
        external
        onlyOwner
        returns (uint256 requestId)
    {
        bytes memory extraArgs = VRFV2PlusClient._argsToBytes(
            VRFV2PlusClient.ExtraArgsV1({nativePayment: enableNativePayment})
        );

        uint256 reqPrice;
        if (enableNativePayment) {
            (requestId, reqPrice) = requestRandomnessPayInNative(
                callbackGasLimit,
                requestConfirmations,
                numWords,
                extraArgs
            );
        } else {
            (requestId, reqPrice) = requestRandomness(
                callbackGasLimit,
                requestConfirmations,
                numWords,
                extraArgs
            );
        }

        s_requests[requestId] = RequestStatus({
            paid: reqPrice,
            fulfilled: false,
            randomWords: new uint256[](0),
            native: enableNativePayment
        });
        requestIds.push(requestId);
        lastRequestId = requestId;
        emit RequestSent(requestId, numWords);
    }

    // Wrapper consumers require memory, unlike subscription consumers' calldata.
    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords)
        internal
        override
    {
        RequestStatus storage request = s_requests[requestId];
        if (request.paid == 0 || request.fulfilled || randomWords.length == 0) return;
        request.fulfilled = true;
        request.randomWords = randomWords;
        emit RequestFulfilled(requestId, randomWords, request.paid);
    }

    function getRequestStatus(uint256 requestId)
        external
        view
        returns (uint256 paid, bool fulfilled, uint256[] memory randomWords)
    {
        if (s_requests[requestId].paid == 0) revert RequestNotFound(requestId);
        RequestStatus memory request = s_requests[requestId];
        return (request.paid, request.fulfilled, request.randomWords);
    }

    // i_linkToken is inherited from VRFV2PlusWrapperConsumerBase.
    function withdrawLink(address beneficiary, uint256 amount) external onlyOwner {
        if (!i_linkToken.transfer(beneficiary, amount)) revert WithdrawFailed();
    }

    function withdrawNative(address beneficiary, uint256 amount) external onlyOwner {
        (bool success,) = beneficiary.call{value: amount}("");
        if (!success) revert WithdrawFailed();
    }

    receive() external payable {}
}
```

Tune `callbackGasLimit` to measured callback work. `requestConfirmations` defaults to 3 but should reflect value at risk. `numWords` is 2 here and cannot exceed `VRFV2Wrapper.getConfig().maxNumWords`.

## Differences from Subscriptions

| Aspect | Subscription | Direct funding |
|---|---|---|
| Base | `VRFConsumerBaseV2Plus` | `VRFV2PlusWrapperConsumerBase` |
| Funds | Shared subscription | Consumer balance |
| Billing | Post-fulfillment, actual callback gas | Upfront estimate; full callback gas limit |
| Return | `uint256 requestId` | `(uint256 requestId, uint256 reqPrice)` |
| Constructor | Coordinator address | Wrapper address only |
| Callback words | `uint256[] calldata` | `uint256[] memory` |
| LINK request | Coordinator `RandomWordsRequest` | `requestRandomness(..., extraArgs)` |
| Native request | `ExtraArgsV1({nativePayment: true})` | `requestRandomnessPayInNative(..., extraArgs)` |

The V2 constructor `VRFV2WrapperConsumerBase(linkAddress, wrapperAddress)` must not be used. The v2.5 constructor is `VRFV2PlusWrapperConsumerBase(wrapperAddress)`.

## Funding and Accounting

Transfer sufficient ERC-677 LINK or native coin to the consumer before requesting. The recorded `paid` value is the upfront request price and supports accounting. Use [`billing.md`](billing.md) for formulas and PegSwap requirements.

Make `wrapperAddress` the consumer's only constructor argument and pass it to `VRFV2PlusWrapperConsumerBase`; never hardcode a wrapper address in the contract. Whenever an answer supplies a live wrapper address, place this instruction adjacent to the value, even if copied from an embedded reference: `Verify this value against https://docs.chain.link/vrf/v2-5/supported-networks.md immediately before deploying.`
