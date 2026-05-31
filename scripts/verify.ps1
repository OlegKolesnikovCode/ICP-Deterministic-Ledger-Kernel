Set-StrictMode -Version 2.0
$ErrorActionPreference = "Continue"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$Failures = 0
$Warnings = 0
$NotApplicable = 0
$Passed = 0

function Invoke-VerificationStep {
    param(
        [string]$Name,
        [scriptblock]$Command,
        [switch]$AllowWarningOnly
    )

    Write-Output ""
    Write-Output "== $Name =="
    $global:LASTEXITCODE = 0
    $rawOutput = & $Command 2>&1
    $exitCode = $LASTEXITCODE
    $output = @()
    foreach ($item in $rawOutput) {
        if ($item -is [System.Management.Automation.ErrorRecord]) {
            if ($item.Exception.Message) {
                $output += $item.Exception.Message
            } else {
                $output += $item.ToString()
            }
        } else {
            $output += $item.ToString()
        }
    }
    $text = ($output -join [Environment]::NewLine).Trim()
    if ($text.Length -gt 0) {
        Write-Output $text
    }

    if ($exitCode -ne 0) {
        if ($AllowWarningOnly -and $text -match "WARNING_ONLY") {
            Write-Output "RESULT: WARNING_ONLY"
            $script:Warnings += 1
            return
        }
        Write-Output "RESULT: FAIL"
        $script:Failures += 1
        return
    }

    if ($text -match "FAIL: BLOCKING" -or $text -match "RESULT: FAIL") {
        Write-Output "RESULT: FAIL"
        $script:Failures += 1
        return
    }

    if ($text -match "WARNING_ONLY") {
        Write-Output "RESULT: WARNING_ONLY"
        $script:Warnings += 1
        return
    }

    if ($text -match "NOT_APPLICABLE") {
        Write-Output "RESULT: NOT_APPLICABLE"
        $script:NotApplicable += 1
        return
    }

    Write-Output "RESULT: PASS"
    $script:Passed += 1
}

Invoke-VerificationStep "validate_src" {
    & python -B tools\source_validator\validate_src.py --sources sources --reports reports
} -AllowWarningOnly

Invoke-VerificationStep "validate_bld" {
    & python -B tools\source_validator\validate_bld.py --sources sources --reports reports
} -AllowWarningOnly

Invoke-VerificationStep "validate_all" {
    & python -B tools\source_validator\validate_all.py --sources sources --reports reports
} -AllowWarningOnly

Invoke-VerificationStep "source_validator_unittests" {
    & cmd /c "python -B -m unittest discover -s tools\source_validator\tests 2>&1"
}

$checkScripts = @(
    "scripts\check-authority-trace.ps1",
    "scripts\check-forbidden-api.ps1",
    "scripts\check-forbidden-internal-patterns.ps1",
    "scripts\check-no-await-consistency-boundary.ps1",
    "scripts\check-candid-api-surface.ps1",
    "scripts\check-file-ownership-map.ps1",
    "scripts\check-module-test-coverage.ps1"
)

foreach ($script in $checkScripts) {
    Invoke-VerificationStep $script {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $script
    } -AllowWarningOnly
}

if (Test-Path -LiteralPath "dfx.json") {
    Invoke-VerificationStep "dfx build" {
        & dfx build
    }
} else {
    Write-Output ""
    Write-Output "== dfx build =="
    Write-Output "NOT_APPLICABLE: dfx.json does not exist in pre-code verification mode."
    Write-Output "RESULT: NOT_APPLICABLE"
    $NotApplicable += 1
}

Invoke-VerificationStep "git diff --check" {
    & git diff --check
}

Write-Output ""
Write-Output "SUMMARY: PASS=$Passed WARNING_ONLY=$Warnings NOT_APPLICABLE=$NotApplicable FAIL=$Failures"

if ($Failures -gt 0) {
    Write-Output "VERIFY RESULT: FAIL"
    exit 1
}

if ($Warnings -gt 0) {
    Write-Output "VERIFY RESULT: WARNING_ONLY"
    exit 0
}

Write-Output "VERIFY RESULT: PASS"
exit 0
