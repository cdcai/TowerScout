param(
    [string] $ProviderId = "podman-compose-pypi-1.5.0",

    [string] $InstallDir = "",

    [string] $Python = "python",

    [switch] $Apply,

    [switch] $Force
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutPodmanComposeProvider.ps1"

function Test-TowerScoutInstallerChildPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Parent,

        [Parameter(Mandatory = $true)]
        [string] $Child
    )

    $parentFull = [System.IO.Path]::GetFullPath($Parent)
    $childFull = [System.IO.Path]::GetFullPath($Child)
    $trimChars = [char[]]@([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $parentPrefix = $parentFull.TrimEnd($trimChars) + [System.IO.Path]::DirectorySeparatorChar

    return $childFull.StartsWith($parentPrefix, [System.StringComparison]::OrdinalIgnoreCase)
}

function Invoke-TowerScoutInstallerCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FileName,

        [string[]] $Arguments = @(),

        [Parameter(Mandatory = $true)]
        [string] $FailureMessage
    )

    Write-Host "$FileName $([string]::Join(' ', $Arguments))"
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Stop"
    try {
        try {
            $output = & $FileName @Arguments 2>&1
            $exitCode = $LASTEXITCODE
            if ($null -eq $exitCode) {
                $exitCode = 0
            }
        }
        catch {
            $message = $_.Exception.Message
            if ([string]::IsNullOrWhiteSpace($message)) {
                $message = "command failed"
            }
            throw "$FailureMessage`n$message"
        }

        if ($exitCode -ne 0) {
            $outputText = ([string]::Join([Environment]::NewLine, @($output))).Trim()
            if (-not [string]::IsNullOrWhiteSpace($outputText)) {
                throw "$FailureMessage`n$outputText"
            }
            throw $FailureMessage
        }
        return @($output)
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Get-TowerScoutInstallerVenvPython {
    param(
        [Parameter(Mandatory = $true)]
        [string] $VenvDir
    )

    foreach ($relativePath in @("Scripts\python.exe", "bin\python")) {
        $candidate = Join-Path $VenvDir $relativePath
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    throw "The provider virtual environment was created, but no Python executable was found under $VenvDir."
}

function Assert-TowerScoutInstallerPythonVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Python,

        [string] $Requirement = ">=3.9"
    )

    if ($Requirement -ne ">=3.9") {
        throw "Unsupported provider Python requirement '$Requirement'. Expected catalog requirement >=3.9."
    }

    # The provider itself supports 3.9; secure pip bootstrap requires at least 3.10.
    $versionCheck = "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
    Invoke-TowerScoutInstallerCommand `
        -FileName $Python `
        -Arguments @("-c", $versionCheck) `
        -FailureMessage "Secure provider installation requires Python 3.10 or newer. Select the tested 64-bit Python 3.12 prerequisite and retry." | Out-Null
}

$repoRoot = Get-TowerScoutProviderRepoRoot
if ([string]::IsNullOrWhiteSpace($InstallDir)) {
    $InstallDir = Join-Path $repoRoot "tools\podman-compose-provider\$ProviderId"
}
$managedInstallRoot = Join-Path $repoRoot "tools\podman-compose-provider"
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)

$catalog = Get-TowerScoutPodmanComposeProviderCatalog
$provider = @($catalog.providers | Where-Object { [string] $_.id -eq $ProviderId } | Select-Object -First 1)
if ($provider.Count -eq 0) {
    throw "Unknown Podman Compose provider id '$ProviderId'."
}
$provider = $provider[0]
$requiresPython = (Get-TowerScoutProviderObjectValue -InputObject $provider -Name "requires_python").Trim()
if ([string]::IsNullOrWhiteSpace($requiresPython)) {
    $requiresPython = ">=3.9"
}

$sourceUrl = [string] $provider.source_url
$expectedSha256 = ([string] $provider.package_sha256).Trim().ToLowerInvariant()
if ([string]::IsNullOrWhiteSpace($sourceUrl) -or [string]::IsNullOrWhiteSpace($expectedSha256)) {
    throw "Provider '$ProviderId' does not have a download URL and SHA-256 in the approved catalog."
}

$managedInstall = Test-TowerScoutInstallerChildPath -Parent $managedInstallRoot -Child $InstallDir
$existingWrapper = Join-Path $InstallDir "podman-compose.cmd"
if (Test-Path -LiteralPath $InstallDir) {
    if (-not $managedInstall) {
        throw "Existing provider directories may only be replaced inside the managed provider cache: $managedInstallRoot"
    }
    if (-not $Force -and (Test-Path -LiteralPath $existingWrapper -PathType Leaf)) {
        $existingCheck = Test-TowerScoutApprovedPodmanComposeProvider -ProviderPath $existingWrapper -Provider $provider
        if ($existingCheck.Accepted) {
            $existingPython = Get-TowerScoutInstallerVenvPython -VenvDir (Join-Path $InstallDir ".venv")
            Assert-TowerScoutInstallerPythonVersion -Python $existingPython -Requirement $requiresPython
            Invoke-TowerScoutInstallerCommand `
                -FileName $existingPython `
                -Arguments @("-I", (Join-Path $PSScriptRoot "bootstrap-pip.py")) `
                -FailureMessage "Failed to secure pip in the existing provider environment." | Out-Null
            Set-TowerScoutPodmanComposeProviderEnv -ProviderPath $existingWrapper -RootPath $repoRoot -Apply:$Apply | Out-Null
            return
        }
    }
}

