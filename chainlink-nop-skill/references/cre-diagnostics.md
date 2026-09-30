# CRE diagnostics

One-node observations only: never infer fleet/DON health or an external root cause from one node's log. Messages below are exact production templates. `W`, `E`, and `C` mean warning, error, and critical; fields name the decisive structured context. A drop, skip, fallback, retry, or cleanup entry describes only the stated local boundary.

## Construction and configuration skips

| Sev | Exact log message | Node-local condition, fields, and limit |
|---|---|---|
| W | `Skipping orgResolver, no linking service configured` | Linking URL is empty, so construction omits only the organization resolver. |
| W | `Skipping capabilities and workflow registry syncer, no dispatcher configured (peering disabled)` | Dispatcher is nil; neither registry-syncer path is constructed. Already assembled services remain. |
| W | `Skipping capabilities registry syncer, not configured` | External-registry address is empty; construction returns before the capability and workflow syncers. This is configuration absence, not a failed sync. |
| W | `Skipping workflow registry syncer (v1 requires on-chain address)` | Workflow-registry address is empty for contract major v1; capability-registry services built earlier are unaffected. |
| W | `Skipping workflow registry syncer, not configured` | No workflow-registry address and, for v2, no additional source; only the workflow syncer is skipped. |
| W | `Failed to register shard routing steady signal metrics; continuing without steady instrumentation` | Sharding is enabled and steady-metric registration fails (`err`); routing still receives a steady signal, but without this instrumentation. |
| W | `unsupported workflow registry version` | Parsed registry major is not 2 (`version`); code still enters the v2 construction path, so this is compatibility evidence, not proof startup failed. |
| W | `getPeerID() failed, will extract default peerID from Keystore` | Callback failed (`error`); standard-capability construction falls back to `GetOrFirst`. |
| W | `No capability ID mapping for command, using legacy config only` | Command cannot map to a capability ID (`command`); oracle-factory setup continues with legacy config. |
| W | `Capabilities registry is nil; falling back to workflow DON ID for event labeling` | Capability-DON lookup lacks a registry (`capabilityID`); only event labeling falls back. |
| W | `getPeerID is nil; falling back to workflow DON ID for event labeling` | Capability-DON lookup lacks the callback (`capabilityID`); only event labeling falls back. |
| W | `Failed to get local peer ID; falling back to workflow DON ID for event labeling` | Callback fails (`capabilityID`, `err`); capability construction is not aborted here. |
| W | `DONsForCapability failed; falling back to workflow DON ID for event labeling` | Best-effort registry query fails (`capabilityID`, `err`); this does not diagnose global registry health. |
| W | `No DON found for local peer on capability; falling back to workflow DON ID for event labeling` | No returned DON contains this peer (`peerID`, `capabilityID`); only labels fall back. |
| W | `Local peer belongs to multiple DONs for capability; cannot disambiguate, falling back to workflow DON ID for event labeling` | More than one DON matches (`peerID`, `capabilityID`, `matched`); no authoritative capability DON is chosen for labels. |
| E | `error waiting for standard capabilities service to start: %v` | Asynchronous LOOP `WaitCtx` fails/times out; readiness and health expose the error even if `Start` already returned nil. |
| E | `error initialising standard capabilities service: %v` | LOOP starts but `Service.Initialise` fails asynchronously; this is the standard-capability readiness boundary. |
| E | `error getting standard capabilities service info: %v` | LOOP initializes but `Service.Infos` fails; the service becomes unready/unhealthy, without attributing a workflow failure. |

## Registry and reconciliation

