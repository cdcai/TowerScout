Set-StrictMode -Version Latest

function Get-TowerScoutPodmanGpuRepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Get-TowerScoutPodmanGpuEnvFileValueFromPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,

        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            Found = $false
            Value = ""
        }
    }

    $pattern = "^\s*" + [regex]::Escape($Name) + "\s*=\s*(.*)\s*$"
    foreach ($line in Get-Content -LiteralPath $Path) {
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
            return [pscustomobject]@{
                Found = $true
                Value = $value
            }
        }
    }

    return [pscustomobject]@{
        Found = $false
        Value = ""
    }
}

function Get-TowerScoutPodmanGpuEnvFileValue {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    $repoRoot = Get-TowerScoutPodmanGpuRepoRoot
    foreach ($fileName in @(".env", ".env.example")) {
        $entry = Get-TowerScoutPodmanGpuEnvFileValueFromPath -Path (Join-Path $repoRoot $fileName) -Name $Name
        if ($entry.Found) {
            return $entry.Value
        }
    }

    return ""
}

function Join-TowerScoutPodmanGpuImageDigest {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Image,

        [string] $Digest = ""
    )

    $resolvedImage = $Image.Trim()
    if (-not [string]::IsNullOrWhiteSpace($Digest) -and $resolvedImage -notmatch "@sha256:") {
        return "$resolvedImage@$($Digest.Trim())"
    }

    return $resolvedImage
}

function Get-TowerScoutPodmanGpuEnvFileImage {
    $repoRoot = Get-TowerScoutPodmanGpuRepoRoot
    foreach ($fileName in @(".env", ".env.example")) {
        $envPath = Join-Path $repoRoot $fileName
        $imageEntry = Get-TowerScoutPodmanGpuEnvFileValueFromPath -Path $envPath -Name "TOWERSCOUT_IMAGE"
        if (-not $imageEntry.Found -or [string]::IsNullOrWhiteSpace([string] $imageEntry.Value)) {
            continue
        }

        $digestEntry = Get-TowerScoutPodmanGpuEnvFileValueFromPath -Path $envPath -Name "TOWERSCOUT_IMAGE_DIGEST"
        return Join-TowerScoutPodmanGpuImageDigest -Image $imageEntry.Value -Digest $digestEntry.Value
    }

    return ""
}

function Get-TowerScoutPodmanGpuImage {
    param(
        [string] $Image = ""
    )

    if (-not [string]::IsNullOrWhiteSpace($Image)) {
        return $Image.Trim()
    }
    if (-not [string]::IsNullOrWhiteSpace($env:TOWERSCOUT_IMAGE)) {
        return Join-TowerScoutPodmanGpuImageDigest -Image $env:TOWERSCOUT_IMAGE -Digest $env:TOWERSCOUT_IMAGE_DIGEST
    }

    $envFileImage = Get-TowerScoutPodmanGpuEnvFileImage
    if (-not [string]::IsNullOrWhiteSpace($envFileImage)) {
        return $envFileImage
    }

    return "ghcr.io/j-schulein/towerscout:latest-cpu"
}

function Get-TowerScoutImageReferenceParts {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Image
    )

    $reference = $Image.Trim()
    $digest = ""
    $withoutDigest = $reference
    $digestIndex = $reference.IndexOf("@sha256:", [System.StringComparison]::OrdinalIgnoreCase)
    if ($digestIndex -ge 0) {
        $withoutDigest = $reference.Substring(0, $digestIndex)
        $digest = $reference.Substring($digestIndex + 1)
    }

    $repository = $withoutDigest
    $tag = ""
    $lastSlash = $withoutDigest.LastIndexOf("/")
    $lastColon = $withoutDigest.LastIndexOf(":")
    if ($lastColon -gt $lastSlash) {
        $repository = $withoutDigest.Substring(0, $lastColon)
        $tag = $withoutDigest.Substring($lastColon + 1)
    }

    return [pscustomobject]@{
        Reference = $reference
        Repository = $repository
        Tag = $tag
        Digest = $digest
        ReferenceWithoutDigest = $withoutDigest
    }
}

