# GENERATION_PACKET_002

## 1. Packet Identity

```text
packet_id: GENERATION_PACKET_002
packet_title: Stage 3 generation packet final authority reconciliation
target_stage: Stage 3 - Domain, Failure, and Stable State Model
status: FINAL_AUTHORITY_RECONCILED_PACKET_ONLY
implementation_authorized_by_this_packet: false
remediation_status: FUTURE_STAGE_3_READY_FOR_REDUCED_ENUM_FAILURE_SUBSET_ONLY
stable_state_status: DEFERRED_NOT_AUTHORIZED
primitive_representation_status: UNRESOLVED_PRIMITIVE_ALIASES_DEFERRED
allowed_file_for_this_packet: docs/GENERATION_PACKET_002.md
```

This packet does not generate Stage 3 implementation code. It reconciles the
future Stage 3 implementation authority after identifying that the current
GOV/SRC/BLD authority does not uniquely determine Motoko primitive
representations for required domain and stable-state aliases.

Stage 3 implementation is safe to begin only for the reduced subset explicitly
authorized in this packet:

```text
domain enum declarations
failure-code enum declaration
deterministic external failure-code mapping
future Stage 3 verification harness updates for this reduced subset
```

Stage 3 implementation is not authorized for:

```text
primitive-backed domain aliases
domain records that depend on unresolved primitive-backed fields
stable mirror records
StableState aggregate
upgrade hooks
public APIs
Candid surface changes
transfer execution logic
balance logic
ledger commit logic
idempotency execution logic
read models
```

## 2. Authority Inspected For This Reconciliation

The future Stage 3 implementation prompt must inspect these authority files
again before editing:

```text
AGENTS.md
sources/gov/GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl
sources/src/SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl
sources/bld/BLD-INDEX__BUILD_TRACEABILITY__LOOKUP_ROUTING.jsonl
sources/src/SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl
sources/src/SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl
sources/src/SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl
sources/src/SRC-05__LEDGER_JOURNAL_INVARIANTS__SOURCE__SYSTEM.jsonl
sources/src/SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl
sources/src/SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl
sources/src/SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl
sources/src/SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl
sources/bld/BLD-02__DOMAIN_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl
sources/bld/BLD-03__TRANSFER_PIPELINE_IMPLEMENTATION__BUILD__SYSTEM.jsonl
sources/bld/BLD-04__IDEMPOTENCY_REPLAY_IMPLEMENTATION__BUILD__SYSTEM.jsonl
sources/bld/BLD-05__LEDGER_JOURNAL_COMMIT_IMPLEMENTATION__BUILD__SYSTEM.jsonl
sources/bld/BLD-06__FAILURE_HANDLING_IMPLEMENTATION__BUILD__SYSTEM.jsonl
sources/bld/BLD-08__UPGRADE_SAFETY_IMPLEMENTATION__BUILD__SYSTEM.jsonl
sources/bld/BLD-09__API_SURFACE_IMPLEMENTATION__BUILD__SYSTEM.jsonl
sources/bld/BLD-10__TEST_PROOF_IMPLEMENTATION__BUILD__SYSTEM.jsonl
docs/GENERATION_PACKET_002.md
docs/IMPLEMENTATION_FILE_MAP.md
docs/SCRIPTED_VERIFICATION.md
scripts/verify.ps1
```

## 3. Reconciled Scope Decision

Authority conclusion:

```text
1. Source and build authority define required domain concepts, stable records,
   canonical result serialization, replay semantics, ledger proof, and upgrade
   preservation obligations.
2. Source and build authority do not uniquely authorize Motoko primitive
   representations such as Text, Nat, Nat64, Blob, Principal, arrays, or maps
   for the primitive-backed aliases and fields listed in this packet.
3. A Stage 3 implementation packet must not choose those primitive
   representations by inference.
4. StableState is mandatory in the eventual kernel, but the complete and
   stable-compatible Motoko record layout cannot be authorized until the
   primitive representation registry and every stable mirror record are
   resolved.
5. Therefore Stage 3 is reduced to exact non-primitive enum foundations and
   the failure-code registry only.
```

StableState reconciliation option selected:

```text
Option B: defer StableState and state/StableState.mo.
```

