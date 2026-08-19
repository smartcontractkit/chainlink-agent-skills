# CCIP Solidity Examples

Contract-first floor for CCIP v1.6.x EVM. Verify against current official tutorials when fetch is available.

## Imports

```solidity
import {IRouterClient} from "@chainlink/contracts-ccip/contracts/interfaces/IRouterClient.sol";
import {CCIPReceiver} from "@chainlink/contracts-ccip/contracts/applications/CCIPReceiver.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {EnumerableMap} from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
```

## Concrete senders

`DataSender` is a copyable data-only sender with complete router/LINK setup and destination allowlisting. The optional concrete `TokenSender` adds only the token message shape. Generic senders: native/LINK fees, refund excess native, owner recovery.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {IRouterClient} from "@chainlink/contracts-ccip/contracts/interfaces/IRouterClient.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract DataSender is OwnerIsCreator {
    using SafeERC20 for IERC20;

    error NotEnoughBalance(uint256 currentBalance, uint256 calculatedFees);
    error DestinationChainNotAllowed(uint64 destinationChainSelector);

    event MessageSent(bytes32 indexed messageId, uint64 indexed destinationChainSelector,
        address receiver, string text, address feeToken, uint256 fees);

    IRouterClient public immutable router;
    IERC20 public immutable link;
    mapping(uint64 => bool) public allowlistedDestinationChains;

    constructor(address routerAddress, address linkAddress) {
        router = IRouterClient(routerAddress);
        link = IERC20(linkAddress);
    }

    modifier onlyAllowedDestination(uint64 selector) {
        if (!allowlistedDestinationChains[selector])
            revert DestinationChainNotAllowed(selector);
        _;
    }

    function allowlistDestinationChain(uint64 selector, bool allowed) external onlyOwner {
        allowlistedDestinationChains[selector] = allowed;
    }

    function quoteFee(uint64 selector, address receiver, string calldata text)
        external view returns (uint256)
    {
        return router.getFee(selector, _dataMessage(receiver, text));
    }

    function sendMessage(uint64 selector, address receiver, string calldata text)
        external onlyOwner onlyAllowedDestination(selector) returns (bytes32 id)
    {
        Client.EVM2AnyMessage memory message = _dataMessage(receiver, text);
        uint256 fees;
        (id, fees) = _quoteApproveSend(selector, message, address(0), 0);
        emit MessageSent(id, selector, receiver, text, address(link), fees);
    }

    function _quoteApproveSend(
        uint64 selector,
        Client.EVM2AnyMessage memory message,
        address token,
        uint256 amount
    ) internal returns (bytes32 messageId, uint256 fees) {
        fees = router.getFee(selector, message);
        uint256 balance = link.balanceOf(address(this));
        if (fees > balance) revert NotEnoughBalance(balance, fees);
        link.forceApprove(address(router), fees);
        if (amount != 0) IERC20(token).forceApprove(address(router), amount);
        messageId = router.ccipSend(selector, message);
    }

    function _dataMessage(address receiver, string memory text)
        internal view returns (Client.EVM2AnyMessage memory)
    {
        return Client.EVM2AnyMessage({
            receiver: abi.encode(receiver),
            data: abi.encode(text),
            tokenAmounts: new Client.EVMTokenAmount[](0),
            extraArgs: Client._argsToBytes(Client.GenericExtraArgsV2({
                gasLimit: 200_000, allowOutOfOrderExecution: true
            })),
            feeToken: address(link)
        });
    }
}

contract TokenSender is DataSender {
    event TokensSent(bytes32 indexed messageId, uint64 indexed destinationChainSelector,
        address receiver, address token, uint256 amount, address feeToken, uint256 fees);

    constructor(address routerAddress, address linkAddress)
        DataSender(routerAddress, linkAddress) {}

    function transferTokens(uint64 selector, address receiver, address token, uint256 amount)
        external onlyOwner onlyAllowedDestination(selector) returns (bytes32 id)
    {
        Client.EVMTokenAmount[] memory amounts = new Client.EVMTokenAmount[](1);
        amounts[0] = Client.EVMTokenAmount({token: token, amount: amount});
        Client.EVM2AnyMessage memory message = Client.EVM2AnyMessage({
            receiver: abi.encode(receiver),
            data: "",
            tokenAmounts: amounts,
            extraArgs: Client._argsToBytes(Client.GenericExtraArgsV2({
                gasLimit: 0, allowOutOfOrderExecution: true
            })),
            feeToken: address(link)
        });
        uint256 fees;
        (id, fees) = _quoteApproveSend(selector, message, token, amount);
        emit TokensSent(id, selector, receiver, token, amount, address(link), fees);
    }
}
```

## Data receiver

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {CCIPReceiver} from "@chainlink/contracts-ccip/contracts/applications/CCIPReceiver.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";

contract DataReceiver is CCIPReceiver, OwnerIsCreator {
    error SourceChainNotAllowed(uint64 selector);
    error SenderNotAllowed(address sender);
    event MessageReceived(bytes32 indexed messageId, uint64 indexed sourceChainSelector,
        address sender, string text);

    mapping(uint64 => bool) public allowlistedSourceChains;
    mapping(address => bool) public allowlistedSenders;
    string private s_lastReceivedText;

    constructor(address router) CCIPReceiver(router) {}

    function allowlistSourceChain(uint64 selector, bool allowed) external onlyOwner {
        allowlistedSourceChains[selector] = allowed;
    }
    function allowlistSender(address sender, bool allowed) external onlyOwner {
        allowlistedSenders[sender] = allowed;
    }
    function _ccipReceive(Client.Any2EVMMessage memory message) internal override {
        address sender = abi.decode(message.sender, (address));
        if (!allowlistedSourceChains[message.sourceChainSelector])
            revert SourceChainNotAllowed(message.sourceChainSelector);
        if (!allowlistedSenders[sender]) revert SenderNotAllowed(sender);
        s_lastReceivedText = abi.decode(message.data, (string));
        emit MessageReceived(message.messageId, message.sourceChainSelector, sender, s_lastReceivedText);
    }
    function getLastReceivedText() external view returns (string memory) {
        return s_lastReceivedText;
    }
}
```

