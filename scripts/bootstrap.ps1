param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [int] $Port = $(if ($env:TOWERSCOUT_PORT) { [int] $env:TOWERSCOUT_PORT } else { 5000 }),

    [ValidateSet("off", "auto", "on")]
    [string] $Gpu = "off",

    [int] $TimeoutSeconds = 180,

    [int] $RestartWaitSeconds = 180,

    [int] $SessionMaxHours = 12,

    [string] $AssetsPath = "assets",

    [string] $AssetZip = "",

    [string] $PackageZip = "",

    [int] $MinimumFreeGB = 15,

    [switch] $VerifyOnly,

    [switch] $NoBrowser,

    [switch] $SkipAssetImport
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"
. "$PSScriptRoot\lib\TowerScoutBootstrap.ps1"

if ($TimeoutSeconds -lt 5) {
    throw "TimeoutSeconds must be at least 5."
}
if ($RestartWaitSeconds -lt 5) {
    throw "RestartWaitSeconds must be at least 5."
}
if ($SessionMaxHours -lt 0) {
    throw "SessionMaxHours must be 0 or greater."
}

$repoRoot = Get-TowerScoutRepoRoot
$resolvedAssetsPath = Resolve-TowerScoutBootstrapPath -RootPath $repoRoot -Path $AssetsPath

Write-Host "TowerScout bootstrap preflight"
Write-Host "Package folder: $repoRoot"
Write-Host "Assets folder: $resolvedAssetsPath"
Write-Host ""

Test-TowerScoutReleaseHandoff -RootPath $repoRoot

if (-not [string]::IsNullOrWhiteSpace($PackageZip)) {
    $resolvedPackageZip = Resolve-TowerScoutBootstrapPath -RootPath $repoRoot -Path $PackageZip
    Test-TowerScoutChecksumSidecar -ArtifactPath $resolvedPackageZip | Out-Null
}

$resolvedAssetZip = ""
if (-not [string]::IsNullOrWhiteSpace($AssetZip)) {
    $resolvedAssetZip = Resolve-TowerScoutBootstrapPath -RootPath $repoRoot -Path $AssetZip
    Test-TowerScoutChecksumSidecar -ArtifactPath $resolvedAssetZip | Out-Null
    Test-TowerScoutAssetZipLayout -ZipPath $resolvedAssetZip | Out-Null
    Test-TowerScoutAssetZipReleaseMatch -RootPath $repoRoot -ZipPath $resolvedAssetZip
}

$hasExistingStagedAssets = Test-TowerScoutStagedAssets -RootPath $repoRoot -AssetsPath $resolvedAssetsPath
$effectiveEngine = Resolve-TowerScoutBootstrapEngine -Engine $Engine -Port $Port -RootPath $repoRoot -MinimumFreeGB $MinimumFreeGB
Write-TowerScoutImagePullReadiness -RootPath $repoRoot -Engine $effectiveEngine

if ($VerifyOnly) {
    Write-Host ""
    Write-Host "Verify-only preflight passed. No assets were imported and TowerScout was not started."
    if (-not [string]::IsNullOrWhiteSpace($resolvedAssetZip)) {
        Write-Host "Asset ZIP was verified but not staged because -VerifyOnly was used."
    }
    elseif ($hasExistingStagedAssets) {
        Write-Host "Staged assets are present and ready for import."
    }
    else {
        Write-Host "No staged assets were found. TowerScout can start, but readiness may be degraded until assets are imported."
    }
    exit 0
}

if (-not [string]::IsNullOrWhiteSpace($resolvedAssetZip)) {
    Expand-TowerScoutAssetZip -RootPath $repoRoot -ZipPath $resolvedAssetZip -AssetsPath $resolvedAssetsPath
}

$hasStagedAssets = Test-TowerScoutStagedAssets -RootPath $repoRoot -AssetsPath $resolvedAssetsPath

if ($hasStagedAssets -and -not $SkipAssetImport) {
    Write-Host ""
    Write-Host "Importing staged assets with hash verification enabled..."
    & (Join-Path $PSScriptRoot "import-assets.ps1") `
        -Engine $effectiveEngine `
        -Source $resolvedAssetsPath `
        -Port $Port `
        -Gpu $Gpu `
        -RestartWaitSeconds $RestartWaitSeconds `
        -SessionMaxHours $SessionMaxHours `
        -VerifyHashes
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
elseif ($hasStagedAssets -and $SkipAssetImport) {
    Write-Host ""
    Write-Host "Staged assets were found, but asset import was skipped by request."
}
else {
    Write-Host ""
    Write-Host "No staged assets were found. TowerScout will start, but readiness may be degraded until assets are imported."
}

Write-Host ""
Write-Host "Starting TowerScout after preflight..."
& (Join-Path $PSScriptRoot "launch.ps1") `
    -Engine $effectiveEngine `
    -Port $Port `
    -Gpu $Gpu `
    -TimeoutSeconds $TimeoutSeconds `
    -SessionMaxHours $SessionMaxHours `
    -NoBrowser:$NoBrowser
exit $LASTEXITCODE