No partial StableState aggregate is authorized by this packet.

## 4. Future Stage 3 Allowed File Manifest

| File | Classification | Authority | Stage 3 Rule |
| --- | --- | --- | --- |
| `canisters/ledger_kernel/src/domain/Types.mo` | REQUIRED | SRC-02, SRC-03, SRC-04, SRC-05, SRC-06, BLD-02, BLD-03, BLD-04, BLD-05, BLD-06 | May contain only the exact authorized enum declarations listed in this packet. Must not define primitive aliases or records. |
| `canisters/ledger_kernel/src/domain/Errors.mo` | REQUIRED | SRC-06, SRC-03 result failure records, BLD-06 | May contain only `FailureCode` and deterministic mappings from each code variant to the canonical external `FAIL-###` text. Must not define rejection-reason or response records. |
| `canisters/ledger_kernel/src/domain/Constants.mo` | DEFERRED_NOT_AUTHORIZED | SRC-02, SRC-06, BLD-02, BLD-06 | Do not create in reduced Stage 3. Constants depending on primitive representations, amount bounds, timestamp formats, or domain records require future representation authority. |
| `canisters/ledger_kernel/src/state/StateTypes.mo` | DEFERRED_NOT_AUTHORIZED | SRC-08, BLD-08 | Do not create in reduced Stage 3. Stable mirror records depend on deferred primitive representations and complete stable schema authority. |
| `canisters/ledger_kernel/src/state/StableState.mo` | DEFERRED_NOT_AUTHORIZED | SRC-08, BLD-08 | Do not create in reduced Stage 3. StableState is deferred until all required stable records and version fields are uniquely represented. |
| `scripts/check-stage3-domain-state-model.ps1` | REQUIRED | SRC-10, BLD-10, this packet | Must enforce the reduced subset and fail closed on deferred aliases, records, stable-state files, or unauthorized primitive choices. |
| `scripts/verify.ps1` | REQUIRED | AGENTS.md, BLD-10 | Must invoke the Stage 3 check script after it exists. |
| `docs/IMPLEMENTATION_FILE_MAP.md` | REQUIRED | AGENTS.md, BLD-10 | Must map every Stage 3 implementation and verification file created or modified. |
| `docs/SCRIPTED_VERIFICATION.md` | REQUIRED | AGENTS.md, BLD-10 | Must document the new Stage 3 check script and reduced-scope obligations. |
| `reports/` generated validation output | OPTIONAL_GENERATED | existing validators | May be updated by validators only. |
| `.dfx/` generated build output | OPTIONAL_GENERATED_REMOVE_AFTER_VALIDATION | dfx build | May be generated during validation and must be removed before final status. |

Forbidden in reduced Stage 3:

```text
canisters/ledger_kernel/src/Main.mo
canisters/ledger_kernel/ledger_kernel.did
dfx.json
docs/GENERATION_PACKET_001.md
docs/GENERATION_PACKET_002.md
canisters/ledger_kernel/src/state/StateTypes.mo
canisters/ledger_kernel/src/state/StableState.mo
canisters/ledger_kernel/src/state/UpgradeHooks.mo
canisters/ledger_kernel/src/transfer/**
canisters/ledger_kernel/src/balance/**
canisters/ledger_kernel/src/ledger/**
canisters/ledger_kernel/src/idempotency/**
canisters/ledger_kernel/src/read_model/**
canisters/ledger_kernel/src/api/**
any public API method
any Candid surface change
any unsupported operation type
```

## 5. Exact Authorized Motoko Type Representations

These are the only structures authorized for future reduced Stage 3
implementation.

