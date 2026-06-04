Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $RepoRoot

function Convert-ToSlashPath {
    param([string]$Path)
    return $Path -replace "\\", "/"
}

$candidateFiles = @()
foreach ($root in @("canisters", "src")) {
    if (Test-Path -LiteralPath $root) {
        $candidateFiles += Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object {
            $_.Extension -in @(".mo", ".rs", ".ts", ".js") -and
            ($_.Name -match "TransferExecutor|ConsistencyBoundary" -or (Convert-ToSlashPath $_.FullName) -match "/transfer/")
        }
    }
}

if ($candidateFiles.Count -eq 0) {
    Write-Output "NOT_APPLICABLE: No TransferExecutor, consistency boundary, or transfer implementation files found."
    exit 0
}

$matches = Select-String -LiteralPath ($candidateFiles.FullName) -Pattern "\bawait\b" -CaseSensitive:$false
if ($matches) {
    Write-Output "FAIL: BLOCKING await found inside transfer consistency-boundary candidate files."
    $matches | ForEach-Object {
        Write-Output "$($_.Path):$($_.LineNumber): $($_.Line.Trim())"
    }
    exit 1
}

Write-Output "PASS: No await token found in transfer consistency-boundary candidate files."
exit 0
