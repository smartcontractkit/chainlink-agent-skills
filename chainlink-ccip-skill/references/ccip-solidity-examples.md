# CCIP Solidity Examples

Use this file as the floor for contract-first CCIP workflows. These examples are based on the official CCIP tutorials and represent production-ready patterns for CCIP v1.6.x on EVM.

When documentation-fetching tools are available, verify these patterns against the latest official tutorials. When they are not, use these as the authoritative starting point.

## Table of Contents

1. [Import paths](#import-paths)
2. [Data-only sender](#data-only-sender)
3. [Data-only receiver](#data-only-receiver)
4. [Token transfer sender](#token-transfer-sender)
5. [Defensive programmable token transfer receiver](#defensive-programmable-token-transfer-receiver)

## Import Paths

Core CCIP contracts:

```solidity
import {IRouterClient} from "@chainlink/contracts-ccip/contracts/interfaces/IRouterClient.sol";
import {CCIPReceiver} from "@chainlink/contracts-ccip/contracts/applications/CCIPReceiver.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
```

Access control (from Chainlink contracts):

```solidity
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";
```

Token handling (from OpenZeppelin):

```solidity
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
```

For defensive receivers that need failure tracking:

```solidity
import {EnumerableMap} from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
```

## Data-Only Sender

Minimal sender for arbitrary messaging. Pays fees in LINK. Source: official CCIP getting-started tutorial.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {IRouterClient} from "@chainlink/contracts-ccip/contracts/interfaces/IRouterClient.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract CCIPSender is OwnerIsCreator {
    error NotEnoughBalance(uint256 currentBalance, uint256 calculatedFees);
    error DestinationChainNotAllowed(uint64 destinationChainSelector);

    event MessageSent(
        bytes32 indexed messageId,
        uint64 indexed destinationChainSelector,
        address receiver,
        string text,
        address feeToken,
        uint256 fees
    );

    IRouterClient private s_router;
    IERC20 private s_linkToken;

    mapping(uint64 => bool) public allowlistedDestinationChains;

    constructor(address _router, address _link) {
        s_router = IRouterClient(_router);
        s_linkToken = IERC20(_link);
    }

    modifier onlyAllowlistedDestinationChain(uint64 _destinationChainSelector) {
        if (!allowlistedDestinationChains[_destinationChainSelector])
            revert DestinationChainNotAllowed(_destinationChainSelector);
        _;
    }

    function allowlistDestinationChain(uint64 _destinationChainSelector, bool _allowed) external onlyOwner {
        allowlistedDestinationChains[_destinationChainSelector] = _allowed;
    }

    function sendMessage(
        uint64 destinationChainSelector,
        address receiver,
        string calldata text
    ) external onlyOwner onlyAllowlistedDestinationChain(destinationChainSelector) returns (bytes32 messageId) {
        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(receiver),
            data: abi.encode(text),
            tokenAmounts: new Client.EVMTokenAmount[](0),
            extraArgs: Client._argsToBytes(
                Client.GenericExtraArgsV2({gasLimit: 200_000, allowOutOfOrderExecution: true})
            ),
            feeToken: address(s_linkToken)
        });

        uint256 fees = s_router.getFee(destinationChainSelector, evm2AnyMessage);

        if (fees > s_linkToken.balanceOf(address(this)))
            revert NotEnoughBalance(s_linkToken.balanceOf(address(this)), fees);

        s_linkToken.approve(address(s_router), fees);
        messageId = s_router.ccipSend(destinationChainSelector, evm2AnyMessage);

        emit MessageSent(messageId, destinationChainSelector, receiver, text, address(s_linkToken), fees);
    }
}
```

Key patterns: fee quoting before send, LINK approval to router, destination chain allowlist, owner-only send.

## Data-Only Receiver

Minimal receiver for arbitrary messaging. Validates source chain and sender. Source: official CCIP tutorials.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {CCIPReceiver} from "@chainlink/contracts-ccip/contracts/applications/CCIPReceiver.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";

contract CCIPReceiver_DataOnly is CCIPReceiver, OwnerIsCreator {
    error SourceChainNotAllowed(uint64 sourceChainSelector);
    error SenderNotAllowed(address sender);

    event MessageReceived(
        bytes32 indexed messageId,
        uint64 indexed sourceChainSelector,
        address sender,
        string text
    );

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
        uint64 sourceChainSelector = any2EvmMessage.sourceChainSelector;
        address sender = abi.decode(any2EvmMessage.sender, (address));

        if (!allowlistedSourceChains[sourceChainSelector])
            revert SourceChainNotAllowed(sourceChainSelector);
        if (!allowlistedSenders[sender])
            revert SenderNotAllowed(sender);

        s_lastReceivedText = abi.decode(any2EvmMessage.data, (string));

        emit MessageReceived(any2EvmMessage.messageId, sourceChainSelector, sender, s_lastReceivedText);
    }

    function getLastReceivedText() external view returns (string memory) {
        return s_lastReceivedText;
    }
}
```

Key patterns: source chain allowlist, sender allowlist, router check inherited from CCIPReceiver, payload decode and store.

## Token Transfer Sender

Sender that transfers ERC-20 tokens via CCIP. Pays fees in LINK. Source: official token transfer tutorial.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {IRouterClient} from "@chainlink/contracts-ccip/contracts/interfaces/IRouterClient.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract CCIPTokenSender is OwnerIsCreator {
    using SafeERC20 for IERC20;

    error NotEnoughBalance(uint256 currentBalance, uint256 calculatedFees);
    error DestinationChainNotAllowed(uint64 destinationChainSelector);

    event TokensSent(
        bytes32 indexed messageId,
        uint64 indexed destinationChainSelector,
        address receiver,
        address token,
        uint256 tokenAmount,
        address feeToken,
        uint256 fees
    );

    IRouterClient private s_router;
    IERC20 private s_linkToken;

    mapping(uint64 => bool) public allowlistedDestinationChains;

    constructor(address _router, address _link) {
        s_router = IRouterClient(_router);
        s_linkToken = IERC20(_link);
    }

    modifier onlyAllowlistedDestinationChain(uint64 _destinationChainSelector) {
        if (!allowlistedDestinationChains[_destinationChainSelector])
            revert DestinationChainNotAllowed(_destinationChainSelector);
        _;
    }

    function allowlistDestinationChain(uint64 _destinationChainSelector, bool _allowed) external onlyOwner {
        allowlistedDestinationChains[_destinationChainSelector] = _allowed;
    }

    function transferTokens(
        uint64 destinationChainSelector,
        address receiver,
        address token,
        uint256 amount
    ) external onlyOwner onlyAllowlistedDestinationChain(destinationChainSelector) returns (bytes32 messageId) {
        Client.EVMTokenAmount[] memory tokenAmounts = new Client.EVMTokenAmount[](1);
        tokenAmounts[0] = Client.EVMTokenAmount({token: token, amount: amount});

        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(receiver),
            data: "",
            tokenAmounts: tokenAmounts,
            extraArgs: Client._argsToBytes(
                Client.GenericExtraArgsV2({gasLimit: 0, allowOutOfOrderExecution: true})
            ),
            feeToken: address(s_linkToken)
        });

        uint256 fees = s_router.getFee(destinationChainSelector, evm2AnyMessage);

        if (fees > s_linkToken.balanceOf(address(this)))
            revert NotEnoughBalance(s_linkToken.balanceOf(address(this)), fees);

        s_linkToken.approve(address(s_router), fees);
        IERC20(token).safeApprove(address(s_router), amount);

        messageId = s_router.ccipSend(destinationChainSelector, evm2AnyMessage);

        emit TokensSent(messageId, destinationChainSelector, receiver, token, amount, address(s_linkToken), fees);
    }
}
```

Key patterns: token approval to router before send, fee quoting, gasLimit=0 for token-only (no receiver callback), SafeERC20 for token operations.

## Defensive Programmable Token Transfer Receiver

Receiver that handles both tokens and data with failure recovery. If business logic reverts, tokens are locked safely and can be retried. Source: official defensive programmable token transfer tutorial.

The key insight: a naive receiver that reverts in `_ccipReceive` causes the entire message (including token delivery) to fail and enter a stuck state requiring manual execution. The defensive pattern catches failures, locks tokens, and allows retry.

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

    enum ErrorCode { RESOLVED, FAILED }

    event MessageReceived(bytes32 indexed messageId, uint64 indexed sourceChainSelector, address sender, string text, address token, uint256 tokenAmount);
    event MessageFailed(bytes32 indexed messageId, bytes reason);
    event MessageRecovered(bytes32 indexed messageId);

    mapping(uint64 => bool) public allowlistedSourceChains;
    mapping(address => bool) public allowlistedSenders;
    mapping(bytes32 => Client.Any2EVMMessage) public s_messageContents;
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

    /// @notice Entry point for CCIP messages. Catches failures to prevent token loss.
    function _ccipReceive(Client.Any2EVMMessage memory any2EvmMessage) internal override {
        uint64 sourceChain = any2EvmMessage.sourceChainSelector;
        address sender = abi.decode(any2EvmMessage.sender, (address));

        if (!allowlistedSourceChains[sourceChain]) revert SourceChainNotAllowed(sourceChain);
        if (!allowlistedSenders[sender]) revert SenderNotAllowed(sender);

        try this.processMessage(any2EvmMessage) {
            // Success
        } catch (bytes memory err) {
            s_failedMessages.set(any2EvmMessage.messageId, uint256(ErrorCode.FAILED));
            s_messageContents[any2EvmMessage.messageId] = any2EvmMessage;
            emit MessageFailed(any2EvmMessage.messageId, err);
            return;
        }
    }

    /// @notice Processes the message payload. Called via this.processMessage() so failures are catchable.
    function processMessage(Client.Any2EVMMessage calldata any2EvmMessage) external onlySelf {
        // Decode and handle the payload here.
        // If this reverts, tokens are safe and the message can be retried.
        string memory text = abi.decode(any2EvmMessage.data, (string));

        emit MessageReceived(
            any2EvmMessage.messageId,
            any2EvmMessage.sourceChainSelector,
            abi.decode(any2EvmMessage.sender, (address)),
            text,
            any2EvmMessage.destTokenAmounts[0].token,
            any2EvmMessage.destTokenAmounts[0].amount
        );
    }

    /// @notice Retry a failed message. Only callable by the owner.
    function retryFailedMessage(bytes32 messageId, address tokenReceiver) external onlyOwner {
        if (s_failedMessages.get(messageId) != uint256(ErrorCode.FAILED))
            revert MessageNotFailed(messageId);

        s_failedMessages.set(messageId, uint256(ErrorCode.RESOLVED));

        Client.Any2EVMMessage memory message = s_messageContents[messageId];
        IERC20(message.destTokenAmounts[0].token).safeTransfer(tokenReceiver, message.destTokenAmounts[0].amount);

        emit MessageRecovered(messageId);
    }
}
```

Key patterns: try/catch around `this.processMessage()` so reverts in business logic don't block token delivery, failed message storage for retry, `onlySelf` modifier so `processMessage` can only be called internally, owner-controlled recovery path.