| Structure | Exact Motoko Representation | Owning Authority | Stable Compatibility | Canonical Serialization Requirement | Unique Representation Authority | Authority Status |
| --- | --- | --- | --- | --- | --- | --- |
| `AccountStatus` | `public type AccountStatus = { #ACTIVE; #FROZEN; #CLOSED };` | SRC-02 `ACCOUNT-008`; BLD-02 account status obligations | Compatible as a domain enum only. Stable record use is deferred. | No external serialization authorized in reduced Stage 3. | YES. Exact enum variants are source-governed. | AUTHORIZED |
| `AssetStatus` | `public type AssetStatus = { #ACTIVE; #DISABLED };` | SRC-02 asset status authority; BLD-02 asset model obligations | Compatible as a domain enum only. Stable record use is deferred. | No external serialization authorized in reduced Stage 3. | YES. Exact enum variants are source-governed. | AUTHORIZED |
| `OperationType` | `public type OperationType = { #TRANSFER };` | SRC-02 `OPER-014`; BLD-02 operation type restrictions | Compatible as a domain enum only. Stable record use is deferred. | Must not add Deposit, Withdraw, Mint, Burn, Fee, Reversal, BatchTransfer, AdminAdjustment, or equivalent operations. | YES. MVP operation set is exactly Transfer. | AUTHORIZED |
| `OperationStatus` | `public type OperationStatus = { #RECEIVED; #COMMITTED; #REJECTED };` | SRC-02 operation status authority; SRC-03 lifecycle/result authority; BLD-03 | Compatible as a domain enum only. Stable record use is deferred. | No external serialization authorized in reduced Stage 3. | YES. Exact lifecycle statuses are source-governed. | AUTHORIZED |
| `IdempotencyStatus` | `public type IdempotencyStatus = { #COMMITTED; #REJECTED; #IN_PROGRESS };` | SRC-04 `IDEMP-032`; BLD-04 `BLD-04-STATE-001` | Compatible as a domain enum only. Stable record use is deferred. | No external serialization authorized in reduced Stage 3. | YES. Exact idempotency statuses are source-governed. | AUTHORIZED |
| `IdempotencyRecoveryState` | `public type IdempotencyRecoveryState = { #NONE; #STALE_IN_PROGRESS; #RECOVERY_REQUIRED };` | SRC-04 `IDEMP-033`; BLD-04 `BLD-04-STATE-002` | Compatible as a domain enum only. Stable record use is deferred. | No external serialization authorized in reduced Stage 3. | YES. Exact recovery states are source-governed. | AUTHORIZED |
| `LedgerEntryDirection` | `public type LedgerEntryDirection = { #DEBIT; #CREDIT };` | SRC-05 `LEDGER-009`; BLD-05 `BLD-05-DATA-001` | Compatible as a domain enum only. Stable record use is deferred. | No external serialization authorized in reduced Stage 3. | YES. Exact debit/credit directions are source-governed. | AUTHORIZED |
| `FailureCode` | `public type FailureCode = { #FAIL_001; #FAIL_002; #FAIL_003; #FAIL_004; #FAIL_005; #FAIL_006; #FAIL_007; #FAIL_008; #FAIL_009; #FAIL_010; #FAIL_011; #FAIL_012; #FAIL_013; #FAIL_014; #FAIL_015; #FAIL_016; #FAIL_017; #FAIL_018; #FAIL_019; #FAIL_020 };` | SRC-06 `FAIL-001` through `FAIL-020`; SRC-03 result failure authority; BLD-06 `BLD-06-TARGET-003` | Compatible as a domain enum only. Stable record use is deferred. | A pure mapping function may return canonical external text `FAIL-001` through `FAIL-020`. No stored primitive alias is authorized. | YES. Exact failure code set is source-governed. | AUTHORIZED |

No other Motoko type, alias, record, variant, class, actor method, mutable state,
stable variable, map, or collection is authorized by this packet.

## 6. Primitive Representation Registry

Every row below is explicitly deferred. Future implementation must not define
these names or choose `Text`, `Nat`, `Nat64`, `Int`, `Blob`, `Principal`,
arrays, maps, or any other primitive/container representation unless a future
governed representation packet grants exact authority.

