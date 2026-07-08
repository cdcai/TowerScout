Set-StrictMode -Version Latest
$script:TowerScoutComposeExitCode = 0
$script:TowerScoutCpuPytorchIndexUrl = "https://download.pytorch.org/whl/cpu"
$script:TowerScoutCudaPytorchIndexUrl = "https://download.pytorch.org/whl/cu121"
$script:TowerScoutDefaultPodmanMachineName = "podman-machine-default"
. "$PSScriptRoot\TowerScoutPodmanComposeProvider.ps1"

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
    Initialize-TowerScoutPodmanComposeProvider | Out-Null

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
    return Get-TowerScoutEnvFileValueFromPath -Path $envPath -Name $Name
}

function Get-TowerScoutEnvFileValueFromPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,

        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    $envPath = $Path
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

function Get-TowerScoutReleaseManifest {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $manifestPath = Join-Path $RootPath "release-manifest.v1.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        return $null
    }

    try {
        return (Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json)
    }
    catch {
        return $null
    }
}

function Test-TowerScoutReleasePackageRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $manifest = Get-TowerScoutReleaseManifest -RootPath $RootPath
    if ($null -eq $manifest) {
        return $false
    }

    $version = (Get-TowerScoutObjectPropertyValue -InputObject $manifest -Name "release_version").Trim()
    return (-not [string]::IsNullOrWhiteSpace($version) -and $version -ne "template")
}

function Assert-TowerScoutPackageEnvImageMatch {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    if (-not (Test-TowerScoutReleasePackageRoot -RootPath $RootPath)) {
        return
    }

    $envPath = Join-Path $RootPath ".env"
    $templatePath = Join-Path $RootPath ".env.example"
    if (
        -not (Test-Path -LiteralPath $envPath -PathType Leaf) -or
        -not (Test-Path -LiteralPath $templatePath -PathType Leaf)
    ) {
        return
    }

    $expectedImage = [string] (Get-TowerScoutEnvFileValueFromPath -Path $templatePath -Name "TOWERSCOUT_IMAGE")
    $actualImage = [string] (Get-TowerScoutEnvFileValueFromPath -Path $envPath -Name "TOWERSCOUT_IMAGE")
    $expectedDigest = [string] (Get-TowerScoutEnvFileValueFromPath -Path $templatePath -Name "TOWERSCOUT_IMAGE_DIGEST")
    $actualDigest = [string] (Get-TowerScoutEnvFileValueFromPath -Path $envPath -Name "TOWERSCOUT_IMAGE_DIGEST")

    $mismatches = @()
    if (-not [string]::IsNullOrWhiteSpace($expectedImage) -and $actualImage -ne $expectedImage) {
        $mismatches += "TOWERSCOUT_IMAGE expected '$expectedImage' but found '$actualImage'"
    }
    if (-not [string]::IsNullOrWhiteSpace($expectedDigest) -and $actualDigest -ne $expectedDigest) {
        $mismatches += "TOWERSCOUT_IMAGE_DIGEST expected '$expectedDigest' but found '$actualDigest'"
    }

    if ($mismatches.Count -gt 0) {
        throw (
            "Package image mismatch: .env does not match this package's pinned image. " +
            ($mismatches -join "; ") +
            ". Back up .env, copy .env.example to .env, then reapply provider/TLS settings. " +
            "Do not reuse .env from another TowerScout package variant."
        )
    }
}

function Get-TowerScoutPackagePytorchFlavor {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $manifest = Get-TowerScoutReleaseManifest -RootPath $RootPath
    if ($null -ne $manifest) {
        $manifestFlavor = (Get-TowerScoutObjectPropertyValue -InputObject $manifest -Name "pytorch_flavor").Trim().ToLowerInvariant()
        if (-not [string]::IsNullOrWhiteSpace($manifestFlavor)) {
            return $manifestFlavor
        }
    }

    $envFlavor = [string] (Get-TowerScoutEnvFileValue -Name "TOWERSCOUT_PYTORCH_FLAVOR")
    if (-not [string]::IsNullOrWhiteSpace($envFlavor)) {
        return $envFlavor.Trim().ToLowerInvariant()
    }

    return ""
}