Assert-TowerScoutInstallerPythonVersion -Python $Python -Requirement $requiresPython
$installParent = Split-Path -Parent $InstallDir
New-Item -ItemType Directory -Force -Path $installParent | Out-Null
$stageDir = Join-Path $installParent (".towerscout-provider-stage-" + [guid]::NewGuid().ToString("N"))
$backupDir = ""
try {
    New-Item -ItemType Directory -Path $stageDir | Out-Null
    $downloadPath = Join-Path $stageDir ([System.IO.Path]::GetFileName($sourceUrl))
    Write-Host "Downloading approved provider package:"
    Write-Host $sourceUrl
    Invoke-WebRequest -UseBasicParsing -Uri $sourceUrl -OutFile $downloadPath

    $actualSha256 = Get-TowerScoutProviderFileSha256 -Path $downloadPath
    if ($actualSha256 -ne $expectedSha256) {
        throw "Downloaded provider package SHA-256 mismatch. Expected $expectedSha256 but got $actualSha256."
    }
    Write-Host "Provider package SHA-256 verified."

    $venvDir = Join-Path $stageDir ".venv"
    Invoke-TowerScoutInstallerCommand `
        -FileName $Python `
        -Arguments @("-m", "venv", $venvDir) `
        -FailureMessage "Failed to create the provider virtual environment." | Out-Null

    $venvPython = Get-TowerScoutInstallerVenvPython -VenvDir $venvDir
    Invoke-TowerScoutInstallerCommand `
        -FileName $venvPython `
        -Arguments @("-I", (Join-Path $PSScriptRoot "bootstrap-pip.py")) `
        -FailureMessage "Failed to securely bootstrap provider pip; dependencies were not installed." | Out-Null
    $dependencyRequirements = @()
    foreach ($dependency in @($provider.dependencies)) {
        $requirement = (Get-TowerScoutProviderObjectValue -InputObject $dependency -Name "requirement").Trim()
        if (-not [string]::IsNullOrWhiteSpace($requirement)) {
            $dependencyRequirements += $requirement
        }
    }

    $pipInstallArguments = @(
        "-m", "pip", "install", "--disable-pip-version-check",
        "--no-warn-script-location", "--only-binary", ":all:", $downloadPath
    ) + $dependencyRequirements
    Invoke-TowerScoutInstallerCommand `
        -FileName $venvPython `
        -Arguments $pipInstallArguments `
        -FailureMessage "Failed to install the approved Podman Compose provider and its pinned runtime dependencies." | Out-Null

    $stageWrapper = Join-Path $stageDir "podman-compose.cmd"
    @"
@echo off
set "TOWERSCOUT_PODMAN_COMPOSE_PROVIDER_HOME=%~dp0"
"%~dp0.venv\Scripts\python.exe" -c "import podman_compose; podman_compose.main()" %*
"@ | Set-Content -LiteralPath $stageWrapper -Encoding ASCII

    $check = Test-TowerScoutApprovedPodmanComposeProvider -ProviderPath $stageWrapper -Provider $provider
    if (-not $check.Accepted) {
        throw "Installed provider did not pass the approved-provider check: $($check.Reason)"
    }

    if (Test-Path -LiteralPath $InstallDir) {
        $backupDir = Join-Path $installParent (".towerscout-provider-previous-" + [guid]::NewGuid().ToString("N"))
        Move-Item -LiteralPath $InstallDir -Destination $backupDir
    }
    try {
        Move-Item -LiteralPath $stageDir -Destination $InstallDir
    }
    catch {
        if ($backupDir -and (Test-Path -LiteralPath $backupDir) -and -not (Test-Path -LiteralPath $InstallDir)) {
            Move-Item -LiteralPath $backupDir -Destination $InstallDir
        }
        throw
    }
}
finally {
    if (Test-Path -LiteralPath $stageDir) {
        Remove-Item -LiteralPath $stageDir -Recurse -Force
    }
}

if ($backupDir) {
    Write-Host "Previous managed provider state was preserved at $backupDir"
}
Set-TowerScoutPodmanComposeProviderEnv -ProviderPath $existingWrapper -RootPath $repoRoot -Apply:$Apply | Out-Null