| Alias / Field | Exact Motoko Representation | Owning SRC / BLD Authority | Stable Compatibility | Canonical Serialization Requirement | Dependent Records / Structures | Unique Representation Authority | Authority Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `AccountId` | DEFERRED_NOT_AUTHORIZED | SRC-02 account identity authority; SRC-03 `RESULT-041`; SRC-08 `STABLE-017`; BLD-02 account model | BLOCKED until exact primitive representation is authorized. | External committed results require stable textual account identifiers, but that does not authorize internal Motoko representation. | `Account`, `Balance`, transfer request/result records, ledger records, stable account/balance records | NO. Primitive representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `AssetId` | DEFERRED_NOT_AUTHORIZED | SRC-02 asset identity authority; SRC-03 `RESULT-041`; SRC-08 `STABLE-018`; BLD-02 asset model | BLOCKED until exact primitive representation is authorized. | External committed results require stable textual asset identifiers, but that does not authorize internal Motoko representation. | `Asset`, `Balance`, transfer request/result records, ledger records, stable asset/balance records | NO. Primitive representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `OperationId` | DEFERRED_NOT_AUTHORIZED | SRC-02 `OPER-012`; SRC-03 `RESULT-042`; SRC-08 `STABLE-019`; BLD-02 operation model | BLOCKED until exact primitive representation is authorized. | External committed results require stable textual operation identifiers, but that does not authorize internal Motoko representation. | `Operation`, `TransferRecord`, result records, idempotency records, ledger trace links, stable operation records | NO. Primitive representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `RequestId` | DEFERRED_NOT_AUTHORIZED | SRC-03 transfer request and result authority; SRC-04 idempotency identity authority; BLD-03, BLD-04 | BLOCKED until exact primitive representation is authorized. | Request identity must deterministically replay, but primitive representation is not uniquely selected. | `TransferRequest`, `RequestIdentity`, `IdempotencyRecord`, request outcome records | NO. Primitive representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `RequestIdentity` | DEFERRED_NOT_AUTHORIZED | SRC-04 idempotency identity and replay authority; BLD-04 | BLOCKED until exact primitive representation and field set are authorized. | Canonical identity material must be deterministic, but Motoko structure is not uniquely selected. | `IdempotencyRecord`, request outcome records, replay lookup state | NO. Primitive representation and record shape are not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `IdempotencyKey` | DEFERRED_NOT_AUTHORIZED | SRC-04 idempotency key authority; SRC-03 result replay authority; BLD-04 | BLOCKED until exact primitive representation is authorized. | Key matching must be deterministic, but primitive representation is not uniquely selected. | `RequestIdentity`, `IdempotencyRecord`, replay lookup state | NO. Primitive representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `LedgerEntryId` | DEFERRED_NOT_AUTHORIZED | SRC-05 ledger entry identity authority; SRC-03 `RESULT-043`; SRC-08 `STABLE-021`; BLD-05 | BLOCKED until exact primitive representation is authorized. | Ledger entry identifiers must be stable and traceable, but primitive representation is not uniquely selected. | `LedgerEntry`, transfer ledger-link records, stable ledger records | NO. Primitive representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `Amount` | DEFERRED_NOT_AUTHORIZED | SRC-02 amount minor-unit authority; SRC-03 `RESULT-040`; BLD-02 amount model | BLOCKED until exact integer representation and bounds are authorized. | Amounts must be canonical unsigned minor-unit quantities with no floating point use, but Motoko `Nat`, `Nat64`, or other exact type is not uniquely authorized. | `Balance`, `TransferRequest`, committed result records, ledger records, stable balance/ledger records | NO. Integer representation and bound type are not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `createdAt` | DEFERRED_NOT_AUTHORIZED | SRC-02 creation timestamp fields; SRC-03 time/result authority; SRC-08 stable preservation; BLD-02, BLD-03, BLD-08 | BLOCKED until exact timestamp representation is authorized. | Canonical result timestamps require deterministic formatting where exposed, but internal Motoko representation is not uniquely selected. | account, asset, operation, idempotency, ledger, and stable records | NO. Timestamp representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `updatedAt` | DEFERRED_NOT_AUTHORIZED | SRC-02 update timestamp fields; SRC-03 time authority; SRC-08 stable preservation; BLD-02, BLD-08 | BLOCKED until exact timestamp representation is authorized. | Canonical formatting requirements do not authorize internal representation. | balance and mutable state records, stable records | NO. Timestamp representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `completedAt` | DEFERRED_NOT_AUTHORIZED | SRC-03 result completion timestamp authority; SRC-04 idempotency completion authority; SRC-08 stable preservation; BLD-03, BLD-04, BLD-08 | BLOCKED until exact timestamp representation is authorized. | Canonical committed/rejected result timestamps must be deterministic, but internal representation is unresolved. | operation result, idempotency outcome, replay, and stable records | NO. Timestamp representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `canonicalTimestamp` | DEFERRED_NOT_AUTHORIZED | SRC-03 `RESULT-039`; transfer time authority; BLD-03 | BLOCKED until exact primitive representation is authorized. | External serialization requires RFC3339Nano-compatible UTC text with exactly nine fractional digits and trailing `Z`; this does not authorize a Motoko alias representation. | result records, deterministic response hashing, replay outcomes | NO. Canonical external serialization exists, but internal alias representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `StableStateVersion` | DEFERRED_NOT_AUTHORIZED | SRC-08 `STABLE-023`, `STABLE-024`; BLD-08 `BLD-08-TARGET-003` | BLOCKED until exact version representation is authorized. | Version data must be queryable/inspectable, but Motoko representation is unresolved. | `StableState`, `StableVersionData`, upgrade metadata | NO. Version representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `StableSchemaVersion` | DEFERRED_NOT_AUTHORIZED | SRC-08 `STABLE-015`, `STABLE-023`, `STABLE-024`, `STABLE-027`; BLD-08 `BLD-08-TARGET-003` | BLOCKED until exact schema-version representation is authorized. | Schema version must control upgrade compatibility and reject unsupported unknown schemas, but Motoko representation is unresolved. | `StableState`, stable version boundary, migration checks | NO. Schema-version representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `responseHash` | DEFERRED_NOT_AUTHORIZED | SRC-04 replay hash authority; SRC-03 `RESULT-023`; BLD-04 | BLOCKED until exact primitive representation is authorized. | Canonical response hash must be SHA-256 lowercase hexadecimal over canonical response bytes, but storage representation is unresolved. | `IdempotencyRecord`, replay outcome records, stable idempotency records | NO. Hash storage representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `deterministicResponse` | DEFERRED_NOT_AUTHORIZED | SRC-04 deterministic replay authority; SRC-03 canonical result authority; BLD-04 | BLOCKED until exact primitive representation is authorized. | Replay response must match canonical deterministic result bytes/content, but Motoko representation is unresolved. | `RequestOutcome`, `IdempotencyRecord`, stable idempotency/replay records | NO. Response storage representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `Asset.symbol` | DEFERRED_NOT_AUTHORIZED | SRC-02 asset symbol authority; BLD-02 asset model | BLOCKED until exact primitive representation is authorized. | Asset display metadata is governed, but Motoko representation is unresolved. | `Asset`, stable asset records, result/display metadata if later exposed | NO. Symbol representation is not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `Asset.decimals` | DEFERRED_NOT_AUTHORIZED | SRC-02 asset decimal precision authority; SRC-02 amount minor-unit authority; BLD-02 amount and asset model | BLOCKED until exact primitive representation and bounds are authorized. | Decimal precision governs amount interpretation, but Motoko representation is unresolved. | `Asset`, `Amount` validation constants, stable asset records | NO. Decimal precision representation and bounds are not uniquely determined. | DEFERRED_NOT_AUTHORIZED |
| `rejectionReason` | DEFERRED_NOT_AUTHORIZED | SRC-03 rejected result authority; SRC-06 deterministic failure model; BLD-06 | BLOCKED until exact primitive representation and allowed content are authorized. | Rejected outcomes must be deterministic and replayable, but free-form or coded reason representation is unresolved. | rejected result records, request outcome records, idempotency records, stable replay records | NO. Rejection reason representation and allowed content are not uniquely determined. | DEFERRED_NOT_AUTHORIZED |

