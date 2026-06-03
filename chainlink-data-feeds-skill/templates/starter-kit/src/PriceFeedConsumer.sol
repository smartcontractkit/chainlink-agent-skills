// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

/**
 * @title PriceFeedConsumer
 * @notice Reads the latest answer from a Chainlink Data Feed with basic safety checks.
 */
contract PriceFeedConsumer {
    AggregatorV3Interface internal immutable priceFeed;
    uint256 public immutable stalenessThreshold;

    error IncompleteRound();
    error StalePrice(uint256 updatedAt);
    error InvalidPrice(int256 price);

    constructor(address _priceFeed, uint256 _stalenessThreshold) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        stalenessThreshold = _stalenessThreshold;
    }

    /**
     * @notice Returns the latest validated price.
     * @return latest price using the feed's decimals.
     */
    function getLatestPrice() public view returns (int256) {
        (, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();

        if (updatedAt == 0) {
            revert IncompleteRound();
        }
        if (block.timestamp - updatedAt > stalenessThreshold) {
            revert StalePrice(updatedAt);
        }
        if (price <= 0) {
            revert InvalidPrice(price);
        }

        return price;
    }

    /**
     * @notice Returns the number of decimals used by the feed answer.
     * @return feed decimals.
     */
    function getDecimals() public view returns (uint8) {
        return priceFeed.decimals();
    }

    /**
     * @notice Returns the Price Feed address.
     * @return Price Feed contract.
     */
    function getPriceFeed() public view returns (AggregatorV3Interface) {
        return priceFeed;
    }
}
