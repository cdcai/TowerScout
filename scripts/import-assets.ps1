param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [string] $Source = "assets",

    [int] $Port = $(if ($env:TOWERSCOUT_PORT) { [int] $env:TOWERSCOUT_PORT } else { 5000 }),

    [ValidateSet("off", "auto", "on")]
    [string] $Gpu = "off",

    [int] $RestartWaitSeconds = 120,

    [int] $SessionMaxHours = 12,

    [switch] $Build,

    [switch] $VerifyHashes
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

if ($SessionMaxHours -lt 0) {
    throw "SessionMaxHours must be 0 or greater."
}

$repoRoot = Get-TowerScoutRepoRoot
Initialize-TowerScoutEnvFile -RootPath $repoRoot
$env:TOWERSCOUT_PORT = "$Port"
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
$composeCommand = Get-TowerScoutComposeCommand -Engine $Engine
$effectiveEngine = [string] $composeCommand["Executable"]
Set-TowerScoutGpuEnvironment -Gpu $Gpu -Build:$Build
Invoke-TowerScoutStaleContainerGuard -EngineName $effectiveEngine -SessionMaxHours $SessionMaxHours | Out-Null
Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @("up", "-d", "towerscout")
if ($script:TowerScoutComposeExitCode -ne 0) {
    exit $script:TowerScoutComposeExitCode
}

Write-Host "Importing model assets from $modelSource..."
Copy-TowerScoutContainerPath `
    -Engine $Engine `
    -Build:$Build `
    -Gpu $Gpu `
    -LocalPath (Join-Path $modelSource ".") `
    -ContainerPath "/app/webapp/model_params/"
if ($script:TowerScoutComposeExitCode -ne 0) {
    exit $script:TowerScoutComposeExitCode
}

Write-Host "Importing data assets from $dataSource..."
Copy-TowerScoutContainerPath `
    -Engine $Engine `
    -Build:$Build `
    -Gpu $Gpu `
    -LocalPath (Join-Path $dataSource ".") `
    -ContainerPath "/app/webapp/data/"
if ($script:TowerScoutComposeExitCode -ne 0) {
    exit $script:TowerScoutComposeExitCode
}

Write-Host "Restarting TowerScout so imported model assets are discovered..."
Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
    "restart",
    "towerscout"
)
if ($script:TowerScoutComposeExitCode -ne 0) {
    exit $script:TowerScoutComposeExitCode
}

Write-Host "Waiting for TowerScout to reload imported assets..."
$waitPython = @'
import json
import sys
import time
import urllib.request

timeout_seconds = int(sys.argv[1])
deadline = time.time() + timeout_seconds
last_status = str()


def get_json(path):
    with urllib.request.urlopen('http://127.0.0.1:5000' + path, timeout=3) as response:
        return json.load(response)


while time.time() < deadline:
    try:
        health = get_json('/api/health')
        readiness = get_json('/api/readiness')
        engines = get_json('/getengines')
        assets = readiness.get('components', {}).get('assets', {})
        health_status = health.get('status')
        readiness_state = readiness.get('state')
        asset_status = assets.get('status')
        engine_count = len(engines) if isinstance(engines, list) else 0
        last_status = 'health={} state={} asset_status={} engine_count={}'.format(
            health_status,
            readiness_state,
            asset_status,
            engine_count,
        )
        if health_status == 'ok' and asset_status == 'ok' and engine_count > 0:
            print('post_import_' + last_status)
            raise SystemExit(0)
    except Exception as exc:
        last_status = f'{type(exc).__name__}: {exc}'
    time.sleep(2)

print('post_import_wait_error=' + last_status)
raise SystemExit(1)
'@
Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
    "exec",
    "-T",
    "towerscout",
    "python",
    "-c",
    $waitPython,
    "$RestartWaitSeconds"
)
if ($script:TowerScoutComposeExitCode -ne 0) {
    exit $script:TowerScoutComposeExitCode
}

$verifyArg = if ($VerifyHashes) { "True" } else { "False" }
$python = "import ts_assets; s=ts_assets.build_asset_status(verify_hashes=$verifyArg); print('asset_status=' + s['status']); print('verify_hashes=' + str(s['verify_hashes'])); print('missing=' + ','.join(s['missing'])); print('corrupt=' + ','.join(s['corrupt'])); print('optional_missing=' + ','.join(s['optional_missing'])); raise SystemExit(0 if s['status'] == 'ok' else 1)"

Write-Host "Verifying imported assets with TowerScout manifest..."
Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
    "exec",
    "-T",
    "towerscout",
    "python",
    "-c",
    $python
)
exit $script:TowerScoutComposeExitCode