| Sev | Exact log message | Node-local condition, fields, and limit |
|---|---|---|
| E | `node's peerID changed at runtime, this should never happen` | Cached and current peer IDs differ (`cachedLocalNodePeer`, `currentPeerID`); lookup continues using the new ID. |
| E | `Configuration error: node belongs to more than one workflowDON` | A peer appears in a second workflow-accepting DON (`peerID`); the lookup still returns the first plus capability DONs. |
| E | `failed to sync with remote registry` | Initial or periodic v1/v2 `Sync` failed (`error`). Persisted state may already be loaded; no freshness, usability, or fleet verdict follows. |
| E | `failed to save state to local registry` | v1/v2 ORM persistence fails after an update (`error`); the update loop continues. |
| E | `error calling launcher: %s` | On this node, in both v1 and v2 `Sync`, one listener's `OnNewRegistry` callback returns formatted `err`; the syncer emits this message, increments the launcher-failure metric, and continues the listener loop. This is a per-listener callback/reconciliation failure, not proof that registry synchronization or the DON failed. |
| W | `failed to find capability ID for hashed ID, skipping` | v1 import cannot backfill one hashed ID (`hashedID`); that node slot is empty and import continues. |
| W | `sync called, but no listeners are registered; no-op` | v1/v2 has no listeners; it returns nil without contacting or persisting the registry. |
| W | `failed to sync with local registry, using remote registry instead` | Initial persisted-state read fails (`error`); v1/v2 proceeds to remote import. |
| W | `failed to parse capability metadata, skipping` | One v2 capability's metadata is invalid (`capabilityID`, `error`); that capability alone is omitted. |
| W | `failed to hash capability ID, skipping` | One v2 node capability ID cannot be hashed (`capabilityID`, `error`); node/import processing continues. |
| E | `failed to close a sub-service` | One launcher subservice fails to close (`name`, `error`); shutdown continues and the error is suppressed there. |
| E | `failed to close workflow DON binding gate limiter` | Binding-gate limiter close fails (`error`); launcher shutdown continues. |
| E | `failed to close workflow tag hash flag limiter` | Workflow-tag limiter close fails (`error`); launcher shutdown continues. |
| W | `My node doesn't belong to any DON families. No filtering will be applied.` | This local node has no family; remote workflow/capability DONs are deliberately left unfiltered. Empty families overlap; this is not a DON-health conclusion. |
| E | `Failed to reconcile local capabilities` | Local capability manager returns an error (`error`); launcher continues registry processing and peer-connection update. |
| W | `multiple in-family capability DONs host the same capability; only the lowest DON ID will be routed to, check DON family configuration` | More than one family-filtered remote DON declares a capability (`capabilityID`, sorted `donIDs`); routing deterministically chooses the lowest. |
| E | `could not unmarshal capability config` | Remote-add fields: `myDON`, `remoteDON`, `capabilityID`, `error`; local-serve fields: `localDON`, `capabilityID`, `error`. Only that capability is skipped. |
| E | `capability method config is nil` | Remote-add fields: `myDON`, `remoteDON`, `capabilityID`; local-serve fields: `localDON`, `capabilityID`, `error`. Only that wiring attempt is skipped. |
| E | `could not find capability in local registry` | A remote DON references an absent local ID (`myDON`, `remoteDON`, `capabilityID`); best-effort siblings continue. |
| E | `failed to add remote capability ` | `addRemoteCapabilityV2` fails (`myDON`, `remoteDON`, `capabilityID`, `err`); the source template has the trailing space shown, and only that capability is skipped. |
| E | `failed to serve capability` | Local exposure setup fails (`myPeerID`, `localDON`, `capabilityID`, `err`); only that capability is skipped. |
| E | `no remote config found` | A method has neither remote trigger nor executable config (`method`, `capID`); only that method is skipped. |
| E | `failed to start receiver` | A trigger subscriber, executable client, trigger publisher, or executable server shim cannot start (`capID`, `method`, `error`); that method is skipped and no shim is cached. |
| E | `failed to update client config` | Executable client `SetConfig` fails (`capID`, `method`, `error`); only that remote method is skipped. |
| E | `Failed to stop capability on shutdown` | One running capability fails to close (`key`, `error`); remaining closes continue and errors are joined for return. |
| E | `Failed to stop removed capability` | Removed `(capability,DON)` services fail to close (`capID`, `donID`, `error`); reconcile still deletes manager state for the entry. |
| E | `Failed to stop capability for config update` | Old services fail to close (`capID`, `error`); reconcile deletes the old entry and attempts replacement. |
| E | `Failed to start capability` | Per-capability start fails (`capID`, `donID`, `error`); reconciliation continues. The error may retain `could not resolve capability binary`, `build config`, `build services`, or `start service`. |
| E | `Failed to close service during rollback` | A prior service also fails to close after a later start failure (`capID`, `serviceIndex`, `error`); the primary failure is returned and logged by the preceding start message. |
| W | `Failed to unmarshal onchain config, using local config only` | Nonempty on-chain config is invalid (`capID`, `error`); that capability keeps local config only. Equal raw-registry hashes are a no-op; the hash excludes local TOML, and valid on-chain values win. |

## Remote capabilities

Logger scope supplies capability/method and, where applicable, workflow/capability DON, request, response, and peer identifiers. Each entry is a single receiver, request, peer send, or protocol boundary.

