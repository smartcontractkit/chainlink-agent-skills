// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {Test} from "forge-std/Test.sol";
import {PriceFeedConsumer} from "../src/PriceFeedConsumer.sol";
import {MockV3Aggregator} from "./mocks/MockV3Aggregator.sol";

contract PriceFeedConsumerTest is Test {
    uint8 public constant DECIMALS = 8;
    int256 public constant INITIAL_ANSWER = 2000e8;
    uint256 public constant STALENESS_THRESHOLD = 3600;

    PriceFeedConsumer public priceFeedConsumer;
    MockV3Aggregator public mockV3Aggregator;

    function setUp() public {
        mockV3Aggregator = new MockV3Aggregator(DECIMALS, INITIAL_ANSWER);
        priceFeedConsumer = new PriceFeedConsumer(address(mockV3Aggregator), STALENESS_THRESHOLD);
    }

    function testConsumerReturnsStartingValue() public view {
        int256 price = priceFeedConsumer.getLatestPrice();

        assertEq(price, INITIAL_ANSWER);
    }

    function testConsumerReturnsFeedDecimals() public view {
        assertEq(priceFeedConsumer.getDecimals(), DECIMALS);
    }

    function testConsumerRevertsOnStalePrice() public {
        vm.warp(block.timestamp + STALENESS_THRESHOLD + 1);

        vm.expectRevert();
        priceFeedConsumer.getLatestPrice();
    }

    function testConsumerRevertsOnInvalidPrice() public {
        mockV3Aggregator.updateAnswer(0);

        vm.expectRevert();
        priceFeedConsumer.getLatestPrice();
    }
}
