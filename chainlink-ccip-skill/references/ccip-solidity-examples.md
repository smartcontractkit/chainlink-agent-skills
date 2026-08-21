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

    IRouterClient public immutable s_router;
    IERC20 public immutable s_linkToken;
    mapping(uint64 => bool) public allowlistedDestinationChains;

    constructor(address _router, address _link) {
        s_router = IRouterClient(_router);
        s_linkToken = IERC20(_link);
    }

    modifier onlyAllowedDestination(uint64 _destinationChainSelector) {
        if (!allowlistedDestinationChains[_destinationChainSelector])
            revert DestinationChainNotAllowed(_destinationChainSelector);
        _;
    }

    function allowlistDestinationChain(uint64 _destinationChainSelector, bool _allowed) external onlyOwner {
        allowlistedDestinationChains[_destinationChainSelector] = _allowed;
    }

    function quoteFee(uint64 destinationChainSelector, address receiver, string calldata text)
        external view returns (uint256)
    {
        return s_router.getFee(destinationChainSelector, _dataMessage(receiver, text));
    }

    function sendMessage(uint64 destinationChainSelector, address receiver, string calldata text)
        external onlyOwner onlyAllowedDestination(destinationChainSelector) returns (bytes32 messageId)
    {
        Client.EVM2AnyMessage memory evm2AnyMessage = _dataMessage(receiver, text);
        uint256 fees;
        (messageId, fees) = _quoteApproveSend(destinationChainSelector, evm2AnyMessage, address(0), 0);
        emit MessageSent(messageId, destinationChainSelector, receiver, text, address(s_linkToken), fees);
    }

    function _quoteApproveSend(
        uint64 _destinationChainSelector,
        Client.EVM2AnyMessage memory evm2AnyMessage,
        address token,
        uint256 amount
    ) internal returns (bytes32 messageId, uint256 fees) {
        fees = s_router.getFee(_destinationChainSelector, evm2AnyMessage);
        uint256 balance = s_linkToken.balanceOf(address(this));
        if (fees > balance) revert NotEnoughBalance(balance, fees);
        s_linkToken.forceApprove(address(s_router), fees);
        if (amount != 0) IERC20(token).forceApprove(address(s_router), amount);
        messageId = s_router.ccipSend(_destinationChainSelector, evm2AnyMessage);
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
            feeToken: address(s_linkToken)
        });
    }
}

