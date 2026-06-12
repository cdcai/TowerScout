Set-StrictMode -Version Latest
$script:TowerScoutComposeExitCode = 0
$script:TowerScoutCpuPytorchIndexUrl = "https://download.pytorch.org/whl/cpu"
$script:TowerScoutCudaPytorchIndexUrl = "https://download.pytorch.org/whl/cu121"

function Get-TowerScoutRepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Test-TowerScoutCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Test-TowerScoutEngineReady {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $EngineName
    )

    if (-not (Test-TowerScoutCommand $EngineName)) {
        return $false
    }

    try {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            & $EngineName info 2>$null | Out-Null
        }
        finally {
            $ErrorActionPreference = $previousErrorActionPreference
        }
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Get-TowerScoutComposeCommand {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto"
    )

    if ($Engine -eq "auto") {
        $dockerAvailable = Test-TowerScoutCommand "docker"
        $podmanAvailable = Test-TowerScoutCommand "podman"

        if ($dockerAvailable -and (Test-TowerScoutEngineReady -EngineName "docker")) {
            $Engine = "docker"
        }
        elseif ($podmanAvailable -and (Test-TowerScoutEngineReady -EngineName "podman")) {
            if ($dockerAvailable) {
                Write-Host "Docker CLI was found but the Docker engine is not reachable; automatic engine selection chose Podman."
            }
            $Engine = "podman"
        }
        else {
            if ($dockerAvailable -or $podmanAvailable) {
                throw "No reachable container engine found. Start Docker Desktop or a support-approved Podman machine and try again."
            }
            throw "No supported container engine found. Install Docker or Podman and try again."
        }
    }

    if ($Engine -eq "docker") {
        if (-not (Test-TowerScoutCommand "docker")) {
            throw "Docker was selected but the docker command was not found."
        }
        return @{
            Executable = "docker"
            Arguments = @("compose")
        }
    }

    if (-not (Test-TowerScoutCommand "podman")) {
        throw "Podman was selected but the podman command was not found."
    }

    return @{
        Executable = "podman"
        Arguments = @("compose")
    }
}

function Test-TowerScoutCommandOrPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Value
    )

    if (Test-Path -LiteralPath $Value -PathType Leaf) {
        return $true
    }

    return $null -ne (Get-Command $Value -ErrorAction SilentlyContinue)
}

function Get-TowerScoutObjectPropertyValue {
    param(
        [Parameter(Mandatory = $true)]
        [object] $InputObject,

        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    if ($null -eq $InputObject) {
        return ""
    }
    if ($InputObject.PSObject.Properties.Name -notcontains $Name) {
        return ""
    }
    return [string] $InputObject.PSObject.Properties[$Name].Value
}

function Get-TowerScoutEnvFileValue {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    $envPath = Join-Path (Get-TowerScoutRepoRoot) ".env"
    if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
        return $null
    }

    $pattern = "^\s*" + [regex]::Escape($Name) + "\s*=\s*(.*)\s*$"
    foreach ($line in Get-Content -LiteralPath $envPath) {
        $text = [string] $line
        if ($text.TrimStart().StartsWith("#")) {
            continue
        }
        if ($text -match $pattern) {
            $value = $matches[1].Trim()
            if ($value.Length -ge 2) {
                $first = $value.Substring(0, 1)
                $last = $value.Substring($value.Length - 1, 1)
                if (($first -eq '"' -and $last -eq '"') -or ($first -eq "'" -and $last -eq "'")) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
            }
            return $value
        }
    }

    return $null
}

function Initialize-TowerScoutEnvFile {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $envPath = Join-Path $RootPath ".env"
    $templatePath = Join-Path $RootPath ".env.example"
    if ((Test-Path -LiteralPath $envPath -PathType Leaf) -or -not (Test-Path -LiteralPath $templatePath -PathType Leaf)) {
        return
    }

    Copy-Item -LiteralPath $templatePath -Destination $envPath
    Write-Host "Created .env from .env.example."
}

