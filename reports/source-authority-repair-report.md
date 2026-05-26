# Source Authority Repair Report

## Files Changed

- `doc/GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl`
- `doc/SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl`
- `doc/SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl`
- `doc/SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl`
- `doc/SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl`
- `tools/validate-governed-sources.mjs`
- `reports/source-authority-repair-report.md`

## Records Changed

- `GOV-SCOPE-004`: declared `SYSTEM` as an aggregate scope token.
- `GOV-AUTH-010`: changed `REPORT` numeric authority level from `7` to `8`.
- `ASSET-012`: removed trace to `BOOT-004`.
- `TRANSFER-039`: removed trace to `FAIL-020`.
- `UPG-015`: removed trace to `FAIL-RULE-501`.
- `SRC-INDEX-GENERATION-ORDER-001` through `SRC-INDEX-GENERATION-ORDER-005`: removed trace to deleted `SRC-INDEX-BLD-PRECONDITION-001`.
- `AMOUNT-020` and `AMOUNT-028`: removed trace to deleted `SRC-INDEX-BLD-PRECONDITION-005`.

## Records Deleted

- `SRC-INDEX-GENERATION-ORDER-006`
- `SRC-INDEX-GENERATION-ORDER-007`
- `SRC-INDEX-GENERATION-ORDER-008`
- `SRC-INDEX-GENERATION-ORDER-009`
- `SRC-INDEX-GENERATION-ORDER-010`
- `SRC-INDEX-GENERATION-ORDER-011`
- `SRC-INDEX-GENERATION-ORDER-012`
- `SRC-INDEX-BLD-PRECONDITION-001`
- `SRC-INDEX-BLD-PRECONDITION-002`
- `SRC-INDEX-BLD-PRECONDITION-003`
- `SRC-INDEX-BLD-PRECONDITION-004`
- `SRC-INDEX-BLD-PRECONDITION-005`

## Defects Fixed

- Removed the `TRANSFER-039 <-> FAIL-020` cycle while preserving `FAIL-020 -> TRANSFER-039`, so SRC-03 owns transfer validation and SRC-06 owns failure classification.
- Removed the maintenance-mode cycle by keeping failure rules routed to `UPG-015` while removing `UPG-015`'s dependency on detailed `FAIL-RULE-501`.
- Removed the `BOOT-004 <-> ASSET-012` cycle while preserving `BOOT-004 -> ASSET-012`, so SRC-01 owns bootstrap/admin authority boundaries and SRC-02 owns Asset runtime behavior.
- Made scope declaration consistent by declaring `SYSTEM` in `GOV-SCOPE-004` while keeping it authorized in `GOV-REG-003`.
- Restored strict `TRACE > REPORT` precedence by assigning `REPORT=8` under `GOV-AUTH-010`.
- Removed SRC-INDEX overreach into BLD/code/test/report generation and removed all remaining traces to those deleted records.

## Source-Basis Drift Note

`doc/archive/ICP-Ledger-Source-Basis-Report_UPDATED.txt` was inspected as extraction input only. It was not treated as active governed authority. The active SRC-INDEX namespace registry already declares `AUTH-CALLER-*`, `FAIL-RULE-*`, `ATOMIC-*`, and `COMMIT-*`, so the source-basis namespace-table drift is documented here and left unchanged.

## Validation

Command used:

```powershell
node .\tools\validate-governed-sources.mjs
```

Result summary:

- JSONL parse: PASS
- Required fields: PASS
- Duplicate IDs: PASS
- Trace resolution: PASS
- Trace cycles: PASS / zero cycles
- Scope registry: PASS
- Authority levels: PASS
- Deleted-record trace safety: PASS
- SRC-INDEX boundary: PASS