function Assert-TowerScoutPackageGpuCompatibility {
    param(
        [ValidateSet("off", "auto", "on")]
        [string] $Gpu = "off",

        [switch] $Build
    )

    if ($Gpu -ne "on" -or $Build) {
        return
    }

    $rootPath = Get-TowerScoutRepoRoot
    if (-not (Test-TowerScoutReleasePackageRoot -RootPath $rootPath)) {
        return
    }

    $packageFlavor = Get-TowerScoutPackagePytorchFlavor -RootPath $rootPath
    if ($packageFlavor -eq "cpu") {
        throw "This CPU TowerScout package does not support -Gpu on. Use the CUDA 12.1 package for GPU validation, or launch this CPU package with -Gpu off."
    }
}

function Get-TowerScoutConfiguredPodmanMachineName {
    param(
        [string] $MachineName = ""
    )

    if (-not [string]::IsNullOrWhiteSpace($MachineName)) {
        return ([string] $MachineName).Trim()
    }

    if (-not [string]::IsNullOrWhiteSpace([string] $env:TOWERSCOUT_PODMAN_MACHINE)) {
        return ([string] $env:TOWERSCOUT_PODMAN_MACHINE).Trim()
    }

    $envFileMachine = [string] (Get-TowerScoutEnvFileValue -Name "TOWERSCOUT_PODMAN_MACHINE")
    if (-not [string]::IsNullOrWhiteSpace($envFileMachine)) {
        return $envFileMachine.Trim()
    }

    return $script:TowerScoutDefaultPodmanMachineName
}

function Resolve-TowerScoutCommandOrPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Value
    )

    if (Test-Path -LiteralPath $Value -PathType Leaf) {
        return (Resolve-Path -LiteralPath $Value).Path
    }

    $command = Get-Command $Value -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return ""
    }

    if (
        $command.PSObject.Properties.Name -contains "Source" -and
        -not [string]::IsNullOrWhiteSpace([string] $command.Source)
    ) {
        return [string] $command.Source
    }
    if (
        $command.PSObject.Properties.Name -contains "Path" -and
        -not [string]::IsNullOrWhiteSpace([string] $command.Path)
    ) {
        return [string] $command.Path
    }

    return [string] $command.Name
}

function Test-TowerScoutDockerDesktopComposeProvider {
    param(
        [string] $Value = ""
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }

    $normalized = ([string] $Value).Replace("/", "\")
    # Podman prints external provider paths with escaped separators
    # (for example C:\\Program Files\\Docker\\...). Collapse them before matching.
    $normalized = $normalized -replace '\\{2,}', '\'
    return (
        $normalized -match "(?i)\\Docker\\Docker\\resources\\bin\\docker-compose(\.exe)?(\s|`"|$)" -or
        $normalized -match "(?i)Docker Desktop"
    )
}

function Get-TowerScoutPodmanComposeProviderOverride {
    $providerOverride = [string] $env:PODMAN_COMPOSE_PROVIDER
    if ([string]::IsNullOrWhiteSpace($providerOverride)) {
        $providerOverride = [string] (Get-TowerScoutEnvFileValue -Name "PODMAN_COMPOSE_PROVIDER")
    }

    return ([string] $providerOverride).Trim()
}

function Initialize-TowerScoutPodmanComposeProvider {
    $providerOverride = Get-TowerScoutPodmanComposeProviderOverride

    if (-not [string]::IsNullOrWhiteSpace($providerOverride)) {
        $check = Test-TowerScoutAnyApprovedPodmanComposeProvider -ProviderPath $providerOverride
        if (-not $check.Accepted) {
            if ((Test-TowerScoutDockerDesktopComposeProvider -Value $providerOverride) -or (Test-TowerScoutDockerDesktopComposeProvider -Value ([string] $check.Path))) {
                throw "PODMAN_COMPOSE_PROVIDER points to Docker Desktop's bundled docker-compose.exe. Select an approved non-Docker-Desktop Compose provider for the Podman path."
            }
            throw "PODMAN_COMPOSE_PROVIDER is set to '$providerOverride', but it is not an approved Podman Compose provider: $($check.Reason). Run scripts\install-podman-compose-provider.cmd -Apply or set PODMAN_COMPOSE_PROVIDER to an approved provider path."
        }

        $env:PODMAN_COMPOSE_PROVIDER = $check.Path
        return $check.Path
    }

    $approvedProviders = @(Find-TowerScoutApprovedPodmanComposeProviders)
    if ($approvedProviders.Count -eq 1) {
        $env:PODMAN_COMPOSE_PROVIDER = $approvedProviders[0].Path
        return $approvedProviders[0].Path
    }

    if ($approvedProviders.Count -gt 1) {
        $providerList = [string]::Join(
            [Environment]::NewLine,
            @($approvedProviders | ForEach-Object { "  - $($_.Provider.display_name): $($_.Path)" })
        )
        throw "Multiple approved Podman Compose providers were found. Set PODMAN_COMPOSE_PROVIDER in .env to one of these paths before using the Podman path:$([Environment]::NewLine)$providerList"
    }

    throw "No approved Podman Compose provider was found. Run scripts\install-podman-compose-provider.cmd -Apply, or set PODMAN_COMPOSE_PROVIDER in .env to an approved provider path."
}