function Write-TowerScoutComposeProviderSummary {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto"
    )

    $command = Get-TowerScoutComposeCommand -Engine $Engine
    $effectiveEngine = [string] $command["Executable"]

    if ($effectiveEngine -eq "podman") {
        $providerOverride = $env:PODMAN_COMPOSE_PROVIDER
        if ([string]::IsNullOrWhiteSpace($providerOverride)) {
            Write-Host "Podman Compose provider: selected by podman compose. Set PODMAN_COMPOSE_PROVIDER to force an approved provider."
        }
        else {
            if (-not (Test-TowerScoutCommandOrPath -Value $providerOverride)) {
                throw "PODMAN_COMPOSE_PROVIDER is set to '$providerOverride', but that file or command was not found."
            }
            Write-Host "Podman Compose provider override: $providerOverride"
        }

        try {
            $previousErrorActionPreference = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            try {
                $versionOutput = & podman compose version 2>&1
            }
            finally {
                $ErrorActionPreference = $previousErrorActionPreference
            }
            foreach ($line in $versionOutput) {
                $normalizedLine = ([string] $line).Replace([string][char]0, "")
                $normalizedLine = $normalizedLine -replace ([string][char]27 + "\[[0-9;]*m"), ""
                if ($normalizedLine -eq "System.Management.Automation.RemoteException") {
                    continue
                }
                if (-not [string]::IsNullOrWhiteSpace($normalizedLine)) {
                    Write-Host "  $normalizedLine"
                }
            }
            if ($LASTEXITCODE -ne 0) {
                Write-Host "  podman compose version exited with code $LASTEXITCODE."
            }
        }
        catch {
            Write-Host "  Could not inspect podman compose provider: $($_.Exception.Message)"
        }
    }
    elseif ($effectiveEngine -eq "docker") {
        try {
            $previousErrorActionPreference = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            try {
                $versionOutput = & docker compose version 2>&1
            }
            finally {
                $ErrorActionPreference = $previousErrorActionPreference
            }
            foreach ($line in $versionOutput) {
                $normalizedLine = ([string] $line).Replace([string][char]0, "")
                $normalizedLine = $normalizedLine -replace ([string][char]27 + "\[[0-9;]*m"), ""
                if ($normalizedLine -eq "System.Management.Automation.RemoteException") {
                    continue
                }
                if (-not [string]::IsNullOrWhiteSpace($normalizedLine)) {
                    Write-Host "Docker Compose provider: $normalizedLine"
                }
            }
        }
        catch {
            Write-Host "Docker Compose provider could not be inspected: $($_.Exception.Message)"
        }
    }
}

function Set-TowerScoutGpuEnvironment {
    param(
        [ValidateSet("off", "auto", "on")]
        [string] $Gpu = "off",

        [switch] $Build
    )

    $env:TOWERSCOUT_GPU_MODE = $Gpu

    if ($Gpu -eq "off") {
        $env:TOWERSCOUT_DEVICE = "cpu"
        if ($Build) {
            $env:PYTORCH_INDEX_URL = $script:TowerScoutCpuPytorchIndexUrl
            $env:TOWERSCOUT_PYTORCH_FLAVOR = "cpu"
        }
        return
    }

    if ($Gpu -eq "auto") {
        $env:TOWERSCOUT_DEVICE = "auto"
    }
    elseif ($Gpu -eq "on") {
        $env:TOWERSCOUT_DEVICE = "cuda"
    }

    if ($Build -and (
        [string]::IsNullOrWhiteSpace($env:PYTORCH_INDEX_URL) -or
        $env:PYTORCH_INDEX_URL -eq "https://download.pytorch.org/whl/cpu"
    )) {
        $env:PYTORCH_INDEX_URL = $script:TowerScoutCudaPytorchIndexUrl
    }

    if ($Build) {
        if ($env:PYTORCH_INDEX_URL -eq $script:TowerScoutCudaPytorchIndexUrl) {
            $env:TOWERSCOUT_PYTORCH_FLAVOR = "cuda121"
        }
        elseif ($env:PYTORCH_INDEX_URL -eq $script:TowerScoutCpuPytorchIndexUrl) {
            $env:TOWERSCOUT_PYTORCH_FLAVOR = "cpu"
        }
    }
}

