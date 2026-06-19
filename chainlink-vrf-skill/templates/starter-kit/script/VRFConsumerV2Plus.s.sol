// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script} from "forge-std/Script.sol";
import {VRFConsumerV2Plus} from "../src/VRFConsumerV2Plus.sol";
import {VRFCoordinatorV2_5Mock} from "@chainlink/contracts/src/v0.8/vrf/mocks/VRFCoordinatorV2_5Mock.sol";

/**
 * @notice Deploys VRFConsumerV2Plus.
 *
 * On Ethereum Sepolia (chainid 11155111) it wires the consumer to the live VRF v2.5 coordinator and
 * 500 gwei key hash, reading the subscription ID from the SUBSCRIPTION_ID env var. Create and fund a
 * subscription at https://vrf.chain.link, then add the deployed contract as a consumer.
 *
 * On any other chain (e.g. a local Anvil node) it deploys a VRFCoordinatorV2_5Mock, creates and funds
 * a subscription, deploys the consumer, and adds it as a consumer so the project is runnable end-to-end.
 *
 * Always verify coordinator addresses and key hashes against https://docs.chain.link/vrf/v2-5/supported-networks
 * before deploying.
 */
contract DeployVRFConsumerV2Plus is Script {
    // Ethereum Sepolia VRF v2.5 configuration.
    address internal constant SEPOLIA_VRF_COORDINATOR = 0x9DdfaCa8183c41ad55329BdeeD9F6A8d53168B1B;
    bytes32 internal constant SEPOLIA_KEY_HASH_500_GWEI =
        0x787d74caea10b2b357790d5b5247c2f63d1d91572a9846f780606e4d953677ae;

    // Local mock configuration.
    uint96 internal constant BASE_FEE = 0.1 ether;
    uint96 internal constant GAS_PRICE_LINK = 1e9;
    int256 internal constant WEI_PER_UNIT_LINK = 4e15;
    uint256 internal constant FUND_AMOUNT = 100 ether;

    function run() external returns (VRFConsumerV2Plus consumer) {
        if (block.chainid == 11155111) {
            uint256 subscriptionId = vm.envUint("SUBSCRIPTION_ID");

            vm.startBroadcast();
            consumer = new VRFConsumerV2Plus(SEPOLIA_VRF_COORDINATOR, subscriptionId, SEPOLIA_KEY_HASH_500_GWEI);
            vm.stopBroadcast();
        } else {
            vm.startBroadcast();
            VRFCoordinatorV2_5Mock coordinator =
                new VRFCoordinatorV2_5Mock(BASE_FEE, GAS_PRICE_LINK, WEI_PER_UNIT_LINK);
            uint256 subscriptionId = coordinator.createSubscription();
            coordinator.fundSubscription(subscriptionId, FUND_AMOUNT);
            consumer = new VRFConsumerV2Plus(address(coordinator), subscriptionId, bytes32(0));
            coordinator.addConsumer(subscriptionId, address(consumer));
            vm.stopBroadcast();
        }

        return consumer;
    }
}
