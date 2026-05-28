# ICP Deterministic Ledger Kernel 2 — Code Creation Plan With Scripted Verification

## 1. Purpose

This plan defines the recommended implementation process for creating the **ICP Deterministic Ledger Kernel 2** codebase.

The project must not be built like a normal application where UI, convenience endpoints, and demo features come first. It must be built as a **source-governed correctness kernel**.

The implementation sequence is:

```text
Authority → Verification Harness → ICP Skeleton → Domain → Stable State
→ Authority Boundary → Validation/Lifecycle → Balance Control
→ Ledger Journal → Idempotency → Transfer Executor → Read Model
→ Public API/Candid Lock → Proof Tests → Runtime dfx Verification
→ Documentation/Proof Report → Optional Demo Client
```

The goal is to prevent implementation drift away from the governed source files and make Codex output mechanically checkable.

---

## 2. Core Build Principle

The kernel must prove this before any optional demo client is added:

```text
A transfer request can mutate balances only through the governed execution path,
produce append-only ledger proof,
preserve deterministic idempotency/replay,
survive upgrade constraints,
avoid partial commits,
expose only safe public APIs,
and pass scripted verification before each phase advances.
```

The product is not the UI.

The product is the governed deterministic ledger kernel.

---

## 3. Correct Tool Responsibilities

| Tool | Responsibility |
|---|---|
| **ChatGPT** | Architecture review, authority alignment, phase planning, Codex prompt generation, risk analysis, implementation review, proof report review |
| **Codex** | Repo edits, code generation, script generation, test generation, validator execution, patching failed implementation, producing exact change reports |
| **dfx / ICP local tooling** | Build, deploy, local canister execution, manual runtime verification |
| **GitHub** | Version control, diff review, phase history, rollback point |

UI/demo work is deferred and non-authoritative.

---

## 4. Operating Model

Use this loop for every implementation phase:

```text
1. ChatGPT creates a narrow Codex prompt for one phase.
2. Codex inspects the required GOV/SRC/BLD authority files.
3. Codex generates or patches only the files for that phase.
4. Codex creates or updates matching scripts/tests/proof entries.
5. Codex runs validators, build commands, tests, scans, or dfx checks.
6. Codex reports exact changes and proof status.
7. The user pastes Codex's result back into ChatGPT.
8. ChatGPT reviews the result and generates the next prompt.
```

Codex should do code generation.

ChatGPT should provide prompts, constraints, review, and architecture control.

Codex must not independently decide architecture.

---

## 5. Required Codex Phase Report Format

Every Codex phase must end with this report:

```text
PHASE:
STATUS: PASS | WARNING_ONLY | BLOCKED | FAILED

AUTHORITY INSPECTED:
- GOV-00 ...
- SRC-...
- BLD-...

FILES CREATED:
- ...

FILES MODIFIED:
- ...

FILES INTENTIONALLY NOT TOUCHED:
- ...

SCRIPTS CREATED OR UPDATED:
- ...

TESTS CREATED OR UPDATED:
- ...

IMPLEMENTATION FILE MAP UPDATES:
- ...

COMMANDS RUN:
- ...

TEST / BUILD / SCRIPT RESULT:
- ...

FORBIDDEN API CHECK:
- PASS | FAIL
- Details:

FORBIDDEN INTERNAL PATTERN CHECK:
- PASS | FAIL
- Details:

NO-AWAIT CONSISTENCY CHECK:
- PASS | FAIL
- Details:

CANDID/API SURFACE CHECK:
- PASS | FAIL | NOT_APPLICABLE
- Details:

KNOWN GAPS / BLOCKERS:
- ...

GIT DIFF SUMMARY:
- ...
```

A vague Codex response is not acceptable.

Codex must produce an auditable implementation report after each phase.

---

## 6. Global Hard Rules

These rules apply to every phase.

### 6.1 Authority Rules

```text
GOV/SRC/BLD files are authority.
Code is downstream output.
Generated implementation must not override authority.
Codex must not invent unsupported operations, roles, states, APIs, or failure codes.
```

### 6.2 Transfer-Only MVP Rule