| Sev | Exact log message | Emitting boundary, decisive fields, and limit |
|---|---|---|
| E | `Recovered goroutine panic` | A registered receiver panics (`panic`, sanitized `capabilityId`, `donId`, `methodName`, `msgMethod`, `sender`); that receiver goroutine is isolated. |
| E | `rate limit exceeded, dropping message` | One inbound P2P sender exceeds the dispatcher limiter (`sender`); that message is dropped. |
| E | `receiver channel full, dropping message` | Matched receiver buffer is full (`capabilityId`, `donId`); local back-pressure drops the message. |
| E | `received message but config is not set` | Trigger publisher receives a message before config and discards it. |
| E | `failed to convert message sender to PeerID` | Publisher or subscriber cannot decode `msg.Sender` (`err`); that inbound message is discarded. |
| E | `received a message with error` | Publisher sees nonempty remote `ErrorMsg` (`method`, `sender`, `errorMsg`); handling continues by method, and the log does not identify the remote cause. |
| E | `failed to unmarshal trigger registration request` | Registration payload decode fails (`err`); request is discarded. |
| E | `received a message from unsupported workflow DON` | Register or ACK caller DON is absent from publisher config (`callerDonId`); handling stops. |
| E | `sender not a member of its workflow DON` | Register or ACK sender is absent from the configured caller DON (`callerDonId`, `sender`); handling stops. |
| E | `received trigger request with invalid trigger ID` | Registration trigger ID is invalid (`triggerID`); request is discarded. |
| E | `received trigger request with invalid workflow ID` | Workflow/execution-ID validation fails (`workflowId`, `err`); request is discarded. |
| E | `failed to aggregate trigger registrations` | Ready registration quorum cannot aggregate (`workflowId`, `triggerID`, `err`); underlying registration is not called. |
| E | `failed to unmarshal request` | Aggregated registration bytes cannot decode (`err`); underlying registration is not called. |
| E | `trigger registration failed with user error; will not retry` | Underlying registration returns a user-origin error (`workflowId`, `triggerID`, `err`); failure is retained to suppress retry. |
| E | `trigger registration failed with system error; will retry` | Underlying registration returns a non-user error (`workflowId`, `triggerID`, `err`); cached quorum is removed so a later quorum can retry. |
| E | `failed to schedule RegisterTrigger task` | Local parallel executor rejects the task (`workflowId`, `triggerID`, `err`); no registration task runs. |
| E | `received unregister with nil metadata` | Unregister has no trigger metadata (`sender`); it is discarded. |
| E | `received unregister with unexpected metadata sizes` | Unregister does not contain exactly one workflow and trigger ID (`sender`, `workflowIdsLen`, `triggerIdsLen`); it is discarded. |
| E | `received unregister from unsupported workflow DON` | Unregister caller DON is not configured (`callerDonId`); it is discarded. |
| E | `unregister sender not a member of its workflow DON` | Sender is absent from its configured caller DON (`callerDonId`, `sender`); unregister is discarded. |
| E | `failed to unregister trigger on underlying` | Unregister quorum removed local state, then underlying unregister failed (`workflowID`, `triggerID`, `err`); local state is already gone. |
| E | `trigger request failed with error` | Incoming trigger-event message is an error response (`method`, `sender`, `errorMsg`); remote response boundary only. |
| E | `received empty trigger event ack metadata` | ACK lacks metadata (`sender`); it is discarded. |
| E | `did not receive single triggerID in ACK request` | ACK has other than one trigger ID (`callerDonId`, `sender`, `triggerIDs`); it is discarded. |
| E | `failed to AckEvent on underlying trigger capability` | ACK quorum task reaches the underlying trigger and it fails (`eventID`, `capabilityID`, `err`). |
| E | `failed to schedule AckEvent task` | Local executor cannot accept an ACK task (`triggerEventId`, `triggerID`, `err`). |
| E | `received message with unknown method` | Publisher receives an unsupported method (`method`, `sender`); protocol boundary only. |
| E | `cacheCleanupLoop started but config not set` | Publisher cleanup goroutine starts without config and exits. |
| E | `registrationCheckLoop started but config not set` | Publisher registration-check goroutine starts without config and exits. |
| E | `config not set during sendBatch` | Ready trigger-event batch has no current config and is not sent. |
| E | `failed to send trigger event` | Send to one workflow-DON peer fails (`peerID`, `err`); other peers/batches continue. |
| E | `batchingLoop started but config not set` | Publisher batching goroutine starts without config and exits. |
| E | `failed to send message` | Individual publisher registration-check, subscriber ACK/registration/unregister, or executable-request send fails. Fields vary: `donId`, `peerId`, `err`, or executable `peerID`, `error`; remaining peer sends continue. |
| W | `RegisterTrigger re-registering trigger` | Subscriber updates an existing local registration (`donId`, `workflowID`, `triggerID`); refresh observation, not failure. |
| E | `config not set - call SetConfig() first` | Trigger subscriber receives before config and discards the message. |
| E | `received message from unexpected node` | Sender is not a configured capability-DON member (`sender`); message is discarded. |
| E | `received message with invalid trigger metadata` | Trigger event has no metadata (`sender`); it is discarded. |
| E | `received message with too many workflow IDs - truncating` | Batch has more than 1000 workflow IDs (`nWorkflows`, `sender`); local processing truncates the list. |
| E | `received message for unregistered workflow/trigger` | Workflow is absent or its trigger disappears/is missing (`workflowID`, `sender`, and sometimes `triggerID`); that item is skipped. |
| E | `received message without triggerID but workflow has multiple trigger - picking a random one` | Legacy event omits trigger ID for a multi-trigger workflow (`workflowID`, `sender`); map iteration chooses one, so this is a protocol ambiguity. |
| E | `replay AckEvent failed` | Duplicate event was already ACKed by the engine and ACK replay errors (`triggerID`, `triggerEventID`, `err`). Current `AckEvent` normally logs sends and returns nil, so this source-complete branch is not expected today. |
| E | `failed to aggregate responses` | Trigger-event response cache is ready but aggregation fails (`triggerEventID`, `workflowId`, `triggerID`, `err`); event is not delivered locally. |
| E | `received registration check with nil metadata` | Registration check lacks metadata (`sender`); it is discarded. |
| E | `received registration check with mismatched workflow and trigger IDs` | Parallel ID lists differ (`sender`, `workflowIdsLen`, `triggerIdsLen`); message is discarded. |
| E | `received trigger event with unknown method` | Subscriber sees a method other than event/check (`method`, `sender`, sanitized `err`); message is discarded. |
| E | `invalid message ID` | Executable client response ID is invalid (`err`, sanitized `id`); response is discarded. |
| W | `received response for unknown message ID ` | Valid executable response has no stored request (`messageID`); the source template has the trailing space shown. |
| E | `failed to add response to request` | Stored executable request rejects a response (`messageID`, `err`), such as sender, payload, or duplicate validation. |
| W | `no message hasher provided, using default V1 hasher` | Executable server config omits a hasher; V1 is used. |
| W | `ServerMaxParallelRequests changed but it won't be applied until node restart` | Live positive parallelism changes; current executor capacity stays until restart. |
| E | `failed to cancel request` | Expired server request cancel/fan-out fails (`request`, `err`); per-request timeout/response boundary. |
| E | `config not set, cannot process request` | Executable server receives before config and discards the request. |
| E | `received request for unsupported method type` | Method is not execute (`method`); request is discarded. |
| E | `invalid message id` | Executable server request ID is invalid (`err`, sanitized `id`); request is discarded. |
| E | `failed to get message hash` | Configured hasher fails (`err`); request is discarded. |
| W | `received messages with the same id and different payloads` | One ID maps to multiple payload hashes (`messageID`, `lenRequestIDs`); identity/integrity warning, not proof of an attack. |
| E | `received request from unregistered don` | First request names no configured workflow DON (`donId`); request is discarded. |
| E | `failed to instantiate server request` | Local server-request construction fails (`err`); request is discarded. |
| E | `failed to execute on message` | Scheduled server request processing/fan-out errors (`messageID`, `err`); per-request boundary. |
| E | `failed to execute on message task` | Local executor cannot accept the `OnMessage` task (`messageID`, `err`). |
| E | `failed to emit transmission schedule event` | Durable schedule-event emission fails (`error`); executable request creation and network fan-out continue. |
| W | `invalid metering detail` | Successful peer response has unusable metering metadata (`err`, plus request/response/peer context); report is omitted but response can still count. |
| W | `received multiple unique responses for the same request` | More than one successful response hash arrived (`count for responseID`); per-request consensus evidence only. |
| W | `received multiple different errors for the same request` | More than one remote error text arrived (`numDifferentErrors`); no broader attribution follows. |
| W | `response quorum unreachable, failing early` | Remaining peers cannot produce identical-response quorum (`responsesReceived`, `remoteNodeCount`, `uniqueResponseCount`, `maxMatchingResponseCount`, `requiredResponseConfirmations`, `pendingResponses`). |
| E | `Attestation is present, but not valid. This is most likely a bug and requires investigation - falling back to identical responses verification` | OCR attestation verification fails (`error`); client falls back to identical responses rather than failing solely on this signal. |
| W | `received error response` | Client request resolves with an error (`error`), which may be remote, quorum, cancellation, or another terminal request outcome. |
| E | `failed to unmarshal capability request` | Quorum-winning payload cannot decode (`err`); server returns a generic internal error. |
| E | `failed to evaluate workflow DON binding gate` | Runtime gate lookup fails (`err`); server returns a generic internal error. |
| E | `workflow DON ID in request metadata does not match calling DON` | Enabled binding gate finds metadata/caller mismatch (`metadataWorkflowDonID`, `callingDonID`); execution is rejected. |
| E | `received execution error` | Underlying executable capability returns an error (`error`); response is serialized when reportable. |
| E | `failed to marshal capability request` | Underlying response cannot marshal (`error`); server returns a generic internal error. |

