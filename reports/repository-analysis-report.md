# Repository Analysis Report

Generated: 2026-05-28

Repository: ICP Deterministic Ledger Kernel

## Executive Summary

The repository is a governed source/build authority corpus plus a Python validation toolchain. It does not yet contain application runtime implementation code; the active assets are the GOV/SRC/BLD JSONL authority records, generated validation reports, a source-basis document, a staged code creation plan, and validator tooling.

Current validation status is strong at the hard-failure level:

- Combined validation: `WARNING_ONLY`
- Blocking issues: `0`
- Errors: `0`
- Warnings: `329`
- Info findings: `1042`
- Unit tests: `17` tests passing
- Python compile sanity check: passing

The remaining warnings are concentrated in two source files:

- `SRC-09`: `208` `API_RULE_NOT_ROUTED_OR_TESTED` warnings
- `SRC-06`: `121` `FAILURE_RULE_NOT_REFERENCED` warnings

The BLD corpus validates cleanly with `PASS` across all `25` governed files and `3127` records.

## Scope Analyzed

All visible repository files were inventoried and reviewed at repository level:

- `sources/`: governed GOV/SRC/BLD JSONL authority records
- `tools/source_validator/`: validator CLI, core models, rule registries, validators, output renderers, tests
- `reports/`: generated validation reports
- `basis/`: source-basis extraction input
- `plans/`: implementation plan currently untracked in git

Repository inventory at scan time:

| Area | Files | Bytes |
| --- | ---: | ---: |
| `basis/` | 1 | 7241 |
| `plans/` | 1 | 35305 |
| `reports/` | 7 | 2077249 |
| `sources/` | 25 | 2094825 |
| `tools/` | 58 | 133418 |

Total visible files before this report was added: `92`, about `4246.1 KiB`.

## File Type Inventory

| Extension | Files | Bytes |
| --- | ---: | ---: |
| `.py` | 52 | 133412 |
| `.jsonl` | 25 | 2094825 |
| `.gitkeep` | 6 | 6 |
| `.md` | 5 | 671774 |
| `.json` | 3 | 1440780 |
| `.txt` | 1 | 7241 |

## Governed Record Inventory

The governed JSONL corpus contains `3127` records across `25` files.

| Class | Records |
| --- | ---: |
| `SOURCE` | 1662 |
| `BUILD` | 1077 |
| `INDEX` | 280 |
| `GOVERNANCE` | 108 |

| Type | Records |
| --- | ---: |
| `MUST` | 1032 |
| `DECLARES` | 737 |
| `MUST_NOT` | 678 |
| `REQUIRES` | 537 |
| `FORBIDS` | 76 |
| `MAY` | 51 |
| `SHOULD` | 12 |
| `OVERRIDES` | 4 |

| Authority Level | Records |
| --- | ---: |
| `0` | 108 |
| `1` | 144 |
| `2` | 1662 |
| `3` | 136 |
| `4` | 1077 |

## Source And Build File Inventory

