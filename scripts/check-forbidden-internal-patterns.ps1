Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $RepoRoot

function Convert-ToSlashPath {
    param([string]$Path)
    return $Path -replace "\\", "/"
}

function Get-ImplementationFiles {
    $files = @()
    foreach ($root in @("canisters", "src")) {
        if (Test-Path -LiteralPath $root) {
            $files += Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object {
                (Convert-ToSlashPath $_.FullName) -notmatch "/node_modules/" -and
                (Convert-ToSlashPath $_.FullName) -notmatch "/\.dfx/" -and
                $_.Extension -in @(".mo", ".did", ".rs", ".ts", ".js", ".mjs", ".cjs")
            }
        }
    }
    return $files
}

$implementationFiles = @(Get-ImplementationFiles)
if ($implementationFiles.Count -eq 0) {
    Write-Output "NOT_APPLICABLE: No implementation files found for forbidden internal pattern scan."
    exit 0
}

$blockingFindings = @()

$unsupportedOperationPattern = "\b(Deposit|Withdrawal|Withdraw|Mint|Burn|Fee|Reversal|BatchTransfer|AdminAdjustment)\b"
$unsupportedMatches = @(Select-String -LiteralPath ($implementationFiles.FullName) -Pattern $unsupportedOperationPattern -CaseSensitive:$false)
foreach ($match in $unsupportedMatches) {
    $blockingFindings += "$($match.Path):$($match.LineNumber): unsupported operation token: $($match.Line.Trim())"
}

$publicApiFiles = @($implementationFiles | Where-Object { $_.Name -match "PublicApi|Main" -or $_.Extension -eq ".did" })
if ($publicApiFiles.Count -gt 0) {
    $directStorePattern = "\b(BalanceStore|LedgerJournal|StableState|IdempotencyStore)\b"
    $directStoreMatches = @(Select-String -LiteralPath ($publicApiFiles.FullName) -Pattern $directStorePattern -CaseSensitive:$false)
    foreach ($match in $directStoreMatches) {
        $blockingFindings += "$($match.Path):$($match.LineNumber): public API direct store/journal dependency: $($match.Line.Trim())"
    }
}

$balanceMutationPattern = "\b(putBalance|setBalance|overwriteBalance|mintBalance|debitBalance|creditBalance)\b|balances\.(put|set|delete)|balances\s*:="
$balanceFiles = @($implementationFiles | Where-Object { (Convert-ToSlashPath $_.FullName) -notmatch "/balances/" -and $_.Name -notmatch "BalanceControl|TransferExecutor" })
if ($balanceFiles.Count -gt 0) {
    $balanceMatches = @(Select-String -LiteralPath ($balanceFiles.FullName) -Pattern $balanceMutationPattern -CaseSensitive:$false)
    foreach ($match in $balanceMatches) {
        $blockingFindings += "$($match.Path):$($match.LineNumber): balance mutation outside governed owner: $($match.Line.Trim())"
    }
}

$ledgerMutationPattern = "\b(appendLedger|createLedgerEntry|rewriteLedgerEntry|deleteLedgerEntry|rewriteJournal)\b|ledgerEntries\.(put|set|delete)"
$ledgerFiles = @($implementationFiles | Where-Object { (Convert-ToSlashPath $_.FullName) -notmatch "/ledger/" -and $_.Name -notmatch "LedgerJournal|TransferExecutor" })
if ($ledgerFiles.Count -gt 0) {
    $ledgerMatches = @(Select-String -LiteralPath ($ledgerFiles.FullName) -Pattern $ledgerMutationPattern -CaseSensitive:$false)
    foreach ($match in $ledgerMatches) {
        $blockingFindings += "$($match.Path):$($match.LineNumber): ledger mutation outside governed journal path: $($match.Line.Trim())"
    }
}

$stateSetterPattern = "\b(setTransferState|setOperationState|forceCommitTransfer|forceCommitOperation|bypassIdempotency)\b"
$setterMatches = @(Select-String -LiteralPath ($implementationFiles.FullName) -Pattern $stateSetterPattern -CaseSensitive:$false)
foreach ($match in $setterMatches) {
    $blockingFindings += "$($match.Path):$($match.LineNumber): arbitrary state/idempotency bypass pattern: $($match.Line.Trim())"
}

if ($blockingFindings.Count -gt 0) {
    Write-Output "FAIL: BLOCKING forbidden internal pattern found."
    $blockingFindings | ForEach-Object { Write-Output $_ }
    exit 1
}

Write-Output "PASS: No forbidden internal patterns found in implementation files."
exit 0
