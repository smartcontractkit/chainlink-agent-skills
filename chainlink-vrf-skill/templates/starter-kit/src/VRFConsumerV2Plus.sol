// SPDX-License-Identifier: MIT
// An example of a consumer contract that relies on a VRF v2.5 subscription for funding.
pragma solidity ^0.8.19;

import {VRFConsumerBaseV2Plus} from "@chainlink/contracts/src/v0.8/vrf/dev/VRFConsumerBaseV2Plus.sol";
import {VRFV2PlusClient} from "@chainlink/contracts/src/v0.8/vrf/dev/libraries/VRFV2PlusClient.sol";

/**
 * @title VRFConsumerV2Plus
 * @notice A Chainlink VRF v2.5 subscription consumer that requests and stores random words.
 * @dev Uses VRFConsumerBaseV2Plus (v2.5). The legacy VRFConsumerBaseV2 base, uint64 subscription
 *      IDs, and positional requestRandomWords arguments do not compile against current coordinators.
 */
contract VRFConsumerV2Plus is VRFConsumerBaseV2Plus {
    event RequestSent(uint256 requestId, uint32 numWords);
    event RequestFulfilled(uint256 requestId, uint256[] randomWords);

    struct RequestStatus {
        bool fulfilled;
        bool exists;
        uint256[] randomWords;
    }

    // requestId => RequestStatus
    mapping(uint256 => RequestStatus) public s_requests;

    // Your subscription ID. uint256 in v2.5 (was uint64 in V2).
    uint256 public s_subscriptionId;

    // Past request IDs and the most recent one.
    uint256[] public requestIds;
    uint256 public lastRequestId;

    // The gas lane to use, which specifies the maximum gas price to bump to.
    // Copy the key hash for your network from the Chainlink docs / supported-networks reference.
    bytes32 public keyHash;

    // Depends on the number of requested values you want sent to fulfillRandomWords().
    // Storing each word costs about 20,000 gas, so 100,000 is a safe default for this example.
    // Test and adjust this limit based on the network, request size, and callback processing.
    uint32 public callbackGasLimit = 100_000;

    // The default is 3, but you can set this higher for more security against reorgs.
    uint16 public requestConfirmations = 3;

    // For this example, retrieve 2 random values in one request.
    // Cannot exceed VRFCoordinatorV2_5.MAX_NUM_WORDS.
    uint32 public numWords = 2;

    /**
     * @notice Constructor inherits VRFConsumerBaseV2Plus.
     * @param vrfCoordinator the VRF coordinator address for your network.
     * @param subscriptionId the subscription ID that this contract uses for funding requests.
     * @param _keyHash the gas lane to use, which specifies the maximum gas price to bump to.
     */
    constructor(address vrfCoordinator, uint256 subscriptionId, bytes32 _keyHash)
        VRFConsumerBaseV2Plus(vrfCoordinator)
    {
        s_subscriptionId = subscriptionId;
        keyHash = _keyHash;
    }

    /**
     * @notice Requests randomness from the VRF coordinator.
     * @dev Assumes the subscription is funded sufficiently and this contract is an approved consumer.
     * @param enableNativePayment true = pay in native coin, false = pay in LINK. Pass true only if
     *        the subscription is funded with native coin.
     */
    function requestRandomWords(bool enableNativePayment) external onlyOwner returns (uint256 requestId) {
        // Will revert if the subscription is not set and funded.
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
        s_requests[requestId] = RequestStatus({randomWords: new uint256[](0), exists: true, fulfilled: false});
        requestIds.push(requestId);
        lastRequestId = requestId;
        emit RequestSent(requestId, numWords);
        return requestId;
    }

    /**
     * @notice Callback used by the VRF coordinator to deliver randomness.
     * @dev v2.5 requires the random words to be `calldata` (V2 used `memory`).
     * @param _requestId id of the request.
     * @param _randomWords array of random results from the VRF coordinator.
     */
    function fulfillRandomWords(uint256 _requestId, uint256[] calldata _randomWords) internal override {
        require(s_requests[_requestId].exists, "request not found");
        s_requests[_requestId].fulfilled = true;
        s_requests[_requestId].randomWords = _randomWords;
        emit RequestFulfilled(_requestId, _randomWords);
    }

    /**
     * @notice Returns the fulfillment status and random words for a request.
     */
    function getRequestStatus(uint256 _requestId)
        external
        view
        returns (bool fulfilled, uint256[] memory randomWords)
    {
        require(s_requests[_requestId].exists, "request not found");
        RequestStatus memory request = s_requests[_requestId];
        return (request.fulfilled, request.randomWords);
    }
}