function Invoke-TowerScoutPodmanGpuCommand {
    param(
        [string] $FileName = "podman",

        [string[]] $Arguments = @(),

        [int] $TimeoutSeconds = 60
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & $FileName @Arguments 2>&1
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            StdOut = [string]::Join([Environment]::NewLine, @($output))
            StdErr = ""
            Command = "$FileName $([string]::Join(' ', $Arguments))"
        }
    }
    catch {
        return [pscustomobject]@{
            ExitCode = 1
            StdOut = ""
            StdErr = $_.Exception.Message
            Command = "$FileName $([string]::Join(' ', $Arguments))"
        }
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function New-TowerScoutPodmanGpuStepResult {
    param(
        [string] $Name,

        [string] $Status,

        [string] $Message = "",

        [bool] $Mutating = $false
    )

    return [pscustomobject]@{
        Name = $Name
        Status = $Status
        Message = $Message
        Mutating = $Mutating
    }
}

function Get-TowerScoutPodmanGpuMachine {
    param(
        [string] $MachineName,

        [string] $InspectJson
    )

    try {
        $parsed = $InspectJson | ConvertFrom-Json
        $machines = @($parsed)
        foreach ($machine in $machines) {
            $name = ""
            if ($machine.PSObject.Properties.Name -contains "Name") {
                $name = [string] $machine.PSObject.Properties["Name"].Value
            }
            if ([string]::IsNullOrWhiteSpace($MachineName) -or $name -eq $MachineName) {
                return $machine
            }
        }
    }
    catch {
        return $null
    }

    return $null
}

function Get-TowerScoutPodmanGpuProperty {
    param(
        [object] $InputObject,

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

function Get-TowerScoutPodmanMachineVmType {
    param(
        [object] $Machine
    )

    if ($null -eq $Machine) {
        return ""
    }

    if ($Machine.PSObject.Properties.Name -contains "VMType") {
        $vmType = ([string] $Machine.PSObject.Properties["VMType"].Value).Trim()
        if (-not [string]::IsNullOrWhiteSpace($vmType)) {
            return $vmType.ToLowerInvariant()
        }
    }

    if ($Machine.PSObject.Properties.Name -contains "ConfigDir") {
        $configDir = $Machine.PSObject.Properties["ConfigDir"].Value
        if ($null -ne $configDir -and $configDir.PSObject.Properties.Name -contains "Path") {
            $configPath = [string] $configDir.PSObject.Properties["Path"].Value
            if (-not [string]::IsNullOrWhiteSpace($configPath)) {
                $trimmed = $configPath -replace '[\\/]+$', ''
                $idx = $trimmed.LastIndexOfAny([char[]]@('\', '/'))
                return $trimmed.Substring($idx + 1).Trim().ToLowerInvariant()
            }
        }
    }

    return ""
}

function Invoke-TowerScoutPodmanGpuPlanStep {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name,

        [Parameter(Mandatory = $true)]
        [string] $Description,

        [Parameter(Mandatory = $true)]
        [string[]] $Arguments,

        [switch] $Mutating,

        [switch] $DryRun,

        [switch] $VerifyOnly,

        [int] $TimeoutSeconds = 60
    )

    $commandText = "podman $([string]::Join(' ', $Arguments))"
    if ($DryRun) {
        Write-Host ("  - {0,-44} {1}" -f $Description, $commandText)
        return New-TowerScoutPodmanGpuStepResult -Name $Name -Status "planned" -Message $commandText -Mutating:$Mutating
    }

    if ($VerifyOnly -and $Mutating) {
        Write-Host "  [skip] ${Name}: skipped by -VerifyOnly."
        return New-TowerScoutPodmanGpuStepResult -Name $Name -Status "skipped" -Message "Skipped by -VerifyOnly." -Mutating:$Mutating
    }

    $result = Invoke-TowerScoutPodmanGpuCommand -FileName "podman" -Arguments $Arguments -TimeoutSeconds $TimeoutSeconds
    $message = (($result.StdOut + [Environment]::NewLine + $result.StdErr).Trim())
    if ($result.ExitCode -ne 0) {
        Write-Host "  [FAIL] ${Name}: $message"
        return New-TowerScoutPodmanGpuStepResult -Name $Name -Status "failed" -Message $message -Mutating:$Mutating
    }

    Write-Host "  [ OK ] ${Name}: $Description"
    return New-TowerScoutPodmanGpuStepResult -Name $Name -Status "ok" -Message $message -Mutating:$Mutating
}

function Invoke-TowerScoutPodmanGpuEnablement {
    param(
        [string] $MachineName = "podman-machine-default",

        [string] $Image = "",

        [string] $EvidenceDir = "",

        [switch] $DryRun,

        [switch] $VerifyOnly,

        [switch] $Force
    )

    $resolvedImage = Get-TowerScoutPodmanGpuImage -Image $Image
    $repoRoot = Get-TowerScoutPodmanGpuRepoRoot
    if ([string]::IsNullOrWhiteSpace($EvidenceDir)) {
        $EvidenceDir = Join-Path $repoRoot ".agent_work\evidence\TASK-083\podman-gpu"
    }

    $steps = @()

    Write-Host "TowerScout Podman GPU CDI enablement"
    Write-Host "Machine: $MachineName"
    Write-Host "Image: $resolvedImage"

    if ($DryRun) {
        Write-Host "Dry run: commands that would be executed:"
    }

    $inspect = Invoke-TowerScoutPodmanGpuPlanStep `
        -Name "machine-inspect" `
        -Description "Check Podman machine liveness and backend" `
        -Arguments @("machine", "inspect", $MachineName) `
        -DryRun:$DryRun `
        -VerifyOnly:$VerifyOnly `
        -TimeoutSeconds 15
    $steps += $inspect
    if ($DryRun) {
        $steps += Invoke-TowerScoutPodmanGpuPlanStep `
            -Name "machine-gpu" `
            -Description "Confirm GPU is visible inside the machine" `
            -Arguments @("machine", "ssh", $MachineName, "--", "/usr/lib/wsl/lib/nvidia-smi", "-L") `
            -DryRun
        $steps += Invoke-TowerScoutPodmanGpuPlanStep `
            -Name "toolkit-install" `
            -Description "Install nvidia-container-toolkit if missing" `
            -Arguments @("machine", "ssh", $MachineName, "--", "sudo", "sh", "-c", "rpm -q nvidia-container-toolkit || (curl -fsSL https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo && sudo dnf install -y nvidia-container-toolkit)") `
            -DryRun `
            -Mutating
        $steps += Invoke-TowerScoutPodmanGpuPlanStep `
            -Name "cdi-generate" `
            -Description "Generate the NVIDIA CDI spec" `
            -Arguments @("machine", "ssh", $MachineName, "--", "sudo", "nvidia-ctk", "cdi", "generate", "--output=/etc/cdi/nvidia.yaml") `
            -DryRun `
            -Mutating
        $steps += Invoke-TowerScoutPodmanGpuPlanStep `
            -Name "cdi-verify" `
            -Description "Verify nvidia.com/gpu is registered" `
            -Arguments @("machine", "ssh", $MachineName, "--", "nvidia-ctk", "cdi", "list") `
            -DryRun
        $steps += Invoke-TowerScoutPodmanGpuPlanStep `
            -Name "container-smoke" `
            -Description "Run a transient CDI GPU container smoke" `
            -Arguments @("run", "--rm", "--device", "nvidia.com/gpu=all", "--security-opt=label=disable", $resolvedImage, "nvidia-smi", "-L") `
            -DryRun
        return [pscustomobject]@{
            Success = $true
            Steps = $steps
            EvidenceDir = $EvidenceDir
        }
    }

    if ($inspect.Status -ne "ok") {
        throw "Podman machine '$MachineName' was not found or is not running. Run 'podman machine start $MachineName' or initialize the machine, then retry."
    }

    $machine = Get-TowerScoutPodmanGpuMachine -MachineName $MachineName -InspectJson $inspect.Message
    if ($null -eq $machine) {
        throw "Podman machine '$MachineName' inspect output could not be parsed."
    }

    $running = (Get-TowerScoutPodmanGpuProperty -InputObject $machine -Name "Running").Trim().ToLowerInvariant()
    $state = (Get-TowerScoutPodmanGpuProperty -InputObject $machine -Name "State").Trim().ToLowerInvariant()
    if ($running -notin @("true", "1") -and $state -notin @("running", "started")) {
        throw "Podman machine '$MachineName' is not running. Run 'podman machine start $MachineName' and retry."
    }

    $vmType = Get-TowerScoutPodmanMachineVmType -Machine $machine
    if ($vmType -ne "wsl") {
        throw "Podman GPU requires the WSL2 machine backend. Machine '$MachineName' reports VMType='$vmType'."
    }

    $machineGpu = Invoke-TowerScoutPodmanGpuPlanStep `
        -Name "machine-gpu" `
        -Description "Confirm GPU is visible inside the machine" `
        -Arguments @("machine", "ssh", $MachineName, "--", "/usr/lib/wsl/lib/nvidia-smi", "-L") `
        -VerifyOnly:$VerifyOnly `
        -TimeoutSeconds 20
    $steps += $machineGpu
    if ($machineGpu.Status -ne "ok" -or $machineGpu.Message -notmatch "GPU") {
        throw "WSL GPU paravirtualization is not exposed to the Podman machine. Update the Windows NVIDIA driver and WSL, then restart the Podman machine."
    }

    $toolkit = Invoke-TowerScoutPodmanGpuPlanStep `
        -Name "toolkit-install" `
        -Description "Install nvidia-container-toolkit if missing" `
        -Arguments @("machine", "ssh", $MachineName, "--", "sudo", "sh", "-c", "rpm -q nvidia-container-toolkit || (curl -fsSL https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo && sudo dnf install -y nvidia-container-toolkit)") `
        -VerifyOnly:$VerifyOnly `
        -Mutating `
        -TimeoutSeconds 300
    $steps += $toolkit
    if (-not $VerifyOnly -and $toolkit.Status -ne "ok") {
        throw "NVIDIA Container Toolkit install failed. The Podman machine may need internet egress or a site-approved offline RPM procedure. $($toolkit.Message)"
    }

    if ($Force -or -not $VerifyOnly) {
        $generate = Invoke-TowerScoutPodmanGpuPlanStep `
            -Name "cdi-generate" `
            -Description "Generate the NVIDIA CDI spec" `
            -Arguments @("machine", "ssh", $MachineName, "--", "sudo", "nvidia-ctk", "cdi", "generate", "--output=/etc/cdi/nvidia.yaml") `
            -VerifyOnly:$VerifyOnly `
            -Mutating `
            -TimeoutSeconds 60
        $steps += $generate
        if (-not $VerifyOnly -and $generate.Status -ne "ok") {
            throw "NVIDIA CDI spec generation failed. $($generate.Message)"
        }
    }

    $cdi = Invoke-TowerScoutPodmanGpuPlanStep `
        -Name "cdi-verify" `
        -Description "Verify nvidia.com/gpu is registered" `
        -Arguments @("machine", "ssh", $MachineName, "--", "nvidia-ctk", "cdi", "list") `
        -VerifyOnly:$VerifyOnly `
        -TimeoutSeconds 20
    $steps += $cdi
    if ($cdi.Status -ne "ok" -or $cdi.Message -notmatch "nvidia\.com/gpu") {
        throw "CDI spec does not list nvidia.com/gpu. Run this script without -VerifyOnly after support approval, or rerun with -Force if the spec is stale."
    }

    if ($VerifyOnly) {
        return [pscustomobject]@{
            Success = $true
            Steps = $steps
            EvidenceDir = $EvidenceDir
        }
    }

    $smoke = Invoke-TowerScoutPodmanGpuPlanStep `
        -Name "container-smoke" `
        -Description "Run a transient CDI GPU container smoke" `
        -Arguments @("run", "--rm", "--device", "nvidia.com/gpu=all", "--security-opt=label=disable", $resolvedImage, "nvidia-smi", "-L") `
        -TimeoutSeconds 60
    $steps += $smoke
    if ($smoke.Status -ne "ok" -and ($smoke.Message -match "unresolvable CDI devices")) {
        Write-Host "  [heal] stale CDI device reference detected; regenerating CDI once and retrying the smoke."
        $regen = Invoke-TowerScoutPodmanGpuPlanStep `
            -Name "cdi-regenerate-after-smoke-failure" `
            -Description "Regenerate CDI after stale-device smoke failure" `
            -Arguments @("machine", "ssh", $MachineName, "--", "sudo", "nvidia-ctk", "cdi", "generate", "--output=/etc/cdi/nvidia.yaml") `
            -Mutating `
            -TimeoutSeconds 60
        $steps += $regen
        if ($regen.Status -eq "ok") {
            $smoke = Invoke-TowerScoutPodmanGpuPlanStep `
                -Name "container-smoke-retry" `
                -Description "Retry transient CDI GPU container smoke" `
                -Arguments @("run", "--rm", "--device", "nvidia.com/gpu=all", "--security-opt=label=disable", $resolvedImage, "nvidia-smi", "-L") `
                -TimeoutSeconds 60
            $steps += $smoke
        }
    }

    if ($smoke.Status -ne "ok" -or $smoke.Message -notmatch "GPU") {
        throw "Podman GPU container smoke failed. $($smoke.Message)"
    }

    if (-not (Test-Path -LiteralPath $EvidenceDir -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
    }
    $runtimeVersions = [ordered]@{
        generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        machine_name = $MachineName
        image = $resolvedImage
        cdi_device = "nvidia.com/gpu=all"
        smoke = $smoke.Message
    }
    $runtimePath = Join-Path $EvidenceDir "runtime-versions.json"
    $runtimeVersions | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $runtimePath -Encoding UTF8
    Write-Host "Runtime evidence written to $runtimePath"

    return [pscustomobject]@{
        Success = $true
        Steps = $steps
        EvidenceDir = $EvidenceDir
        RuntimeVersions = $runtimePath
    }
}
