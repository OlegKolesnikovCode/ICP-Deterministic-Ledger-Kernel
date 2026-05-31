Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$apiFiles = @()
foreach ($root in @("canisters", "src")) {
    if (Test-Path -LiteralPath $root) {
        $apiFiles += Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object {
            $_.Extension -eq ".did" -or $_.Name -match "Main\.mo|PublicApi\.mo"
        }
    }
}

if ($apiFiles.Count -eq 0) {
    Write-Output "NOT_APPLICABLE: No Candid, Main.mo, or PublicApi.mo files found."
    exit 0
}

$allowedMethods = @(
    "submitTransfer",
    "getTransfer",
    "getBalance",
    "getLedgerEntriesForTransfer",
    "getRequestOutcome",
    "health",
    "status"
)

$forbiddenPattern = "\b(setBalance|createLedgerEntry|rewriteLedgerEntry|deleteLedgerEntry|setTransferState|forceCommitTransfer|bypassIdempotency|mutateReadModel|setRequestOutcome|adminAdjustBalance|submitDeposit|submitWithdrawal|executeDeposit|executeWithdrawal|mintBalance|overwriteBalance)\b"
$forbiddenMatches = Select-String -LiteralPath ($apiFiles.FullName) -Pattern $forbiddenPattern -CaseSensitive:$false
if ($forbiddenMatches) {
    Write-Output "FAIL: BLOCKING forbidden method name found in API surface."
    $forbiddenMatches | ForEach-Object { Write-Output "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
    exit 1
}

$unknownMethods = @()
foreach ($file in $apiFiles) {
    $lines = Get-Content -LiteralPath $file.FullName
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($file.Extension -eq ".did" -and $line -match "^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:") {
            $method = $Matches[1]
            if ($allowedMethods -notcontains $method) {
                $unknownMethods += "$($file.FullName):$($i + 1): public candid method not in allowlist: $method"
            }
        }
        if ($file.Extension -eq ".mo" -and $line -match "\bpublic\b.*\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)") {
            $method = $Matches[1]
            if ($allowedMethods -notcontains $method) {
                $unknownMethods += "$($file.FullName):$($i + 1): public Motoko method not in allowlist: $method"
            }
        }
    }
}

if ($unknownMethods.Count -gt 0) {
    Write-Output "FAIL: BLOCKING API method outside governed allowlist found."
    $unknownMethods | ForEach-Object { Write-Output $_ }
    exit 1
}

Write-Output "PASS: API surface matches pre-code allowlist scan."
exit 0
