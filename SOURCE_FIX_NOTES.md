# Source Fix Notes

## Scope

This pass repaired GOV/SRC source documents only. No implementation code, BLD files, or project scope changes were added.

## Files Changed

- `doc/SRC-01__CANISTER_AUTHORITY_MODEL__SOURCE__SYSTEM.jsonl`
- `doc/SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl`
- `doc/SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl`
- `doc/SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl`
- `doc/SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl`
- `doc/SRC-07__READ_MODEL_DERIVATION__SOURCE__SYSTEM.jsonl`
- `doc/SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl`
- `doc/SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl`
- `scripts/validate_sources.py`
- `SOURCE_FIX_NOTES.md`

## Records Changed

- Owner-boundary routing: `BOOT-004`, `ASSET-012`, `FAIL-RULE-301`, `FAIL-RULE-007`, `FAIL-RULE-008`, `FAIL-RULE-501`, `READ-010`, `READ-014`, `FORBID-015`, `FORBID-016`, `FORBID-017`, `FORBID-018`, `FORBID-026`.
- Canonical result serialization: `RESULT-023`, `RESULT-037`, `RESULT-038`, `RESULT-039`, `RESULT-040`, `RESULT-041`, `RESULT-042`, `RESULT-043`, `RESULT-044`.
- Idempotency fingerprint and recovery: `IDEMP-089`.
- Amount grammar: `AMOUNT-030`, `AMOUNT-031`, `AMOUNT-032`, `AMOUNT-034`, `AMOUNT-035`.
- Test coverage traces and mappings: `TEST-024`, `TEST-025`, `TEST-026`, `TEST-029`.

## Records Added

- Balance existence and runtime creation authority: `BAL-014`, `BAL-015`, `BAL-016`, `BAL-017`.
- Transfer dependency rules: `TRANSFER-039`, `TRANSFER-040`.
- Idempotency recovery determinism: `IDEMP-093`, `IDEMP-094`, `IDEMP-095`, `IDEMP-096`, `IDEMP-097`.
- Failure classification and rule: `FAIL-020`, `FAIL-RULE-508`.
- Test proof coverage: `TEST-030`, `TEST-ACCEPT-073`, `TEST-ACCEPT-074`, `TEST-ACCEPT-075`, `TEST-ACCEPT-076`, `TEST-ACCEPT-077`, `TEST-ACCEPT-078`, `TEST-MAP-029`, `TEST-MAP-030`, `FALSIFIER-020`, `DONE-030`, `RISK-020`.

## Records Deleted Or Superseded

- No records were deleted.
- No ID was reused for a different namespace.
- `AMOUNT-035` now preserves the strict leading-zero rejection decision and blocks the former canonicalization interpretation.
- Duplicate non-owner records were converted to routing/dependency wording instead of being deleted.

## Duplicate Groups Resolved

- `UPG-015` remains the maintenance-mode behavior owner; `FAIL-RULE-008` and `FAIL-RULE-501` now route/classify without redefining maintenance-mode behavior.
- `AUTH-READMODEL-005` and `AUTH-READMODEL-007` remain authority-boundary owners; `READ-010` and `READ-014` now reference those boundaries from SRC-07.
- `ASSET-012` owns MVP runtime asset-creation exclusion; `BOOT-004` now prevents bootstrap/admin bypass.
- `IDEMP-051` owns final idempotency outcome storage exclusion for nondeterministic failures; `FAIL-RULE-301` and `FAIL-RULE-007` now route failure classification to the idempotency owner.
- `FORBID-088` through `FORBID-091` and `FORBID-082` remain controlling forbidden API records; `FORBID-015` through `FORBID-018` and `FORBID-026` now route to them.

## Determinism Repairs

- Committed result serialization now has one field order, one timestamp encoding, one operation id encoding, one ledgerEntryIds ordering rule, one deterministic error-code representation, and one response-hash algorithm/digest encoding.
- Request fingerprinting now defines exact fields, field order, no-whitespace UTF-8 JSON input serialization, SHA-256 hashing, and lowercase hexadecimal digest encoding.
- IN_PROGRESS recovery now defines Ledger Core-only recovery authority, non-timeout stale trigger, required observations, committed recovery behavior, and rejection-storage limits.
- Transfer balance existence is explicit: both source and destination `Balance(accountId,assetId)` records must exist before commit, runtime zero-balance creation is not allowed, and missing balances route to `FAIL-020`.
- Amount grammar now rejects redundant leading zeros for nonzero integer parts and rejects over-precision without rounding.

## Remaining Unresolved Issues

- No blocking JSONL, trace, scope, ownership, duplicate-group, RESULT canonicalization, or IDEMP fingerprint validation issue remains in the edited areas.
- This pass did not fully redesign SRC-10; it added only direct proof coverage for newly added or materially changed critical rules.

## Validation Commands Run

```powershell
python .\scripts\validate_sources.py .\doc
```

## Validation Result

```text
records: 1916
json_errors: 0
duplicate_ids: 0
field_order_errors: 0
invalid_types: 0
invalid_classes: 0
invalid_scope_tokens: 0
invalid_trace_shapes: 0
unresolved_trace_refs: 0
authority_level_errors: 0
file_field_errors: 0
id_owner_errors: 0
semantic_errors: 0
VALIDATION_STATUS: PASS
```
