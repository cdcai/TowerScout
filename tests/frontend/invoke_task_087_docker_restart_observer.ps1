param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^towerscout-task087-[a-z0-9][a-z0-9-]*$")]
    [string] $ProjectName,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 65535)]
    [int] $AppPort,

    [Parameter(Mandatory = $true)]
    [string] $EdgePath,

    [ValidateRange(30, 600)]
    [int] $TimeoutSeconds = 180,

    [ValidateSet("setup_required", "degraded", "ready")]
    [string] $ExpectedReadinessState = "setup_required"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$composePath = Join-Path $repoRoot "compose.yaml"
$observerPath = Join-Path $PSScriptRoot "test_task_087_docker_restart_edge_observer.js"
$resolvedEdgePath = (Resolve-Path -LiteralPath $EdgePath).Path
if ([System.IO.Path]::GetFileName($resolvedEdgePath).ToLowerInvariant() -ne "msedge.exe") {
    throw "EdgePath must identify msedge.exe."
}

$docker = Get-Command "docker.exe" -CommandType Application -ErrorAction Stop
$node = Get-Command "node.exe" -CommandType Application -ErrorAction Stop
$taskkill = Get-Command "taskkill.exe" -CommandType Application -ErrorAction Stop

function Stop-Task087ProcessTree {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process] $Process,

        [int] $TimeoutMilliseconds = 10000
    )

    if ($Process.HasExited) {
        return
    }

    & $taskkill.Source /PID $Process.Id /T /F 2>$null | Out-Null
    $taskkillExitCode = $LASTEXITCODE
    try {
        $Process.Refresh()
    }
    catch {
        # The verified wait below is authoritative.
    }
    $nativeTerminationVerified = $taskkillExitCode -eq 0 -and $Process.HasExited
    if (-not $nativeTerminationVerified -and -not $Process.HasExited) {
        try {
            $Process.Kill()
        }
        catch {
            # The verified wait below decides whether cleanup succeeded.
        }
    }

    $exited = $Process.HasExited
    if (-not $exited) {
        try {
            $exited = $Process.WaitForExit($TimeoutMilliseconds)
        }
        catch {
            $exited = $false
        }
    }
    if (-not $exited) {
        try {
            $Process.Refresh()
            $exited = $Process.HasExited
        }
        catch {
            $exited = $false
        }
    }
    if (-not $exited) {
        throw "A Task-087 review process tree did not exit within the cleanup timeout."
    }
}