## Workflow intake

| Sev | Exact log message | Source condition, decisive fields, and limit |
|---|---|---|
| C | `centralized workflow source did not provide an organization ID; cannot verify workflow owner` | Centralized owner verification is enabled but `orgID` is blank (`source`, `claimedWorkflowOwner`, `tenantID`); intake fails closed for that workflow. |
| C | `centralized workflow owner does not match owner derived from its organization ID: possible data corruption or malicious workflow registry` | Derived and claimed owners differ (`source`, `claimedWorkflowOwner`, `organizationID`, `derivedWorkflowOwner`, `tenantID`); intake fails closed without proving which upstream is at fault. |
| W | `Workflow has incomplete metadata from contract, skipping` | One on-chain record fails completeness checks (`source`, workflow identity/URLs/status); only that record is skipped. |
| W | `Failed to parse workflow metadata, skipping` | Matching-DON file or gRPC record cannot convert (`workflowName`, `error`, plus file `source`); that record is skipped and the source continues. |
| E | `Non-retryable error from GRPC source` | Page request returns a non-retryable status (`error`, `start`, `pageSize`); this source's reconciliation is skipped for the tick. |
| W | `Retryable error from GRPC source` | Page request returns a retryable status (`error`, `attempt`, `maxRetries`); backoff continues unless exhausted/cancelled. |
| E | `Max retries exceeded for GRPC request` | The retryable page reaches its configured budget (`error`, `maxRetries`); source reconciliation is skipped for the tick. |
| E | `Failed to create file workflow source` | Configured file-source constructor fails (`name`, `path`, `error`); that source is omitted. |
| E | `Failed to create GRPC workflow source` | Configured gRPC-source constructor fails (`name`, `url`, `error`); that source is omitted. |
| W | `Some additional sources failed to initialize` | At least one source construction failed (`expected`, `active`, `failed`); successful sources remain active. |
| E | `abandoning workflow activation` | Activation is non-retryable or its runtime retry budget is exhausted (`reason`, counts/policy, event/workflow fields, `err`). Abandonment is in-memory and clears on restart; an abandoned-status event is attempted next. |
| E | `failed to emit activation abandoned event` | Best-effort external abandoned event fails (`err`) after activation is already abandoned; it does not reverse abandonment. |
| W | `skipping pre-dispatch drain due to invalid event payload type` | A deletion event has the wrong concrete payload (`eventID`, `eventType`); only pre-dispatch drain is skipped. |
| E | `failed to call getAllowlistedRequests` | Contract allowlist read fails (`err`); current in-memory allowlist remains until a later tick. |
| E | `failed to get get don from notifier` | Workflow-DON notifier fails (`err`); no source polling/reconciliation occurs that tick. |
| W | `failed to list persisted workflow specs; skipping orphaned-spec reconciliation this tick` | Durable-spec list fails (`err`); normal source/engine reconciliation continues, but orphan sweep is suppressed. |
| E | `Failed to fetch from source, skipping reconciliation for this source` | One source listing fails (`source`, `error`, `durationMs`); it emits no events/deletions and prevents that tick's orphan sweep. |
| E | `failed to filter workflows by shard, skipping reconciliation for this source` | Shard resolution fails (`err`, `source`); that source and the all-source orphan sweep are skipped. |
| E | `Failed to generate reconciliation events for source` | Post-fetch diff generation fails (`source`, `error`); that source emits no events this tick. |
| E | `failed to handle event, backing off...` | A nonterminal handler failure is scheduled (`err`, `type`, `nextRetryAt`, `retryCount`, `retryPolicy`, `workflowInfo`). Runtime values, not this text, define the cutoff. |
| W | `orphaned-spec reconciliation: skipping unparseable persisted workflow_id` | Engine-less persisted spec has invalid ID (`workflowID`, `err`); it is not released. |
| W | `failed to release orphaned workflow spec` | Synthetic deletion fails (`workflowID`, `err`); spec remains for a later tick. |
| E | `WARNING: Debug mode is enabled for workflow syncer, this is not suitable for production` | Syncer constructed in debug mode; OTel tracing is enabled. This is configuration evidence, not activation failure. |
| W | `Per-owner local secret overrides are active; vault is used for secret IDs not listed under each owner` | Nonempty overrides configured (`numOwners`, `owners`); this is the intentional override/vault split. |
| W | `Failed to get organization from linking service` | Org lookup fails during activate, pause, delete, spec creation, or abandoned-event emission (`workflowOwner`, `error`); caller continues with empty org context. |
| E | `failed to emit status changed event: %+v` | Best-effort activated/paused/deleted status-event emission fails (formatted `err2`); original handler result is unchanged. |
| E | `failed to handle workflow activated event` | Activation handler fails (`error`, `workflowID`); it attempts a customer message and returns to retry/abandon logic. |
| E | `failed to read workflow spec during deletion, proceeding without metadata` | Spec lookup fails other than not-found (`workflowID`, `error`); deletion proceeds without owner/name metadata. |
| W | `failed to backfill registered_at/source/workflow_tag` | Legacy-field/tag upsert fails (`workflowID`, `err`); processing continues with the prior stored row. |
| W | `Failed to get organization ID from org resolver` | Resolver returns an error (`workflowOwner`, `error`); callers generally continue with empty organization context. |
| W | `No organization ID returned from org resolver` | Resolver succeeds but returns empty (`workflowOwner`); callers generally continue with empty context. |
| W | `Failed to cache module binary to disk, LRU eviction disabled for this workflow` | Module-store persistence fails (`workflowID`, `err`); loaded module remains usable without disk-backed eviction. |
| W | `Failed to delete cached module binary` | Cleanup cannot remove disk cache (`workflowID`, `err`); cache residue remains. |
| E | `failed to close engine after context cancellation` | Initialization wait is cancelled and engine close also fails (`error`, `workflowID`); create returns the cancellation/init error. |
| E | `failed to close engine after initialization failure` | Init hook fails and engine close also fails (`error`, `workflowID`); create returns the init error. |
| W | `WorkflowID collision detected: workflow already exists from different source` | Registry already contains the ID under another source (`workflowID`, `attemptedSource`, `existingSource`, `hint`); creation returns an invariant error. |
| E | `invalid workflow owner for local secret overrides` | Configured override owner cannot normalize (`owner`, `err`); no override fetcher is selected, while the normal secret path remains. |
| E | `failed to send custom message with msg: %s, err: %v` | Syncer handler or legacy artifact store cannot emit an external customer message; formatted `msg`/`err` describe delivery failure, not necessarily the underlying workflow condition. |
| W | `failed to resolve org ID for metering` | Spec delta fallback resolution fails (`owner`, `err`); delta still carries empty `OrgID`. |
| W | `failed to list persisted workflow specs for metering snapshot; skipping tick` | Durable v2 spec list fails (`err`); no snapshot entries are returned that tick. |
| W | `failed to resolve org ID for metering snapshot` | One spec's fallback resolution fails (`owner`, `err`); utilization still carries empty `OrgID`. |
| W | `Received WORKFLOW_STATUS_UNSPECIFIED from proto, treating as paused` | gRPC metadata status is unspecified; it is safely mapped to paused. |
| W | `Unknown proto status, treating as paused` | gRPC metadata has an unknown enum (`status`); it is safely mapped to paused. |
| W | `rejecting cached module binary: engine version mismatch` | Cached/current engine versions differ (`workflowID`, `cachedEngineVersion`, `currentEngineVersion`); binary is rejected and stale deletion is attempted. |
| W | `failed to delete stale cached module` | Stale-version cache deletion fails (`workflowID`, `err`); mismatch is still returned and cache remains. |
| E | `could not refresh secrets: proceeding with stale secrets for workflowID %s: %s` | Legacy/v1 secret refresh fails for an absent/stale stored payload; it continues by decrypting the stale payload and emits a customer message. |
| W | `failed to delete workflow spec: not found` | Legacy/v1 ORM delete returns not-found (`workflowID`); deletion is treated as idempotent success. |

