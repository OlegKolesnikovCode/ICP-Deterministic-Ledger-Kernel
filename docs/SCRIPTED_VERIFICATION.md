# Scripted Verification

Status: PRE_CODE_HARNESS_ONLY.

These scripts are verification rails for later implementation phases. They are not source authority and do not replace GOV/SRC/BLD records.

## Entrypoint

### `scripts/verify.ps1`

Runs the local verification stack:

- `python -B tools/source_validator/validate_src.py --sources sources --reports reports`
- `python -B tools/source_validator/validate_bld.py --sources sources --reports reports`
- `python -B tools/source_validator/validate_all.py --sources sources --reports reports`
- `python -B -m unittest discover -s tools/source_validator/tests`
- every `scripts/check-*.ps1` script created for the pre-code harness
- `dfx build` when `dfx.json` exists
- `git diff --check`

The entrypoint is expected to run under WSL/Linux PowerShell with `pwsh -File ./scripts/verify.ps1` and under Windows PowerShell with `powershell -ExecutionPolicy Bypass -File scripts\verify.ps1`. The harness constructs repository paths with PowerShell path APIs or portable forward-slash paths, invokes child checks through the current PowerShell host, and runs Python unittest discovery directly without `cmd.exe`.

What it checks:

- Authority validators still run before product code generation.
- Scripted scans are invoked through one command.
- `WARNING_ONLY` validator status is reported without being collapsed into PASS.
- `NOT_APPLICABLE` is allowed only for checks whose implementation target does not exist yet.
- Command-not-found errors, parser errors, PowerShell script failures, and native command nonzero exits are blocking failures unless the step explicitly returns the known validator `WARNING_ONLY` status.

What it cannot prove:

- Runtime ledger correctness.
- Upgrade safety.
- Transfer executor atomicity beyond static no-await scanning.
- Completeness of future tests before the matching implementation exists.

Failure meaning:

- `FAIL` means a blocking command or scan failed.
- `WARNING_ONLY` means no blocking command failed, but authority validators or trace checks still report warnings.
- `NOT_APPLICABLE` means no matching implementation target exists yet.

## Individual Scripts

### `scripts/check-authority-trace.ps1`

Checks that all required GOV/SRC/BLD authority files exist, parse, and declare active metadata in their first record. If `reports/validation-results.json` exists, it treats blocking or error counts as blocking and warning counts as `WARNING_ONLY`.

Cannot prove semantic correctness beyond the existing source validators.

Failure means required authority is missing, inactive, unparsable, or a validation report contains blocking/errors.

### `scripts/check-forbidden-api.ps1`

Scans implementation files under future product roots for forbidden public API names and equivalents, including balance setters, ledger entry creation/rewrite/delete methods, idempotency bypasses, and non-Transfer operation submission names.

Pre-code behavior: `NOT_APPLICABLE` when no implementation files exist.

Cannot prove that an allowed public API is semantically routed correctly; route-through-executor tests are still required in later phases.

Failure means a forbidden API or equivalent name appears in implementation files.

### `scripts/check-forbidden-internal-patterns.ps1`

Scans implementation files for high-risk internal shortcuts:

- unsupported operation family tokens
- Public API direct dependencies on stores or journals
- balance mutation outside governed balance/executor owners
- ledger mutation outside governed journal/executor owners
- arbitrary state/idempotency bypass setters

Pre-code behavior: `NOT_APPLICABLE` when no implementation files exist.

Cannot prove all semantic side effects; invariant tests and code review remain required.

Failure means a forbidden internal pattern was detected.

### `scripts/check-no-await-consistency-boundary.ps1`

Scans future transfer executor, consistency boundary, or transfer implementation files for `await`.

Pre-code behavior: `NOT_APPLICABLE` when no transfer consistency-boundary files exist.

Cannot prove absence of asynchronous behavior hidden behind non-`await` abstractions; code review and tests remain required.

Failure means `await` appears in a consistency-boundary candidate file.

### `scripts/check-candid-api-surface.ps1`

Scans future `.did`, `Main.mo`, and `PublicApi.mo` files for allowed public methods and forbidden API names.

Pre-code behavior: `NOT_APPLICABLE` when no Candid/API files exist.

Allowed methods in the pre-code scan are:

- `submitTransfer`
- `getTransfer`
- `getBalance`
- `getLedgerEntriesForTransfer`
- `getRequestOutcome`
- `health`
- `status`

Cannot prove that allowed methods are read-only or route correctly; tests and review remain required.

Failure means a forbidden method exists or a public method is outside the governed allowlist.

### `scripts/check-file-ownership-map.ps1`

Checks that `docs/IMPLEMENTATION_FILE_MAP.md` exists, has the required table header, and maps every implementation file once product implementation files exist.

Pre-code behavior: PASS when the map exists and no implementation files require current mapping.

Cannot prove the mapped verification obligations are sufficient; later phase reports must provide command evidence.

Failure means the map is missing, malformed, or omits implementation files.

### `scripts/check-module-test-coverage.ps1`

Checks that each implementation file has a required verification obligation in `docs/IMPLEMENTATION_FILE_MAP.md`.

Pre-code behavior: `NOT_APPLICABLE` when no implementation files exist.

Cannot prove the tests pass or that their assertions are complete.

Failure means an implementation file lacks a verification obligation or uses placeholder coverage text.

## Current SRC Warning Triage

The existing source validators report 329 warnings. This task does not modify GOV/SRC/BLD files and does not mass-fix these warnings.

| Warning Category | Count | Files | Classification | Current Handling |
|---|---:|---|---|---|
| `API_RULE_NOT_ROUTED_OR_TESTED` | 208 | `SRC-09` | `DEFER_TO_IMPLEMENTATION_PROOF` | Keep as warning-only for Stage 1. Future API/Candid/static-scan proof must map these records before public API completion. |
| `FAILURE_RULE_NOT_REFERENCED` | 121 | `SRC-06` | `DEFER_TO_IMPLEMENTATION_PROOF` | Keep as warning-only for Stage 1. Future failure handling tests and proof matrix must map deterministic rejection and failure-class coverage. |

No warning is reclassified as source truth by this document. If a later phase needs these warnings to block generation, that must be governed by active GOV/SRC/BLD records or an explicit user-approved phase gate.

## Pre-Code Expected Result

Before implementation modules exist:

- Authority validators may report `WARNING_ONLY` because of existing SRC warning coverage.
- Forbidden API scan should return `NOT_APPLICABLE`.
- Forbidden internal pattern scan should return `NOT_APPLICABLE`.
- No-await consistency boundary scan should return `NOT_APPLICABLE`.
- Candid/API surface scan should return `NOT_APPLICABLE`.
- File ownership map check should PASS because this document exists and no current implementation files require mapping.
- Module test coverage should return `NOT_APPLICABLE`.
