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

`DataSender` is a copyable data-only sender with complete router/LINK setup, a destination allowlist, an explicit router-supported-chain check before every send, and no token branch. `TokenSender` adds only the token-only message shape: empty data, zero destination gas, zero-address/zero-amount checks, an allowance that never collides when the transfer token is also the fee token, and a passive `TokenReceiver` with no CCIP callback. `TokenDataSender` is the complete reusable programmable data-plus-token sender: nonzero destination gas, a raw `bytes` payload alongside the token amount, and the same zero-input checks and non-colliding allowance handling as `TokenSender`; preserve it in full and pass `data` through unmodified, so the caller's ABI encoding must match the selected receiver. Three separate receiver patterns follow, each with a pair-bound source-selector-and-sender allowlist (never two independent lists): `DataReceiver` (data-only), `TokenDataReceiver` (small/auditable programmable data-plus-token, no self-call/try-catch/recovery), and `DefensiveTokenReceiver` (active data-plus-token callback whose business logic may itself revert). Use `TokenDataReceiver` for a plain programmable/data-plus-token request; use `DefensiveTokenReceiver` whenever the request says secure, secured, defensive, or callback-capable. Use the passive `TokenReceiver` only for an explicitly token-only/no-callback destination. Emit one compile-coherent final sender, never a broken draft followed by a corrected snippet. Generic senders: native/LINK fees, refund excess native, owner recovery, and the same router-supported-chain check before send.

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
    error DestinationChainNotSupported(uint64 destinationChainSelector);
    error ZeroAddress();
    error ZeroAmount();

    event MessageSent(bytes32 indexed messageId, uint64 indexed destinationChainSelector,
        address receiver, string text, address feeToken, uint256 fees);

    IRouterClient public immutable s_router;
    IERC20 public immutable s_linkToken;
    mapping(uint64 => bool) public allowlistedDestinationChains;

    constructor(address _router, address _link) {
        if (_router == address(0) || _link == address(0)) revert ZeroAddress();
        s_router = IRouterClient(_router);
        s_linkToken = IERC20(_link);
    }

    modifier onlyAllowedDestination(uint64 _destinationChainSelector) {
        if (!s_router.isChainSupported(_destinationChainSelector))
            revert DestinationChainNotSupported(_destinationChainSelector);
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
        if (!s_router.isChainSupported(destinationChainSelector))
            revert DestinationChainNotSupported(destinationChainSelector);
        return s_router.getFee(destinationChainSelector, _dataMessage(receiver, text));
    }

    function sendMessage(uint64 destinationChainSelector, address receiver, string calldata text)
        external onlyOwner onlyAllowedDestination(destinationChainSelector) returns (bytes32 messageId)
    {
        Client.EVM2AnyMessage memory evm2AnyMessage = _dataMessage(receiver, text);
        uint256 fees;
        (messageId, fees) = _quoteAndSend(destinationChainSelector, evm2AnyMessage);
        emit MessageSent(messageId, destinationChainSelector, receiver, text, address(s_linkToken), fees);
    }

    function _quoteAndSend(
        uint64 _destinationChainSelector,
        Client.EVM2AnyMessage memory evm2AnyMessage
    ) internal returns (bytes32 messageId, uint256 fees) {
        fees = s_router.getFee(_destinationChainSelector, evm2AnyMessage);
        uint256 balance = s_linkToken.balanceOf(address(this));
        if (fees > balance) revert NotEnoughBalance(balance, fees);
        s_linkToken.forceApprove(address(s_router), fees);
        messageId = s_router.ccipSend(_destinationChainSelector, evm2AnyMessage);
    }

    function _dataMessage(address receiver, string memory text)
        internal view returns (Client.EVM2AnyMessage memory)
    {
        if (receiver == address(0)) revert ZeroAddress();
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
    using SafeERC20 for IERC20;

    event TokensSent(bytes32 indexed messageId, uint64 indexed destinationChainSelector,
        address receiver, address token, uint256 amount, address feeToken, uint256 fees);

    constructor(address _router, address _link)
        DataSender(_router, _link) {}

    function transferTokens(uint64 destinationChainSelector, address receiver, address token, uint256 amount)
        external onlyOwner onlyAllowedDestination(destinationChainSelector) returns (bytes32 messageId)
    {
        if (receiver == address(0) || token == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();

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
        uint256 fees = s_router.getFee(destinationChainSelector, evm2AnyMessage);
        uint256 balance = s_linkToken.balanceOf(address(this));
        if (fees > balance) revert NotEnoughBalance(balance, fees);

        // forceApprove sets an exact allowance, so approving LINK for `fees` and then
        // the transfer token for `amount` would silently overwrite one another when the
        // transfer token is LINK itself; combine them into a single approval in that case.
        if (token == address(s_linkToken)) {
            s_linkToken.forceApprove(address(s_router), fees + amount);
        } else {
            s_linkToken.forceApprove(address(s_router), fees);
            IERC20(token).forceApprove(address(s_router), amount);
        }
        messageId = s_router.ccipSend(destinationChainSelector, evm2AnyMessage);
        emit TokensSent(messageId, destinationChainSelector, receiver, token, amount, address(s_linkToken), fees);
    }
}

contract TokenDataSender is DataSender {
    using SafeERC20 for IERC20;

    event TokenDataSent(bytes32 indexed messageId, uint64 indexed destinationChainSelector,
        address receiver, address token, uint256 amount, address feeToken, uint256 fees);

    constructor(address _router, address _link)
        DataSender(_router, _link) {}

    // `data` is passed through unmodified: the caller must ABI-encode it to match
    // whatever the destination receiver expects to decode, since the two receiver
    // shapes below use different payload schemas. Pairing with `TokenDataReceiver`
    // (stores `data` raw, no decode): any opaque `bytes`, for example `abi.encode("note")`.
    // Pairing with `DefensiveTokenReceiver` (decodes `data` as the token beneficiary):
    // it must be exactly `abi.encode(<beneficiary address>)`.
    function sendTokenAndData(
        uint64 destinationChainSelector,
        address receiver,
        address token,
        uint256 amount,
        bytes calldata data
    ) external onlyOwner onlyAllowedDestination(destinationChainSelector) returns (bytes32 messageId) {
        if (receiver == address(0) || token == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();

        Client.EVMTokenAmount[] memory tokenAmounts = new Client.EVMTokenAmount[](1);
        tokenAmounts[0] = Client.EVMTokenAmount({token: token, amount: amount});
        Client.EVM2AnyMessage memory evm2AnyMessage = Client.EVM2AnyMessage({
            receiver: abi.encode(receiver),
            data: data,
            tokenAmounts: tokenAmounts,
            extraArgs: Client._argsToBytes(Client.GenericExtraArgsV2({
                gasLimit: 200_000, allowOutOfOrderExecution: true
            })),
            feeToken: address(s_linkToken)
        });
        uint256 fees = s_router.getFee(destinationChainSelector, evm2AnyMessage);
        uint256 balance = s_linkToken.balanceOf(address(this));
        if (fees > balance) revert NotEnoughBalance(balance, fees);

        // Same LINK-as-transfer-token allowance collision as `TokenSender`: combine into
        // one approval when the transfer token is also the fee token.
        if (token == address(s_linkToken)) {
            s_linkToken.forceApprove(address(s_router), fees + amount);
        } else {
            s_linkToken.forceApprove(address(s_router), fees);
            IERC20(token).forceApprove(address(s_router), amount);
        }
        messageId = s_router.ccipSend(destinationChainSelector, evm2AnyMessage);
        emit TokenDataSent(messageId, destinationChainSelector, receiver, token, amount, address(s_linkToken), fees);
    }
}

contract TokenReceiver is OwnerIsCreator {
    using SafeERC20 for IERC20;

    error ZeroAddress();
    error ZeroAmount();

    function recoverToken(address token, address recipient, uint256 amount) external onlyOwner {
        if (token == address(0) || recipient == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        IERC20(token).safeTransfer(recipient, amount);
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
    error SourceSenderNotAllowed(uint64 sourceChainSelector, address sender);
    error ZeroAddress();
    event MessageReceived(bytes32 indexed messageId, uint64 indexed sourceChainSelector,
        address sender, string text);

    // Pair-bound: an allowed sender is scoped to one source chain, not global.
    mapping(uint64 => mapping(address => bool)) public allowlistedSourceSenders;
    string private s_lastReceivedText;

    constructor(address _router) CCIPReceiver(_router) {
        if (_router == address(0)) revert ZeroAddress();
    }

    function allowlistSourceSender(uint64 _sourceChainSelector, address _sender, bool _allowed) external onlyOwner {
        allowlistedSourceSenders[_sourceChainSelector][_sender] = _allowed;
    }
    function _ccipReceive(Client.Any2EVMMessage memory any2EvmMessage) internal override {
        address sender = abi.decode(any2EvmMessage.sender, (address));
        if (!allowlistedSourceSenders[any2EvmMessage.sourceChainSelector][sender])
            revert SourceSenderNotAllowed(any2EvmMessage.sourceChainSelector, sender);
        s_lastReceivedText = abi.decode(any2EvmMessage.data, (string));
        emit MessageReceived(any2EvmMessage.messageId, any2EvmMessage.sourceChainSelector, sender, s_lastReceivedText);
    }
    function getLastReceivedText() external view returns (string memory) {
        return s_lastReceivedText;
    }
}
```

## Small programmable receiver

A plain, auditable token-plus-data receiver for requests that do not ask for defensive failure handling: router authentication from `CCIPReceiver`, a source-selector-and-sender pair-bound allowlist (not two independent lists), an allowed-token set, and no self-call, try/catch, or recovery. The allowlists, rejection of empty/zero token entries, and loop accounting for every received token are mandatory correctness and asset-safety controls—not speculative business-logic complexity—so briefly explain why they remain even in the small version.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {CCIPReceiver} from "@chainlink/contracts-ccip/contracts/applications/CCIPReceiver.sol";
import {Client} from "@chainlink/contracts-ccip/contracts/libraries/Client.sol";
import {OwnerIsCreator} from "@chainlink/contracts/src/v0.8/shared/access/OwnerIsCreator.sol";

contract TokenDataReceiver is CCIPReceiver, OwnerIsCreator {
    error SourceSenderNotAllowed(uint64 sourceChainSelector, address sender);
    error ZeroAddress();
    error NoTokensReceived();
    error TokenNotAllowed(address token);
    error ZeroTokenAmount(address token);

    event MessageReceived(bytes32 indexed messageId, uint64 indexed sourceChainSelector,
        address sender, address token, uint256 amount, bytes data);

    // Pair-bound: an allowed sender is scoped to one source chain, not global.
    mapping(uint64 => mapping(address => bool)) public allowlistedSourceSenders;
    mapping(address => bool) public allowlistedTokens;
    mapping(address => uint256) public receivedTotals;
    bytes public lastData;

    constructor(address _router) CCIPReceiver(_router) {
        if (_router == address(0)) revert ZeroAddress();
    }

    function allowlistSourceSender(uint64 _sourceChainSelector, address _sender, bool _allowed) external onlyOwner {
        allowlistedSourceSenders[_sourceChainSelector][_sender] = _allowed;
    }

    function allowlistToken(address _token, bool _allowed) external onlyOwner {
        if (_token == address(0)) revert ZeroAddress();
        allowlistedTokens[_token] = _allowed;
    }

    function _ccipReceive(Client.Any2EVMMessage memory any2EvmMessage) internal override {
        address sender = abi.decode(any2EvmMessage.sender, (address));
        if (!allowlistedSourceSenders[any2EvmMessage.sourceChainSelector][sender])
            revert SourceSenderNotAllowed(any2EvmMessage.sourceChainSelector, sender);
        if (any2EvmMessage.destTokenAmounts.length == 0) revert NoTokensReceived();

        lastData = any2EvmMessage.data;
        for (uint256 i; i < any2EvmMessage.destTokenAmounts.length; ++i) {
            Client.EVMTokenAmount memory received = any2EvmMessage.destTokenAmounts[i];
            if (!allowlistedTokens[received.token]) revert TokenNotAllowed(received.token);
            if (received.amount == 0) revert ZeroTokenAmount(received.token);
            receivedTotals[received.token] += received.amount;
            emit MessageReceived(
                any2EvmMessage.messageId,
                any2EvmMessage.sourceChainSelector,
                sender,
                received.token,
                received.amount,
                any2EvmMessage.data
            );
        }
    }
}
```

## Defensive programmable token receiver

This active callback receiver is the default for requests that say secure, secured, defensive, or callback-capable. Router authentication, pair-bound source authorization, allowed-token validation, complete token-amount accounting, concrete try/catch, failed-message storage, and owner recovery prevent business-logic failure from forcing token delivery into a stuck manual-execution state. Never replace this requested shape with the passive token-only vault.

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

    error SourceSenderNotAllowed(uint64 sourceChainSelector, address sender);
    error ZeroAddress();
    error OnlySelf();
    error MessageNotFailed(bytes32 messageId);
    error NoTokensReceived();
    error TokenNotAllowed(address token);
    error ZeroTokenAmount(address token);
    enum ErrorCode { RESOLVED, FAILED }

    event MessageReceived(bytes32 indexed messageId, uint64 indexed sourceChainSelector,
        address sender, address token, uint256 tokenAmount, address beneficiary);
    event MessageFailed(bytes32 indexed messageId, bytes reason);
    event MessageRecovered(bytes32 indexed messageId);

    // Pair-bound: an allowed sender is scoped to one source chain, not global.
    mapping(uint64 => mapping(address => bool)) public allowlistedSourceSenders;
    mapping(address => bool) public allowlistedTokens;
    mapping(bytes32 => Client.Any2EVMMessage) public s_messageContents;
    mapping(address => uint256) public s_receivedTotals;
    EnumerableMap.Bytes32ToUintMap internal s_failedMessages;

    constructor(address _router) CCIPReceiver(_router) {
        if (_router == address(0)) revert ZeroAddress();
    }
    modifier onlySelf() {
        if (msg.sender != address(this)) revert OnlySelf();
        _;
    }

    function allowlistSourceSender(uint64 _sourceChainSelector, address _sender, bool _allowed) external onlyOwner {
        allowlistedSourceSenders[_sourceChainSelector][_sender] = _allowed;
    }

    function allowlistToken(address _token, bool _allowed) external onlyOwner {
        if (_token == address(0)) revert ZeroAddress();
        allowlistedTokens[_token] = _allowed;
    }

    function _ccipReceive(Client.Any2EVMMessage memory any2EvmMessage) internal override {
        address sender = abi.decode(any2EvmMessage.sender, (address));
        if (!allowlistedSourceSenders[any2EvmMessage.sourceChainSelector][sender])
            revert SourceSenderNotAllowed(any2EvmMessage.sourceChainSelector, sender);

        if (any2EvmMessage.destTokenAmounts.length == 0) revert NoTokensReceived();
        for (uint256 i; i < any2EvmMessage.destTokenAmounts.length; ++i) {
            Client.EVMTokenAmount memory received = any2EvmMessage.destTokenAmounts[i];
            if (!allowlistedTokens[received.token]) revert TokenNotAllowed(received.token);
            if (received.amount == 0) revert ZeroTokenAmount(received.token);
        }

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
        address beneficiary = abi.decode(any2EvmMessage.data, (address));
        if (beneficiary == address(0)) revert ZeroAddress();

        for (uint256 i; i < any2EvmMessage.destTokenAmounts.length; ++i) {
            Client.EVMTokenAmount calldata received = any2EvmMessage.destTokenAmounts[i];
            s_receivedTotals[received.token] += received.amount;
            IERC20(received.token).safeTransfer(beneficiary, received.amount);
            emit MessageReceived(
                any2EvmMessage.messageId,
                any2EvmMessage.sourceChainSelector,
                abi.decode(any2EvmMessage.sender, (address)),
                received.token,
                received.amount,
                beneficiary
            );
        }
    }

    function retryFailedMessage(bytes32 messageId, address tokenReceiver) external onlyOwner {
        if (tokenReceiver == address(0)) revert ZeroAddress();
        if (s_failedMessages.get(messageId) != uint256(ErrorCode.FAILED))
            revert MessageNotFailed(messageId);
        s_failedMessages.set(messageId, uint256(ErrorCode.RESOLVED));
        Client.Any2EVMMessage memory any2EvmMessage = s_messageContents[messageId];
        for (uint256 i; i < any2EvmMessage.destTokenAmounts.length; ++i) {
            Client.EVMTokenAmount memory received = any2EvmMessage.destTokenAmounts[i];
            IERC20(received.token).safeTransfer(tokenReceiver, received.amount);
        }
        emit MessageRecovered(messageId);
    }
}
```