## Defensive programmable token receiver

Concrete try/catch, failed-message storage, and owner recovery prevent business-logic failure from forcing token delivery into a stuck manual-execution state.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {CCIPReceiver} from "@chainlink/contracts-ccip/contracts/applications/CCIPReceiver.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {EnumerableMap} from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";

contract DefensiveTokenReceiver is CCIPReceiver, OwnerIsCreator {
    using EnumerableMap for EnumerableMap.Bytes32ToUintMap;
    using SafeERC20 for IERC20;

    error SourceChainNotAllowed(uint64 sourceChainSelector);
    error SenderNotAllowed(address sender);
    error OnlySelf();
    error MessageNotFailed(bytes32 messageId);
    error NoTokensReceived();
    enum ErrorCode { RESOLVED, FAILED }

    event MessageReceived(bytes32 indexed messageId, uint64 indexed sourceChainSelector,
        address sender, address token, uint256 tokenAmount, address beneficiary);
    event MessageFailed(bytes32 indexed messageId, bytes reason);
    event MessageRecovered(bytes32 indexed messageId);

    mapping(uint64 => bool) public allowlistedSourceChains;
    mapping(address => bool) public allowlistedSenders;
    mapping(bytes32 => Client.Any2EVMMessage) public s_messageContents;
    mapping(address => uint256) public s_receivedTotals;
    EnumerableMap.Bytes32ToUintMap internal s_failedMessages;

    constructor(address router) CCIPReceiver(router) {}
    modifier onlySelf() {
        if (msg.sender != address(this)) revert OnlySelf();
        _;
    }

    function allowlistSourceChain(uint64 selector, bool allowed) external onlyOwner {
        allowlistedSourceChains[selector] = allowed;
    }
    function allowlistSender(address sender, bool allowed) external onlyOwner {
        allowlistedSenders[sender] = allowed;
    }

    function _ccipReceive(Client.Any2EVMMessage memory message) internal override {
        address sender = abi.decode(message.sender, (address));
        if (!allowlistedSourceChains[message.sourceChainSelector])
            revert SourceChainNotAllowed(message.sourceChainSelector);
        if (!allowlistedSenders[sender]) revert SenderNotAllowed(sender);

        try this.processMessage(message) {
            // Success.
        } catch (bytes memory reason) {
            s_failedMessages.set(message.messageId, uint256(ErrorCode.FAILED));
            s_messageContents[message.messageId] = message;
            emit MessageFailed(message.messageId, reason);
            return;
        }
    }

    function processMessage(Client.Any2EVMMessage calldata message) external onlySelf {
        if (message.destTokenAmounts.length == 0 || message.destTokenAmounts[0].amount == 0)
            revert NoTokensReceived();
        address token = message.destTokenAmounts[0].token;
        uint256 amount = message.destTokenAmounts[0].amount;
        address beneficiary = abi.decode(message.data, (address));
        s_receivedTotals[token] += amount;
        IERC20(token).safeTransfer(beneficiary, amount);
        emit MessageReceived(
            message.messageId,
            message.sourceChainSelector,
            abi.decode(message.sender, (address)),
            token,
            amount,
            beneficiary
        );
    }

    function retryFailedMessage(bytes32 messageId, address tokenReceiver) external onlyOwner {
        if (s_failedMessages.get(messageId) != uint256(ErrorCode.FAILED))
            revert MessageNotFailed(messageId);
        s_failedMessages.set(messageId, uint256(ErrorCode.RESOLVED));
        Client.Any2EVMMessage memory message = s_messageContents[messageId];
        IERC20(message.destTokenAmounts[0].token).safeTransfer(
            tokenReceiver, message.destTokenAmounts[0].amount
        );
        emit MessageRecovered(messageId);
    }
}
```
