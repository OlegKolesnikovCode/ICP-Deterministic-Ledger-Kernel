# GENERATION_PACKET_001

## 1. Target name

ICP Skeleton and Build Harness.

## 2. Phase/stage number

Stage 2.

## 3. Purpose

Create the first minimal ICP build skeleton for the governed kernel without implementing ledger, transfer, balance, authority, idempotency, persistence, read model, public API, or proof-test behavior.

This packet is for a future implementation task only. It does not authorize implementation code generation in the current packet-creation task.

## 4. Authority basis

- `AGENTS.md`: stage order places `ICP Skeleton and Build Harness` after `Pre-Code Verification Harness` and before domain/stable-state implementation.
- `GOV-00`: generated code remains downstream of GOV, SRC, and BLD authority; missing authority, broken trace, conflict, or invalid schema blocks dependent generation.
- `SRC-INDEX`: `SRC-00` owns project identity and scope; `SRC-09` owns API surface and forbidden API semantics; `SRC-10` owns test proof requirements.
- `BLD-INDEX`: `BLD-00` routes to `SRC-00`; `BLD-09` routes to `SRC-09`, `SRC-06`, and `SRC-10`; `BLD-10` routes to `SRC-10`.
- `docs/IMPLEMENTATION_FILE_MAP.md`: the first mapped implementation files for `ICP Skeleton and Build Harness` are `dfx.json` and `canisters/ledger_kernel/src/Main.mo`.
- `docs/SCRIPTED_VERIFICATION.md`: the existing verification harness already defines `scripts/verify.ps1`, forbidden-surface scans, Candid/API scan behavior, file-map checks, module verification checks, and pre-code warning handling.

## 5. Owning BLD file

Primary owning BLD file:

- `sources/bld/BLD-00__IMPLEMENTATION_IDENTITY__BUILD__GLOBAL.jsonl`

Cross-cutting BLD files for this target:

- `sources/bld/BLD-09__API_SURFACE_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-10__TEST_PROOF_IMPLEMENTATION__BUILD__SYSTEM.jsonl`

Routing authority:

- `sources/bld/BLD-INDEX__BUILD_TRACEABILITY__LOOKUP_ROUTING.jsonl`

Important constraint:

- `BLD-00` provides project identity and scope framing only. It must not be used to implement domain behavior, runtime mutation behavior, detailed module internals, public API behavior, or future-stage code.

## 6. Governing SRC files/records

Primary governing SRC file:

- `sources/src/SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl`

Required SRC-00 trace records:

- `PROJECT-FILE-001`
- `PROJECT-RESPONSIBILITY-001`
- `PROJECT-RESPONSIBILITY-002`
- `PROJECT-IDENTITY-001`
- `PROJECT-IDENTITY-002`
- `PROJECT-IDENTITY-003`
- `PROJECT-IDENTITY-007`
- `PROJECT-IDENTITY-008`
- `PROJECT-THESIS-001`
- `PROJECT-THESIS-002`
- `PROJECT-SCOPE-001`
- `PROJECT-SCOPE-002`
- `PROJECT-SCOPE-003`
- `PROJECT-SCOPE-006`
- `PROJECT-SCOPE-007`
- `ADR-001`
- `ADR-007`
- `ADR-008`
- `ADR-009`
- `ADR-010`
- `ADR-012`
- `PROJECT-SOURCE-LIMIT-001` through `PROJECT-SOURCE-LIMIT-011`
- `PROJECT-AUTHORITY-001` through `PROJECT-AUTHORITY-005`

Cross-cutting governing SRC files:

- `sources/src/SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl` for current warning triage only.

Required SRC-09 trace records:

- `API-FILE-001`
- `API-RESPONSIBILITY-001`
- `API-011`
- `API-012`
- `API-017`
- `API-018`
- `API-097`
- `FORBID-001` through `FORBID-014`
- `FORBID-019` through `FORBID-097`
- `FORBID-AUTHORITY-001`
- `FORBID-AUTHORITY-002`
- `FORBID-AUTHORITY-003`

Required SRC-10 trace records:

