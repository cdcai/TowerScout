[CmdletBinding()]
param(
    [ValidateSet("docker", "podman")]
    [string] $Engine = "docker",

    [ValidateSet("off", "auto", "on")]
    [string] $Gpu = "off",

    [int] $Port = 5000,

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

. (Join-Path $PSScriptRoot "lib\TowerScoutCompose.ps1")
. (Join-Path $PSScriptRoot "lib\TowerScoutBootstrap.ps1")

$repoRoot = Get-TowerScoutRepoRoot

Write-Host "TowerScout setup"
Write-Host "Engine: $Engine"
Write-Host "GPU: $Gpu"
Write-Host "Port: $Port"

$resolvedAssetZip = ""
if (-not $SkipAssetImport) {
    $resolvedAssetZip = Find-TowerScoutSetupAssetZip -RootPath $repoRoot -AssetZip $AssetZip
    Write-Host "Model & Data Package ZIP: $resolvedAssetZip"
}
else {
    Write-Host "Model & Data Package import: skipped"
}

$resolvedPackageZip = Find-TowerScoutSetupPackageZip -RootPath $repoRoot -PackageZip $PackageZip
if (-not [string]::IsNullOrWhiteSpace($resolvedPackageZip)) {
    Write-Host "Application Package ZIP: $resolvedPackageZip"
}

$bootstrapScript = Join-Path $PSScriptRoot "bootstrap.ps1"
$bootstrapParams = @{
    Engine = $Engine
    Port = $Port
    Gpu = $Gpu
    TimeoutSeconds = $TimeoutSeconds
    RestartWaitSeconds = $RestartWaitSeconds
    SessionMaxHours = $SessionMaxHours
    AssetsPath = $AssetsPath
    MinimumFreeGB = $MinimumFreeGB
}

if (-not [string]::IsNullOrWhiteSpace($resolvedAssetZip)) {
    $bootstrapParams["AssetZip"] = $resolvedAssetZip
}
if (-not [string]::IsNullOrWhiteSpace($resolvedPackageZip)) {
    $bootstrapParams["PackageZip"] = $resolvedPackageZip
}
if ($VerifyOnly) {
    $bootstrapParams["VerifyOnly"] = $true
}
if ($NoBrowser) {
    $bootstrapParams["NoBrowser"] = $true
}
if ($SkipAssetImport) {
    $bootstrapParams["SkipAssetImport"] = $true
}

& $bootstrapScript @bootstrapParams
exit $LASTEXITCODE
