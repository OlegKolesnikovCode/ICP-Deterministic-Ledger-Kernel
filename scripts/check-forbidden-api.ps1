Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

function Get-ImplementationFiles {
    $files = @()
    foreach ($root in @("canisters", "src")) {
        if (Test-Path -LiteralPath $root) {
            $files += Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object {
                $_.FullName -notmatch "\\node_modules\\" -and
                $_.FullName -notmatch "\\.dfx\\" -and
                $_.Extension -in @(".mo", ".did", ".rs", ".ts", ".js", ".mjs", ".cjs")
            }
        }
    }
    foreach ($topLevel in @("dfx.json", "mops.toml", "package.json")) {
        if (Test-Path -LiteralPath $topLevel) {
            $files += Get-Item -LiteralPath $topLevel
        }
    }
    return $files
}

$implementationFiles = @(Get-ImplementationFiles)
if ($implementationFiles.Count -eq 0) {
    Write-Output "NOT_APPLICABLE: No implementation files found for forbidden API scan."
    exit 0
}

$forbiddenNames = @(
    "setBalance",
    "createLedgerEntry",
    "rewriteLedgerEntry",
    "deleteLedgerEntry",
    "setTransferState",
    "forceCommitTransfer",
    "bypassIdempotency",
    "mutateReadModel",
    "setRequestOutcome",
    "adminAdjustBalance",
    "patchBalance",
    "setOperationState",
    "rewriteJournal",
    "forceCommitOperation",
    "mutateReadModelAsAuthority",
    "gatewayDebitAccount",
    "gatewayCreditAccount",
    "operationModuleWriteBalance",
    "operationModuleAppendJournal",
    "mintBalance",
    "overwriteBalance",
    "submitDeposit",
    "submitWithdrawal",
    "executeDeposit",
    "executeWithdrawal"
)

$pattern = "\b(" + (($forbiddenNames | ForEach-Object { [regex]::Escape($_) }) -join "|") + ")\b"
$matches = Select-String -LiteralPath ($implementationFiles.FullName) -Pattern $pattern -CaseSensitive:$false -AllMatches

if ($matches) {
    Write-Output "FAIL: BLOCKING forbidden public API or equivalent name found."
    $matches | ForEach-Object {
        Write-Output "$($_.Path):$($_.LineNumber): $($_.Line.Trim())"
    }
    exit 1
}

Write-Output "PASS: No forbidden API names found in implementation files."
exit 0