```text
The MVP supports Transfer only.
No Deposit, Withdraw, Mint, Burn, Fee, Reversal, BatchTransfer, or AdminAdjustment
may be introduced unless the governed source files explicitly authorize it.
```

### 6.3 Single Mutation Path Rule

```text
All balance-affecting mutation must enter through submitTransfer.
Internal mutation must route through the governed TransferExecutor / Consistency Boundary.
No public API may mutate balances, ledger entries, transfer states, read models, or request outcomes directly.
```

### 6.4 No-Await Consistency Boundary Rule

```text
The balance-affecting transfer consistency boundary must not use await.
The transfer execution path must not perform inter-canister calls during mutation planning or commit.
```

Required internal order:

```text
authority check
→ idempotency check
→ validation
→ lifecycle transition
→ balance mutation plan
→ ledger journal plan
→ commit governed state changes
→ persist request outcome
→ return deterministic result
```

If an `await` is introduced inside this path, the phase is blocked unless the authority files explicitly govern it and tests prove it safe.

### 6.5 Ledger Proof Rule

```text
No committed balance mutation is valid without ledger proof.
A committed transfer must have append-only ledger entries linked to the transfer.
```

### 6.6 Replay Rule

```text
A duplicate request identity must return the same stored outcome.
It must not execute transfer logic a second time.
Both successful and rejected outcomes must replay deterministically.
```

### 6.7 Upgrade Safety Rule

```text
Correctness-critical data must survive canister upgrade.
No balances, ledger entries, transfer records, request outcomes, or idempotency records
may exist only in non-stable memory unless explicitly rebuildable from stable state.
```

### 6.8 Scripted Verification Rule

```text
No implementation phase is complete until Codex has created or updated the scripts/tests/proof entries that verify the files it generated.
```

### 6.9 No Unverified Implementation File Rule

Every implementation file must have at least one verification obligation:

```text
1. a direct unit or integration test,
2. a static script check,
3. a runtime dfx verification step,
4. an invariant/proof test,
5. or an explicit blocker in docs/IMPLEMENTATION_FILE_MAP.md.
```

Codex must not create unverified implementation files.

---

## 7. Forbidden Public APIs

The final public API must not expose:

```text
setBalance
createLedgerEntry
rewriteLedgerEntry
deleteLedgerEntry
setTransferState
forceCommitTransfer
bypassIdempotency
mutateReadModel
setRequestOutcome
adminAdjustBalance
```

Allowed public API categories:

```text
submitTransfer
getTransfer
getBalance
getLedgerEntriesForTransfer
getRequestOutcome
health/status query, if non-mutating
```

---

## 8. Forbidden Internal Patterns

Codex must not introduce:

```text
balance mutation outside BalanceControl / TransferExecutor
ledger append outside governed journal path
request outcome writes after an await
duplicate request re-execution
public API calling BalanceStore directly
public API calling LedgerJournal directly
public API calling state mutation functions directly
arbitrary transfer-state setter
tests that only assert implementation details instead of governed behavior
invented operation types beyond Transfer
invented roles or authority classes not present in GOV/SRC/BLD
non-stable correctness-critical state
silent fallback behavior for failed validation
partial commit behavior
```

---

## 9. Verification Strategy

The assurance model is layered:

```text
authority validation
→ implementation file map
→ static scripts
→ unit tests
→ invariant/proof tests
→ integration tests
→ upgrade tests
→ Candid/API surface scan
→ runtime dfx verification
→ authority trace/proof reports
→ ChatGPT/human review of Codex diff
```

### 9.1 What must exist before implementation code

Create the verification harness before generating kernel modules.

Pre-code verification layer:

```text
scripts/
  verify.ps1
  check-authority-trace.ps1
  check-forbidden-api.ps1
  check-forbidden-internal-patterns.ps1
  check-no-await-consistency-boundary.ps1
  check-candid-api-surface.ps1
  check-file-ownership-map.ps1
  check-module-test-coverage.ps1

docs/
  IMPLEMENTATION_FILE_MAP.md
```

Optional Python helpers may exist under:

