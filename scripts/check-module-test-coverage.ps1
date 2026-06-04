Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $RepoRoot

$mapPath = "docs/IMPLEMENTATION_FILE_MAP.md"
if (-not (Test-Path -LiteralPath $mapPath)) {
    Write-Output "FAIL: BLOCKING docs/IMPLEMENTATION_FILE_MAP.md is missing."
    exit 1
}

function Convert-ToSlashPath {
    param([string]$Path)
    return $Path -replace "\\", "/"
}

$implementationFiles = @()
foreach ($root in @("canisters", "src")) {
    if (Test-Path -LiteralPath $root) {
        $implementationFiles += Get-ChildItem -LiteralPath $root -Recurse -File | Where-Object {
            (Convert-ToSlashPath $_.FullName) -notmatch "/node_modules/" -and
            (Convert-ToSlashPath $_.FullName) -notmatch "/\.dfx/" -and
            $_.Extension -in @(".mo", ".did", ".rs", ".ts", ".js", ".mjs", ".cjs", ".json", ".toml")
        }
    }
}
foreach ($topLevel in @("dfx.json", "mops.toml", "package.json")) {
    if (Test-Path -LiteralPath $topLevel) {
        $implementationFiles += Get-Item -LiteralPath $topLevel
    }
}

if ($implementationFiles.Count -eq 0) {
    Write-Output "NOT_APPLICABLE: No implementation files found for module verification coverage."
    exit 0
}

$mapLines = Get-Content -LiteralPath $mapPath
$unverified = @()
foreach ($file in $implementationFiles) {
    $relative = Resolve-Path -LiteralPath $file.FullName -Relative
    $relative = $relative.TrimStart(".", "\", "/")
    $slashRelative = $relative -replace "\\", "/"
    $row = $mapLines | Where-Object { $_ -match [regex]::Escape($relative) -or $_ -match [regex]::Escape($slashRelative) } | Select-Object -First 1
    if (-not $row) {
        $unverified += "$relative missing map row"
        continue
    }
    $cells = $row.Split("|") | ForEach-Object { $_.Trim() }
    if ($cells.Count -lt 7 -or [string]::IsNullOrWhiteSpace($cells[6]) -or $cells[6] -match "TBD|none|unknown") {
        $unverified += "$relative missing required verification obligation"
    }
}

if ($unverified.Count -gt 0) {
    Write-Output "FAIL: BLOCKING implementation files lack verification obligations."
    $unverified | ForEach-Object { Write-Output "UNVERIFIED: $_" }
    exit 1
}

Write-Output "PASS: All implementation files have verification obligations in the file map."
exit 0
