Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$requiredFiles = @(
    "sources\gov\GOV-00__SOURCE_CONSTITUTION__GOVERNANCE__GLOBAL.jsonl",
    "sources\src\SRC-INDEX__SOURCE_TRACEABILITY__LOOKUP_ROUTING.jsonl",
    "sources\src\SRC-00__PROJECT_IDENTITY__SOURCE__GLOBAL.jsonl",
    "sources\src\SRC-01__CANISTER_AUTHORITY_MODEL__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-02__DOMAIN_ENTITIES__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-03__TRANSFER_OPERATION__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-04__IDEMPOTENCY_REPLAY__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-05__LEDGER_JOURNAL_INVARIANTS__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-06__FAILURE_MODEL__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-07__READ_MODEL_DERIVATION__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-08__UPGRADE_SAFETY__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-09__API_SURFACE_FORBIDDEN_APIS__SOURCE__SYSTEM.jsonl",
    "sources\src\SRC-10__TEST_PROOF_REQUIREMENTS__SOURCE__SYSTEM.jsonl",
    "sources\bld\BLD-INDEX__BUILD_TRACEABILITY__LOOKUP_ROUTING.jsonl",
    "sources\bld\BLD-00__IMPLEMENTATION_IDENTITY__BUILD__GLOBAL.jsonl",
    "sources\bld\BLD-01__CANISTER_AUTHORITY_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-02__DOMAIN_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-03__TRANSFER_PIPELINE_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-04__IDEMPOTENCY_REPLAY_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-05__LEDGER_JOURNAL_COMMIT_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-06__FAILURE_HANDLING_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-07__READ_MODEL_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-08__UPGRADE_SAFETY_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-09__API_SURFACE_IMPLEMENTATION__BUILD__SYSTEM.jsonl",
    "sources\bld\BLD-10__TEST_PROOF_IMPLEMENTATION__BUILD__SYSTEM.jsonl"
)

$missing = @()
$inactive = @()
$parseErrors = @()

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        $missing += $file
        continue
    }

    try {
        $firstLine = Get-Content -LiteralPath $file -TotalCount 1
        $record = $firstLine | ConvertFrom-Json
        if ($record.statement -notmatch "status=ACTIVE") {
            $inactive += "$file first record does not declare status=ACTIVE"
        }
    } catch {
        $parseErrors += "$file $($_.Exception.Message)"
    }
}

if ($missing.Count -gt 0 -or $inactive.Count -gt 0 -or $parseErrors.Count -gt 0) {
    Write-Output "FAIL: BLOCKING authority trace precondition failed."
    $missing | ForEach-Object { Write-Output "MISSING: $_" }
    $inactive | ForEach-Object { Write-Output "INACTIVE_OR_INVALID_META: $_" }
    $parseErrors | ForEach-Object { Write-Output "PARSE_ERROR: $_" }
    exit 1
}

$reportPath = "reports\validation-results.json"
if (Test-Path -LiteralPath $reportPath) {
    $report = Get-Content -Raw -LiteralPath $reportPath | ConvertFrom-Json
    $blocking = [int]$report.counts.blocking
    $errors = [int]$report.counts.errors
    $warnings = [int]$report.counts.warnings
    if ($blocking -gt 0 -or $errors -gt 0) {
        Write-Output "FAIL: BLOCKING validation report contains blocking=$blocking errors=$errors."
        exit 1
    }
    if ($warnings -gt 0) {
        Write-Output "WARNING_ONLY: Authority files are present and active, but validation report contains warnings=$warnings."
        exit 0
    }
}

Write-Output "PASS: Authority files are present, active, and have no blocking validation report findings."
exit 0
