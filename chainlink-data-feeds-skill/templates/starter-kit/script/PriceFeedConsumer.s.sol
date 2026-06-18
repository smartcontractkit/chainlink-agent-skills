// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {Script} from "forge-std/Script.sol";
import {PriceFeedConsumer} from "../src/PriceFeedConsumer.sol";
import {MockV3Aggregator} from "../test/mocks/MockV3Aggregator.sol";

contract DeployPriceFeedConsumer is Script {
    uint8 internal constant DECIMALS = 8;
    int256 internal constant INITIAL_ANSWER = 2000e8;
    uint256 internal constant STALENESS_THRESHOLD = 3600;

    address internal constant SEPOLIA_ETH_USD_FEED = 0x694AA1769357215DE4FAC081bf1f309aDC325306;

    function run() external returns (PriceFeedConsumer) {
        vm.startBroadcast();
        address priceFeed =
            block.chainid == 11155111 ? SEPOLIA_ETH_USD_FEED : address(new MockV3Aggregator(DECIMALS, INITIAL_ANSWER));
        PriceFeedConsumer consumer = new PriceFeedConsumer(priceFeed, STALENESS_THRESHOLD);
        vm.stopBroadcast();

        return consumer;
    }
}