function Get-TowerScoutPodmanComposeVersionResult {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $versionOutput = & podman compose version 2>&1
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            Lines = @($versionOutput)
        }
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Assert-TowerScoutPodmanComposeProviderAllowed {
    param(
        [string[]] $Lines = @()
    )

    foreach ($line in @($Lines)) {
        $normalizedLine = ([string] $line).Replace([string][char]0, "")
        $normalizedLine = $normalizedLine -replace ([string][char]27 + "\[[0-9;]*m"), ""
        if (Test-TowerScoutDockerDesktopComposeProvider -Value $normalizedLine) {
            throw "Podman Compose resolved to Docker Desktop's bundled docker-compose.exe. Set PODMAN_COMPOSE_PROVIDER to an approved non-Docker-Desktop provider before using the Podman path."
        }
    }
}

function Initialize-TowerScoutEnvFile {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $envPath = Join-Path $RootPath ".env"
    $templatePath = Join-Path $RootPath ".env.example"
    if (-not (Test-Path -LiteralPath $templatePath -PathType Leaf)) {
        return
    }
    if (Test-Path -LiteralPath $envPath -PathType Leaf) {
        Assert-TowerScoutPackageEnvImageMatch -RootPath $RootPath
        Sync-TowerScoutPackageEnvToProcess -RootPath $RootPath
        return
    }

    Copy-Item -LiteralPath $templatePath -Destination $envPath
    Write-Host "Created .env from .env.example."
    Sync-TowerScoutPackageEnvToProcess -RootPath $RootPath
}

function Get-TowerScoutPackageManagedEnvironmentNames {
    return @(
        "COMPOSE_PROJECT_NAME",
        "NVIDIA_DRIVER_CAPABILITIES",
        "NVIDIA_VISIBLE_DEVICES",
        "PODMAN_COMPOSE_PROVIDER",
        "PYTORCH_INDEX_URL",
        "REQUESTS_CA_BUNDLE",
        "SSL_CERT_FILE",
        "TOWERSCOUT_ALLOW_INSECURE_TLS",
        "TOWERSCOUT_CONTAINER_ENGINE",
        "TOWERSCOUT_DEVICE",
        "TOWERSCOUT_GPU_AUTO_OVERLAY",
        "TOWERSCOUT_GPU_CONCURRENCY",
        "TOWERSCOUT_GPU_MODE",
        "TOWERSCOUT_IMAGE",
        "TOWERSCOUT_IMAGE_DIGEST",
        "TOWERSCOUT_MAX_REQUEST_BODY_BYTES",
        "TOWERSCOUT_PILOT_MAX_TILES",
        "TOWERSCOUT_PODMAN_GPU_OVERLAY",
        "TOWERSCOUT_PODMAN_MACHINE",
        "TOWERSCOUT_PORT",
        "TOWERSCOUT_PYTORCH_FLAVOR",
        "TOWERSCOUT_VERIFY_ASSET_HASHES",
        "YOLO_CONFIG_DIR"
    )
}