## Workflow engine

Engine context normally includes workflow identity/owner/name, DON parameters, peer ID, registry address/selector, engine version, SDK, and—during execution—execution/trigger/event/capability/callback identifiers. Conditions below remain per-engine or per-execution.

| Sev | Exact log message | Engine boundary, decisive fields, and limit |
|---|---|---|
| E | `no metering report found` | Capability call has no report for its execution; step metering-state boundary. |
| E | `could not deduct balance for capability request` | Capability spend or standard compute pre-deduction fails (`capReq`, callback/`err` variants); execution continues. |
| E | `failed to set metering for capability request` | Capability response arrives but settlement fails (`err`); step-metering boundary. |
| W | `Exceeded max allowed user log messages, dropping` | Execution helper or disallowed helper cannot enqueue another user log; only that log is dropped. |
| W | `failed to resolve organization ID` | Confidential module owner resolution fails (`error`); execution continues with returned/empty org ID. |
| E | `failed to get regions from confidential-workflows capability, assuming no supported regions: %v` | `ProvidedTees` request fails; module assumes no supported regions. |
| E | `WARNING: Debug mode is enabled, this is not suitable for production` | Engine config enables debug mode; production-safety configuration warning. |
| W | `Failed to resolve organization ID, continuing without it` | Engine-start resolver fails (`workflowOwner`, `err`); engine starts without org ID. |
| E | `Workflow count limit reached for unexpected scope` | Global-workflow limiter returns resource-limited under an unexpected `scope` (`err`); initialization fails. |
| E | `failed to subscribe to DON notifier` | DON-change subscription fails (`error`); initialization boundary. |
| E | `Workflow Engine initialization failed` | Trigger-subscription phase fails (`err`); engine startup boundary. |
| E | `could not get local node state: %s` | DON notification refresh cannot obtain local state; hook receives the formatted error. |
| E | `Trigger registration failed` | One `RegisterTrigger` fails (`triggerID`, `err`). |
| E | `One or more trigger registrations failed - reverting all` | Concurrent registration group fails (`err`); successful registrations are unregistered. |
| E | `Received a trigger event with error, dropping` | Trigger response carries `event.Err` (`triggerID`, `err`); that event is dropped. |
| E | `Trigger event queue is full, dropping event` | Queue returns full (`triggerID`, `triggerIndex`, `err`); this is followed by the generic enqueue-error log. |
| E | `Failed to enqueue trigger event` | Any queue put fails (`triggerID`, `triggerIndex`, `err`); that event is dropped. |
| E | `Failed to get trigger event queue time limit` | Queue-age limiter cannot provide its limit (`err`); dequeued event is dropped. |
| W | `Trigger event is too old, skipping execution` | Queue residence exceeds runtime limit (`triggerID`, `eventID`, `eventAgeMs`); that event is dropped. |
| E | `Failed to acquire executions semaphore` | Concurrency-semaphore wait fails (`err`); that event is dropped. |
| E | `Failed to generate execution ID` | Workflow/event/trigger identity generation fails (`err`, `triggerID`); event is dropped. |
| W | `Failed to get DON time for execution timestamp, falling back to local time` | Initial DON-time query fails (`err`, `executionTimestamp`); execution uses local clock. |
| E | `failed to re-ACK trigger event` | Duplicate execution is detected but ACK retry fails (`eventID`, `err`). |
| E | `Failed to register execution in store, proceeding anyway` | Nonduplicate store add fails (`executionID`, `err`); workflow still runs. |
| E | `Failed to finish execution in store` | Deferred completion persistence fails (`executionID`, `status`, `err`). |
| W | `Shard ownership check failed (orchestrator error); skipping execution` | Ownership cannot be determined (`err`); execution is marked errored/dropped and ACK is attempted. |
| E | `failed to ACK trigger after shard ownership orchestrator error` | ACK after indeterminate-ownership denial fails (`eventID`, `err`). |
| E | `failed to ACK trigger after shard ownership denial` | ACK after deterministic not-owner denial fails (`eventID`, `err`). |
| E | `could start metering workflow execution. continuing without metering` | Meter-report start fails (`err`); execution continues unmetered. Preserve the source wording. |
| E | `could not reserve metering` | Started report cannot reserve (`err`); event is dropped before execution. |
| E | `Failed to get execution time limit` | Execution timeout creation fails and drops admission, or standard-deduction duration lookup fails and skips that deduction (`err`). |
| E | `Failed to get log event limit` | Per-execution user-log limit cannot be read (`err`); event is dropped before module call. |
| E | `Failed to convert trigger index to uint64` | SDK trigger-index conversion fails (`err`); event is dropped. |
| E | `failed to ACK trigger event (eventID=%s): %v` | Normal pre-execution ACK fails; module execution still proceeds. |
| E | `Failed to emit execution profile` | Post-execution profile event emission fails (`err`); observability boundary. |
| E | `Failed to marshal execution profile to JSON` | Generated profile cannot marshal for its log (`err`); observability boundary. |
| W | `ExecutionTimestampsEnabled is false - creating a new DON time provider` | Local time is disabled and timestamp setup did not precreate a provider; provider-selection observation. |
| E | `Failed to get execution response size limit` | Limiter cannot provide module response size (`err`); execution status is errored/event dropped. |
| E | `invalid moduleExecuteMaxResponseSizeBytes; must not be negative: %d` | Configured size is negative; execution status is errored/event dropped. |
| E | `could not set metering for compute` | Compute settlement fails (`err`); execution metering boundary. |
| E | `could not end metering report` | Report end fails (`err`); execution metering-completion boundary. |
| E | `Workflow execution failed with module execution error` | Module `Execute` returns error/timeout (`status`, `durationMs`, `err`); module/system boundary. |
| E | `Workflow execution failed` | SDK result contains nonempty error text (`status`, `durationMs`, `error`); user-result boundary only—inspect the returned error before attribution. |
| E | `Failed to purge executions on close` | Workflow execution-state deletion fails during engine close (`err`). |
| E | `Failed to evict workflow from scoped limiters` | Limiter eviction fails during engine close (`err`). |
| E | `Failed to unregister trigger` | One teardown unregister fails (`registrationId`, `err`); remaining triggers are attempted. |
| W | `Max user log events per execution reached, dropping event` | User-log bounded limiter is reached (`maxEvents`, `err`); only that event is dropped. |
| E | `Failed to get user log event limit` | Non-bound limiter error occurs (`err`); user-log processing stops. |
| E | `Failed to get user log line limit` | Line-length limit cannot be read (`err`); user-log processing stops. |
| E | `Failed to emit user logs` | Durable user-log emission fails (`err`); processing continues to the next line. |
| W | `Timeout reached while draining user logs` | Execution context ends and buffered logs do not drain within 30 seconds. |
| E | `Failed to get DON time request timeout` | Timeout limiter errors (`err`); default timeout is returned. |
| W | `DON time request timeout is less than or equal to 0, using default timeout` | Configured value is nonpositive (`defaultTimeout`); default is returned. |
| W | `Secrets fetching failed for request` | Whole batch/fallback secret lookup fails (`vaultRequestID`, metadata, `error`, latency); request-secret boundary. |
| E | `local override fetcher failed - this should never happen` | Vault had failures and configured local fallback also fails (`error`). |
| E | `failed to fetch secrets` | Vault capability `Execute` fails (`err`); raw retrieval boundary. |
| E | `failed to unmarshal vault payload to GetSecretsResponse` | Vault response payload cannot decode (`err`); raw response boundary. |
| E | `No DON time reached for time call sequence %d on executionID %s; returning local node time as fallback. This may result in non-deterministic behavior across nodes for this workflow step` | DON-time responses error with no consensus time; step returns the last observed local-node time. |