```text
tools/
  verification/
    check_authority_trace.py
    check_forbidden_api.py
    check_forbidden_patterns.py
    check_no_await_consistency_boundary.py
    check_candid_api_surface.py
    check_module_test_coverage.py
    check_file_ownership_map.py
```

### 9.2 What should grow phase by phase

Behavior tests should grow with implementation code.

Do not write every final behavior test before the implementation shape exists.

Instead, create test harnesses early and add concrete tests as the matching modules are created.

Phase-generated proof layer:

```text
tests/
  domain/
  authority/
  balances/
  ledger/
  idempotency/
  transfer/
  read_model/
  api/
  upgrade/
```

### 9.3 Master verification script

`scripts/verify.ps1` should run the full local verification stack:

```powershell
python -B tools\source_validator\validate_src.py --sources sources --reports reports
python -B tools\source_validator\validate_bld.py --sources sources --reports reports
python -B tools\source_validator\validate_all.py --sources sources --reports reports
python -B -m unittest discover -s tools\source_validator\tests

.\scripts\check-authority-trace.ps1
.\scripts\check-forbidden-api.ps1
.\scripts\check-forbidden-internal-patterns.ps1
.\scripts\check-no-await-consistency-boundary.ps1
.\scripts\check-candid-api-surface.ps1
.\scripts\check-file-ownership-map.ps1
.\scripts\check-module-test-coverage.ps1

dfx build

git diff --check
```

If a Motoko or integration test runner is added, include it in `scripts/verify.ps1`.

### 9.4 File ownership map

Every implementation file should be mapped to:

```text
1. owning phase
2. owning BLD file
3. governing SRC file
4. allowed dependencies
5. forbidden dependencies
6. required tests
7. required scripts or proof obligations
```

`docs/IMPLEMENTATION_FILE_MAP.md` should use this structure:

| File | Phase | Governed By | May Import | Must Not Import | Required Verification |
|---|---|---|---|---|---|
| `transfer/TransferExecutor.mo` | Transfer Executor | `SRC-03`, `SRC-04`, `SRC-05`, `BLD-03`, `BLD-04`, `BLD-05` | authority, validation, balance control, ledger, idempotency | public API direct mutation helpers | happy path, rejection path, replay, no partial commit, no-await scan |
| `balances/BalanceControl.mo` | Balance Control | `SRC-02`, `SRC-03`, `SRC-06`, `BLD-03`, `BLD-06` | domain, state | api, read_model | insufficient funds, no negative balance, asset mismatch |
| `ledger/LedgerJournal.mo` | Ledger Journal | `SRC-05`, `BLD-05` | domain, state | api, balance direct mutation | append-only, transfer traceability |
| `api/PublicApi.mo` | Public API | `SRC-09`, `BLD-09` | executor, read_model | BalanceStore direct, LedgerJournal direct, TransferLifecycle direct setters | forbidden API scan, Candid allowlist, route-through-executor test |

The file ownership map is a control artifact.

Codex must update it whenever it creates or modifies implementation files.

---

# Stage 0 — Authority Freeze and Codex Operating Mode

## Why

This prevents Codex from inventing architecture or implementing convenience logic that violates the project model.

## What

Organize and freeze the authority set:

```text
sources/
  gov/
    GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl

  src/
    SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl
    SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl
    SRC-01__CANISTER_AUTHORITY_MODEL__SOURCE__SYSTEM.jsonl
    SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl
    SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl
    SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl
    SRC-05__LEDGER_JOURNAL_INVARIANTS__SOURCE__SYSTEM.jsonl
    SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl
    SRC-07__READ_MODEL_DERIVATION__SOURCE__SYSTEM.jsonl
    SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl
    SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl
    SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl

  bld/
    BLD-INDEX__BUILD_TRACEABILITY__LOOKUP_ROUTING.jsonl
    BLD-00__IMPLEMENTATION_IDENTITY__BUILD__GLOBAL.jsonl
    BLD-01__CANISTER_AUTHORITY_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-02__DOMAIN_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-03__TRANSFER_PIPELINE_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-04__IDEMPOTENCY_REPLAY_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-05__LEDGER_JOURNAL_COMMIT_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-06__FAILURE_HANDLING_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-07__READ_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-08__UPGRADE_SAFETY_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-09__API_SURFACE_IMPLEMENTATION__BUILD__SYSTEM.jsonl
    BLD-10__TEST_PROOF_IMPLEMENTATION__BUILD__SYSTEM.jsonl
```

