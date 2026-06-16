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
        throw "Unsupported provider Python requirement '$Requirement'. The installer currently enforces >=3.9."
    }

    $versionCheck = "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)"
    Invoke-TowerScoutInstallerCommand `
        -FileName $Python `
        -Arguments @("-c", $versionCheck) `
        -FailureMessage "Podman Compose provider '$ProviderId' requires Python $Requirement. Install Python 3.9 or newer and retry." | Out-Null
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

$sourceUrl = [string] $provider.source_url
$expectedSha256 = ([string] $provider.package_sha256).Trim().ToLowerInvariant()
if ([string]::IsNullOrWhiteSpace($sourceUrl) -or [string]::IsNullOrWhiteSpace($expectedSha256)) {
    throw "Provider '$ProviderId' does not have a download URL and SHA-256 in the approved catalog."
}

if ((Test-Path -LiteralPath $InstallDir) -and -not $Force) {
    throw "Install directory already exists: $InstallDir. Use -Force to replace it."
}

if (Test-Path -LiteralPath $InstallDir) {
    if (-not (Test-TowerScoutInstallerChildPath -Parent $managedInstallRoot -Child $InstallDir)) {
        throw "-Force replacement is only allowed inside the managed provider cache: $managedInstallRoot"
    }
    Remove-Item -LiteralPath $InstallDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

$downloadPath = Join-Path $InstallDir ([System.IO.Path]::GetFileName($sourceUrl))
Write-Host "Downloading approved provider package:"
Write-Host $sourceUrl
Invoke-WebRequest -UseBasicParsing -Uri $sourceUrl -OutFile $downloadPath

$actualSha256 = (Get-FileHash -LiteralPath $downloadPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualSha256 -ne $expectedSha256) {
    throw "Downloaded provider package SHA-256 mismatch. Expected $expectedSha256 but got $actualSha256."
}
Write-Host "Provider package SHA-256 verified."

$requiresPython = (Get-TowerScoutProviderObjectValue -InputObject $provider -Name "requires_python").Trim()
if ([string]::IsNullOrWhiteSpace($requiresPython)) {
    $requiresPython = ">=3.9"
}
Assert-TowerScoutInstallerPythonVersion -Python $Python -Requirement $requiresPython

$venvDir = Join-Path $InstallDir ".venv"
Invoke-TowerScoutInstallerCommand `
    -FileName $Python `
    -Arguments @("-m", "venv", $venvDir) `
    -FailureMessage "Failed to create the provider virtual environment." | Out-Null

$venvPython = Get-TowerScoutInstallerVenvPython -VenvDir $venvDir
$dependencyRequirements = @()
foreach ($dependency in @($provider.dependencies)) {
    $requirement = (Get-TowerScoutProviderObjectValue -InputObject $dependency -Name "requirement").Trim()
    if (-not [string]::IsNullOrWhiteSpace($requirement)) {
        $dependencyRequirements += $requirement
    }
}

$pipInstallArguments = @(
    "-m",
    "pip",
    "install",
    "--disable-pip-version-check",
    "--no-warn-script-location",
    "--only-binary",
    ":all:",
    $downloadPath
) + $dependencyRequirements
Invoke-TowerScoutInstallerCommand `
    -FileName $venvPython `
    -Arguments $pipInstallArguments `
    -FailureMessage "Failed to install the approved Podman Compose provider and its pinned runtime dependencies." | Out-Null

$venvProviderPath = Join-Path $venvDir "Scripts\podman-compose.exe"
if (-not (Test-Path -LiteralPath $venvProviderPath -PathType Leaf)) {
    throw "Provider installation completed, but the expected virtual-environment executable was not found: $venvProviderPath"
}

$wrapperPath = Join-Path $InstallDir "podman-compose.cmd"
@"
@echo off
set "TOWERSCOUT_PODMAN_COMPOSE_PROVIDER_HOME=%~dp0"
"%~dp0.venv\Scripts\podman-compose.exe" %*
"@ | Set-Content -LiteralPath $wrapperPath -Encoding ASCII

$check = Test-TowerScoutApprovedPodmanComposeProvider -ProviderPath $wrapperPath -Provider $provider
if (-not $check.Accepted) {
    throw "Installed provider did not pass the approved-provider check: $($check.Reason)"
}

Set-TowerScoutPodmanComposeProviderEnv -ProviderPath $wrapperPath -RootPath $repoRoot -Apply:$Apply | Out-Null