## Metering, store, and retry helpers

| Sev | Exact log message | Local condition, fields, and limit |
|---|---|---|
| W | `SubmitWorkflowReceipt failed, retrying` | Billing receipt RPC failed retryably (`attempt`, `maxRetries`, `error`, `retryDelay`); a retry is about to occur, not proof of final loss. |
| E | `switching to metering mode` | First fail-open accounting cause for one report (`workflowExecutionID`, `err`); local credit accounting disables while spend gathering continues. Later causes are joined in memory without another log. |
| W | `Found and pruned non completed workflow executions older than the maximum execution age` | Periodic in-memory cleanup removes unfinished stale entries (`maximumExecutionAge`, `prunedExecutionIDs`); it does not explain why they remained unfinished. |
| E | `error: %s, retrying in %s` | Generic retry callback failed; current production use is capability-registry readiness every 500 ms until context completion. The log precedes retry/exhaustion checks. |
| E | `max retries (%d) reached, aborting` | Generic helper's finite budget is exhausted. Current non-test caller passes zero (infinite), so this direct production template is presently not reachable through that caller; do not infer a terminal readiness failure from its absence. |

## Web API and gateway

### Node-side Web API capability

| Sev | Exact log message | Node-side condition, fields, and limit |
|---|---|---|
| E | `failed to unmarshal err payload` | Single-node response says internal error but its wire error cannot decode (`messageID`, `workflowID`, `err`); caller receives unknown internal error. |
| W | `all available gateway nodes attempted without connection, backing off` | Every available gateway has been attempted (`messageID`, `workflowID`, `waitTime`); retry loop sleeps/resets until connection or context end. |
| W | `failed to await connection to gateway node, retrying` | One one-second gateway connection attempt fails (`selectedGateway`, `error`, request context); loop tries another. |
| E | `failed to validate request` | Inbound gateway response validation fails (`err`, `gatewayID`); handler logs and returns nil. |
| W | `no response channel found; this may indicate that the node timed out the request` | Valid response has no local message-ID channel (`gatewayID`, `method`, `messageID`); late/unknown response is ignored. |
| E | `request rate-limited` | Incoming sender/global limiter denies response forwarding (`gatewayID`, `method`, `messageID`); an internal-error response is sent locally. |
| E | `failed to marshal err payload` | Rate-limit wire-error serialization fails (`gatewayID`, `method`, `messageID`, `err`); handler still sends the constructed message. |
| E | `failed to unmarshal payload` | Accepted response method payload cannot decode (`gatewayID`, `method`, `messageID`, `err`); handler returns nil. |
| E | `unsupported method` | Node outgoing handler rejects a response method (`gatewayID`, `method`, `messageID`); node trigger handler rejects a non-`web_api_trigger` method (`id`, `method`) and attempts an error response; the legacy gateway handler likewise rejects a non-`web_api_trigger` user method (`method`) and sends an unsupported-method callback. |
| E | `failed to generate execution ID` | Accepted web-API trigger cannot derive execution ID (`err`); telemetry uses an empty ID and delivery continues. |
| E | `failed to emit trigger execution started event` | Accepted trigger cannot emit lifecycle telemetry (`err`); delivery continues. |
| E | `error validating message from request` | Inbound trigger request validation fails (`err`, full `request`); handler returns nil. |
| E | `error decoding payload` | Node trigger payload cannot decode (`err`) and an error response is attempted. The same exact gateway-side legacy message also covers invalid JSON or a zero timestamp. |
| E | `error sending response` | Node trigger error-response delivery fails after decode or unsupported-method handling (`err`); handler returns nil. |
| E | `Error processing trigger` | Valid trigger processing fails (`gatewayID`, full `body`, returned `response` error); handler then sends an error response. |
| E | `Error sending response` | Main node trigger response delivery fails (`body`, `response`, `err`); capitalization distinguishes this source template. |
| E | `error marshalling payload` | Shared node trigger response payload cannot marshal (`err`); it substitutes a marshaled error payload and continues signing/sending. |