## Commands

```powershell
python -B tools\source_validator\validate_src.py --sources sources --reports reports
python -B tools\source_validator\validate_bld.py --sources sources --reports reports
python -B tools\source_validator\validate_all.py --sources sources --reports reports
python -B -m unittest discover -s tools\source_validator\tests
git diff --check
```

## Completion Gate

Proceed only when:

```text
GOV/SRC/BLD files exist.
BLD-INDEX routes all BLD files correctly.
Validators show no blocking authority errors.
Codex custom instructions are changed to implementation mode.
```

---

# Stage 1 — Pre-Code Verification Harness

## Why

Codex should not start generating kernel code without rails.

This stage creates the scripts and control artifacts that later phases must pass.

## What

Create:

```text
scripts/
  verify.ps1
  check-authority-trace.ps1
  check-forbidden-api.ps1
  check-forbidden-internal-patterns.ps1
  check-no-await-consistency-boundary.ps1
  check-candid-api-surface.ps1
  check-file-ownership-map.ps1
  check-module-test-coverage.ps1

docs/
  IMPLEMENTATION_FILE_MAP.md
  SCRIPTED_VERIFICATION.md
```

Optional:

```text
tools/
  verification/
```

## Rules

```text
Create the verification harness before implementation modules.
Scripts may be initially conservative and allow NOT_APPLICABLE where code does not exist yet.
Scripts must fail closed for forbidden public APIs and forbidden mutation patterns once matching files exist.
Scripts must produce clear PASS | FAIL | NOT_APPLICABLE output.
```

## Completion Gate

```text
scripts/verify.ps1 exists.
Forbidden API script exists.
Forbidden internal pattern script exists.
No-await consistency boundary script exists.
Candid/API surface script exists.
File ownership map exists.
Verification scripts can run before implementation and report PASS or NOT_APPLICABLE without crashing.
```

---

# Stage 2 — ICP Skeleton and Build Harness

## Why

The repo must compile early.

Do not wait until many files exist before checking whether the ICP/Motoko project structure works.

## What

Create:

```text
dfx.json
canisters/
  ledger_kernel/
    src/
      Main.mo
      domain/
      authority/
      state/
      transfer/
      idempotency/
      balances/
      ledger/
      read_model/
      api/
      upgrade/
    tests/
README.md
```

Optional if the test runner requires it:

```text
package.json
mops.toml
```

## Rules

```text
Do not implement transfer execution.
Do not expose mutation APIs beyond what is explicitly allowed.
Do not generate UI.
Do not create unsupported operation folders.
Update docs/IMPLEMENTATION_FILE_MAP.md for created implementation files.
```

## Completion Gate

```text
dfx build succeeds, or failure is documented as expected placeholder state.
Folder structure mirrors governed boundaries.
No forbidden public API exists.
No unsupported operation exists.
Verification scripts run.
Codex reports exact files created.
```

---

# Stage 3 — Domain, Failure, and Stable State Model

## Why

The domain model and stable state model form the implementation vocabulary.

Loose strings and ad hoc records cause later drift.

## What

Create:

```text
domain/
  Types.mo
  Errors.mo
  Constants.mo

state/
  StateTypes.mo
  StableState.mo

upgrade/
  UpgradeHooks.mo
```

Define governed equivalents of:

```text
AccountId
AssetId
BalanceKey
TransferId
RequestId
Amount
Transfer
TransferState
LedgerEntry
RequestOutcome
FailureCode
```

Stable state should include storage for:

```text
accounts
assets
balances
transfers
ledger entries
request outcomes / idempotency records
journal counters or deterministic ordering data
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Add compile/type checks where supported.
Add or update stable-state verification script if needed.
Add tests or documented proof obligations for failure codes and transfer states.
```

## Completion Gate