contract TokenSender is DataSender {
    event TokensSent(bytes32 indexed messageId, uint64 indexed destinationChainSelector,
        address receiver, address token, uint256 amount, address feeToken, uint256 fees);

    constructor(address _router, address _link)
        DataSender(_router, _link) {}

    function transferTokens(uint64 destinationChainSelector, address receiver, address token, uint256 amount)
        external onlyOwner onlyAllowedDestination(destinationChainSelector) returns (bytes32 messageId)
    {
        Client.EVMTokenAmount[] memory tokenAmounts = new Client.EVMTokenAmount[](1);
        tokenAmounts[0] = Client.EVMTokenAmount({token: token, amount: amount});
        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(receiver),
            data: "",
            tokenAmounts: tokenAmounts,
            extraArgs: Client._argsToBytes(Client.GenericExtraArgsV2({
                gasLimit: 0, allowOutOfOrderExecution: true
            })),
            feeToken: address(s_linkToken)
        });
        uint256 fees;
        (messageId, fees) = _quoteApproveSend(destinationChainSelector, evm2AnyMessage, token, amount);
        emit TokensSent(messageId, destinationChainSelector, receiver, token, amount, address(s_linkToken), fees);
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
    error SourceChainNotAllowed(uint64 sourceChainSelector);
    error SenderNotAllowed(address sender);
    event MessageReceived(bytes32 indexed messageId, uint64 indexed sourceChainSelector,
        address sender, string text);

    mapping(uint64 => bool) public allowlistedSourceChains;
    mapping(address => bool) public allowlistedSenders;
    string private s_lastReceivedText;

    constructor(address _router) CCIPReceiver(_router) {}

    function allowlistSourceChain(uint64 _sourceChainSelector, bool _allowed) external onlyOwner {
        allowlistedSourceChains[_sourceChainSelector] = _allowed;
    }
    function allowlistSender(address _sender, bool _allowed) external onlyOwner {
        allowlistedSenders[_sender] = _allowed;
    }
    function _ccipReceive(Client.Any2EVMMessage memory any2EvmMessage) internal override {
        address sender = abi.decode(any2EvmMessage.sender, (address));
        if (!allowlistedSourceChains[any2EvmMessage.sourceChainSelector])
            revert SourceChainNotAllowed(any2EvmMessage.sourceChainSelector);
        if (!allowlistedSenders[sender]) revert SenderNotAllowed(sender);
        s_lastReceivedText = abi.decode(any2EvmMessage.data, (string));
        emit MessageReceived(any2EvmMessage.messageId, any2EvmMessage.sourceChainSelector, sender, s_lastReceivedText);
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

    constructor(address _router) CCIPReceiver(_router) {}
    modifier onlySelf() {
        if (msg.sender != address(this)) revert OnlySelf();
        _;
    }

    function allowlistSourceChain(uint64 _sourceChainSelector, bool _allowed) external onlyOwner {
        allowlistedSourceChains[_sourceChainSelector] = _allowed;
    }
    function allowlistSender(address _sender, bool _allowed) external onlyOwner {
        allowlistedSenders[_sender] = _allowed;
    }

    function _ccipReceive(Client.Any2EVMMessage memory any2EvmMessage) internal override {
        address sender = abi.decode(any2EvmMessage.sender, (address));
        if (!allowlistedSourceChains[any2EvmMessage.sourceChainSelector])
            revert SourceChainNotAllowed(any2EvmMessage.sourceChainSelector);
        if (!allowlistedSenders[sender]) revert SenderNotAllowed(sender);

        try this.processMessage(any2EvmMessage) {
            // Success.
        } catch (bytes memory reason) {
            s_failedMessages.set(any2EvmMessage.messageId, uint256(ErrorCode.FAILED));
            s_messageContents[any2EvmMessage.messageId] = any2EvmMessage;
            emit MessageFailed(any2EvmMessage.messageId, reason);
            return;
        }
    }

    function processMessage(Client.Any2EVMMessage calldata any2EvmMessage) external onlySelf {
        if (any2EvmMessage.destTokenAmounts.length == 0 || any2EvmMessage.destTokenAmounts[0].amount == 0)
            revert NoTokensReceived();
        address token = any2EvmMessage.destTokenAmounts[0].token;
        uint256 amount = any2EvmMessage.destTokenAmounts[0].amount;
        address beneficiary = abi.decode(any2EvmMessage.data, (address));
        s_receivedTotals[token] += amount;
        IERC20(token).safeTransfer(beneficiary, amount);
        emit MessageReceived(
            any2EvmMessage.messageId,
            any2EvmMessage.sourceChainSelector,
            abi.decode(any2EvmMessage.sender, (address)),
            token,
            amount,
            beneficiary
        );
    }

    function retryFailedMessage(bytes32 messageId, address tokenReceiver) external onlyOwner {
        if (s_failedMessages.get(messageId) != uint256(ErrorCode.FAILED))
            revert MessageNotFailed(messageId);
        s_failedMessages.set(messageId, uint256(ErrorCode.RESOLVED));
        Client.Any2EVMMessage memory any2EvmMessage = s_messageContents[messageId];
        IERC20(any2EvmMessage.destTokenAmounts[0].token).safeTransfer(
            tokenReceiver, any2EvmMessage.destTokenAmounts[0].amount
        );
        emit MessageRecovered(messageId);
    }
}
```
