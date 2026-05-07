param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [string] $Source = "assets",

    [switch] $Build,

    [switch] $VerifyHashes
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

$repoRoot = Get-TowerScoutRepoRoot
$sourcePath = Resolve-Path -LiteralPath (Join-Path $repoRoot $Source) -ErrorAction SilentlyContinue
if ($null -eq $sourcePath) {
    $sourcePath = Resolve-Path -LiteralPath $Source -ErrorAction SilentlyContinue
}
if ($null -eq $sourcePath) {
    throw "Asset source '$Source' was not found."
}

$assetRoot = $sourcePath.Path
$modelSource = Join-Path $assetRoot "model_params"
$dataSource = Join-Path $assetRoot "data"

if (-not (Test-Path -LiteralPath $modelSource -PathType Container)) {
    throw "Asset source is missing required model_params directory: $modelSource"
}
if (-not (Test-Path -LiteralPath $dataSource -PathType Container)) {
    throw "Asset source is missing required data directory: $dataSource"
}

Write-Host "Starting TowerScout container so named volumes are available..."
Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @("up", "-d", "towerscout")
if ($script:TowerScoutComposeExitCode -ne 0) {
    exit $script:TowerScoutComposeExitCode
}

Write-Host "Importing model assets from $modelSource..."
Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @(
    "cp",
    (Join-Path $modelSource "."),
    "towerscout:/app/webapp/model_params/"
)
if ($script:TowerScoutComposeExitCode -ne 0) {
    exit $script:TowerScoutComposeExitCode
}

Write-Host "Importing data assets from $dataSource..."
Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @(
    "cp",
    (Join-Path $dataSource "."),
    "towerscout:/app/webapp/data/"
)
if ($script:TowerScoutComposeExitCode -ne 0) {
    exit $script:TowerScoutComposeExitCode
}

$verifyArg = if ($VerifyHashes) { "True" } else { "False" }
$python = "import ts_assets; s=ts_assets.build_asset_status(verify_hashes=$verifyArg); print('asset_status=' + s['status']); print('verify_hashes=' + str(s['verify_hashes'])); print('missing=' + ','.join(s['missing'])); print('corrupt=' + ','.join(s['corrupt'])); print('optional_missing=' + ','.join(s['optional_missing'])); raise SystemExit(0 if s['status'] == 'ok' else 1)"

Write-Host "Verifying imported assets with TowerScout manifest..."
Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @(
    "exec",
    "-T",
    "towerscout",
    "python",
    "-c",
    $python
)
exit $script:TowerScoutComposeExitCode
