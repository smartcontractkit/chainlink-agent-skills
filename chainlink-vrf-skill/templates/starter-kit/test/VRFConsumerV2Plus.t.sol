// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Test} from "forge-std/Test.sol";
import {VRFConsumerV2Plus} from "../src/VRFConsumerV2Plus.sol";
import {VRFCoordinatorV2_5Mock} from "@chainlink/contracts/src/v0.8/vrf/mocks/VRFCoordinatorV2_5Mock.sol";

contract VRFConsumerV2PlusTest is Test {
    // Mock coordinator configuration.
    uint96 public constant BASE_FEE = 0.1 ether;
    uint96 public constant GAS_PRICE_LINK = 1e9;
    int256 public constant WEI_PER_UNIT_LINK = 4e15;
    uint256 public constant FUND_AMOUNT = 100 ether;

    bytes32 public constant KEY_HASH = keccak256("test-key-hash");

    VRFCoordinatorV2_5Mock public coordinator;
    VRFConsumerV2Plus public consumer;
    uint256 public subId;

    event RequestSent(uint256 requestId, uint32 numWords);
    event RequestFulfilled(uint256 requestId, uint256[] randomWords);

    function setUp() public {
        coordinator = new VRFCoordinatorV2_5Mock(BASE_FEE, GAS_PRICE_LINK, WEI_PER_UNIT_LINK);
        subId = coordinator.createSubscription();
        coordinator.fundSubscription(subId, FUND_AMOUNT);
        consumer = new VRFConsumerV2Plus(address(coordinator), subId, KEY_HASH);
        coordinator.addConsumer(subId, address(consumer));
    }

    function testCanRequestRandomness() public {
        uint256 requestId = consumer.requestRandomWords(false);
        assertEq(consumer.lastRequestId(), requestId);

        (bool fulfilled,) = consumer.getRequestStatus(requestId);
        assertFalse(fulfilled);
    }

    function testCanGetRandomResponse() public {
        uint256 requestId = consumer.requestRandomWords(false);

        // When testing locally you MUST call fulfillRandomWords yourself, since there is no
        // Chainlink VRF node on your local network.
        coordinator.fulfillRandomWords(requestId, address(consumer));

        (bool fulfilled, uint256[] memory randomWords) = consumer.getRequestStatus(requestId);
        assertTrue(fulfilled);
        assertEq(randomWords.length, consumer.numWords());
    }

    function testEmitsEventOnRequest() public {
        // Topics are unknown ahead of time; check that the event with numWords is emitted.
        vm.expectEmit(false, false, false, true);
        emit RequestSent(1, consumer.numWords());
        consumer.requestRandomWords(false);
    }

    function testOnlyOwnerCanRequest() public {
        vm.prank(address(0xBEEF));
        vm.expectRevert();
        consumer.requestRandomWords(false);
    }
}