Any primitive-backed alias, field, record member, map key, map value, list element,
or stable-field representation not explicitly authorized in Section 5 is also
deferred.

## 7. StableState Completeness Reconciliation

Decision:

```text
StableState is DEFERRED_NOT_AUTHORIZED for reduced Stage 3.
canisters/ledger_kernel/src/state/StableState.mo is DEFERRED_NOT_AUTHORIZED.
canisters/ledger_kernel/src/state/StateTypes.mo is DEFERRED_NOT_AUTHORIZED.
```

Governing stable-state authority requires the eventual stable boundary to
include at least:

```text
accounts
assets
balances
operations
idempotency records
ledger entries
schema version
maintenance flag where used
version data required by StableStateVersion / StableSchemaVersion authority
```

This follows SRC-08 `STABLE-009` through `STABLE-015`,
SRC-08 `STABLE-023`, SRC-08 `STABLE-024`, SRC-08 `STABLE-027`,
and BLD-08 `BLD-08-TARGET-002`, `BLD-08-TARGET-003`, and
`BLD-08-REVIEW-001`.

No complete field set is authorized in this packet because the required stable
records depend on unresolved primitive representations and unresolved mirror
record layouts.

Deferred stable structures:

```text
StableState
StableAccountRecord
StableAssetRecord
StableBalanceRecord
StableOperationRecord
StableTransferRecord
StableRequestRecord
StableIdempotencyRecord
StableLedgerEntryRecord
StableJournalRecord
StableVersionData
StableSchemaVersionData
StableProjectionMetadata
UpgradeCheckpointData
MaintenanceDiagnosticData
UpgradeProofReportData
```