| File | Records | Bytes |
| --- | ---: | ---: |
| `sources/bld/BLD-00__IMPLEMENTATION_IDENTITY__BUILD__GLOBAL.jsonl` | 61 | 40528 |
| `sources/bld/BLD-01__CANISTER_AUTHORITY_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 107 | 83287 |
| `sources/bld/BLD-02__DOMAIN_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 115 | 95134 |
| `sources/bld/BLD-03__TRANSFER_PIPELINE_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 68 | 55655 |
| `sources/bld/BLD-04__IDEMPOTENCY_REPLAY_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 84 | 78688 |
| `sources/bld/BLD-05__LEDGER_JOURNAL_COMMIT_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 78 | 61766 |
| `sources/bld/BLD-06__FAILURE_HANDLING_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 130 | 111566 |
| `sources/bld/BLD-07__READ_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 123 | 115636 |
| `sources/bld/BLD-08__UPGRADE_SAFETY_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 129 | 128016 |
| `sources/bld/BLD-09__API_SURFACE_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 81 | 64736 |
| `sources/bld/BLD-10__TEST_PROOF_IMPLEMENTATION__BUILD__SYSTEM.jsonl` | 101 | 73579 |
| `sources/bld/BLD-INDEX__BUILD_TRACEABILITY__LOOKUP_ROUTING.jsonl` | 136 | 87208 |
| `sources/gov/GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl` | 108 | 58227 |
| `sources/src/SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl` | 72 | 39351 |
| `sources/src/SRC-01__CANISTER_AUTHORITY_MODEL__SOURCE__SYSTEM.jsonl` | 104 | 61016 |
| `sources/src/SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl` | 137 | 73877 |
| `sources/src/SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl` | 132 | 77066 |
| `sources/src/SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl` | 121 | 73453 |
| `sources/src/SRC-05__LEDGER_JOURNAL_INVARIANTS__SOURCE__SYSTEM.jsonl` | 153 | 84425 |
| `sources/src/SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl` | 139 | 84225 |
| `sources/src/SRC-07__READ_MODEL_DERIVATION__SOURCE__SYSTEM.jsonl` | 129 | 75780 |
| `sources/src/SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl` | 171 | 104413 |
| `sources/src/SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl` | 223 | 138857 |
| `sources/src/SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl` | 281 | 154915 |
| `sources/src/SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl` | 144 | 73421 |

## Validation Results

Commands run:

```powershell
python -B tools\source_validator\validate_all.py
python -B -m unittest discover -s tools\source_validator\tests
python -B -m compileall -q tools\source_validator
```

Results:

| Check | Verdict | Files | Records | Blocking | Errors | Warnings | Info |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Combined GOV/SRC/BLD validation | `WARNING_ONLY` | 25 | 3127 | 0 | 0 | 329 | 1042 |
| SRC validation | `WARNING_ONLY` | 13 | 1914 | 0 | 0 | 329 | 1042 |
| BLD validation | `PASS` | 25 | 3127 | 0 | 0 | 0 | 0 |

The combined validator exits with code `1` when warnings exist. In this run, that non-zero exit represented warning-only status, not a tool crash or schema failure.

## Warning Breakdown

| Severity | Category | Count | Location |
| --- | --- | ---: | --- |
| `WARNING` | `API_RULE_NOT_ROUTED_OR_TESTED` | 208 | `SRC-09` |
| `WARNING` | `FAILURE_RULE_NOT_REFERENCED` | 121 | `SRC-06` |
| `INFO` | `SOURCE_RECORD_ZERO_INBOUND_TRACES` | 1041 | SRC graph-wide |
| `INFO` | `BLD_FILES_IGNORED` | 1 | SRC-only validator behavior |

The actionable warnings are not distributed across the whole project. They are concentrated in API/forbidden API routing and failure model routing.

Recommended repair order:

1. Add SRC-INDEX routing or SRC-10 proof coverage for API/FORBID rules in `SRC-09`.
2. Add proof, lifecycle, transfer, or failure references for FAIL rules in `SRC-06`.
3. Review zero-inbound source records as governance hygiene. These are informational and may include intentionally terminal authority records.

## Zero-Inbound Info Distribution

| File | Info Count |
| --- | ---: |
| `SRC-10` | 218 |
| `SRC-09` | 203 |
| `SRC-08` | 141 |
| `SRC-06` | 100 |
| `SRC-07` | 81 |
| `SRC-05` | 58 |
| `SRC-02` | 54 |
| `SRC-00` | 50 |
| `SRC-04` | 50 |
| `SRC-03` | 43 |
| `SRC-01` | 43 |

Interpretation: this does not mean these records are invalid. The validator marks records with no inbound trace in the current SRC-only graph so maintainers can decide whether they are terminal authority, acceptance records, risk records, or missing routing.

## Tooling Analysis

The validator implementation is small and direct. It uses Python standard library only: `argparse`, `json`, `pathlib`, `dataclasses`, `collections`, `enum`, `re`, `tempfile`, `traceback`, `typing`, and `unittest`.

The toolchain is organized around:

- CLI entry points: `cli.py`, `bld_cli.py`, `all_cli.py`
- thin wrapper scripts: `validate_src.py`, `validate_bld.py`, `validate_all.py`
- core model/index/path/report utilities under `core/`
- rule registries under `rules/`
- focused validators under `validators/`
- report renderers under `outputs/`
- unit tests under `tests/`

Strengths:

- Schema validation rejects duplicate JSON keys, wrong field order, missing/extra fields, wrong primitive types, empty required text, and empty non-GOV traces.
- Record indexing detects duplicate IDs globally and within files and builds inbound/outbound trace maps.
- SRC validation separates trace resolution, trace direction, namespace ownership, source ownership, SRC-INDEX routing, SRC-10 proof-boundary checks, and coverage hygiene.
- BLD validation checks file manifest rules, token registry usage, BLD trace resolution/direction, template requirements, statement grammar, target traces, and guardrails.
- Unit tests cover the most important hard-failure paths and BLD guardrails.

Risks and gaps:

- Test coverage is useful but narrow: `17` unit tests for a validator that enforces many governance rules. More negative fixtures would reduce regression risk.
- Generated validation summaries are very large because every issue is rendered inline. This is useful for repair but noisy for top-level review.
- `exit_code_for_report` currently returns `1` for warnings regardless of the `fail_on` argument. The CLI help says the threshold is retained for compatibility and exit codes still report warning/error/blocking outcomes, so this appears intentional, but CI users should know warning-only validation is non-zero.
- There is no runtime canister/application implementation yet. The repository is ready for governed implementation generation, not application deployment.

## Documentation And Planning Assets

`basis/ICP-Ledger-Source-Basis-Report_UPDATED.txt` is explicitly marked as source-basis/extraction input, not active governed source authority until converted into GOV-compliant JSONL records and activated through GOV/SRC routing.

`plans/ICP_Deterministic_Ledger_Kernel_2_Code_Creation_Plan_WITH_SCRIPTED_VERIFICATION.md` defines a staged implementation sequence from authority freeze through verification harness, skeleton creation, domain/failure/stable-state model, authority boundary, transfer lifecycle, balance control, ledger journal, idempotency, executor boundary, read model, API surface, proof tests, local deployment, and proof reporting.

Git status before this report was created showed `plans/` as untracked. Existing validator report files did not show as modified after refreshing validation outputs.

## Readiness Assessment

The governed source/build corpus is internally consistent enough to proceed with planned implementation work after warning triage decisions are made.

Practical readiness:

- Governance and schema integrity: ready
- BLD implementation authority: ready
- Validator execution: ready
- Unit-test baseline: ready but should expand as rules evolve
- Runtime implementation: not present yet
- Remaining source hygiene: warning-only, concentrated in `SRC-06` and `SRC-09`

## Recommended Next Steps

1. Decide whether warning-free SRC validation is required before implementation starts.
2. If yes, repair `SRC-09` first by routing or test-covering API/FORBID records.
3. Repair `SRC-06` by linking FAIL records into tests, lifecycle rules, transfer rules, or failure-to-failure routing.
4. Add validator tests for the two active warning categories so repairs cannot regress silently.
5. Keep `reports/validation-summary.md` as the exhaustive repair ledger, and use this report as the concise project-level status report.