- `TEST-FILE-001`
- `TEST-PROOF-001` through `TEST-PROOF-019`
- `TEST-PROOF-015`
- `DONE-016`
- `DONE-RULE-005`
- `DONE-RULE-006`
- `DONE-RULE-007`
- `RISK-016`
- `RISK-017`
- `RISK-018`

Required SRC-06 warning-triage records:

- `FAIL-FILE-001`
- `FAIL-RESPONSIBILITY-001`
- `FAIL-MODEL-001` through `FAIL-MODEL-010`
- `FAIL-001` through `FAIL-020`
- `FAIL-RULE-101` through `FAIL-RULE-118`
- `FAIL-RULE-201` through `FAIL-RULE-205`

## 7. Allowed future file manifest

The next implementation task may create or modify only these files:

- `dfx.json`
- `canisters/ledger_kernel/src/Main.mo`
- `docs/IMPLEMENTATION_FILE_MAP.md`

Directory creation is allowed only as required to host the allowed files:

- `canisters/`
- `canisters/ledger_kernel/`
- `canisters/ledger_kernel/src/`

Allowed implementation content limits:

- `dfx.json` may define only the minimal local canister build harness for the ledger kernel canister.
- `Main.mo` may contain only a minimal canister actor required for compilation.
- `Main.mo` must not expose balance-affecting update calls.
- `Main.mo` must not expose `submitTransfer` during this skeleton target unless the future prompt explicitly authorizes public API work under the later Public API stage.
- If a non-mutating health/status query is added, it must remain read-only and must not depend on ledger, balance, transfer, idempotency, or read-model state.
- `docs/IMPLEMENTATION_FILE_MAP.md` may be updated only to keep the rows for the files created or modified by this target accurate.

## 8. Forbidden future file manifest

The next implementation task must not create or modify these implementation files:

- `canisters/ledger_kernel/src/domain/Types.mo`
- `canisters/ledger_kernel/src/domain/Errors.mo`
- `canisters/ledger_kernel/src/domain/Constants.mo`
- `canisters/ledger_kernel/src/state/StateTypes.mo`
- `canisters/ledger_kernel/src/state/StableState.mo`
- `canisters/ledger_kernel/src/upgrade/UpgradeHooks.mo`
- `canisters/ledger_kernel/src/authority/CanisterAuthority.mo`
- `canisters/ledger_kernel/src/transfer/TransferTypes.mo`
- `canisters/ledger_kernel/src/transfer/TransferValidation.mo`
- `canisters/ledger_kernel/src/transfer/TransferLifecycle.mo`
- `canisters/ledger_kernel/src/balances/BalanceStore.mo`
- `canisters/ledger_kernel/src/balances/BalanceControl.mo`
- `canisters/ledger_kernel/src/ledger/LedgerEntry.mo`
- `canisters/ledger_kernel/src/ledger/LedgerJournal.mo`
- `canisters/ledger_kernel/src/idempotency/IdempotencyStore.mo`
- `canisters/ledger_kernel/src/idempotency/Replay.mo`
- `canisters/ledger_kernel/src/transfer/TransferExecutor.mo`
- `canisters/ledger_kernel/src/read_model/ReadModel.mo`
- `canisters/ledger_kernel/src/api/PublicApi.mo`
- `canisters/ledger_kernel/ledger_kernel.did`

The next implementation task must not modify these authority/control files:

- `AGENTS.md`
- `sources/gov/GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl`
- `sources/src/SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl`
- `sources/src/SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl`
- `sources/src/SRC-01__CANISTER_AUTHORITY_MODEL__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-05__LEDGER_JOURNAL_INVARIANTS__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-07__READ_MODEL_DERIVATION__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl`
- `sources/src/SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl`
- `sources/bld/BLD-INDEX__BUILD_TRACEABILITY__LOOKUP_ROUTING.jsonl`
- `sources/bld/BLD-00__IMPLEMENTATION_IDENTITY__BUILD__GLOBAL.jsonl`
- `sources/bld/BLD-01__CANISTER_AUTHORITY_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-02__DOMAIN_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-03__TRANSFER_PIPELINE_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-04__IDEMPOTENCY_REPLAY_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-05__LEDGER_JOURNAL_COMMIT_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-06__FAILURE_HANDLING_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-07__READ_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-08__UPGRADE_SAFETY_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-09__API_SURFACE_IMPLEMENTATION__BUILD__SYSTEM.jsonl`
- `sources/bld/BLD-10__TEST_PROOF_IMPLEMENTATION__BUILD__SYSTEM.jsonl`