function Test-TowerScoutNvidiaGpuDetected {
    $override = $env:TOWERSCOUT_GPU_AUTO_OVERLAY
    if ([string]::IsNullOrWhiteSpace($override)) {
        $override = Get-TowerScoutEnvFileValue -Name "TOWERSCOUT_GPU_AUTO_OVERLAY"
    }

    $normalizedOverride = ([string] $override).Trim()
    if ($normalizedOverride -in @("1", "true", "TRUE", "yes", "YES", "on", "ON")) {
        return $true
    }
    if ($normalizedOverride -in @("0", "false", "FALSE", "no", "NO", "off", "OFF")) {
        return $false
    }

    return $false
}

function Test-TowerScoutUseGpuOverlay {
    param(
        [Parameter(Mandatory = $true)]
        [string] $EngineName,

        [ValidateSet("off", "auto", "on")]
        [string] $Gpu = "off"
    )

    if ($Gpu -eq "off") {
        return $false
    }

    if ($Gpu -eq "on") {
        return $true
    }

    return ($EngineName -eq "docker" -and (Test-TowerScoutNvidiaGpuDetected))
}

function Write-TowerScoutGpuModeSummary {
    param(
        [Parameter(Mandatory = $true)]
        [string] $EngineName,

        [ValidateSet("off", "auto", "on")]
        [string] $Gpu = "off",

        [switch] $Build
    )

    if ($Gpu -eq "off") {
        Write-Host "GPU mode: off. TowerScout will force CPU execution for this launch."
        return
    }

    if ($Gpu -eq "auto") {
        if (Test-TowerScoutUseGpuOverlay -EngineName $EngineName -Gpu $Gpu) {
            Write-Host "GPU mode: auto. Explicit Docker GPU overlay validation override is enabled; Docker GPU overlay will be requested and TowerScout will fall back to CPU if CUDA is unavailable."
        }
        else {
            Write-Host "GPU mode: auto. No explicit Docker GPU overlay validation override is set; starting without the GPU overlay and using TowerScout CPU fallback."
        }
    }
    elseif ($Gpu -eq "on") {
        Write-Host "GPU mode: on. Docker GPU overlay will be requested; TowerScout readiness will fail if CUDA is unavailable."
    }

    if ($Build) {
        Write-Host "PyTorch build index: $env:PYTORCH_INDEX_URL"
    }
}

function Get-TowerScoutComposeServiceContainerIds {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto",

        [string] $ServiceName = "towerscout"
    )

    $repoRoot = Get-TowerScoutRepoRoot
    $command = Get-TowerScoutComposeCommand -Engine $Engine
    $composeFiles = @("-f", (Join-Path $repoRoot "compose.yaml"))

    Push-Location $repoRoot
    try {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $output = & $command["Executable"] @(($command["Arguments"]) + $composeFiles + @("ps", "-a", "-q", $ServiceName)) 2>$null
        if ($LASTEXITCODE -ne 0) {
            return @()
        }

        return @($output | ForEach-Object { ([string] $_).Trim() } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        Pop-Location
    }
}

function Get-TowerScoutComposeProjectName {
    if (-not [string]::IsNullOrWhiteSpace($env:COMPOSE_PROJECT_NAME)) {
        return $env:COMPOSE_PROJECT_NAME.Trim()
    }
    return (Split-Path (Get-TowerScoutRepoRoot) -Leaf).ToLowerInvariant()
}