### Gateway legacy and v2 handlers

| Sev | Exact log message | Gateway condition, fields, and limit |
|---|---|---|
| E/W | `error while sending HTTP request to external endpoint` | Legacy handler logs E when outbound send fails (`url`, `messageId`, `method`, `timeout`, `err`) and attempts an execution-error response; v2 logs W specifically for `ErrHTTPSend` (`requestID`, `method`, `timeout`, `err`) and returns an external-endpoint error. |
| E | `error while marshalling payload` | Legacy execution-error response cannot marshal (request context, `err`); goroutine returns without sending. |
| E | `error transforming message to request` | Legacy generated node response or legacy user trigger cannot become a validated request; response goroutine returns, or user parse-error callback is sent. |
| E | `failed to send to node` | Legacy response send to `nodeAddr` fails (request context, `err`, `to`); goroutine returns. |
| E | `stale message` | Legacy trigger exceeds configured message age; handler sends an error callback. |
| E | `received response with empty result from node` | V2 node response has nil `Result` (`nodeAddr`, `error`); handler returns an error. |
| W | `HTTP request blocked` | V2 send matches blocked-request policy (`requestID`, `method`, `timeout`, `err`); validation-error response and blocked metric follow. |
| W | `error while reading HTTP response from external endpoint` | V2 send matches response-read failure (`requestID`, `method`, `timeout`, `err`); external-endpoint error is returned. |
| E | `error while sending HTTP request` | V2 unclassified send failure (`requestID`, `method`, `timeout`, `err`); outbound response contains the error. |
| E | `failed to handle user trigger request` | V2 trigger handler fails (`requestID`, `err`) after already sending the user's error; outer handler deliberately returns nil. |
| E | `error sending response to node` | Separate delivery context cannot return an HTTP-action result (`requestID`, `method`, `timeout`, `err`, `nodeAddr`); failure metric increments. |
| E | `failed to close HTTP trigger handler` | Child close fails (`err`); parent shutdown continues. |
| E | `failed to close HTTP auth handler` | Metadata-handler close fails (`err`); parent shutdown continues. |
| E | `failed to close global node rate limiter` | Global limiter close fails (`err`); parent shutdown continues. |
| E | `failed to close per-node rate limiter` | One per-node limiter close fails (`nodeAddr`, `err`); loop continues. |
| E | `failed to close mtls request rate limiter` | mTLS request limiter close fails (`err`); parent shutdown continues. |
| E | `failed to close mtls concurrency limiter` | mTLS concurrency limiter close fails (`err`); parent shutdown continues and returns nil. |
| E | `failed to start execution: per workflow rate limit exceeded` | V2 workflow-scoped limiter denies (`workflowID`, `workflowOwner`, `requestID`, `err`); limit-exceeded callback is sent. |
| E | `failed to start execution: unexpected rate limit for scope %s` | Limiter denies under another scope (same identity fields, `err`); limit-exceeded callback is sent. |
| E/W | `returning error to user` | V2 logs E for internal/overloaded/unknown/limit/conflict JSON-RPC codes and W for other codes (`code`, `message`, `requestID`); it then builds/sends the callback. |
| E | `failed to marshal error response` | User JSON-RPC error cannot marshal (`err`, `requestID`); no callback is sent. |
| E | `failed to send user callback` | Marshaled user error cannot be delivered (`err`, `requestID`). |
| E | `Failed to verify JWT` | Request JWT verification fails (`error`); authorization rejects. |
| W | `JWT token has already been used` | Replay-cache hit (`workflowID`, `signer`, `jti`); request is rejected. |
| E | `Workflow ID not found in authorized keys` | No loaded key set for workflow (`workflowID`); authorization rejects. |
| E | `Signer not found in authorized keys` | Verified signer absent from workflow's set (`signer`); authorization rejects. |
| E | `Failed to send pull request` | Periodic metadata pull has node-send failures (`error`); ticker continues. |
| E | `Failed to close WorkflowMetadataAggregator` | One shard aggregator close fails (`shard`, `error`); loop continues and close returns nil. |

