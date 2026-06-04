Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $RepoRoot

$mapPath = "docs/IMPLEMENTATION_FILE_MAP.md"
if (-not (Test-Path -LiteralPath $mapPath)) {
    Write-Output "FAIL: BLOCKING docs/IMPLEMENTATION_FILE_MAP.md is missing."
    exit 1
}

$mapContent = Get-Content -Raw -LiteralPath $mapPath
if ($mapContent -notmatch "\| File \| Phase \| Governed By \| May Import \| Must Not Import \| Required Verification \|") {
    Write-Output "FAIL: BLOCKING implementation file map does not contain the required table header."
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
    Write-Output "PASS: Implementation file map exists; no implementation files require current mapping in pre-code mode."
    exit 0
}

$missing = @()
foreach ($file in $implementationFiles) {
    $relative = Resolve-Path -LiteralPath $file.FullName -Relative
    $relative = $relative.TrimStart(".", "\", "/")
    $slashRelative = $relative -replace "\\", "/"
    if ($mapContent -notmatch [regex]::Escape($relative) -and $mapContent -notmatch [regex]::Escape($slashRelative)) {
        $missing += $relative
    }
}

if ($missing.Count -gt 0) {
    Write-Output "FAIL: BLOCKING implementation files missing from docs/IMPLEMENTATION_FILE_MAP.md."
    $missing | ForEach-Object { Write-Output "UNMAPPED: $_" }
    exit 1
}

Write-Output "PASS: All implementation files are mapped."
exit 0
