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

function Get-TowerScoutComposeCommand {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto"
    )

    if ($Engine -eq "auto") {
        if (Test-TowerScoutCommand "docker") {
            $Engine = "docker"
        }
        elseif (Test-TowerScoutCommand "podman") {
            $Engine = "podman"
        }
        else {
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
        & $command["Executable"] @(($command["Arguments"]) + $composeFiles + $ComposeArguments)
        $script:TowerScoutComposeExitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}
