param(
    [ValidateSet("cpu", "cuda")]
    [string] $Profile = "cpu",

    [string] $TorchVersion = "2.10.0",

    [string] $TorchvisionVersion = "0.25.0",

    [string] $OutputDirectory = ".agent_work/tmp/task098-qualification",

    [string] $BuildCaBundlePath = "",

    # CUDA wheel index tag used for -Profile cuda (the flavor is derived as cuda<digits>).
    [ValidatePattern('^cu1[0-9]{2}$')]
    [string] $CudaWheelTag = "cu128",

    # TASK-103 pilot mode: run an existing image instead of building one.
    [string] $Image = "",

    # TASK-103 pilot mode: absolute evidence root. When set, phases run one per
    # container and every run gets a unique, never-overwritten directory.
    [string] $EvidenceRoot = "",

    [ValidateSet("", "A", "B", "C", "CTRL")]
    [string] $Stage = "",

    [string] $FixtureDirectory = "",

    [string] $FixtureManifest = "",

    [ValidateSet("identity", "startup", "synthetic", "combined", "memory", "inject")]
    [string[]] $Phases = @("identity", "startup", "synthetic", "combined", "memory", "inject"),

    [string] $RunLabel = "",

    # Combined phase runs YOLO only (palette-tile historical continuity check).
    [switch] $NoSecondary
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Test-TowerScoutPathWithinRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,

        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $directorySeparators = @(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $normalizedPath = [System.IO.Path]::GetFullPath($Path).TrimEnd($directorySeparators)
    $normalizedRoot = [System.IO.Path]::GetFullPath($RootPath).TrimEnd($directorySeparators)
    if (
        [string]::Equals(
            $normalizedPath,
            $normalizedRoot,
            [System.StringComparison]::OrdinalIgnoreCase
        )
    ) {
        return $true
    }

    $rootPrefix = $normalizedRoot + [System.IO.Path]::DirectorySeparatorChar
    return $normalizedPath.StartsWith(
        $rootPrefix,
        [System.StringComparison]::OrdinalIgnoreCase
    )
}

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

$flavor = if ($Profile -eq "cuda") { "cuda" + $CudaWheelTag.Substring(2) } else { "cpu" }
$wheelTag = if ($Profile -eq "cuda") { $CudaWheelTag } else { "cpu" }
$indexUrl = "https://download.pytorch.org/whl/$wheelTag"
$expectedCudaBuild = if ($Profile -eq "cuda") {
    $CudaWheelTag.Substring(2, 2) + "." + $CudaWheelTag.Substring(4)
}
else {
    ""
}
$shortCommit = $sourceCommit.Substring(0, 12)
$safeTorch = $TorchVersion.Replace(".", "-")

if ([string]::IsNullOrWhiteSpace($Image)) {
    $image = "towerscout:task098-$shortCommit-$flavor-torch$safeTorch"

    Write-Host "Building isolated Task-098 image $image"
    Write-Host "Existing containers and images will not be stopped, removed, or reused."
    $dockerBuildArgs = @(
        "build",
        "--pull",
        "--no-cache"
    )
    if (-not [string]::IsNullOrWhiteSpace($BuildCaBundlePath)) {
        if (-not (Test-Path -LiteralPath $BuildCaBundlePath -PathType Leaf)) {
            throw "Build CA bundle was not found: $BuildCaBundlePath"
        }
        $resolvedBuildCa = (Resolve-Path -LiteralPath $BuildCaBundlePath).Path
        if (Test-TowerScoutPathWithinRoot -Path $resolvedBuildCa -RootPath $repoRoot) {
            throw "Build CA bundle must be outside the Docker build context: $repoRoot"
        }
        $dockerBuildArgs += @(
            "--secret",
            "id=towerscout_build_ca,src=$resolvedBuildCa"
        )
        Write-Host "Using a BuildKit secret for the build-time CA bundle."
    }
    $dockerBuildArgs += @(
        "--build-arg", "PYTORCH_INDEX_URL=$indexUrl",
        "--build-arg", "TOWERSCOUT_PYTORCH_FLAVOR=$flavor",
        "--build-arg", "TOWERSCOUT_TORCH_VERSION=$TorchVersion",
        "--build-arg", "TOWERSCOUT_TORCHVISION_VERSION=$TorchvisionVersion",
        "--build-arg", "TOWERSCOUT_RELEASE_VERSION=task098-qualification",
        "--build-arg", "TOWERSCOUT_SOURCE_REF=$sourceCommit",
        "--tag", $image,
        $repoRoot
    )
    & docker @dockerBuildArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Task-098 image build failed."
    }
}
else {
    $image = $Image
    Write-Host "Using existing image $image (no build)."
}

$models = (Resolve-Path (Join-Path $repoRoot "webapp/model_params")).Path