function Sync-TowerScoutPackageEnvToProcess {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    if (-not (Test-TowerScoutReleasePackageRoot -RootPath $RootPath)) {
        return
    }

    $envPath = Join-Path $RootPath ".env"
    if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
        return
    }

    foreach ($name in Get-TowerScoutPackageManagedEnvironmentNames) {
        $value = Get-TowerScoutEnvFileValueFromPath -Path $envPath -Name $name
        if ($null -eq $value -or [string]::IsNullOrWhiteSpace([string] $value)) {
            Remove-Item -Path "Env:$name" -ErrorAction SilentlyContinue
        }
        else {
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

function Write-TowerScoutComposeProviderSummary {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto"
    )

    $command = Get-TowerScoutComposeCommand -Engine $Engine
    $effectiveEngine = [string] $command["Executable"]

    if ($effectiveEngine -eq "podman") {
        $providerPath = Initialize-TowerScoutPodmanComposeProvider
        Write-Host "Podman Compose provider: $providerPath"

        try {
            $versionResult = Get-TowerScoutPodmanComposeVersionResult
            Assert-TowerScoutPodmanComposeProviderAllowed -Lines $versionResult.Lines
            foreach ($line in $versionResult.Lines) {
                $normalizedLine = ([string] $line).Replace([string][char]0, "")
                $normalizedLine = $normalizedLine -replace ([string][char]27 + "\[[0-9;]*m"), ""
                if ($normalizedLine -eq "System.Management.Automation.RemoteException") {
                    continue
                }
                if (-not [string]::IsNullOrWhiteSpace($normalizedLine)) {
                    Write-Host "  $normalizedLine"
                }
            }
            if ($versionResult.ExitCode -ne 0) {
                Write-Host "  podman compose version exited with code $($versionResult.ExitCode)."
            }
        }
        catch {
            Write-Host "  Could not inspect podman compose provider: $($_.Exception.Message)"
            throw
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

    Assert-TowerScoutPackageGpuCompatibility -Gpu $Gpu -Build:$Build

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

function Test-TowerScoutBooleanGate {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    $envEntry = Get-Item "env:$Name" -ErrorAction SilentlyContinue
    $override = ""
    if ($null -ne $envEntry) {
        $override = [string] $envEntry.Value
    }
    if ([string]::IsNullOrWhiteSpace($override)) {
        $override = [string] (Get-TowerScoutEnvFileValue -Name $Name)
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

function Test-TowerScoutNvidiaGpuDetected {
    return Test-TowerScoutBooleanGate -Name "TOWERSCOUT_GPU_AUTO_OVERLAY"
}

function Test-TowerScoutPodmanGpuOverlayGate {
    return Test-TowerScoutBooleanGate -Name "TOWERSCOUT_PODMAN_GPU_OVERLAY"
}

function Test-TowerScoutHostNvidiaSmi {
    return $null -ne (Get-Command "nvidia-smi" -ErrorAction SilentlyContinue)
}

function New-TowerScoutPodmanGpuReadyResult {
    param(
        [bool] $Ready,

        [int] $FailedRung,

        [string] $Message
    )

    return [pscustomobject]@{
        Ready = $Ready
        FailedRung = $FailedRung
        Message = $Message
    }
}

function Convert-TowerScoutVersionPart {
    param(
        [string] $Value = ""
    )

    $match = [regex]::Match([string] $Value, "\d+")
    if ($match.Success) {
        return [int] $match.Value
    }
    return 0
}

function Test-TowerScoutPodmanVersionAtLeast {
    param(
        [string] $Version = "",

        [int] $Major = 5,

        [int] $Minor = 4
    )

    $parts = @(([string] $Version).Trim() -split "\.")
    $actualMajor = 0
    $actualMinor = 0
    if ($parts.Count -ge 1) {
        $actualMajor = Convert-TowerScoutVersionPart -Value $parts[0]
    }
    if ($parts.Count -ge 2) {
        $actualMinor = Convert-TowerScoutVersionPart -Value $parts[1]
    }

    return ($actualMajor -gt $Major -or ($actualMajor -eq $Major -and $actualMinor -ge $Minor))
}

function Join-TowerScoutProcessArguments {
    param(
        [string[]] $Arguments = @()
    )

    $quoted = foreach ($argument in $Arguments) {
        $text = [string] $argument
        if ($text -match '[\s"]') {
            '"' + $text.Replace('"', '\"') + '"'
        }
        else {
            $text
        }
    }

    return ($quoted -join " ")
}

function Stop-TowerScoutProcessTree {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process] $Process
    )

    if ($Process.HasExited) {
        return
    }

    if ($env:OS -eq "Windows_NT") {
        try {
            & taskkill.exe /PID $Process.Id /T /F 2>$null | Out-Null
            return
        }
        catch {
            # Fall back to direct process termination below.
        }
    }

    try {
        $Process.Kill()
    }
    catch {
        # Best effort cleanup after a timed-out runtime probe.
    }
}

function Invoke-TowerScoutPodmanCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]] $Arguments,

        [int] $TimeoutSeconds = 30
    )

    if ($TimeoutSeconds -lt 1) {
        $TimeoutSeconds = 1
    }

    $podmanPath = Resolve-TowerScoutCommandOrPath -Value "podman"
    if ([string]::IsNullOrWhiteSpace($podmanPath)) {
        return [pscustomobject]@{
            ExitCode = 127
            TimedOut = $false
            StdOut = ""
            StdErr = "Podman CLI was not found."
        }
    }

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo.FileName = $podmanPath
    $process.StartInfo.Arguments = Join-TowerScoutProcessArguments -Arguments $Arguments
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    $process.StartInfo.CreateNoWindow = $true

    try {
        [void] $process.Start()
        $completed = $process.WaitForExit($TimeoutSeconds * 1000)
        if (-not $completed) {
            Stop-TowerScoutProcessTree -Process $process
            return [pscustomobject]@{
                ExitCode = 124
                TimedOut = $true
                StdOut = ""
                StdErr = "podman command timed out after $TimeoutSeconds seconds."
            }
        }

        return [pscustomobject]@{
            ExitCode = $process.ExitCode
            TimedOut = $false
            StdOut = $process.StandardOutput.ReadToEnd()
            StdErr = $process.StandardError.ReadToEnd()
        }
    }
    catch {
        return [pscustomobject]@{
            ExitCode = 127
            TimedOut = $false
            StdOut = ""
            StdErr = $_.Exception.Message
        }
    }
    finally {
        $process.Dispose()
    }
}