The future governed packet required to unblock this work is:

```text
Stable Schema Representation and Motoko Type Authority Packet
```

That future packet must be subordinate to GOV-00, SRC-02, SRC-03, SRC-04,
SRC-05, SRC-08, SRC-10, BLD-02, BLD-03, BLD-04, BLD-05, BLD-08, and BLD-10.
It must uniquely authorize:

```text
every primitive-backed domain alias
every stable mirror record field
every stable collection representation
StableStateVersion representation
StableSchemaVersion representation
schema version rejection behavior
stable compatibility constraints
canonical serialization or hashing representation where required
domain/stable representation drift checks
```

## 8. Final Stage 3 Authorized Structure List

Future reduced Stage 3 may implement only:

```text
AccountStatus
AssetStatus
OperationType
OperationStatus
IdempotencyStatus
IdempotencyRecoveryState
LedgerEntryDirection
FailureCode
pure deterministic FailureCode -> canonical external FAIL-### text mapping
pure deterministic FailureCode classification helpers only when sourced directly
from SRC-06 without adding new stored data structures
```

Future reduced Stage 3 must not implement:

```text
AccountId
AssetId
OperationId
RequestId
RequestIdentity
IdempotencyKey
LedgerEntryId
Amount
createdAt
updatedAt
completedAt
canonicalTimestamp
StableStateVersion
StableSchemaVersion
responseHash
deterministicResponse
Asset.symbol
Asset.decimals
rejectionReason
Account
Asset
Balance
Operation
TransferRequest
TransferResult
CommittedTransferResult
RejectedTransferResult
RequestOutcome
IdempotencyRecord
LedgerEntry
StableState
any Stable* record
```

## 9. Future Stage 3 Verification Obligations

The future `scripts/check-stage3-domain-state-model.ps1` must fail closed if it
detects any of the following:

```text
1. A deferred alias from Section 6 is declared.
2. A primitive representation such as Text, Nat, Nat64, Int, Blob, Principal,
   array, map, trie, buffer, or hash map is chosen for a deferred alias.
3. Any record declaration for Account, Asset, Balance, Operation,
   TransferRequest, TransferResult, CommittedTransferResult,
   RejectedTransferResult, RequestOutcome, IdempotencyRecord, LedgerEntry, or
   Stable* appears in reduced Stage 3 files.
4. canisters/ledger_kernel/src/state/StateTypes.mo exists.
5. canisters/ledger_kernel/src/state/StableState.mo exists.
6. canisters/ledger_kernel/src/domain/Constants.mo exists.
7. Any enum in Section 5 has missing, extra, renamed, or differently cased
   variants.
8. OperationType contains anything other than #TRANSFER.
9. FailureCode contains anything other than #FAIL_001 through #FAIL_020.
10. FailureCode external mapping emits anything other than FAIL-001 through
    FAIL-020.
11. Unsupported operations appear anywhere in Stage 3 implementation files:
    Deposit, Withdraw, Mint, Burn, Fee, Reversal, BatchTransfer,
    AdminAdjustment, or equivalents.
12. Domain/stable representation drift is possible because a stable mirror
    structure was introduced before the future representation packet.
13. StableState is partial, unversioned, missing authoritative records, or
    missing schema/version authority.
14. Public API or Candid surface changes are introduced.
15. `await` appears in any future consistency-boundary path, if such path is
    accidentally introduced.
```