if ([string]::IsNullOrWhiteSpace($EvidenceRoot)) {
    # Original Task-098 single-container qualification.
    $resolvedOutput = [System.IO.Path]::GetFullPath(
        (Join-Path $repoRoot $OutputDirectory)
    )
    [System.IO.Directory]::CreateDirectory($resolvedOutput) | Out-Null
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
    return
}

# ---------------------------------------------------------------------------
# TASK-103 pilot mode: one container per phase, immutable run directory.
# ---------------------------------------------------------------------------
if (-not [System.IO.Path]::IsPathRooted($EvidenceRoot)) {
    throw "-EvidenceRoot must be an absolute path outside the repository."
}
if (Test-TowerScoutPathWithinRoot -Path $EvidenceRoot -RootPath $repoRoot) {
    throw "-EvidenceRoot must be outside the repository: $repoRoot"
}
if ([string]::IsNullOrWhiteSpace($Stage)) {
    throw "-Stage is required with -EvidenceRoot."
}

$imageJson = & docker image inspect $image
if ($LASTEXITCODE -ne 0) {
    throw "Image not found: $image"
}
$imageInfo = ($imageJson | Out-String | ConvertFrom-Json)[0]
$labels = $imageInfo.Config.Labels
$imageRevision = [string] $labels."org.opencontainers.image.revision"
$imageFlavor = [string] $labels."org.towerscout.pytorch.flavor"
$imageIdentityByFlavor = @{
    "cpu" = @{
        wheel_tag = "cpu"
        cuda_build = ""
    }
    "cuda126" = @{
        wheel_tag = "cu126"
        cuda_build = "12.6"
    }
    "cuda128" = @{
        wheel_tag = "cu128"
        cuda_build = "12.8"
    }
}
if (-not $imageIdentityByFlavor.ContainsKey($imageFlavor)) {
    throw "Image $image has missing or unsupported org.towerscout.pytorch.flavor label: '$imageFlavor'"
}
if ([string]::IsNullOrWhiteSpace($Image)) {
    if ($imageFlavor -ne $flavor) {
        throw "Built image flavor label '$imageFlavor' does not match requested flavor '$flavor'."
    }
}
else {
    # Execution device and image package identity are independent. For example,
    # a cuda128 image can be qualified with explicit CPU execution.
    $flavor = $imageFlavor
    $wheelTag = [string] $imageIdentityByFlavor[$imageFlavor].wheel_tag
    $expectedCudaBuild = [string] $imageIdentityByFlavor[$imageFlavor].cuda_build
}
$revisionShort = if ($imageRevision.Length -ge 12) { $imageRevision.Substring(0, 12) } else { $shortCommit }

$fixtureMountSource = ""
$fixtureArgs = @()
if (-not [string]::IsNullOrWhiteSpace($FixtureManifest)) {
    $resolvedManifest = (Resolve-Path -LiteralPath $FixtureManifest).Path
    $fixtureMountSource = Split-Path -Parent $resolvedManifest
    # Build the container path first: inside @(...) the comma operator binds tighter than +,
    # which would split "/fixtures/" and the file name into separate arguments.
    $containerManifest = "/fixtures/" + (Split-Path -Leaf $resolvedManifest)
    $fixtureArgs = @("--fixture-manifest", $containerManifest)
}
elseif (-not [string]::IsNullOrWhiteSpace($FixtureDirectory)) {
    $fixtureMountSource = (Resolve-Path -LiteralPath $FixtureDirectory).Path
    $fixtureArgs = @("--fixture-dir", "/fixtures")
}
if ($NoSecondary) {
    $fixtureArgs += @("--no-secondary")
}
$needsFixtures = @($Phases | Where-Object { $_ -in @("combined", "memory", "inject") }).Count -gt 0
if ($needsFixtures -and [string]::IsNullOrWhiteSpace($fixtureMountSource)) {
    throw "Phases combined/memory/inject need -FixtureManifest or -FixtureDirectory."
}

$hostName = $env:COMPUTERNAME.ToLowerInvariant()
$timestamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$runId = "{0}_{1}_docker_{2}_{3}_torch{4}_{5}" -f $timestamp, $hostName, $Stage, $flavor, $safeTorch, $revisionShort
if (-not [string]::IsNullOrWhiteSpace($RunLabel)) {
    $runId = "$runId`_$RunLabel"
}
$runDirectory = Join-Path (Join-Path $EvidenceRoot "runs") $runId
if (Test-Path -LiteralPath $runDirectory) {
    throw "Run directory already exists; evidence is never overwritten: $runDirectory"
}
[System.IO.Directory]::CreateDirectory($runDirectory) | Out-Null