function Get-TowerScoutFirstJsonObject {
    param(
        [string] $Json = ""
    )

    if ([string]::IsNullOrWhiteSpace($Json)) {
        return $null
    }

    try {
        $parsed = $Json | ConvertFrom-Json
        $items = @($parsed)
        if ($items.Count -gt 0) {
            return $items[0]
        }
    }
    catch {
        return $null
    }

    return $null
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

function Test-TowerScoutPodmanGpuReady {
    param(
        [string] $MachineName = $(Get-TowerScoutConfiguredPodmanMachineName)
    )

    $MachineName = Get-TowerScoutConfiguredPodmanMachineName -MachineName $MachineName

    if (-not (Test-TowerScoutCommand "podman")) {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 0 -Message "Podman CLI was not found."
    }

    $version = Invoke-TowerScoutPodmanCommand -Arguments @("version", "--format", "{{.Client.Version}}") -TimeoutSeconds 10
    if ($version.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($version.StdOut)) {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 0 -Message "Podman version could not be read."
    }
    if (-not (Test-TowerScoutPodmanVersionAtLeast -Version $version.StdOut -Major 5 -Minor 4)) {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 0 -Message "Podman GPU through Compose requires Podman 5.4 or newer."
    }

    $inspect = Invoke-TowerScoutPodmanCommand -Arguments @("machine", "inspect", $MachineName) -TimeoutSeconds 15
    if ($inspect.ExitCode -ne 0) {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 0 -Message "Podman machine '$MachineName' was not found or could not be inspected."
    }

    $machine = Get-TowerScoutFirstJsonObject -Json $inspect.StdOut
    if ($null -eq $machine) {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 0 -Message "Podman machine '$MachineName' inspect output could not be parsed."
    }

    $running = (Get-TowerScoutObjectPropertyValue -InputObject $machine -Name "Running").Trim().ToLowerInvariant()
    $state = (Get-TowerScoutObjectPropertyValue -InputObject $machine -Name "State").Trim().ToLowerInvariant()
    if ($running -notin @("true", "1") -and $state -notin @("running", "started")) {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 0 -Message "Podman machine '$MachineName' is not running. Run 'podman machine start $MachineName' and retry."
    }

    $vmType = Get-TowerScoutPodmanMachineVmType -Machine $machine
    if ($vmType -ne "wsl") {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 0 -Message "Podman GPU requires the WSL2 machine backend; machine '$MachineName' reports VMType='$vmType'."
    }

    if (-not (Test-TowerScoutHostNvidiaSmi)) {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 1 -Message "No NVIDIA driver tool was found on the Windows host; Podman GPU provisioning is not applicable on this CPU-only host."
    }

    $machineGpu = Invoke-TowerScoutPodmanCommand -Arguments @("machine", "ssh", $MachineName, "--", "/usr/lib/wsl/lib/nvidia-smi", "-L") -TimeoutSeconds 20
    if ($machineGpu.ExitCode -ne 0 -or $machineGpu.StdOut -notmatch "GPU") {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 2 -Message "The NVIDIA GPU is not visible inside the Podman WSL2 machine. Update the Windows NVIDIA driver and WSL, then restart the Podman machine."
    }

    $cdi = Invoke-TowerScoutPodmanCommand -Arguments @("machine", "ssh", $MachineName, "--", "nvidia-ctk", "cdi", "list") -TimeoutSeconds 20
    if ($cdi.ExitCode -ne 0 -or (($cdi.StdOut + $cdi.StdErr) -notmatch "nvidia\.com/gpu")) {
        return New-TowerScoutPodmanGpuReadyResult -Ready:$false -FailedRung 3 -Message "No CDI GPU device (nvidia.com/gpu) is registered inside the Podman machine. Run scripts\enable-podman-gpu.ps1 and retry."
    }

    return New-TowerScoutPodmanGpuReadyResult -Ready:$true -FailedRung -1 -Message "Podman GPU CDI prerequisites are ready."
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

    if ($EngineName -eq "docker") {
        return Test-TowerScoutNvidiaGpuDetected
    }
    if ($EngineName -eq "podman") {
        return Test-TowerScoutPodmanGpuOverlayGate
    }

    return $false
}

function Resolve-TowerScoutGpuComposeOverlay {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $EngineName,

        [ValidateSet("off", "auto", "on")]
        [string] $Gpu = "off",

        [string] $PodmanMachineName = $(Get-TowerScoutConfiguredPodmanMachineName)
    )

    if (-not (Test-TowerScoutUseGpuOverlay -EngineName $EngineName -Gpu $Gpu)) {
        return ""
    }

    if ($EngineName -eq "docker") {
        return "compose.gpu.yaml"
    }

    $resolvedPodmanMachineName = Get-TowerScoutConfiguredPodmanMachineName -MachineName $PodmanMachineName
    $ready = Test-TowerScoutPodmanGpuReady -MachineName $resolvedPodmanMachineName
    if ([bool] $ready.Ready) {
        return "compose.gpu.podman.yaml"
    }

    $message = [string] $ready.Message
    if ([string]::IsNullOrWhiteSpace($message)) {
        $message = "Podman GPU CDI prerequisites are not ready."
    }
    if ($Gpu -eq "on") {
        throw "$message Run scripts\enable-podman-gpu.ps1 -VerifyOnly for diagnostics, then run scripts\enable-podman-gpu.ps1 after support approval."
    }

    Write-Warning "$message Continuing without the Podman GPU overlay because -Gpu auto is CPU-safe."
    return ""
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
            if ($EngineName -eq "podman") {
                Write-Host "GPU mode: auto. Explicit Podman GPU overlay validation override is enabled; Podman CDI readiness will decide whether the overlay is used."
            }
            else {
                Write-Host "GPU mode: auto. Explicit Docker GPU overlay validation override is enabled; Docker GPU overlay will be requested and TowerScout will fall back to CPU if CUDA is unavailable."
            }
        }
        else {
            Write-Host "GPU mode: auto. No explicit $EngineName GPU overlay validation override is set; starting without the GPU overlay and using TowerScout CPU fallback."
        }
    }
    elseif ($Gpu -eq "on") {
        if ($EngineName -eq "podman") {
            Write-Host "GPU mode: on. The Podman GPU overlay (compose.gpu.podman.yaml, CDI) will be requested; TowerScout readiness will fail if CUDA is unavailable."
        }
        else {
            Write-Host "GPU mode: on. Docker GPU overlay will be requested; TowerScout readiness will fail if CUDA is unavailable."
        }
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

function Get-TowerScoutComposeServiceContainerId {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto",

        [string] $ServiceName = "towerscout"
    )

    $command = Get-TowerScoutComposeCommand -Engine $Engine
    $effectiveEngine = [string] $command["Executable"]
    if ($effectiveEngine -eq "podman") {
        return Get-TowerScoutPodmanServiceContainerId -ServiceName $ServiceName
    }

    $containerIds = @(Get-TowerScoutComposeServiceContainerIds -Engine $effectiveEngine -ServiceName $ServiceName)
    if ($containerIds.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace([string] $containerIds[0])) {
        return [string] $containerIds[0]
    }

    return ""
}