function Get-Task087ContainerId {
    $ids = @(
        & $docker.Source ps -a `
            --filter "label=com.docker.compose.project=$ProjectName" `
            --filter "label=com.docker.compose.service=towerscout" `
            --format "{{.ID}}"
    )
    if ($LASTEXITCODE -ne 0) {
        throw "Docker could not inspect the dedicated Task-087 project."
    }
    $ids = @($ids | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($ids.Count -ne 1) {
        throw "Expected exactly one towerscout container in project '$ProjectName'; found $($ids.Count)."
    }
    return ([string] $ids[0]).Trim()
}

function Assert-Task087ContainerIdentity {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ContainerId,

        [switch] $RequireRunning
    )

    $inspectOutput = @(& $docker.Source inspect $ContainerId)
    if ($LASTEXITCODE -ne 0) {
        throw "Docker could not inspect the dedicated Task-087 container."
    }
    try {
        $inspection = @(($inspectOutput -join [Environment]::NewLine) | ConvertFrom-Json)
    }
    catch {
        throw "Docker returned invalid inspection data for the dedicated Task-087 container."
    }
    $projectLabel = [string] $inspection[0].Config.Labels."com.docker.compose.project"
    $serviceLabel = [string] $inspection[0].Config.Labels."com.docker.compose.service"
    $isRunning = [bool] $inspection[0].State.Running
    if (
        $projectLabel -ne $ProjectName -or
        $serviceLabel -ne "towerscout" -or
        $isRunning -ne [bool] $RequireRunning
    ) {
        throw "The Docker container identity or running state did not match the requested Task-087 project."
    }
}

$containerId = Get-Task087ContainerId
Assert-Task087ContainerIdentity -ContainerId $containerId -RequireRunning
$publishedPort = @(& $docker.Source port $containerId "5000/tcp")
if (
    $LASTEXITCODE -ne 0 -or
    $publishedPort.Count -ne 1 -or
    ([string] $publishedPort[0]).Trim() -ne "127.0.0.1:$AppPort"
) {
    throw "The dedicated container must publish 127.0.0.1:$AppPort to container port 5000."
}

$runId = [guid]::NewGuid().ToString("N")
$runStartedAtUtc = [datetime]::UtcNow
$signalPath = Join-Path ([System.IO.Path]::GetTempPath()) "towerscout-task087-$runId.ready"
$browserPidPath = Join-Path ([System.IO.Path]::GetTempPath()) "towerscout-task087-$runId.edge-pid"
$browserProfilePath = Join-Path ([System.IO.Path]::GetTempPath()) "towerscout-task087-$runId-edge-profile"
$stdoutPath = Join-Path ([System.IO.Path]::GetTempPath()) "towerscout-task087-$runId.stdout"
$stderrPath = Join-Path ([System.IO.Path]::GetTempPath()) "towerscout-task087-$runId.stderr"
$environmentNames = @(
    "TOWERSCOUT_BASE_URL",
    "TOWERSCOUT_ALT_BASE_URL",
    "TOWERSCOUT_EXECUTABLE_PATH",
    "TOWERSCOUT_BROWSER_READY_SIGNAL",
    "TOWERSCOUT_BROWSER_PID_SIGNAL",
    "TOWERSCOUT_BROWSER_PROFILE_DIR",
    "TOWERSCOUT_RESTART_TRANSITION_TIMEOUT_MS",
    "TOWERSCOUT_EXPECTED_READINESS_STATE"
)
$savedEnvironment = @{}
foreach ($environmentName in $environmentNames) {
    $savedEnvironment[$environmentName] = [pscustomobject]@{
        Exists = Test-Path "Env:$environmentName"
        Value = [System.Environment]::GetEnvironmentVariable($environmentName, "Process")
    }
}

$observer = $null
$serviceNeedsRestore = $false
$primaryError = $null
$observerOutput = ""
$cleanupErrors = New-Object System.Collections.Generic.List[string]
try {
    New-Item -ItemType Directory -Path $browserProfilePath -ErrorAction Stop | Out-Null
    $env:TOWERSCOUT_BASE_URL = "http://localhost:$AppPort"
    $env:TOWERSCOUT_ALT_BASE_URL = "http://127.0.0.1:$AppPort"
    $env:TOWERSCOUT_EXECUTABLE_PATH = $resolvedEdgePath
    $env:TOWERSCOUT_BROWSER_READY_SIGNAL = $signalPath
    $env:TOWERSCOUT_BROWSER_PID_SIGNAL = $browserPidPath
    $env:TOWERSCOUT_BROWSER_PROFILE_DIR = $browserProfilePath
    $env:TOWERSCOUT_RESTART_TRANSITION_TIMEOUT_MS = [string] ($TimeoutSeconds * 1000)
    $env:TOWERSCOUT_EXPECTED_READINESS_STATE = $ExpectedReadinessState

    $observerArgument = '"{0}"' -f $observerPath
    $observer = Start-Process `
        -FilePath $node.Source `
        -ArgumentList @($observerArgument) `
        -WorkingDirectory $repoRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath `
        -PassThru

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while (-not (Test-Path -LiteralPath $signalPath)) {
        if ($observer.HasExited) {
            throw "The Edge observer exited before it signaled browser readiness."
        }
        if ((Get-Date) -ge $deadline) {
            throw "Timed out waiting for the Edge observer readiness signal."
        }
        Start-Sleep -Milliseconds 250
    }
    if ($observer.HasExited) {
        throw "The Edge observer exited before Docker restart orchestration began."
    }

    $serviceNeedsRestore = $true
    & $docker.Source compose -p $ProjectName -f $composePath stop towerscout
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose could not stop the dedicated Task-087 service."
    }
    Assert-Task087ContainerIdentity -ContainerId $containerId

    & $docker.Source compose -p $ProjectName -f $composePath start towerscout
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose could not restart the dedicated Task-087 service."
    }
    $restartedContainerId = Get-Task087ContainerId
    if ($restartedContainerId -ne $containerId) {
        throw "Docker Compose replaced the dedicated container instead of restarting the verified instance."
    }
    Assert-Task087ContainerIdentity -ContainerId $containerId -RequireRunning
    $serviceNeedsRestore = $false

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while (-not $observer.HasExited) {
        if ((Get-Date) -ge $deadline) {
            throw "Timed out waiting for the Edge observer to complete."
        }
        Start-Sleep -Milliseconds 250
    }
    $observer.WaitForExit()
    $observerExitCode = [int] $observer.ExitCode
    if ($observerExitCode -ne 0) {
        $observerFailureState = "observer_failed"
        $observerStderr = Get-Content -LiteralPath $stderrPath -Raw -ErrorAction SilentlyContinue
        if ($observerStderr -match "sessionStorage") {
            $observerFailureState = "session_storage_not_preserved"
        }
        elseif ($observerStderr -match "Unexpected readiness state") {
            $observerFailureState = "readiness_state_mismatch"
        }
        elseif ($observerStderr -match "Timed out waiting for") {
            $observerFailureState = "restart_transition_timeout"
        }
        throw "The Edge observer failed with exit code $observerExitCode ($observerFailureState)."
    }
    $observerOutput = Get-Content -LiteralPath $stdoutPath -Raw
}
catch {
    $primaryError = $_
}
finally {
    if ($null -ne $observer) {
        try {
            Stop-Task087ProcessTree -Process $observer
        }
        catch {
            $cleanupErrors.Add($_.Exception.Message) | Out-Null
        }
        finally {
            try {
                $observer.Dispose()
            }
            catch {
                $cleanupErrors.Add("The Task-087 observer process handle could not be released.") | Out-Null
            }
        }
    }

    if (Test-Path -LiteralPath $browserPidPath -PathType Leaf) {
        try {
            [int] $browserPid = 0
            if (
                -not [int]::TryParse(
                    (Get-Content -LiteralPath $browserPidPath -Raw),
                    [ref] $browserPid
                ) -or
                $browserPid -lt 1
            ) {
                throw "The Task-087 Edge PID signal was invalid."
            }
            $browserProcess = Get-Process -Id $browserPid -ErrorAction SilentlyContinue
            if ($null -ne $browserProcess) {
                try {
                    if (
                        $browserProcess.ProcessName -ne "msedge" -or
                        $browserProcess.StartTime.ToUniversalTime() -lt $runStartedAtUtc.AddSeconds(-5)
                    ) {
                        throw "The Task-087 Edge PID signal did not identify this review run."
                    }
                    Stop-Task087ProcessTree -Process $browserProcess
                }
                finally {
                    try {
                        $browserProcess.Dispose()
                    }
                    catch {
                        $cleanupErrors.Add("The Task-087 Edge process handle could not be released.") | Out-Null
                    }
                }
            }
        }
        catch {
            $cleanupErrors.Add($_.Exception.Message) | Out-Null
        }
    }

    if ($serviceNeedsRestore) {
        try {
            & $docker.Source compose -p $ProjectName -f $composePath start towerscout | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "Docker Compose could not restore the dedicated Task-087 service."
            }
            $restoredContainerId = Get-Task087ContainerId
            if ($restoredContainerId -ne $containerId) {
                throw "Docker Compose replaced the dedicated container during cleanup."
            }
            Assert-Task087ContainerIdentity -ContainerId $containerId -RequireRunning
            $serviceNeedsRestore = $false
        }
        catch {
            $cleanupErrors.Add($_.Exception.Message) | Out-Null
        }
    }

    foreach ($pathToRemove in @($signalPath, $browserPidPath, $stdoutPath, $stderrPath)) {
        try {
            if (Test-Path -LiteralPath $pathToRemove) {
                Remove-Item -LiteralPath $pathToRemove -Force -ErrorAction Stop
            }
        }
        catch {
            $cleanupErrors.Add("A Task-087 temporary signal file could not be removed.") | Out-Null
        }
    }
    try {
        if (Test-Path -LiteralPath $browserProfilePath) {
            Remove-Item -LiteralPath $browserProfilePath -Recurse -Force -ErrorAction Stop
        }
    }
    catch {
        $cleanupErrors.Add("The dedicated Task-087 Edge profile could not be removed.") | Out-Null
    }

    foreach ($environmentName in $environmentNames) {
        try {
            $savedValue = $savedEnvironment[$environmentName]
            if ($savedValue.Exists) {
                [System.Environment]::SetEnvironmentVariable(
                    $environmentName,
                    [string] $savedValue.Value,
                    "Process"
                )
            }
            else {
                [System.Environment]::SetEnvironmentVariable($environmentName, $null, "Process")
            }
        }
        catch {
            $cleanupErrors.Add("A Task-087 review environment value could not be restored.") | Out-Null
        }
    }
}

if ($null -ne $primaryError) {
    if ($cleanupErrors.Count -gt 0) {
        throw "$($primaryError.Exception.Message) Cleanup also failed: $([string]::Join(' ', [string[]] $cleanupErrors))."
    }
    throw $primaryError
}
if ($cleanupErrors.Count -gt 0) {
    throw "Task-087 cleanup failed: $([string]::Join(' ', [string[]] $cleanupErrors))."
}
$observerOutput