The future Stage 3 verification update must also:

```text
1. Add the Stage 3 check script to scripts/verify.ps1.
2. Document the script in docs/SCRIPTED_VERIFICATION.md.
3. Map all created or modified files in docs/IMPLEMENTATION_FILE_MAP.md.
4. Run Motoko type checks only for implementation files that exist and are
   authorized by this reduced subset.
5. Treat missing deferred files as PASS for reduced Stage 3, not as coverage
   gaps.
6. Treat creation of deferred files as FAIL.
7. Preserve existing source validators, forbidden API checks, forbidden internal
   pattern checks, no-await checks, Candid/API surface checks, file ownership
   map checks, module coverage checks, dfx build checks, and git diff checks.
```

## 10. Embedded Future Stage 3 Codex Prompt Template

```text
PHASE:
Stage 3 reduced enum/failure registry implementation

OBJECTIVE:
Implement only the final authority-reconciled Stage 3 subset from
docs/GENERATION_PACKET_002.md. Do not implement deferred primitive aliases,
domain records, stable mirror records, StableState, public APIs, transfer
execution, balance logic, ledger logic, idempotency execution, read models, or
Candid changes.

PRECONDITION:
Run git status --short before editing. If files other than the allowed Stage 3
targets below are modified or untracked, stop and report BLOCKED unless the
status is clearly generated validation output allowed by AGENTS.md.

AUTHORITY TO INSPECT BEFORE EDITING:
- AGENTS.md
- sources/gov/GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl
- sources/src/SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl
- sources/bld/BLD-INDEX__BUILD_TRACEABILITY__LOOKUP_ROUTING.jsonl
- sources/src/SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl
- sources/src/SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl
- sources/src/SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl
- sources/src/SRC-05__LEDGER_JOURNAL_INVARIANTS__SOURCE__SYSTEM.jsonl
- sources/src/SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl
- sources/src/SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl
- sources/src/SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl
- sources/src/SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl
- sources/bld/BLD-02__DOMAIN_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl
- sources/bld/BLD-03__TRANSFER_PIPELINE_IMPLEMENTATION__BUILD__SYSTEM.jsonl
- sources/bld/BLD-04__IDEMPOTENCY_REPLAY_IMPLEMENTATION__BUILD__SYSTEM.jsonl
- sources/bld/BLD-05__LEDGER_JOURNAL_COMMIT_IMPLEMENTATION__BUILD__SYSTEM.jsonl
- sources/bld/BLD-06__FAILURE_HANDLING_IMPLEMENTATION__BUILD__SYSTEM.jsonl
- sources/bld/BLD-08__UPGRADE_SAFETY_IMPLEMENTATION__BUILD__SYSTEM.jsonl
- sources/bld/BLD-09__API_SURFACE_IMPLEMENTATION__BUILD__SYSTEM.jsonl
- sources/bld/BLD-10__TEST_PROOF_IMPLEMENTATION__BUILD__SYSTEM.jsonl
- docs/GENERATION_PACKET_002.md
- docs/IMPLEMENTATION_FILE_MAP.md
- docs/SCRIPTED_VERIFICATION.md
- scripts/verify.ps1

ALLOWED FILES:
- canisters/ledger_kernel/src/domain/Types.mo
- canisters/ledger_kernel/src/domain/Errors.mo
- scripts/check-stage3-domain-state-model.ps1
- scripts/verify.ps1
- docs/IMPLEMENTATION_FILE_MAP.md
- docs/SCRIPTED_VERIFICATION.md

REQUIRED IMPLEMENTATION:
- In Types.mo, define only:
  - public type AccountStatus = { #ACTIVE; #FROZEN; #CLOSED };
  - public type AssetStatus = { #ACTIVE; #DISABLED };
  - public type OperationType = { #TRANSFER };
  - public type OperationStatus = { #RECEIVED; #COMMITTED; #REJECTED };
  - public type IdempotencyStatus = { #COMMITTED; #REJECTED; #IN_PROGRESS };
  - public type IdempotencyRecoveryState = { #NONE; #STALE_IN_PROGRESS; #RECOVERY_REQUIRED };
  - public type LedgerEntryDirection = { #DEBIT; #CREDIT };
- In Errors.mo, define only:
  - public type FailureCode = { #FAIL_001; #FAIL_002; #FAIL_003; #FAIL_004; #FAIL_005; #FAIL_006; #FAIL_007; #FAIL_008; #FAIL_009; #FAIL_010; #FAIL_011; #FAIL_012; #FAIL_013; #FAIL_014; #FAIL_015; #FAIL_016; #FAIL_017; #FAIL_018; #FAIL_019; #FAIL_020 };
  - pure deterministic mapping from each FailureCode variant to exact external text FAIL-001 through FAIL-020.
  - optional pure classification helpers only if they are directly sourced from SRC-06 and introduce no stored records or aliases.

FORBIDDEN IMPLEMENTATION:
- Do not define AccountId, AssetId, OperationId, RequestId, RequestIdentity,
  IdempotencyKey, LedgerEntryId, Amount, createdAt, updatedAt, completedAt,
  canonicalTimestamp, StableStateVersion, StableSchemaVersion, responseHash,
  deterministicResponse, Asset.symbol, Asset.decimals, or rejectionReason.
- Do not define Account, Asset, Balance, Operation, TransferRequest,
  TransferResult, CommittedTransferResult, RejectedTransferResult,
  RequestOutcome, IdempotencyRecord, LedgerEntry, StableState, or any Stable*
  record.
- Do not create Constants.mo, StateTypes.mo, StableState.mo, or UpgradeHooks.mo.
- Do not edit Main.mo, dfx.json, .did files, docs/GENERATION_PACKET_001.md,
  docs/GENERATION_PACKET_002.md, transfer, balance, ledger, idempotency,
  read_model, api, or unrelated files.
- Do not expose public APIs or Candid methods.
- Do not add unsupported operation types.

REQUIRED VERIFICATION:
- Create scripts/check-stage3-domain-state-model.ps1 to enforce the reduced
  subset and fail closed on deferred aliases, forbidden records, forbidden
  files, unauthorized primitive choices, enum drift, operation drift, failure
  code drift, partial StableState, public API/Candid drift, and use of deferred
  structures.
- Update scripts/verify.ps1 to run the Stage 3 check script.
- Update docs/SCRIPTED_VERIFICATION.md.
- Update docs/IMPLEMENTATION_FILE_MAP.md for every created or modified file.
- Run:
  - python -B tools/source_validator/validate_src.py --sources sources --reports reports
  - python -B tools/source_validator/validate_bld.py --sources sources --reports reports
  - python -B tools/source_validator/validate_all.py --sources sources --reports reports
  - python -B -m unittest discover -s tools/source_validator/tests
  - pwsh -File ./scripts/verify.ps1
  - dfx build --check
  - git diff --check
  - git status --short
- Remove generated .dfx artifacts after validation.

STOP CONDITIONS:
- If any required authority file is missing, report BLOCKED.
- If representation authority is still required for the reduced subset, report
  BLOCKED instead of inventing a representation.
- If StableState, stable records, primitive aliases, or domain records are
  necessary to make the reduced subset compile, report BLOCKED.
- If verify.ps1 cannot pass because of missing tools or out-of-scope failures,
  report BLOCKED or WARNING_ONLY according to AGENTS.md.
```

## 11. Readiness Result

```text
Stage 3 implementation safe to begin:
SAFE_ONLY_FOR_REDUCED_ENUM_FAILURE_REGISTRY_SUBSET

StableState remains authorized for eventual project:
YES, by SRC-08 and BLD-08.

StableState authorized for reduced Stage 3 implementation:
NO.

Exact StableState complete field set authorized in this packet:
NONE. StableState is deferred.

Packet required to resolve StableState:
Stable Schema Representation and Motoko Type Authority Packet.

Prompt template updated:
YES.

Remaining blocker:
Primitive-backed domain and stable-state Motoko representations are not
uniquely determined by existing GOV/SRC/BLD authority and must be resolved
before records, stable mirrors, or StableState can be implemented.
```