function Get-TowerScoutComposeProjectName {
    if (-not [string]::IsNullOrWhiteSpace($env:COMPOSE_PROJECT_NAME)) {
        return $env:COMPOSE_PROJECT_NAME.Trim()
    }

    $envFileProjectName = [string] (Get-TowerScoutEnvFileValue -Name "COMPOSE_PROJECT_NAME")
    if (-not [string]::IsNullOrWhiteSpace($envFileProjectName)) {
        return $envFileProjectName.Trim()
    }

    $leafName = (Split-Path (Get-TowerScoutRepoRoot) -Leaf).ToLowerInvariant()
    return ($leafName -replace "[^a-z0-9_-]", "")
}

function Get-TowerScoutRunningImageIdentity {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto",

        [string] $ServiceName = "towerscout"
    )

    $command = Get-TowerScoutComposeCommand -Engine $Engine
    $effectiveEngine = [string] $command["Executable"]
    $containerId = Get-TowerScoutComposeServiceContainerId -Engine $effectiveEngine -ServiceName $ServiceName
    if ([string]::IsNullOrWhiteSpace($containerId)) {
        return $null
    }

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $imageId = (& $effectiveEngine inspect --type container --format "{{.Image}}" $containerId 2>$null | Select-Object -First 1)
        $configImage = (& $effectiveEngine inspect --type container --format "{{.Config.Image}}" $containerId 2>$null | Select-Object -First 1)
        if ($LASTEXITCODE -ne 0) {
            return $null
        }

        $repoDigestsJson = "[]"
        if (-not [string]::IsNullOrWhiteSpace([string] $imageId)) {
            $repoDigestsResult = & $effectiveEngine inspect --type image --format "{{json .RepoDigests}}" ([string] $imageId).Trim() 2>$null
            if ($LASTEXITCODE -eq 0 -and $null -ne $repoDigestsResult) {
                $repoDigestsJson = [string] ($repoDigestsResult | Select-Object -First 1)
            }
        }
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    $repoDigests = @()
    if (-not [string]::IsNullOrWhiteSpace($repoDigestsJson)) {
        try {
            $parsedDigests = ConvertFrom-Json $repoDigestsJson
            if ($parsedDigests -is [System.Array]) {
                $repoDigests = @($parsedDigests | ForEach-Object { [string] $_ })
            }
            elseif ($null -ne $parsedDigests) {
                $repoDigests = @([string] $parsedDigests)
            }
        }
        catch {
            $repoDigests = @()
        }
    }

    $actualDigest = ""
    foreach ($repoDigest in $repoDigests) {
        if ([string]::IsNullOrWhiteSpace($repoDigest)) {
            continue
        }
        if ($repoDigest -match "@(?<digest>sha256:[0-9a-f]{64})$") {
            $actualDigest = $Matches["digest"]
            break
        }
    }

    return [pscustomobject]@{
        EngineName = $effectiveEngine
        ContainerId = [string] $containerId
        ConfigImage = ([string] $configImage).Trim()
        ImageId = ([string] $imageId).Trim()
        RepoDigests = $repoDigests
        ActualDigest = $actualDigest
    }
}

