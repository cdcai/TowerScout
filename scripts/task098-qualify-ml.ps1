param(
    [ValidateSet("cpu", "cuda")]
    [string] $Profile = "cpu",

    [string] $TorchVersion = "2.6.0",

    [string] $TorchvisionVersion = "0.21.0",

    [string] $OutputDirectory = ".agent_work/tmp/task098-qualification"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$trackedChanges = & git -C $repoRoot status --porcelain --untracked-files=no
if ($LASTEXITCODE -ne 0) {
    throw "Could not read the TowerScout git worktree state."
}
if ($trackedChanges) {
    throw "Task-098 qualification requires a clean tracked worktree."
}

$sourceCommit = (& git -C $repoRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($sourceCommit)) {
    throw "Could not resolve the TowerScout source commit."
}

& docker info --format "{{.ServerVersion}}" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop is not available."
}

$flavor = if ($Profile -eq "cuda") { "cuda126" } else { "cpu" }
$indexUrl = if ($Profile -eq "cuda") {
    "https://download.pytorch.org/whl/cu126"
}
else {
    "https://download.pytorch.org/whl/cpu"
}
$shortCommit = $sourceCommit.Substring(0, 12)
$safeTorch = $TorchVersion.Replace(".", "-")
$image = "towerscout:task098-$shortCommit-$flavor-torch$safeTorch"

Write-Host "Building isolated Task-098 image $image"
Write-Host "Existing containers and images will not be stopped, removed, or reused."
& docker build `
    --pull `
    --no-cache `
    --build-arg "PYTORCH_INDEX_URL=$indexUrl" `
    --build-arg "TOWERSCOUT_PYTORCH_FLAVOR=$flavor" `
    --build-arg "TOWERSCOUT_TORCH_VERSION=$TorchVersion" `
    --build-arg "TOWERSCOUT_TORCHVISION_VERSION=$TorchvisionVersion" `
    --build-arg "TOWERSCOUT_RELEASE_VERSION=task098-qualification" `
    --build-arg "TOWERSCOUT_SOURCE_REF=$sourceCommit" `
    --tag $image `
    $repoRoot
if ($LASTEXITCODE -ne 0) {
    throw "Task-098 image build failed."
}

$resolvedOutput = [System.IO.Path]::GetFullPath(
    (Join-Path $repoRoot $OutputDirectory)
)
[System.IO.Directory]::CreateDirectory($resolvedOutput) | Out-Null
$models = (Resolve-Path (Join-Path $repoRoot "webapp/model_params")).Path
$probe = (Resolve-Path (Join-Path $repoRoot "scripts/task098_ml_qualification.py")).Path

$dockerArgs = @(
    "run",
    "--rm",
    "--read-only",
    "--tmpfs", "/tmp:rw,noexec,nosuid,size=512m",
    "--tmpfs", "/app/webapp/cache:rw,noexec,nosuid,size=64m",
    "--tmpfs", "/app/webapp/config:rw,noexec,nosuid,size=16m",
    "--tmpfs", "/app/webapp/logs:rw,noexec,nosuid,size=64m",
    "--tmpfs", "/app/webapp/temp:rw,noexec,nosuid,size=64m",
    "--mount", "type=bind,source=$models,target=/app/webapp/model_params,readonly",
    "--mount", "type=bind,source=$probe,target=/qualification/task098_ml_qualification.py,readonly",
    "--mount", "type=bind,source=$resolvedOutput,target=/evidence",
    "--env", "TOWERSCOUT_DEVICE=$Profile",
    "--env", "TOWERSCOUT_PYTORCH_FLAVOR=$flavor",
    "--env", "MPLCONFIGDIR=/tmp/matplotlib",
    "--env", "YOLO_CONFIG_DIR=/tmp/ultralytics",
    "--env", "TASK098_EXPECTED_TORCH=$TorchVersion",
    "--env", "TASK098_EXPECTED_TORCHVISION=$TorchvisionVersion",
    "--env", "TASK098_SOURCE_COMMIT=$sourceCommit",
    "--env", "TASK098_IMAGE=$image"
)
if ($Profile -eq "cuda") {
    $dockerArgs += @("--gpus", "all")
}
$dockerArgs += @($image, "python", "/qualification/task098_ml_qualification.py")

& docker @dockerArgs
if ($LASTEXITCODE -ne 0) {
    throw "Task-098 $Profile qualification failed."
}

$evidencePath = Join-Path $resolvedOutput "qualification.json"
if (-not (Test-Path -LiteralPath $evidencePath -PathType Leaf)) {
    throw "Task-098 qualification did not produce $evidencePath."
}
$evidence = Get-Content -LiteralPath $evidencePath -Raw | ConvertFrom-Json
if (-not $evidence.passed) {
    throw "Task-098 qualification evidence reports failure."
}
Write-Host "Task-098 $Profile qualification passed."
Write-Host "Sanitized evidence: $evidencePath"