```text
All core entities exist.
Unsupported operation types do not exist.
Transfer states are not arbitrary strings.
Failure codes are governed, not invented.
Stable containers exist for correctness-critical state.
Upgrade hooks compile.
No correctness-critical state exists only in transient memory unless rebuildable.
Verification scripts pass.
```

---

# Stage 4 — Canister Authority Boundary

## Why

The canister must not trust caller identity supplied in the request body.

Authority must come from ICP caller context or governed gateway rules.

## What

Create:

```text
authority/
  CanisterAuthority.mo
```

Responsibilities:

```text
check caller authorization
reject unauthorized mutation calls
separate caller identity from request payload
define allowed bootstrap/admin behavior only if governed
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Add authorized/unauthorized caller tests or a documented blocker.
Scan for invented roles or authority models.
```

## Completion Gate

```text
Unauthorized mutation callers are rejected.
Request body cannot impersonate trusted caller identity.
Authority behavior does not invent roles not found in GOV/SRC/BLD.
Tests or documented proof exist for authorized and unauthorized paths.
Verification scripts pass.
```

---

# Stage 5 — Transfer Validation and Lifecycle

## Why

A transfer must not move from request to commit without passing governed validation and lifecycle rules.

## What

Create:

```text
transfer/
  TransferTypes.mo
  TransferValidation.mo
  TransferLifecycle.mo
```

Responsibilities:

```text
validate request shape
validate source account
validate destination account
validate asset
validate amount
validate lifecycle transitions
reject malformed or unsupported requests
produce deterministic failure result
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Add validation tests for malformed request, bad amount, bad asset, unsupported operation, and invalid lifecycle transition.
Add scan for arbitrary state setters.
```

## Completion Gate

```text
Invalid transfer cannot reach commit logic.
Terminal states cannot reopen.
Unsupported operations are rejected or unrepresentable.
Failure result is deterministic.
No balance mutation occurs in this stage.
Verification scripts pass.
```

---

# Stage 6 — Balance Control

## Why

Balances are correctness-sensitive.

The system must prevent negative balances, asset mismatch, and direct mutation outside the governed transfer path.

## What

Create:

```text
balances/
  BalanceStore.mo
  BalanceControl.mo
```

Responsibilities:

```text
lookup balance by accountId + assetId
prepare debit/credit mutation plan
reject insufficient funds
reject asset mismatch
prevent direct external mutation
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Add insufficient funds test.
Add no-negative-balance test.
Add asset-mismatch test.
Add forbidden direct balance mutation scan.
```

## Completion Gate

```text
No direct public setBalance API exists.
Negative balances are impossible through the governed path.
Source and destination asset handling is explicit.
Balance mutation can be paired with ledger proof.
BalanceStore is not called directly by public API.
Verification scripts pass.
```

---

# Stage 7 — Ledger Journal

## Why

The ledger journal is the proof layer.

A committed transfer without ledger entries is invalid.

## What

Create:

```text
ledger/
  LedgerEntry.mo
  LedgerJournal.mo
```

Responsibilities:

```text
append ledger entries
link ledger entries to transferId
record debit and credit sides
preserve asset and amount symmetry
preserve append-only journal behavior
support query by transferId
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Add append-only test.
Add transfer traceability test.
Add asset/amount symmetry test.
Add scan for ledger rewrite/delete behavior.
```

## Completion Gate

```text
Ledger entries are append-only.
Ledger entries cannot be rewritten or deleted.
Committed transfer can be traced to journal proof.
No public createLedgerEntry API exists.
LedgerJournal is not called directly by public API.
Verification scripts pass.
```

---

# Stage 8 — Idempotency and Replay

## Why

Duplicate requests are a high-risk path in ledger systems.

The same request identity must return the same persisted outcome and must not execute twice.

## What

Create:

```text
idempotency/
  IdempotencyStore.mo
  Replay.mo
```

Responsibilities:

```text
check if request identity already exists
return stored outcome for duplicate request
prevent duplicate execution
persist outcome after first execution
handle rejected outcomes deterministically
```

## Required Pattern

```text
receive request
→ check idempotency store
→ if existing outcome exists, return stored outcome
→ otherwise continue transfer execution
→ persist outcome
→ return outcome
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Add duplicate successful request replay test.
Add duplicate rejected request replay test.
Add scan for duplicate re-execution behavior where detectable.
```