## Confidential relay

| Sev | Exact log message | Relay condition, fields, and limit |
|---|---|---|
| E | `failed to apply serve timeout, dropping request` | Lifecycle timeout cannot be acquired/applied (`gatewayID`, `requestID`, `err`); request is dropped before dispatch with no reply from this path. |
| E | `failed to send message to gateway` | A selected/constructed response cannot be sent (`gatewayID`, `err`); relay delivery boundary, not execution cause. |
| E | `failed to marshal response` | Result cannot JSON-marshal (`err`); relay substitutes a generic JSON-RPC internal-error response. |
| E | `request error` | Common protocol error response (`errorCode`, `err`); internal metric increments and internal details are hidden on the wire. |

## Vault

| Sev | Exact log message | Vault condition, fields, and limit |
|---|---|---|
| E | `AllowListBasedAuth workflowRegistrySyncer is nil` | Allowlist auth selected without registry syncer (`method`, `requestID`); request returns internal error. |
| E | `auth mechanism returned nil auth result` | Selected mechanism returns `(nil, nil)` (`method`, `requestID`, `hasAuth`); request is rejected. |
| E | `owner binding rejected request` | Secret owner does not match authorized owner (`method`, `requestID`, `owner`, `hasAuth`, `error`); request stops before owner stamping. |
| E | `AllowListBasedAuth unavailable` | Request without `Auth` selects legacy allowlist auth but authorizer is nil (`method`, `requestID`, `error`). |
| E | `JWTBasedAuth unavailable` | Request with `Auth` selects JWT auth but authorizer is nil (`method`, `requestID`, `error`). |
| E | `error closing vault DON request handler after failed registration` | Registry `Add` fails and compensating handler close also fails (`err`); primary registration failure is still returned. |
| E | `get secrets request contains nil secret request` | Validated batch contains a nil element (`index`); capability request is rejected. |
| E | `get secrets request owner mismatch` | Secret identifier owner differs from metadata workflow owner (`index`, `secretOwner`, `workflowOwner`); request is rejected before OCR handling. |
| E | `gateway vault request authorization failed` | Authorization fails before request/parameter stamping (`method`, `requestID`, `hasAuth`, `incomingOwner`, `error`). |
| E | `failed to stamp authorized request params` | Authorization succeeds but method parameters cannot stamp/marshal (`method`, `requestID`, `error`); processing stops. |
| W | `gateway vault request validation failed` | Validator classifies expected invalid caller input (`method`, `requestID`, `error`); rejection occurs before authorization. |
| E | `failed to validate gateway vault request before authorization` | Validator returns a non-input internal error (same fields); processing stops before authorization. |
| E | `Failed to send message to gateway` | Vault gateway handler cannot send its created response (`requestID`, `method`, `gatewayID`, `error`); capitalization distinguishes it from relay. |
| E | `gateway handler error response` | Shared vault JSON-RPC error response (`requestID`, `method`, `gatewayID`, `errorCode`, `error`); internal metric increments. |
| E | `failed to create VaultJWTAuthEnabled limiter` | Settings-backed gate construction fails (`error`); code substitutes a closed/disabled limiter rather than enabling JWT auth. |
| W | `periodic JWKS refresh failed` | Background refresh tick fails (`error`); service remains running and later ticks retry. |
| E | `failed to resolve JWTBasedAuth gate` | Runtime JWT-enabled gate lookup fails (`method`, `requestID`, `error`); authorization rejects. |
| W | `JWKS refresh failed` | Requested `kid` is absent and on-demand refresh fails (`error`, `kid`); that key remains not found. |
| W | `vault request timed out in capability.handleRequest before a response was delivered` | Context ends before response (`requestID`, `furthest_stage`, detailed lifecycle timestamps/sequences); identifies this node's furthest stage, not why OCR stalled. |
| W | `vault request closed with OCR error response` | Non-timeout OCR/capability error closes request (`requestID`, `err`, lifecycle trace); embedded error is the attribution boundary. |
| W | `capabilities registry lookup failed; using cached zone-b membership` | Registry lookup fails but this workflow DON has cached membership (`workflowDonID`, `isZoneB`, `err`); cached value is used. A never-resolved DON instead returns an error without this log. |

## Returned-only and lower-severity context

These facts are deliberately separate from the emitted warning/error/critical catalog:

- `metadataRegistry information not available` is returned by metadata-registry lookup methods when the local pointer is nil; it is not emitted by those methods. A caller may later log the returned error. It says nothing about fleet health.
- `invariant violation: node is part of more than one workflowDON` is returned-only in the inspected capability-registry path. The emitted local-registry diagnostic is instead `Configuration error: node belongs to more than one workflowDON` above.
- `could not resolve capability binary`, `build config`, `build services`, and `start service` are useful nested returned causes carried by `Failed to start capability`, not independent direct log templates here.
- `Engine is draining, dropping trigger event before enqueue` is production Info-level lifecycle behavior, outside this warning-or-higher catalog. Draining proves neither queue failure nor dependency failure.
- `reconciliation tick completed`, `Found my workflow DONs`, `Found my capability DONs`, `Started capability`, `Stopping removed capability`, `Restarting capability due to config change`, and `donPairsToUpdate: filtering out DON pair due to family mismatch` are lower-severity observations. Exact peer inclusion or a filtered family-mismatch pair is node-local; zero membership after workflow/public/config filters is an observation, not a fault. Their absence is not a failure signal.