function Test-TowerScoutRunningImageMatchesPackage {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto",

        [string] $RootPath = $(Get-TowerScoutRepoRoot),

        [string] $ServiceName = "towerscout"
    )

    if (-not (Test-TowerScoutReleasePackageRoot -RootPath $RootPath)) {
        return [pscustomobject]@{
            Checked = $false
            Matches = $true
            Reason = "not_release_package"
            ExpectedImage = ""
            ExpectedDigest = ""
            Identity = $null
        }
    }

    $envPath = Join-Path $RootPath ".env"
    $expectedImage = [string] (Get-TowerScoutEnvFileValueFromPath -Path $envPath -Name "TOWERSCOUT_IMAGE")
    $expectedDigest = [string] (Get-TowerScoutEnvFileValueFromPath -Path $envPath -Name "TOWERSCOUT_IMAGE_DIGEST")
    if ([string]::IsNullOrWhiteSpace($expectedImage) -and [string]::IsNullOrWhiteSpace($expectedDigest)) {
        return [pscustomobject]@{
            Checked = $false
            Matches = $true
            Reason = "no_expected_identity"
            ExpectedImage = $expectedImage
            ExpectedDigest = $expectedDigest
            Identity = $null
        }
    }

    $identity = Get-TowerScoutRunningImageIdentity -Engine $Engine -ServiceName $ServiceName
    if ($null -eq $identity) {
        return [pscustomobject]@{
            Checked = $true
            Matches = $false
            Reason = "container_not_found"
            ExpectedImage = $expectedImage
            ExpectedDigest = $expectedDigest
            Identity = $null
        }
    }

    $isMatch = $true
    if (
        [string]::IsNullOrWhiteSpace($expectedDigest) -and
        -not [string]::IsNullOrWhiteSpace($expectedImage) -and
        $identity.ConfigImage -ne $expectedImage
    ) {
        $isMatch = $false
    }
    if (-not [string]::IsNullOrWhiteSpace($expectedDigest)) {
        $digestMatch = $false
        foreach ($repoDigest in @($identity.RepoDigests)) {
            if ([string] $repoDigest -match "@" + [regex]::Escape($expectedDigest) + "$") {
                $digestMatch = $true
                break
            }
        }
        if (-not $digestMatch -and $identity.ActualDigest -ne $expectedDigest) {
            $isMatch = $false
        }
    }

    return [pscustomobject]@{
        Checked = $true
        Matches = $isMatch
        Reason = if ($isMatch) { "match" } else { "mismatch" }
        ExpectedImage = $expectedImage
        ExpectedDigest = $expectedDigest
        Identity = $identity
    }
}