$qualificationFiles = @(
    "task103_pilot_probe.py",
    "task098_ml_qualification.py",
    "task091_combined_contract.py"
)
$sourceHashes = [ordered]@{}
$mountArgs = @(
    "--mount", "type=bind,source=$models,target=/app/webapp/model_params,readonly",
    "--mount", "type=bind,source=$runDirectory,target=/evidence"
)
foreach ($file in $qualificationFiles) {
    $path = (Resolve-Path (Join-Path $repoRoot "scripts/$file")).Path
    $sourceHashes[$file] = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    $mountArgs += @("--mount", "type=bind,source=$path,target=/qualification/$file,readonly")
}
if (-not [string]::IsNullOrWhiteSpace($fixtureMountSource)) {
    $mountArgs += @("--mount", "type=bind,source=$fixtureMountSource,target=/fixtures,readonly")
}

$startedUtc = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$phaseResults = [ordered]@{}
foreach ($phase in $Phases) {
    $dockerArgs = @(
        "run",
        "--rm",
        "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=1g",
        "--tmpfs", "/app/webapp/cache:rw,noexec,nosuid,size=64m",
        "--tmpfs", "/app/webapp/config:rw,noexec,nosuid,size=16m",
        "--tmpfs", "/app/webapp/logs:rw,noexec,nosuid,size=64m",
        "--tmpfs", "/app/webapp/temp:rw,noexec,nosuid,size=64m",
        "--tmpfs", "/app/webapp/uploads:rw,noexec,nosuid,size=64m"
    ) + $mountArgs + @(
        "--env", "TOWERSCOUT_DEVICE=$Profile",
        "--env", "MPLCONFIGDIR=/tmp/matplotlib",
        "--env", "YOLO_CONFIG_DIR=/tmp/ultralytics",
        "--env", "TASK103_EXPECTED_TORCH=$TorchVersion",
        "--env", "TASK103_EXPECTED_TORCHVISION=$TorchvisionVersion",
        "--env", "TASK103_EXPECTED_CUDA_BUILD=$expectedCudaBuild",
        "--env", "TASK103_EXPECTED_WHEEL_TAG=$wheelTag",
        "--env", "TASK103_STAGE=$Stage",
        "--env", "TASK103_RUN_ID=$runId"
    )
    if ($Profile -eq "cuda") {
        $dockerArgs += @("--gpus", "all")
    }
    $dockerArgs += @($image, "python", "/qualification/task103_pilot_probe.py", "--phase", $phase, "--output", "/evidence/$phase.json") + $fixtureArgs

    Write-Host "[$runId] phase $phase ..."
    $phaseLog = Join-Path $runDirectory "$phase.log"
    $phaseStarted = [DateTime]::UtcNow
    # Native stderr must not become a terminating error; keep logs as UTF-8 text.
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & docker @dockerArgs 2>&1 | ForEach-Object { "$_" } | Out-File -LiteralPath $phaseLog -Encoding utf8
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference
    $phaseResults[$phase] = [ordered]@{
        exit_code = $exitCode
        file = "$phase.json"
        log = "$phase.log"
        seconds = [math]::Round(([DateTime]::UtcNow - $phaseStarted).TotalSeconds, 3)
    }
    Write-Host "[$runId] phase $phase exit=$exitCode"
}

$driver = ""
if ($Profile -eq "cuda") {
    $driver = (& nvidia-smi --query-gpu=name,driver_version --format=csv,noheader) -join "; "
}
$run = [ordered]@{
    schema_version = 1
    run_id = $runId
    stage = $Stage
    host = $hostName
    engine = "docker"
    profile = $Profile
    flavor = $flavor
    expected = [ordered]@{
        torch = $TorchVersion
        torchvision = $TorchvisionVersion
        cuda_build = if ($expectedCudaBuild) { $expectedCudaBuild } else { $null }
        wheel_tag = $wheelTag
    }
    image = [ordered]@{
        ref = $image
        id = $imageInfo.Id
        size_bytes = $imageInfo.Size
        labels = $labels
        label_flavor = $imageFlavor
        label_revision = $imageRevision
    }
    source = [ordered]@{
        worktree_head = $sourceCommit
        probe_sha256 = $sourceHashes["task103_pilot_probe.py"]
        legacy_probe_sha256 = $sourceHashes["task098_ml_qualification.py"]
        contract_sha256 = $sourceHashes["task091_combined_contract.py"]
    }
    fixture_manifest_sha256 = if ($resolvedManifest) { (Get-FileHash -LiteralPath $resolvedManifest -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
    fixture_source = $fixtureMountSource
    phases = $phaseResults
    host_info = [ordered]@{
        docker_server = (& docker version --format "{{.Server.Version}}")
        gpu_driver = $driver
    }
    started_utc = $startedUtc
    finished_utc = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
}
$run | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $runDirectory "run.json") -Encoding UTF8

$failed = @($phaseResults.Keys | Where-Object { $phaseResults[$_].exit_code -ne 0 })
Write-Host "Run directory: $runDirectory"
if ($failed.Count -gt 0) {
    Write-Host "Failed phases: $($failed -join ', ')"
    exit 1
}
Write-Host "All phases passed."
exit 0