## Completion Gate

```text
Duplicate valid request does not mutate balances again.
Duplicate rejected request returns same rejection.
Stored result is authoritative for replay.
Replay does not bypass ledger proof.
Request outcome is persisted in stable state.
Verification scripts pass.
```

---

# Stage 9 — Transfer Executor / Consistency Boundary

## Why

This is the core kernel.

The executor is the only path that should perform balance-affecting mutation.

## What

Create:

```text
transfer/
  TransferExecutor.mo
```

Expected internal order:

```text
1. Authority check
2. Idempotency check
3. Transfer validation
4. Lifecycle transition
5. Balance mutation plan
6. Ledger journal plan
7. Commit all governed state changes
8. Persist request outcome
9. Return deterministic result
```

## Hard Rule

```text
No await inside the balance-affecting consistency boundary.
No inter-canister calls inside the mutation path.
No partial commit through normal execution path.
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Add valid transfer happy-path test.
Add rejected transfer no-mutation test.
Add no partial commit test or documented blocker.
Run no-await consistency boundary script.
Run forbidden internal pattern script.
```

## Completion Gate

```text
Valid transfer debits source.
Valid transfer credits destination.
Valid transfer appends ledger proof.
Rejected transfer does not mutate balances.
Duplicate transfer does not re-execute.
No partial commit is possible through normal execution path.
No await exists inside the consistency boundary.
Verification scripts pass.
```

---

# Stage 10 — Read Model

## Why

Read APIs should report derived state.

They must not become authority and must not mutate state.

## What

Create:

```text
read_model/
  ReadModel.mo
```

Queries:

```text
getBalance(accountId, assetId)
getTransfer(transferId)
getLedgerEntriesForTransfer(transferId)
getRequestOutcome(requestId)
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Add read model derivation test.
Add scan that read model does not mutate state.
```

## Completion Gate

```text
Read model does not mutate state.
Read model does not become source authority.
Read model can explain committed transfers through ledger entries.
Read model derives from governed state, not separate truth.
Verification scripts pass.
```

---

# Stage 11 — Public API and Candid Surface Lock

## Why

The public API is an attack surface.

A correct internal kernel can still be broken by unsafe public methods.

## What

Create:

```text
api/
  PublicApi.mo

canisters/
  ledger_kernel/
    ledger_kernel.did

Main.mo
```

Allowed public API categories:

```text
submitTransfer
getTransfer
getBalance
getLedgerEntriesForTransfer
getRequestOutcome
health/status query, if non-mutating
```

Forbidden public API categories:

```text
setBalance
createLedgerEntry
rewriteLedgerEntry
deleteLedgerEntry
setTransferState
forceCommitTransfer
bypassIdempotency
mutateReadModel
setRequestOutcome
adminAdjustBalance
```

## Required Verification

```text
Update IMPLEMENTATION_FILE_MAP.md.
Run forbidden API scan.
Run Candid/API surface allowlist scan.
Add test that public mutation routes through submitTransfer only.
Add scan that PublicApi does not import BalanceStore or LedgerJournal directly.
```

## Completion Gate

```text
Candid interface is reviewed.
submitTransfer is the only balance-affecting update call.
Read methods are query-only where appropriate.
Forbidden mutation methods are absent.
All transfer mutation enters through submitTransfer.
Public API routes to TransferExecutor or ReadModel only.
No public API bypasses idempotency.
No public API bypasses ledger proof.
Verification scripts pass.
```

---

# Stage 12 — Full Proof Tests and Forbidden Pattern Scan

## Why

Tests are not just quality checks.

For this project, tests are proof artifacts.

## Required Tests

Create or finalize tests for:

```text
valid transfer path
insufficient funds rejection
asset mismatch rejection
duplicate successful request replay
duplicate rejected request replay
ledger append-only behavior
forbidden API absence
unauthorized caller rejection
read model derivation
upgrade safety
failure determinism
no-await consistency boundary scan
no partial commit behavior
implementation file map completeness
```

Recommended test layout:

```text
tests/
  domain/
  authority/
  balances/
  ledger/
  idempotency/
  transfer/
  read_model/
  api/
  upgrade/
  verification/
```

## Required Verification

```text
Run scripts/verify.ps1.
Run all test suites.
Run dfx build.
Run git diff --check.
Confirm all implementation files have a verification obligation.
```

## Completion Gate

```text
All tests pass.
Forbidden APIs are absent.
Forbidden internal patterns are absent.
Duplicate replay does not double-mutate.
Committed transfer has ledger proof.
Rejected transfer does not mutate balances.
Upgrade safety has explicit test or documented blocker.
Implementation file map is complete.
Verification scripts pass.
```

---

# Stage 13 — Local Deployment and Manual Runtime Verification

## Why

A project can pass unit tests and still fail in the actual canister runtime.

Local deployment verifies runtime behavior.

## Commands

Codex should verify exact command availability in the repo before running.

Expected command class:

```powershell
dfx start --clean --background
dfx build
dfx deploy
dfx canister call ledger_kernel submitTransfer "(...)"
dfx canister call ledger_kernel getBalance "(...)"
dfx canister call ledger_kernel getLedgerEntriesForTransfer "(...)"
dfx canister call ledger_kernel getRequestOutcome "(...)"
```

## Manual Verification

Verify:

```text
initial balances
valid transfer submission
source balance decreases
destination balance increases
ledger proof exists
duplicate request returns same result
duplicate request does not mutate balances again
rejection path is deterministic
read model returns derived state
```

## Completion Gate

```text
dfx build passes.
local deploy passes.
manual valid transfer call works.
manual duplicate replay call returns same result.
manual ledger proof query works.
manual rejection path works.
Runtime verification result is recorded in docs/PROOF_REPORT.md.
```

---

# Stage 14 — Documentation and Proof Report

## Why

The project needs an audit trail.

Documentation must reflect the actual implementation, not aspirations.

## What

Create or update:

```text
README.md
docs/API.md
docs/PROOF_REPORT.md
docs/IMPLEMENTATION_FILE_MAP.md
docs/SCRIPTED_VERIFICATION.md
docs/CODEX_PHASE_REPORTS.md
```

## Proof Report Sections

```text
authority files used
implementation files generated
scripted verification layer
invariants enforced
forbidden APIs excluded
forbidden internal patterns excluded
tests run
dfx commands run
manual verification results
known limitations
remaining gaps
```

## Completion Gate

```text
README reflects actual commands.
Proof report reflects actual tests and scripts.
Known gaps are documented honestly.
Implementation map links modules to GOV/SRC/BLD authority.
Codex phase reports are preserved.
Runtime dfx verification is documented.
```

---

# Deferred Stage — Optional Demo Client

## Rule

The demo client is deferred until the governed kernel is proven.

It is not part of the authority model.

It must not define correctness.

## Allowed UI Actions

```text
submit transfer
view transfer result
view balances
view ledger proof
view replay result
```

## Forbidden UI Actions

```text
edit balance directly
manually change transfer state
create ledger entry
force commit
bypass request identity
call forbidden APIs
```

## Completion Gate

```text
Demo client uses only allowed public APIs.
Demo client does not require new forbidden endpoints.
Demo client displays ledger proof for committed transfers.
Demo client can demonstrate duplicate replay behavior.
```

---

# Recommended File Count

| Area | Expected Files |
|---|---:|
| Authority layer | already exists |
| Pre-code verification scripts/docs | 8–12 |
| ICP skeleton/config | 3–6 |
| Domain/failure model | 3–5 |
| Stable state/upgrade | 3–5 |
| Authority boundary | 1–2 |
| Transfer validation/lifecycle | 3–5 |
| Balance control | 2–3 |
| Ledger journal | 2–4 |
| Idempotency/replay | 2–3 |
| Transfer executor | 1–2 |
| Read model | 1–2 |
| Public API/Candid | 2–3 |
| Tests/proofs | 12–18 |
| Docs/reports | 5–8 |
| Optional demo client | deferred |

Kernel-only target:

```text
~65–90 total files including GOV/SRC/BLD authority files.
```

Optional demo client should not be counted in the kernel proof target.

---