function Get-TowerScoutPodmanServiceContainerId {
    param(
        [string] $ServiceName = "towerscout"
    )

    $projectName = Get-TowerScoutComposeProjectName
    $labelSets = @(
        @("io.podman.compose.project=$projectName", "io.podman.compose.service=$ServiceName"),
        @("com.docker.compose.project=$projectName", "com.docker.compose.service=$ServiceName")
    )

    foreach ($labelSet in $labelSets) {
        $ids = & podman ps `
            --filter "label=$($labelSet[0])" `
            --filter "label=$($labelSet[1])" `
            --format "{{.ID}}" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $containerId = @($ids | ForEach-Object { ([string] $_).Trim() } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
            if ($containerId.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($containerId[0])) {
                return [string] $containerId[0]
            }
        }
    }

    return ""
}

function Copy-TowerScoutContainerPath {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto",

        [Parameter(Mandatory = $true)]
        [string] $LocalPath,

        [Parameter(Mandatory = $true)]
        [string] $ContainerPath,

        [switch] $Build,

        [ValidateSet("off", "auto", "on")]
        [string] $Gpu = "off"
    )

    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
        "cp",
        $LocalPath,
        "towerscout:$ContainerPath"
    )
    if ($script:TowerScoutComposeExitCode -eq 0) {
        return
    }

    $copyExitCode = $script:TowerScoutComposeExitCode
    $command = Get-TowerScoutComposeCommand -Engine $Engine
    if ([string] $command["Executable"] -ne "podman") {
        $script:TowerScoutComposeExitCode = $copyExitCode
        return
    }

    Write-Host "Compose provider did not support cp; falling back to direct podman cp."
    $containerId = Get-TowerScoutPodmanServiceContainerId -ServiceName "towerscout"
    if ([string]::IsNullOrWhiteSpace($containerId)) {
        throw "Could not locate the running TowerScout Podman container for direct copy fallback."
    }

    & podman cp $LocalPath "${containerId}:$ContainerPath"
    $script:TowerScoutComposeExitCode = $LASTEXITCODE
}

function Get-TowerScoutContainerSessionInfo {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $EngineName,

        [Parameter(Mandatory = $true)]
        [string] $ContainerId
    )

    $inspectOutput = & $EngineName container inspect $ContainerId 2>$null
    if ($LASTEXITCODE -ne 0 -or $null -eq $inspectOutput) {
        return $null
    }

    $inspect = @($inspectOutput | ConvertFrom-Json)[0]
    $state = $inspect.State
    $healthStatus = ""
    if ($null -ne $state -and $state.PSObject.Properties.Name -contains "Health" -and $null -ne $state.Health) {
        $healthStatus = [string] $state.Health.Status
    }

    $createdAt = $null
    if ($inspect.PSObject.Properties.Name -contains "Created" -and -not [string]::IsNullOrWhiteSpace([string] $inspect.Created)) {
        try {
            $createdAt = [datetime]::Parse(
                [string] $inspect.Created,
                [System.Globalization.CultureInfo]::InvariantCulture,
                [System.Globalization.DateTimeStyles]::AssumeUniversal
            ).ToUniversalTime()
        }
        catch {
            $createdAt = $null
        }
    }

    $envValues = @{}
    if (
        $inspect.PSObject.Properties.Name -contains "Config" -and
        $null -ne $inspect.Config -and
        $inspect.Config.PSObject.Properties.Name -contains "Env" -and
        $null -ne $inspect.Config.Env
    ) {
        foreach ($entry in @($inspect.Config.Env)) {
            $text = [string] $entry
            $separator = $text.IndexOf("=")
            if ($separator -gt 0) {
                $envValues[$text.Substring(0, $separator)] = $text.Substring($separator + 1)
            }
        }
    }

    $imageRef = ""
    if (
        $inspect.PSObject.Properties.Name -contains "Config" -and
        $null -ne $inspect.Config -and
        $inspect.Config.PSObject.Properties.Name -contains "Image"
    ) {
        $imageRef = [string] $inspect.Config.Image
    }

    $hostPort = ""
    if (
        $inspect.PSObject.Properties.Name -contains "NetworkSettings" -and
        $null -ne $inspect.NetworkSettings -and
        $inspect.NetworkSettings.PSObject.Properties.Name -contains "Ports" -and
        $null -ne $inspect.NetworkSettings.Ports -and
        $inspect.NetworkSettings.Ports.PSObject.Properties.Name -contains "5000/tcp"
    ) {
        $portBindings = @($inspect.NetworkSettings.Ports.PSObject.Properties["5000/tcp"].Value)
        if ($portBindings.Count -gt 0 -and $null -ne $portBindings[0] -and $portBindings[0].PSObject.Properties.Name -contains "HostPort") {
            $hostPort = [string] $portBindings[0].HostPort
        }
    }

    return [pscustomobject]@{
        Id = [string] $inspect.Id
        Name = [string] $inspect.Name
        StateStatus = [string] $state.Status
        HealthStatus = $healthStatus
        CreatedAt = $createdAt
        GpuMode = [string] $envValues["TOWERSCOUT_GPU_MODE"]
        DevicePolicy = [string] $envValues["TOWERSCOUT_DEVICE"]
        ContainerEngine = [string] $envValues["TOWERSCOUT_CONTAINER_ENGINE"]
        Image = $imageRef
        HostPort = $hostPort
    }
}

function Get-TowerScoutContainerSessionPlan {
    param(
        [object[]] $Containers = @(),

        [int] $SessionMaxHours = 12,

        [string] $ExpectedGpuMode = "",

        [string] $ExpectedDevicePolicy = "",

        [string] $ExpectedContainerEngine = "",

        [string] $ExpectedImage = "",

        [string] $ExpectedHostPort = "",

        [datetime] $Now = (Get-Date)
    )

    if ($SessionMaxHours -lt 0) {
        throw "SessionMaxHours must be 0 or greater."
    }

    $containerList = @($Containers | Where-Object { $null -ne $_ })
    if ($containerList.Count -eq 0) {
        return [pscustomobject]@{
            Action = "start"
            Reason = "No existing TowerScout container was found."
            ContainerIds = @()
            AgeHours = $null
        }
    }

    $nonRunning = @($containerList | Where-Object { ([string] $_.StateStatus).ToLowerInvariant() -ne "running" })
    if ($nonRunning.Count -gt 0) {
        return [pscustomobject]@{
            Action = "restart"
            Reason = "An existing TowerScout container is not running."
            ContainerIds = @($containerList | ForEach-Object { $_.Id })
            AgeHours = $null
        }
    }

    $unhealthy = @($containerList | Where-Object { ([string] $_.HealthStatus).ToLowerInvariant() -eq "unhealthy" })
    if ($unhealthy.Count -gt 0) {
        return [pscustomobject]@{
            Action = "restart"
            Reason = "An existing TowerScout container is unhealthy."
            ContainerIds = @($containerList | ForEach-Object { $_.Id })
            AgeHours = $null
        }
    }

    $normalizedExpectedGpuMode = ([string] $ExpectedGpuMode).Trim().ToLowerInvariant()
    if (-not [string]::IsNullOrWhiteSpace($normalizedExpectedGpuMode)) {
        $gpuModeMismatch = @($containerList | Where-Object {
            $currentGpuMode = (Get-TowerScoutObjectPropertyValue -InputObject $_ -Name "GpuMode").Trim().ToLowerInvariant()
            -not [string]::IsNullOrWhiteSpace($currentGpuMode) -and $currentGpuMode -ne $normalizedExpectedGpuMode
        })
        if ($gpuModeMismatch.Count -gt 0) {
            return [pscustomobject]@{
                Action = "restart"
                Reason = "An existing TowerScout container was started with a different GPU mode."
                ContainerIds = @($containerList | ForEach-Object { $_.Id })
                AgeHours = $null
            }
        }
    }

    $normalizedExpectedDevicePolicy = ([string] $ExpectedDevicePolicy).Trim().ToLowerInvariant()
    if (-not [string]::IsNullOrWhiteSpace($normalizedExpectedDevicePolicy)) {
        $devicePolicyMismatch = @($containerList | Where-Object {
            $currentDevicePolicy = (Get-TowerScoutObjectPropertyValue -InputObject $_ -Name "DevicePolicy").Trim().ToLowerInvariant()
            -not [string]::IsNullOrWhiteSpace($currentDevicePolicy) -and $currentDevicePolicy -ne $normalizedExpectedDevicePolicy
        })
        if ($devicePolicyMismatch.Count -gt 0) {
            return [pscustomobject]@{
                Action = "restart"
                Reason = "An existing TowerScout container was started with a different ML device policy."
                ContainerIds = @($containerList | ForEach-Object { $_.Id })
                AgeHours = $null
            }
        }
    }

    $normalizedExpectedContainerEngine = ([string] $ExpectedContainerEngine).Trim().ToLowerInvariant()
    if (-not [string]::IsNullOrWhiteSpace($normalizedExpectedContainerEngine)) {
        $containerEngineMismatch = @($containerList | Where-Object {
            $currentContainerEngine = (Get-TowerScoutObjectPropertyValue -InputObject $_ -Name "ContainerEngine").Trim().ToLowerInvariant()
            -not [string]::IsNullOrWhiteSpace($currentContainerEngine) -and $currentContainerEngine -ne $normalizedExpectedContainerEngine
        })
        if ($containerEngineMismatch.Count -gt 0) {
            return [pscustomobject]@{
                Action = "restart"
                Reason = "An existing TowerScout container was started with a different container engine."
                ContainerIds = @($containerList | ForEach-Object { $_.Id })
                AgeHours = $null
            }
        }
    }

    $normalizedExpectedImage = ([string] $ExpectedImage).Trim().ToLowerInvariant()
    if (-not [string]::IsNullOrWhiteSpace($normalizedExpectedImage)) {
        $imageMismatch = @($containerList | Where-Object {
            $currentImage = (Get-TowerScoutObjectPropertyValue -InputObject $_ -Name "Image").Trim().ToLowerInvariant()
            -not [string]::IsNullOrWhiteSpace($currentImage) -and $currentImage -ne $normalizedExpectedImage
        })
        if ($imageMismatch.Count -gt 0) {
            return [pscustomobject]@{
                Action = "restart"
                Reason = "An existing TowerScout container was started with a different image reference."
                ContainerIds = @($containerList | ForEach-Object { $_.Id })
                AgeHours = $null
            }
        }
    }

    $normalizedExpectedHostPort = ([string] $ExpectedHostPort).Trim()
    if (-not [string]::IsNullOrWhiteSpace($normalizedExpectedHostPort)) {
        $portMismatch = @($containerList | Where-Object {
            $currentHostPort = (Get-TowerScoutObjectPropertyValue -InputObject $_ -Name "HostPort").Trim()
            -not [string]::IsNullOrWhiteSpace($currentHostPort) -and $currentHostPort -ne $normalizedExpectedHostPort
        })
        if ($portMismatch.Count -gt 0) {
            return [pscustomobject]@{
                Action = "restart"
                Reason = "An existing TowerScout container was started with a different host port."
                ContainerIds = @($containerList | ForEach-Object { $_.Id })
                AgeHours = $null
            }
        }
    }

    $oldest = @($containerList | Where-Object { $null -ne $_.CreatedAt } | Sort-Object CreatedAt | Select-Object -First 1)
    if ($SessionMaxHours -gt 0 -and $oldest.Count -gt 0) {
        $ageHours = (($Now.ToUniversalTime()) - ($oldest[0].CreatedAt.ToUniversalTime())).TotalHours
        if ($ageHours -ge $SessionMaxHours) {
            return [pscustomobject]@{
                Action = "restart"
                Reason = "An existing TowerScout container is older than $SessionMaxHours hour(s)."
                ContainerIds = @($containerList | ForEach-Object { $_.Id })
                AgeHours = $ageHours
            }
        }
    }

    return [pscustomobject]@{
        Action = "reuse"
        Reason = "An existing TowerScout container is already running."
        ContainerIds = @($containerList | ForEach-Object { $_.Id })
        AgeHours = $null
    }
}

function Invoke-TowerScoutContainerStopRemove {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $EngineName,

        [string[]] $ContainerIds = @()
    )

    foreach ($containerId in $ContainerIds) {
        if ([string]::IsNullOrWhiteSpace($containerId)) {
            continue
        }

        $shortId = $containerId
        if ($shortId.Length -gt 12) {
            $shortId = $shortId.Substring(0, 12)
        }

        Write-Host "Stopping TowerScout container $shortId before starting a fresh UAT session..."
        & $EngineName container stop $containerId 2>$null | Out-Null

        Write-Host "Removing TowerScout container $shortId without deleting named volumes..."
        & $EngineName container rm $containerId 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) {
            & $EngineName container rm --force $containerId 2>$null | Out-Null
        }
        if ($LASTEXITCODE -ne 0) {
            throw "Could not remove existing TowerScout container $shortId. Stop TowerScout through support guidance and try again."
        }
    }
}

function Invoke-TowerScoutStaleContainerGuard {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $EngineName,

        [int] $SessionMaxHours = 12,

        [string] $ExpectedGpuMode = "",

        [string] $ExpectedDevicePolicy = "",

        [string] $ExpectedImage = "",

        [string] $ExpectedHostPort = ""
    )

    if ($SessionMaxHours -lt 0) {
        throw "SessionMaxHours must be 0 or greater."
    }

    $ids = Get-TowerScoutComposeServiceContainerIds -Engine $EngineName -ServiceName "towerscout"
    $containers = @()
    foreach ($id in $ids) {
        $info = Get-TowerScoutContainerSessionInfo -EngineName $EngineName -ContainerId $id
        if ($null -ne $info) {
            $containers += $info
        }
    }

    if ([string]::IsNullOrWhiteSpace($ExpectedGpuMode)) {
        $ExpectedGpuMode = [string] $env:TOWERSCOUT_GPU_MODE
    }
    if ([string]::IsNullOrWhiteSpace($ExpectedDevicePolicy)) {
        $ExpectedDevicePolicy = [string] $env:TOWERSCOUT_DEVICE
    }
    if ([string]::IsNullOrWhiteSpace($ExpectedImage)) {
        $ExpectedImage = [string] $env:TOWERSCOUT_IMAGE
    }
    if ([string]::IsNullOrWhiteSpace($ExpectedImage)) {
        $ExpectedImage = [string] (Get-TowerScoutEnvFileValue -Name "TOWERSCOUT_IMAGE")
    }
    if ([string]::IsNullOrWhiteSpace($ExpectedHostPort)) {
        $ExpectedHostPort = [string] $env:TOWERSCOUT_PORT
    }

    $plan = Get-TowerScoutContainerSessionPlan `
        -Containers $containers `
        -SessionMaxHours $SessionMaxHours `
        -ExpectedGpuMode $ExpectedGpuMode `
        -ExpectedDevicePolicy $ExpectedDevicePolicy `
        -ExpectedContainerEngine $EngineName `
        -ExpectedImage $ExpectedImage `
        -ExpectedHostPort $ExpectedHostPort
    if ($plan.Action -eq "start") {
        Write-Host "UAT session check: no existing TowerScout container found."
        return $plan
    }

    if ($plan.Action -eq "reuse") {
        Write-Host "TowerScout is already running. Reusing the current UAT session if no launch settings changed."
        return $plan
    }

    Write-Host "TowerScout found a stale, stopped, unhealthy, or launch-setting-mismatched session and is starting fresh."
    Write-Host "Reason: $($plan.Reason)"
    Write-Host "Saved setup, imported assets, and support logs are kept in named volumes."
    Invoke-TowerScoutContainerStopRemove -EngineName $EngineName -ContainerIds $plan.ContainerIds
    return $plan
}

function Invoke-TowerScoutCompose {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto",

        [string[]] $ComposeArguments = @(),

        [switch] $Build,

        [ValidateSet("off", "auto", "on")]
        [string] $Gpu = "off"
    )

    $repoRoot = Get-TowerScoutRepoRoot
    $command = Get-TowerScoutComposeCommand -Engine $Engine
    $effectiveEngine = [string] $command["Executable"]
    $useGpuOverlay = Test-TowerScoutUseGpuOverlay -EngineName $effectiveEngine -Gpu $Gpu
    if ($useGpuOverlay -and $effectiveEngine -ne "docker") {
        throw "GPU launch currently requires Docker Compose with NVIDIA GPU support. Podman GPU launch is not validated for this release path."
    }
    if ($Gpu -eq "on" -and $effectiveEngine -ne "docker") {
        throw "GPU launch currently requires Docker Compose with NVIDIA GPU support. Podman GPU launch is not validated for this release path."
    }

    Set-TowerScoutGpuEnvironment -Gpu $Gpu -Build:$Build
    $env:TOWERSCOUT_CONTAINER_ENGINE = $effectiveEngine

    $composeFiles = @("-f", (Join-Path $repoRoot "compose.yaml"))
    if ($Build) {
        $composeFiles += @("-f", (Join-Path $repoRoot "compose.build.yaml"))
    }
    if ($useGpuOverlay) {
        $gpuComposePath = Join-Path $repoRoot "compose.gpu.yaml"
        if (-not (Test-Path -LiteralPath $gpuComposePath -PathType Leaf)) {
            throw "GPU Compose overlay not found: $gpuComposePath"
        }
        $composeFiles += @("-f", $gpuComposePath)
    }

    Push-Location $repoRoot
    try {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $command["Executable"] @(($command["Arguments"]) + $composeFiles + $ComposeArguments)
        $script:TowerScoutComposeExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        Pop-Location
    }
}