## 9. Out-of-scope modules

The following modules and behaviors are out of scope for the next implementation target:

- Domain types, constants, errors, failure classes, stable state, or upgrade hooks.
- Canister authority boundary.
- Transfer request validation, lifecycle, executor, or consistency boundary.
- Balance store, balance control, ledger entry, ledger journal, idempotency, replay, read model, or public API module.
- Candid surface lock or `.did` file generation.
- Unit, integration, or proof-test suite bodies.
- Runtime seed balances, demo state, bootstrap mutation APIs, or admin APIs.
- `Deposit`, `Withdraw`, `Withdrawal`, `Mint`, `Burn`, `Fee`, `Reversal`, `BatchTransfer`, or `AdminAdjustment`.

## 10. Required source traces

Future implementation report must explicitly map the created files to these source traces:

- `dfx.json`: `PROJECT-IDENTITY-001`, `PROJECT-IDENTITY-002`, `PROJECT-SCOPE-001`, `PROJECT-SCOPE-003`, `PROJECT-SCOPE-006`, `PROJECT-AUTHORITY-005`, `TEST-PROOF-001`.
- `canisters/ledger_kernel/src/Main.mo`: `PROJECT-IDENTITY-002`, `PROJECT-SCOPE-003`, `PROJECT-SCOPE-006`, `PROJECT-SOURCE-LIMIT-001` through `PROJECT-SOURCE-LIMIT-011`, `API-RESPONSIBILITY-001`, `FORBID-AUTHORITY-003`, `TEST-PROOF-001`, `TEST-PROOF-015`.
- `docs/IMPLEMENTATION_FILE_MAP.md`: `PROJECT-AUTHORITY-005`, `TEST-PROOF-001`, `TEST-PROOF-016`, `DONE-RULE-005`, `DONE-RULE-006`.

## 11. Required BLD traces

Future implementation report must explicitly map the created files to these BLD traces:

- `dfx.json`: `BLD-INDEX-MANIFEST-001`, `BLD-INDEX-SRC-ROUTE-001`, `BLD-00-ROLE-001`, `BLD-00-IDENTITY-001`, `BLD-00-IDENTITY-002`, `BLD-00-SCOPE-001`, `BLD-00-SCOPE-002`, `BLD-00-SCOPE-006`, `BLD-00-VALIDATION-001`, `BLD-00-VALIDATION-003`.
- `canisters/ledger_kernel/src/Main.mo`: `BLD-00-IDENTITY-001`, `BLD-00-IDENTITY-002`, `BLD-00-SCOPE-002`, `BLD-09-SCOPE-002`, `BLD-09-SCOPE-003`, `BLD-09-FORBID-001` through `BLD-09-FORBID-011`, `BLD-10-TARGET-011`, `BLD-10-FORBID-003`, `BLD-10-FORBID-004`.
- `docs/IMPLEMENTATION_FILE_MAP.md`: `BLD-10-ROLE-004`, `BLD-10-CONTRACT-006`, `BLD-10-FAILURE-001`, `BLD-10-FORBID-001`, `BLD-10-REVIEW-001`.

## 12. Required verification obligations

The next implementation task must verify:

- Source validators still produce no blocking or error findings.
- BLD validators still pass.
- Source validator unit tests pass.
- `scripts/verify.ps1` runs after the skeleton exists.
- `dfx build` runs through `scripts/verify.ps1` because `dfx.json` will exist.
- `scripts/check-forbidden-api.ps1` does not find forbidden API names.
- `scripts/check-forbidden-internal-patterns.ps1` does not find forbidden internal patterns.
- `scripts/check-no-await-consistency-boundary.ps1` remains `NOT_APPLICABLE` unless a transfer consistency-boundary file is incorrectly created, which is forbidden for this target.
- `scripts/check-candid-api-surface.ps1` passes or remains `NOT_APPLICABLE` depending on whether `Main.mo` exposes any public method.
- `scripts/check-file-ownership-map.ps1` passes with the new skeleton files mapped.
- `scripts/check-module-test-coverage.ps1` passes with verification obligations mapped for `dfx.json` and `Main.mo`.
- `git diff --check` passes.