# Practical Execution Order

```text
1. Validate GOV/SRC/BLD authority files.
2. Update Codex custom instructions for implementation mode.
3. Create pre-code verification harness.
4. Create implementation file map.
5. Create ICP canister skeleton.
6. Create build/test harness.
7. Create domain types and failure codes.
8. Create stable state model.
9. Create upgrade hooks and upgrade-safety tests.
10. Create canister authority boundary.
11. Create transfer validation and lifecycle rules.
12. Create balance control.
13. Create ledger journal.
14. Create idempotency/replay store.
15. Create transfer executor with no-await consistency boundary.
16. Create read model.
17. Create public API and Candid interface.
18. Run forbidden API scan.
19. Run forbidden internal pattern scan.
20. Run no-await consistency boundary scan.
21. Run Candid/API surface scan.
22. Run invariant/proof tests.
23. Run local dfx deployment.
24. Run manual duplicate replay and ledger proof calls.
25. Generate implementation map and proof report.
26. Defer optional demo client.
```

---

# Main Risk Controls

## Risk 1 — Codex Invents Architecture

Control:

```text
Codex must inspect GOV/SRC/BLD before implementation.
Each phase must report authority inspected.
ChatGPT reviews each Codex report before the next phase.
```

## Risk 2 — API Bypasses Kernel

Control:

```text
Only submitTransfer may mutate balances.
Public API must route mutation through TransferExecutor.
Forbidden API scan must pass.
Candid surface must be reviewed.
```

## Risk 3 — Replay Double-Spends

Control:

```text
Idempotency check must happen before transfer execution.
Duplicate request must return stored outcome.
Replay determinism tests must pass.
```

## Risk 4 — Balance Mutation Lacks Proof

Control:

```text
Committed transfer must append ledger entries.
No balance-affecting commit without journal proof.
Ledger proof tests must pass.
```

## Risk 5 — Partial Commit From Await

Control:

```text
No await inside balance-affecting consistency boundary.
No inter-canister calls inside mutation path.
No-await scan must pass.
```

## Risk 6 — Upgrade Loses Ledger Truth

Control:

```text
Correctness-critical state must be stable or rebuildable.
Upgrade tests or explicit blockers must exist.
Migration risk must be documented.
```

## Risk 7 — Tests Pass but Authority Is Violated

Control:

```text
Tests are necessary but not sufficient.
Codex must also report authority compliance and semantic completeness.
Implementation map must link modules to GOV/SRC/BLD authority.
```

## Risk 8 — Scripts Become Superficial

Control:

```text
Scripts must be tied to forbidden behavior, API surface, file ownership, and phase gates.
Scripts must fail clearly and explain the offending file/pattern.
Scripts must not replace invariant tests or runtime dfx verification.
```

## Risk 9 — Unverified Files Accumulate

Control:

```text
Every implementation file must have a verification obligation.
check-module-test-coverage.ps1 and check-file-ownership-map.ps1 must pass.
No phase is complete if new implementation files are unmapped.
```

---

# Final Recommendation

Build the project in four major stages:

```text
Stage A — Authority and Verification Harness
Goal: freeze authority and create the script/test rails before implementation.
Success condition:
- authority validators pass
- scripts/verify.ps1 exists
- forbidden scans exist
- implementation file map exists

Stage B — Governed Kernel
Goal: deterministic transfer-only ICP ledger canister.
Success condition:
- dfx build passes
- submitTransfer works
- duplicate request replays same outcome
- balance mutation creates ledger proof
- forbidden APIs are absent
- forbidden internal patterns are absent
- no-await consistency boundary holds
- proof tests pass

Stage C — Documentation and Proof Report
Goal: make the implementation auditable.
Success condition:
- implementation file map exists and is current
- proof report reflects actual tests, scripts, and commands
- known gaps are documented

Stage D — Optional Demo Client
Goal: visual demonstration only.
Success condition:
- client consumes only safe public APIs
- no new correctness authority is introduced
```

The correct project identity is:

```text
A source-governed ICP deterministic ledger kernel,
not a generic finance app,
not a UI-first product,
not an LLM-invented architecture,
and not a convenience API surface.
```