function Get-TowerScoutPodmanServiceContainerId {
    param(
        [string] $ServiceName = "towerscout"
    )

    $composeIds = @(Get-TowerScoutComposeServiceContainerIds -Engine "podman" -ServiceName $ServiceName)
    if ($composeIds.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace([string] $composeIds[0])) {
        return [string] $composeIds[0]
    }

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

    $command = Get-TowerScoutComposeCommand -Engine $Engine
    if ([string] $command["Executable"] -eq "podman") {
        $containerId = Get-TowerScoutPodmanServiceContainerId -ServiceName "towerscout"
        if ([string]::IsNullOrWhiteSpace($containerId)) {
            throw "Could not locate the running TowerScout Podman container for direct copy."
        }

        & podman cp $LocalPath "${containerId}:$ContainerPath"
        $copySucceeded = $?
        try {
            $script:TowerScoutComposeExitCode = [int] $LASTEXITCODE
        }
        catch {
            if ($copySucceeded) {
                $script:TowerScoutComposeExitCode = 0
            }
            else {
                $script:TowerScoutComposeExitCode = 1
            }
        }
        return
    }

    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
        "cp",
        $LocalPath,
        "towerscout:$ContainerPath"
    )
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
        [string] $Gpu = "off",

        [string] $PodmanMachineName = $(Get-TowerScoutConfiguredPodmanMachineName)
    )

    $repoRoot = Get-TowerScoutRepoRoot
    $command = Get-TowerScoutComposeCommand -Engine $Engine
    $effectiveEngine = [string] $command["Executable"]
    $gpuOverlayFile = ""
    if ($effectiveEngine -in @("docker", "podman")) {
        $gpuOverlayFile = Resolve-TowerScoutGpuComposeOverlay `
            -EngineName $effectiveEngine `
            -Gpu $Gpu `
            -PodmanMachineName (Get-TowerScoutConfiguredPodmanMachineName -MachineName $PodmanMachineName)
    }

    Set-TowerScoutGpuEnvironment -Gpu $Gpu -Build:$Build
    $env:TOWERSCOUT_CONTAINER_ENGINE = $effectiveEngine
    if ($effectiveEngine -eq "podman") {
        $versionResult = Get-TowerScoutPodmanComposeVersionResult
        Assert-TowerScoutPodmanComposeProviderAllowed -Lines $versionResult.Lines
        if ($versionResult.ExitCode -ne 0) {
            throw "podman compose version exited with code $($versionResult.ExitCode). Confirm the approved Compose provider is installed and selected."
        }
    }

    $composeFiles = @("-f", (Join-Path $repoRoot "compose.yaml"))
    if ($Build) {
        $composeFiles += @("-f", (Join-Path $repoRoot "compose.build.yaml"))
    }
    if (-not [string]::IsNullOrWhiteSpace($gpuOverlayFile)) {
        $gpuComposePath = Join-Path $repoRoot $gpuOverlayFile
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