## 13. Required implementation file map updates

The next implementation task must update `docs/IMPLEMENTATION_FILE_MAP.md` only if needed to make the current rows exact after creating or modifying:

- `dfx.json`
- `canisters/ledger_kernel/src/Main.mo`

The map rows must retain:

- owning phase: `ICP Skeleton and Build Harness`
- governing authority: `GOV-00`, `SRC-00`, and applicable `SRC-09`, `BLD-00`, `BLD-09`, `BLD-10`
- forbidden dependencies on stores, journals, direct state mutation helpers, demo UI canisters, and unsupported operation canisters
- required verification through `scripts/verify.ps1`, `dfx build`, forbidden API scan, Candid/API scan where applicable, file ownership map check, and module coverage check

## 14. Pre-generation verification commands

Run from repository root before creating future skeleton files:

```powershell
python -B tools\source_validator\validate_src.py --sources sources --reports reports
python -B tools\source_validator\validate_bld.py --sources sources --reports reports
python -B tools\source_validator\validate_all.py --sources sources --reports reports
python -B -m unittest discover -s tools\source_validator\tests
powershell -ExecutionPolicy Bypass -File scripts\verify.ps1
git diff --check
```

Expected pre-generation result:

- SRC validation may return `WARNING_ONLY` only for the existing warning classes triaged below.
- BLD validation must pass.
- `scripts/verify.ps1` may return `WARNING_ONLY` because of existing SRC warnings.
- Forbidden API, forbidden internal pattern, no-await, Candid/API, and module coverage checks may return `NOT_APPLICABLE` before skeleton files exist.
- `git diff --check` must pass.

## 15. Post-generation verification commands

Run from repository root after creating future skeleton files:

```powershell
python -B tools\source_validator\validate_src.py --sources sources --reports reports
python -B tools\source_validator\validate_bld.py --sources sources --reports reports
python -B tools\source_validator\validate_all.py --sources sources --reports reports
python -B -m unittest discover -s tools\source_validator\tests
powershell -ExecutionPolicy Bypass -File scripts\verify.ps1
dfx build
git diff --check
```

Expected post-generation result:

- SRC validation may remain `WARNING_ONLY` only for the existing warning classes triaged below.
- BLD validation must pass.
- `scripts/verify.ps1` must run and must not fail.
- `dfx build` must pass when run directly and through `scripts/verify.ps1`.
- Forbidden API and forbidden internal pattern checks must pass against the created skeleton files.
- Candid/API surface check must pass if `Main.mo` exists.
- File ownership map and module test coverage checks must pass.
- `git diff --check` must pass.

## 16. Failure conditions

The future implementation task fails if:

- Any command above exits nonzero, except validator `WARNING_ONLY` explicitly limited to the existing warning triage below.
- `dfx build` is unavailable or fails after `dfx.json` is created.
- `Main.mo` exposes a forbidden API or balance-affecting update method.
- `Main.mo` imports or references balance, ledger, idempotency, transfer executor, read model, state mutation, or future-stage modules.
- `dfx.json` defines extra canisters, demo clients, unsupported operation canisters, or non-kernel runtime surfaces.
- `docs/IMPLEMENTATION_FILE_MAP.md` omits a created or modified implementation file.
- Static scans report forbidden public APIs, forbidden internal patterns, await in a transfer consistency-boundary candidate, or Candid/API drift.

## 17. STOP conditions

The future implementation task must stop and report `BLOCKED` if:

- Any required authority file is missing or inactive.
- `GOV-00`, `SRC-INDEX`, `SRC-*`, `BLD-INDEX`, or `BLD-*` conflicts with the requested skeleton target.
- The task requires changing GOV/SRC/BLD authority files.
- The task requires creating files outside the allowed future file manifest.
- The task requires public `submitTransfer`, Candid generation, `PublicApi.mo`, transfer executor, balance, ledger, idempotency, read model, stable state, or test-proof implementation.
- The task requires a forbidden operation family or forbidden public API.
- Existing SRC warnings become blocking under updated validator behavior or active GOV/SRC/BLD authority.
- Required verification cannot run and no authority-compliant equivalent exists.

## 18. Existing warning triage

Current SRC validator state:

- Verdict: `WARNING_ONLY`
- Warnings: 329
- Warning classes:
  - `API_RULE_NOT_ROUTED_OR_TESTED` in `SRC-09`: 208 warnings
  - `FAILURE_RULE_NOT_REFERENCED` in `SRC-06`: 121 warnings

Triage:

| Warning Category | File | Classification | Blocks Stage 2 skeleton? | Handling |
|---|---|---|---|---|
| `API_RULE_NOT_ROUTED_OR_TESTED` | `SRC-09` | `DEFER_TO_IMPLEMENTATION_PROOF` | No | Do not fix in Stage 2. Future API/Candid/public surface proof must route or test these before Public API completion. |
| `FAILURE_RULE_NOT_REFERENCED` | `SRC-06` | `DEFER_TO_IMPLEMENTATION_PROOF` | No | Do not fix in Stage 2. Future failure handling, rejection, and proof phases must map these records before failure-proof completion. |

These warnings do not block the first implementation target because Stage 2 is limited to a non-behavioral skeleton/build harness and must not implement public API routing or failure handling. They remain blocking risks for later phases if the relevant implementation proof is still missing when those phases are reached.

Do not mass-fix these warnings during Stage 2.

## 19. Final Codex prompt template for the next phase

```text
PHASE: ICP Skeleton and Build Harness

Goal:
Create the first minimal ICP skeleton/build harness for ICP Deterministic Ledger Kernel 2.

Apply AGENTS.md exactly.
Apply docs/GENERATION_PACKET_001.md exactly.
If this prompt conflicts with AGENTS.md or GOV/SRC/BLD authority, stop and report BLOCKED.

Do not modify GOV/SRC/BLD files.
Do not generate ledger, transfer, balance, authority, idempotency, persistence, read model, public API module, Candid lock, runtime seed state, demo UI, or proof-test implementation modules.
Do not create unsupported operation families.

Authority inspection:
1. Read AGENTS.md.
2. Read GOV-00.
3. Read SRC-INDEX.
4. Read BLD-INDEX.
5. Read docs/GENERATION_PACKET_001.md.
6. Read docs/IMPLEMENTATION_FILE_MAP.md.
7. Read docs/SCRIPTED_VERIFICATION.md.
8. Read SRC-00, SRC-06, SRC-09, and SRC-10.
9. Read BLD-00, BLD-09, and BLD-10.
10. Read all verification scripts under scripts/.

Allowed files:
- dfx.json
- canisters/ledger_kernel/src/Main.mo
- docs/IMPLEMENTATION_FILE_MAP.md

Forbidden files:
- All implementation files listed in docs/GENERATION_PACKET_001.md section 8.
- All GOV/SRC/BLD authority files.
- Any UI/demo/client files.

Task:
1. Run the pre-generation verification commands from docs/GENERATION_PACKET_001.md.
2. Create the minimal dfx build harness.
3. Create only the minimal ledger canister entry file required for build.
4. Keep Main.mo non-mutating and free of ledger, transfer, balance, authority, idempotency, persistence, read model, and public API implementation logic.
5. Update docs/IMPLEMENTATION_FILE_MAP.md only if needed for the files created or modified.
6. Run the post-generation verification commands from docs/GENERATION_PACKET_001.md.
7. Patch only failures within this stage scope.
8. End with the full AGENTS.md final phase report format.

Expected status:
The phase may be PASS only if scripts/verify.ps1 and dfx build run successfully and all applicable scans pass. Existing SRC warnings may remain WARNING_ONLY only for the triaged warning classes in docs/GENERATION_PACKET_001.md.
```
