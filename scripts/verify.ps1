Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
Set-Location -LiteralPath $RepoRoot

$Failures = 0
$Warnings = 0
$NotApplicable = 0
$Passed = 0

function Join-RepoPath {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Parts
    )

    $path = $RepoRoot
    foreach ($part in $Parts) {
        $path = Join-Path -Path $path -ChildPath $part
    }
    return $path
}

function Test-WindowsHost {
    return $PSVersionTable.PSEdition -eq "Desktop" -or [System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT
}

function Get-PowerShellExecutable {
    $currentProcess = Get-Process -Id $PID
    if ($currentProcess.Path) {
        return $currentProcess.Path
    }

    $commandName = "pwsh"
    if (Test-WindowsHost) {
        $commandName = "powershell"
    }

    $command = Get-Command $commandName -ErrorAction Stop
    return $command.Source
}

function Invoke-VerificationStep {
    param(
        [string]$Name,
        [scriptblock]$Command,
        [switch]$AllowWarningOnly
    )

    Write-Output ""
    Write-Output "== $Name =="
    $global:LASTEXITCODE = 0
    $commandFailed = $false
    $rawOutput = @()
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $rawOutput = & $Command 2>&1
        $exitCode = $LASTEXITCODE
    } catch {
        $commandFailed = $true
        $exitCode = 1
        $rawOutput = @($_)
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $output = @()
    foreach ($item in $rawOutput) {
        if ($item -is [System.Management.Automation.ErrorRecord]) {
            $message = $item.ToString()
            if ($message) {
                $output += $message
            } elseif ($item.Exception.Message) {
                $output += $item.Exception.Message
            } else {
                $output += $item.FullyQualifiedErrorId
            }
        } else {
            $output += $item.ToString()
        }
    }
    $text = ($output -join [Environment]::NewLine).Trim()
    if ($text.Length -gt 0) {
        Write-Output $text
    }

    $hasBlockingPowerShellError = $text -match "CommandNotFoundException|ParserError|The term '.+' is not recognized|not recognized as the name of a cmdlet|not recognized as a name of a cmdlet"

    if ($commandFailed -or $hasBlockingPowerShellError -or $exitCode -ne 0) {
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

$ValidateSrc = Join-RepoPath "tools" "source_validator" "validate_src.py"
$ValidateBld = Join-RepoPath "tools" "source_validator" "validate_bld.py"
$ValidateAll = Join-RepoPath "tools" "source_validator" "validate_all.py"
$SourcesDir = "sources"
$ReportsDir = "reports"
$SourceValidatorTests = Join-RepoPath "tools" "source_validator" "tests"
$PowerShellExecutable = Get-PowerShellExecutable

Invoke-VerificationStep "validate_src" {
    & python -B $ValidateSrc --sources $SourcesDir --reports $ReportsDir
} -AllowWarningOnly

Invoke-VerificationStep "validate_bld" {
    & python -B $ValidateBld --sources $SourcesDir --reports $ReportsDir
} -AllowWarningOnly

Invoke-VerificationStep "validate_all" {
    & python -B $ValidateAll --sources $SourcesDir --reports $ReportsDir
} -AllowWarningOnly

Invoke-VerificationStep "source_validator_unittests" {
    & python -B -m unittest discover -s $SourceValidatorTests
}

$checkScripts = @(
    @{ Name = "scripts/check-authority-trace.ps1"; Path = (Join-RepoPath "scripts" "check-authority-trace.ps1") },
    @{ Name = "scripts/check-forbidden-api.ps1"; Path = (Join-RepoPath "scripts" "check-forbidden-api.ps1") },
    @{ Name = "scripts/check-forbidden-internal-patterns.ps1"; Path = (Join-RepoPath "scripts" "check-forbidden-internal-patterns.ps1") },
    @{ Name = "scripts/check-no-await-consistency-boundary.ps1"; Path = (Join-RepoPath "scripts" "check-no-await-consistency-boundary.ps1") },
    @{ Name = "scripts/check-candid-api-surface.ps1"; Path = (Join-RepoPath "scripts" "check-candid-api-surface.ps1") },
    @{ Name = "scripts/check-file-ownership-map.ps1"; Path = (Join-RepoPath "scripts" "check-file-ownership-map.ps1") },
    @{ Name = "scripts/check-module-test-coverage.ps1"; Path = (Join-RepoPath "scripts" "check-module-test-coverage.ps1") }
)

foreach ($script in $checkScripts) {
    Invoke-VerificationStep $script.Name {
        $arguments = @("-NoProfile")
        if (Test-WindowsHost) {
            $arguments += @("-ExecutionPolicy", "Bypass")
        }
        $arguments += @("-File", $script.Path)
        & $PowerShellExecutable @arguments
    } -AllowWarningOnly
}

$DfxJson = Join-RepoPath "dfx.json"
if (Test-Path -LiteralPath $DfxJson) {
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
