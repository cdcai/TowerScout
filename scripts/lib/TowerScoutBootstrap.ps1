Set-StrictMode -Version Latest

function Resolve-TowerScoutBootstrapPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $Path,

        [string] $Label = "Path"
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw "$Label was not provided."
    }

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RootPath $Path))
}

function Test-TowerScoutBootstrapChildPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Parent,

        [Parameter(Mandatory = $true)]
        [string] $Child
    )

    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $childFull = [System.IO.Path]::GetFullPath($Child)

    return $childFull.StartsWith(
        $parentFull + [System.IO.Path]::DirectorySeparatorChar,
        [System.StringComparison]::OrdinalIgnoreCase
    )
}

function Test-TowerScoutBootstrapCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Join-TowerScoutBootstrapArguments {
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

function Invoke-TowerScoutBootstrapCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $FileName,

        [string[]] $Arguments = @(),

        [int] $TimeoutSeconds = 15
    )

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo.FileName = $FileName
    $process.StartInfo.Arguments = Join-TowerScoutBootstrapArguments -Arguments $Arguments
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    $process.StartInfo.CreateNoWindow = $true

    try {
        [void] $process.Start()
        $completed = $process.WaitForExit($TimeoutSeconds * 1000)
        if (-not $completed) {
            try {
                $process.Kill()
            }
            catch {
                # Best effort cleanup after a timed-out prerequisite probe.
            }

            return [pscustomobject]@{
                ExitCode = 124
                TimedOut = $true
                StdOut = ""
                StdErr = "Command timed out after $TimeoutSeconds seconds."
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

function New-TowerScoutBootstrapPreflightResult {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Engine,

        [string[]] $Failures = @(),

        [string[]] $Warnings = @(),

        [string[]] $Details = @()
    )

    return [pscustomobject]@{
        Engine = $Engine
        Healthy = ($Failures.Count -eq 0)
        Failures = @($Failures)
        Warnings = @($Warnings)
        Details = @($Details)
    }
}

function Write-TowerScoutBootstrapPreflightResult {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Result
    )

    Write-Host "$($Result.Engine) preflight:"
    foreach ($detail in $Result.Details) {
        Write-Host "  OK: $detail"
    }
    foreach ($warning in $Result.Warnings) {
        Write-Host "  Warning: $warning"
    }
    foreach ($failure in $Result.Failures) {
        Write-Host "  Failed: $failure"
    }
}

function Test-TowerScoutDockerPreflight {
    $failures = @()
    $warnings = @()
    $details = @()

    if (-not (Test-TowerScoutBootstrapCommand -Name "docker")) {
        $failures += "Docker CLI was not found. Install and start Docker Desktop, or choose -Engine podman if support selected Podman."
        return New-TowerScoutBootstrapPreflightResult -Engine "docker" -Failures $failures -Warnings $warnings -Details $details
    }
    $details += "Docker CLI was found."

    $daemon = Invoke-TowerScoutBootstrapCommand -FileName "docker" -Arguments @("version", "--format", "{{.Server.Version}}") -TimeoutSeconds 15
    if ($daemon.ExitCode -ne 0) {
        $message = ($daemon.StdErr + $daemon.StdOut).Trim()
        if ([string]::IsNullOrWhiteSpace($message)) {
            $message = "Docker daemon did not report a server version."
        }
        $failures += "Docker Desktop is not running or the Docker daemon is not reachable. $message"
    }
    else {
        $details += "Docker daemon is reachable."
    }

    $compose = Invoke-TowerScoutBootstrapCommand -FileName "docker" -Arguments @("compose", "version") -TimeoutSeconds 15
    if ($compose.ExitCode -ne 0) {
        $message = ($compose.StdErr + $compose.StdOut).Trim()
        if ([string]::IsNullOrWhiteSpace($message)) {
            $message = "docker compose version did not complete."
        }
        $failures += "Docker Compose is not available through 'docker compose'. $message"
    }
    else {
        $details += "Docker Compose is available."
    }

    if ($env:OS -eq "Windows_NT") {
        if (Test-TowerScoutBootstrapCommand -Name "wsl.exe") {
            $wsl = Invoke-TowerScoutBootstrapCommand -FileName "wsl.exe" -Arguments @("--status") -TimeoutSeconds 10
            if ($wsl.ExitCode -eq 0) {
                $details += "wsl.exe is available for Docker Desktop's WSL2 backend checks."
            }
            else {
                $warnings += "wsl.exe was found, but WSL status could not be read. Docker Desktop may still work if its backend is already healthy."
            }
        }
        else {
            $warnings += "wsl.exe was not found. Docker Desktop on Windows normally needs WSL2 or another approved virtualization backend."
        }
    }

    return New-TowerScoutBootstrapPreflightResult -Engine "docker" -Failures $failures -Warnings $warnings -Details $details
}

function Test-TowerScoutPodmanPreflight {
    $failures = @()
    $warnings = @()
    $details = @()

    if (-not (Test-TowerScoutBootstrapCommand -Name "podman")) {
        $failures += "Podman CLI was not found. Install Podman or choose -Engine docker for the primary Docker Desktop path."
        return New-TowerScoutBootstrapPreflightResult -Engine "podman" -Failures $failures -Warnings $warnings -Details $details
    }
    $details += "Podman CLI was found."

    $info = Invoke-TowerScoutBootstrapCommand -FileName "podman" -Arguments @("info") -TimeoutSeconds 15
    if ($info.ExitCode -ne 0) {
        $message = ($info.StdErr + $info.StdOut).Trim()
        if ([string]::IsNullOrWhiteSpace($message)) {
            $message = "podman info did not complete."
        }
        $failures += "Podman is not ready. Start the Podman machine and confirm local policy allows Podman. $message"
    }
    else {
        $details += "Podman engine is reachable."
    }

    if ($env:OS -eq "Windows_NT") {
        $machine = Invoke-TowerScoutBootstrapCommand -FileName "podman" -Arguments @("machine", "list") -TimeoutSeconds 10
        if ($machine.ExitCode -eq 0) {
            if ($machine.StdOut -match "(?i)running") {
                $details += "At least one Podman machine appears to be running."
            }
            else {
                $warnings += "Podman machine list did not show a running machine. If Podman is selected, start the machine before launch."
            }
        }
        else {
            $warnings += "Podman machine state could not be read. Support may need to run 'podman machine list'."
        }
    }

    if (Get-Command "Initialize-TowerScoutPodmanComposeProvider" -ErrorAction SilentlyContinue) {
        try {
            $resolvedProvider = Initialize-TowerScoutPodmanComposeProvider
            if (-not [string]::IsNullOrWhiteSpace($resolvedProvider)) {
                $details += "PODMAN_COMPOSE_PROVIDER points to an available approved provider."
            }
        }
        catch {
            $failures += $_.Exception.Message
        }
    }
    else {
        $providerOverride = $env:PODMAN_COMPOSE_PROVIDER
        if (-not [string]::IsNullOrWhiteSpace($providerOverride)) {
            if ((Test-Path -LiteralPath $providerOverride -PathType Leaf) -or (Test-TowerScoutBootstrapCommand -Name $providerOverride)) {
                $details += "PODMAN_COMPOSE_PROVIDER points to an available provider."
            }
            else {
                $failures += "PODMAN_COMPOSE_PROVIDER is set to '$providerOverride', but that file or command was not found."
            }
        }
    }

    $compose = Invoke-TowerScoutBootstrapCommand -FileName "podman" -Arguments @("compose", "version") -TimeoutSeconds 15
    if ($compose.ExitCode -ne 0) {
        $message = ($compose.StdErr + $compose.StdOut).Trim()
        if ([string]::IsNullOrWhiteSpace($message)) {
            $message = "podman compose version did not complete."
        }
        $failures += "Podman Compose is not available through 'podman compose'. Install or configure an approved Compose provider such as podman-compose. $message"
    }
    else {
        if (Get-Command "Assert-TowerScoutPodmanComposeProviderAllowed" -ErrorAction SilentlyContinue) {
            try {
                Assert-TowerScoutPodmanComposeProviderAllowed -Lines @($compose.StdOut, $compose.StdErr)
            }
            catch {
                $failures += $_.Exception.Message
            }
        }
        $details += "Podman Compose provider is available."
    }

    return New-TowerScoutBootstrapPreflightResult -Engine "podman" -Failures $failures -Warnings $warnings -Details $details
}

function Test-TowerScoutPortAvailable {
    param(
        [Parameter(Mandatory = $true)]
        [int] $Port
    )

    $listener = $null
    try {
        $listener = New-Object System.Net.Sockets.TcpListener ([System.Net.IPAddress]::Parse("127.0.0.1"), $Port)
        $listener.Start()
        return $true
    }
    catch {
        return $false
    }
    finally {
        if ($null -ne $listener) {
            $listener.Stop()
        }
    }
}

function Test-TowerScoutReadinessReachable {
    param(
        [Parameter(Mandatory = $true)]
        [int] $Port
    )

    try {
        $request = [System.Net.HttpWebRequest]::Create("http://127.0.0.1:$Port/api/readiness")
        $request.Timeout = 1500
        try {
            $response = $request.GetResponse()
        }
        catch [System.Net.WebException] {
            if ($_.Exception.Response -eq $null) {
                throw
            }
            $response = $_.Exception.Response
        }
        $statusCode = [int] $response.StatusCode
        if ($statusCode -notin @(200, 503)) {
            $response.Close()
            return $false
        }

        $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
        try {
            $body = $reader.ReadToEnd()
        }
        finally {
            $reader.Close()
            $response.Close()
        }

        return Test-TowerScoutReadinessPayload -Body $body
    }
    catch {
        return $false
    }
}

function Test-TowerScoutReadinessPayload {
    param(
        [string] $Body = ""
    )

    if ([string]::IsNullOrWhiteSpace($Body)) {
        return $false
    }

    try {
        $payload = $Body | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $false
    }

    $state = [string] $payload.state
    if ($state -notin @("setup_required", "degraded", "ready", "fatal")) {
        return $false
    }

    $propertyNames = @($payload.PSObject.Properties.Name)
    foreach ($requiredProperty in @("components", "runtime", "recovery")) {
        if ($requiredProperty -notin $propertyNames) {
            return $false
        }
    }

    return $true
}

function Get-TowerScoutPortMappingConflict {
    param(
        [string[]] $Lines = @(),

        [Parameter(Mandatory = $true)]
        [int] $Port
    )

    $conflicts = @(Get-TowerScoutPortMappingConflicts -Lines $Lines -Port $Port)
    if ($conflicts.Count -gt 0) {
        return [string] $conflicts[0]
    }

    return ""
}

function Get-TowerScoutPortMappingConflicts {
    param(
        [string[]] $Lines = @(),

        [Parameter(Mandatory = $true)]
        [int] $Port
    )

    $portPattern = "(:|\[::\]:)" + [regex]::Escape([string] $Port) + "->"
    $conflicts = @()
    foreach ($line in $Lines) {
        $text = [string] $line
        if ($text -notmatch $portPattern) {
            continue
        }
        if ($text -match "(?i)\bUp\b|\brunning\b") {
            continue
        }

        $conflicts += $text.Trim()
    }

    return @($conflicts)
}

function Test-TowerScoutEnginePortMappings {
    param(
        [ValidateSet("docker", "podman")]
        [string] $Engine,

        [Parameter(Mandatory = $true)]
        [int] $Port
    )

    $containers = Invoke-TowerScoutBootstrapCommand -FileName $Engine -Arguments @("ps", "-a", "--format", "{{.Names}} {{.Status}} {{.Ports}}") -TimeoutSeconds 15
    if ($containers.ExitCode -ne 0) {
        Write-Host "Engine port check: could not inspect existing $Engine containers. $($containers.StdErr.Trim())"
        return
    }

    $lines = @($containers.StdOut -split "(`r`n|`n|`r)" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $conflicts = @(Get-TowerScoutPortMappingConflicts -Lines $lines -Port $Port)
    if ($conflicts.Count -gt 0) {
        $conflictList = ($conflicts | ForEach-Object { " - $_" }) -join [Environment]::NewLine
        throw "Engine port check failed: $Engine has stopped or created containers with host port $Port reserved:$([Environment]::NewLine)$conflictList$([Environment]::NewLine)Remove the stale containers through support guidance, or choose a different -Port."
    }

    $activeMapping = @($lines | Where-Object { ([string] $_) -match ("(:|\[::\]:)" + [regex]::Escape([string] $Port) + "->") })
    if ($activeMapping.Count -gt 0) {
        Write-Host "Engine port check: $Engine already has an active container mapping for host port $Port."
    }
    else {
        Write-Host "Engine port check: no stale $Engine container mapping reserves host port $Port."
    }
}

function Test-TowerScoutDiskSpace {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [int] $MinimumFreeGB = 15
    )

    $root = [System.IO.Path]::GetPathRoot([System.IO.Path]::GetFullPath($RootPath))
    $drive = New-Object System.IO.DriveInfo $root
    $freeGb = [math]::Round(($drive.AvailableFreeSpace / 1GB), 2)
    if ($freeGb -lt $MinimumFreeGB) {
        throw "The drive that contains TowerScout has $freeGb GB free. Free at least $MinimumFreeGB GB before first launch."
    }
    Write-Host "Disk space check: $freeGb GB free on $root."
}

function Get-TowerScoutBootstrapEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    foreach ($fileName in @(".env", ".env.example")) {
        $envPath = Join-Path $RootPath $fileName
        if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
            continue
        }

        $pattern = "^\s*" + [regex]::Escape($Name) + "\s*=\s*(.*?)\s*$"
        foreach ($line in Get-Content -LiteralPath $envPath) {
            $text = [string] $line
            if ($text.TrimStart().StartsWith("#")) {
                continue
            }
            if ($text -match $pattern) {
                return $Matches[1].Trim().Trim('"').Trim("'")
            }
        }
    }

    return ""
}

function Get-TowerScoutBootstrapImageReference {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $image = Get-TowerScoutBootstrapEnvValue -RootPath $RootPath -Name "TOWERSCOUT_IMAGE"
    if ([string]::IsNullOrWhiteSpace($image)) {
        return ""
    }

    $digest = Get-TowerScoutBootstrapEnvValue -RootPath $RootPath -Name "TOWERSCOUT_IMAGE_DIGEST"
    if (-not [string]::IsNullOrWhiteSpace($digest) -and $image -notmatch "@sha256:") {
        return "$image@$digest"
    }

    return $image
}

function Write-TowerScoutImagePullReadiness {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [ValidateSet("docker", "podman")]
        [string] $Engine
    )

    $image = Get-TowerScoutBootstrapImageReference -RootPath $RootPath
    if ([string]::IsNullOrWhiteSpace($image)) {
        Write-Host "Image pull check: no TOWERSCOUT_IMAGE value was found. Release packages should pin an image in .env.example."
        return
    }

    $inspect = Invoke-TowerScoutBootstrapCommand -FileName $Engine -Arguments @("image", "inspect", $image, "--format", "{{.Id}}") -TimeoutSeconds 15
    if ($inspect.ExitCode -eq 0) {
        Write-Host "Image pull check: selected image is already present in the $Engine image store."
        return
    }

    Write-Host "Image pull check: selected image is not currently present in the $Engine image store."
    if ($image -match "^ghcr\.io/") {
        Write-Host "Image pull check: first launch may pull $image from GHCR and can take several minutes. Keep PowerShell open."
    }
    else {
        Write-Host "Image pull check: first launch may need to pull or build $image depending on the package configuration. Keep PowerShell open."
    }
}

function Resolve-TowerScoutBootstrapEngine {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto",

        [Parameter(Mandatory = $true)]
        [int] $Port,

        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [int] $MinimumFreeGB = 15
    )

    Test-TowerScoutDiskSpace -RootPath $RootPath -MinimumFreeGB $MinimumFreeGB

    if (Test-TowerScoutPortAvailable -Port $Port) {
        Write-Host "Port check: localhost:$Port is available."
    }
    elseif (Test-TowerScoutReadinessReachable -Port $Port) {
        Write-Host "Port check: localhost:$Port is already in use by a reachable TowerScout instance."
    }
    else {
        throw "Port check failed: localhost:$Port is already in use by another process. Close the other app or choose a different -Port."
    }

    $docker = $null
    $podman = $null
    if ($Engine -in @("auto", "docker")) {
        $docker = Test-TowerScoutDockerPreflight
    }
    if ($Engine -in @("auto", "podman")) {
        $podman = Test-TowerScoutPodmanPreflight
    }

    if ($Engine -eq "docker") {
        Write-TowerScoutBootstrapPreflightResult -Result $docker
        if (-not $docker.Healthy) {
            throw "Docker preflight failed. Start Docker Desktop or choose the qualified Podman path if support selected it."
        }
        Test-TowerScoutEnginePortMappings -Engine "docker" -Port $Port
        return "docker"
    }

    if ($Engine -eq "podman") {
        Write-TowerScoutBootstrapPreflightResult -Result $podman
        if (-not $podman.Healthy) {
            throw "Podman preflight failed. Start the Podman machine and confirm the Compose provider, or use Docker Desktop for the primary pilot path."
        }
        Test-TowerScoutEnginePortMappings -Engine "podman" -Port $Port
        return "podman"
    }

    if ($null -ne $docker) {
        Write-TowerScoutBootstrapPreflightResult -Result $docker
    }
    if ($null -ne $podman) {
        Write-TowerScoutBootstrapPreflightResult -Result $podman
    }

    if ($null -ne $docker -and $docker.Healthy) {
        if ($null -ne $podman) {
            Write-Host "Automatic engine selection chose Docker. Docker and Podman use separate named volumes; keep using the selected engine for setup, assets, status, and logs."
        }
        Test-TowerScoutEnginePortMappings -Engine "docker" -Port $Port
        return "docker"
    }

    if ($null -ne $podman -and $podman.Healthy) {
        Write-Host "Automatic engine selection chose Podman. Docker and Podman use separate named volumes; keep using the selected engine for setup, assets, status, and logs."
        Test-TowerScoutEnginePortMappings -Engine "podman" -Port $Port
        return "podman"
    }

    throw "No selected container engine passed preflight. Start Docker Desktop for the primary pilot path, or use a support-validated Podman machine and Compose provider."
}

function Get-TowerScoutSha256FromSidecar {
    param(
        [Parameter(Mandatory = $true)]
        [string] $SidecarPath
    )

    $content = Get-Content -LiteralPath $SidecarPath -Raw
    if ($content -notmatch "(?i)\b([0-9a-f]{64})\b") {
        throw "Checksum sidecar does not contain a SHA-256 value: $SidecarPath"
    }

    return $Matches[1].ToLowerInvariant()
}

function Get-TowerScoutSha256FileHash {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    if (Test-TowerScoutBootstrapCommand -Name "Get-FileHash") {
        return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    }

    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        try {
            $hashBytes = $sha256.ComputeHash($stream)
            return [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToLowerInvariant()
        }
        finally {
            $sha256.Dispose()
        }
    }
    finally {
        $stream.Close()
    }
}

function Test-TowerScoutChecksumSidecar {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ArtifactPath
    )

    if (-not (Test-Path -LiteralPath $ArtifactPath -PathType Leaf)) {
        throw "Release artifact was not found: $ArtifactPath"
    }

    $sidecarPath = "$ArtifactPath.sha256"
    if (-not (Test-Path -LiteralPath $sidecarPath -PathType Leaf)) {
        throw "Checksum sidecar is required before using this artifact: $sidecarPath"
    }

    $expected = Get-TowerScoutSha256FromSidecar -SidecarPath $sidecarPath
    $actual = Get-TowerScoutSha256FileHash -Path $ArtifactPath
    if ($actual -ne $expected) {
        throw "Checksum mismatch for $ArtifactPath. Expected $expected but found $actual."
    }

    Write-Host "Checksum verified: $([System.IO.Path]::GetFileName($ArtifactPath))"
    return $actual
}

function Test-TowerScoutZipEntryName {
    param(
        [Parameter(Mandatory = $true)]
        [string] $EntryName
    )

    $normalized = $EntryName.Replace("\", "/")
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        throw "Asset ZIP contains an empty entry name."
    }
    if ($normalized.StartsWith("/") -or $normalized.StartsWith("\\") -or $normalized.Contains(":")) {
        throw "Asset ZIP contains an unsafe rooted entry: $EntryName"
    }

    $segments = @($normalized.Split("/") | Where-Object { $_ -ne "" })
    foreach ($segment in $segments) {
        if ($segment -in @(".", "..")) {
            throw "Asset ZIP contains an unsafe relative path entry: $EntryName"
        }
    }

    return $normalized
}

function Test-TowerScoutAssetZipLayout {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ZipPath
    )

    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $hasModel = $false
    $hasData = $false
    $hasManifest = $false
    $unexpectedRoots = New-Object System.Collections.Generic.List[string]

    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        foreach ($entry in $zip.Entries) {
            $normalized = Test-TowerScoutZipEntryName -EntryName $entry.FullName
            if ($normalized.StartsWith("assets/", [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "Asset ZIP contains a nested assets directory. The ZIP root must contain model_params/, data/, and asset_manifest.v1.json directly."
            }

            $top = ($normalized.Split("/") | Select-Object -First 1)
            if ($top -eq "model_params") {
                if ($entry.Length -gt 0) {
                    $hasModel = $true
                }
            }
            elseif ($top -eq "data") {
                if ($entry.Length -gt 0) {
                    $hasData = $true
                }
            }
            elseif ($normalized -eq "asset_manifest.v1.json") {
                $hasManifest = $true
            }
            else {
                $unexpectedRoots.Add($top) | Out-Null
            }
        }
    }
    finally {
        $zip.Dispose()
    }

    $uniqueUnexpectedRoots = @($unexpectedRoots | Sort-Object -Unique)
    if ($uniqueUnexpectedRoots.Count -gt 0) {
        throw "Asset ZIP contains unsupported root entries: $($uniqueUnexpectedRoots -join ', '). Only model_params/, data/, and asset_manifest.v1.json are allowed."
    }
    if (-not $hasModel) {
        throw "Asset ZIP is missing model files under model_params/."
    }
    if (-not $hasData) {
        throw "Asset ZIP is missing data files under data/."
    }
    if (-not $hasManifest) {
        throw "Asset ZIP is missing asset_manifest.v1.json at the ZIP root."
    }

    return $true
}

function Get-TowerScoutJsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
}

function Get-TowerScoutReleaseVersion {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $manifestPath = Join-Path $RootPath "release-manifest.v1.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        return ""
    }

    $manifest = Get-TowerScoutJsonFile -Path $manifestPath
    $version = [string] $manifest.release_version
    if ([string]::IsNullOrWhiteSpace($version) -or $version -eq "template") {
        return ""
    }

    return $version
}

function Get-TowerScoutSetupSearchRoots {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $roots = New-Object System.Collections.Generic.List[string]
    foreach ($candidate in @($RootPath, (Split-Path -Parent $RootPath))) {
        if ([string]::IsNullOrWhiteSpace($candidate)) {
            continue
        }

        try {
            $resolved = (Resolve-Path -LiteralPath $candidate -ErrorAction Stop).Path
        }
        catch {
            continue
        }

        if ($roots -notcontains $resolved) {
            [void] $roots.Add($resolved)
        }
    }

    return @($roots.ToArray())
}

function Find-TowerScoutSetupZipCandidate {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string[]] $Patterns,

        [Parameter(Mandatory = $true)]
        [string] $PackageLabel,

        [switch] $Optional
    )

    $candidates = New-Object System.Collections.Generic.List[object]
    foreach ($root in (Get-TowerScoutSetupSearchRoots -RootPath $RootPath)) {
        foreach ($pattern in $Patterns) {
            foreach ($candidate in @(Get-ChildItem -LiteralPath $root -Filter $pattern -File -ErrorAction SilentlyContinue)) {
                [void] $candidates.Add($candidate)
            }
        }
    }

    $unique = @($candidates | Sort-Object FullName -Unique)
    if ($unique.Count -eq 0) {
        if ($Optional) {
            return ""
        }

        throw "No $PackageLabel ZIP was found. Put the ZIP next to setup-towerscout.cmd or in the parent TowerScout UAT folder, or pass its path with the setup command."
    }

    if ($unique.Count -gt 1) {
        $paths = ($unique | ForEach-Object { " - $($_.FullName)" }) -join [Environment]::NewLine
        throw "More than one $PackageLabel ZIP was found:$([Environment]::NewLine)$paths$([Environment]::NewLine)Move older ZIPs out of this folder, or pass the intended ZIP path with the setup command."
    }

    $sidecarPath = "$($unique[0].FullName).sha256"
    if (-not (Test-Path -LiteralPath $sidecarPath -PathType Leaf)) {
        throw "$PackageLabel checksum sidecar was not found: $sidecarPath. Keep the .sha256 file beside the ZIP."
    }

    return $unique[0].FullName
}

function Find-TowerScoutSetupAssetZip {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [string] $AssetZip = ""
    )

    if (-not [string]::IsNullOrWhiteSpace($AssetZip)) {
        return (Resolve-TowerScoutBootstrapPath -RootPath $RootPath -Path $AssetZip -Label "Model & Data Package ZIP")
    }

    $releaseVersion = Get-TowerScoutReleaseVersion -RootPath $RootPath
    $patterns = @("towerscout-*-assets-*.zip")
    if (-not [string]::IsNullOrWhiteSpace($releaseVersion) -and ($releaseVersion -notlike "*@*")) {
        $patterns = @("towerscout-$releaseVersion-assets-*.zip")
    }

    return (Find-TowerScoutSetupZipCandidate -RootPath $RootPath -Patterns $patterns -PackageLabel "Model & Data Package")
}

function Find-TowerScoutSetupPackageZip {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [string] $PackageZip = ""
    )

    if (-not [string]::IsNullOrWhiteSpace($PackageZip)) {
        return (Resolve-TowerScoutBootstrapPath -RootPath $RootPath -Path $PackageZip -Label "Application Package ZIP")
    }

    $releaseVersion = Get-TowerScoutReleaseVersion -RootPath $RootPath
    if ([string]::IsNullOrWhiteSpace($releaseVersion) -or ($releaseVersion -like "*@*")) {
        return ""
    }

    return (Find-TowerScoutSetupZipCandidate -RootPath $RootPath -Patterns @("towerscout-$releaseVersion.zip") -PackageLabel "Application Package" -Optional)
}

function Test-TowerScoutReleaseHandoff {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $manifestPath = Join-Path $RootPath "release-manifest.v1.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        Write-Host "Warning: release-manifest.v1.json was not found. Source checkouts can omit package metadata, but release packages should include it."
        return
    }

    $releaseManifest = Get-TowerScoutJsonFile -Path $manifestPath
    $releaseVersion = [string] $releaseManifest.release_version
    Write-Host "Release manifest found: $releaseVersion"

    $assetManifestRelative = [string] $releaseManifest.asset_manifest
    if ([string]::IsNullOrWhiteSpace($assetManifestRelative)) {
        throw "release-manifest.v1.json does not identify the asset manifest path."
    }
    $assetManifestPath = Join-Path $RootPath $assetManifestRelative
    if (-not (Test-Path -LiteralPath $assetManifestPath -PathType Leaf)) {
        throw "Control package asset manifest was not found: $assetManifestRelative"
    }

    $imagePath = Join-Path $RootPath "IMAGE.txt"
    if (Test-Path -LiteralPath $imagePath -PathType Leaf) {
        $imageText = Get-Content -LiteralPath $imagePath -Raw
        if ($releaseVersion -ne "template" -and $imageText -match "(?m)^Version:\s*(.+?)\s*$") {
            $imageVersion = $Matches[1].Trim()
            if ($imageVersion -ne $releaseVersion) {
                throw "IMAGE.txt version '$imageVersion' does not match release-manifest.v1.json version '$releaseVersion'."
            }
        }
    }
    else {
        Write-Host "Warning: IMAGE.txt was not found. Generated release packages should include IMAGE.txt."
    }

    $envExamplePath = Join-Path $RootPath ".env.example"
    if (Test-Path -LiteralPath $envExamplePath -PathType Leaf) {
        $envText = Get-Content -LiteralPath $envExamplePath -Raw
        if ($envText -match "(?m)^TOWERSCOUT_IMAGE_DIGEST=(.+?)\s*$") {
            $envDigest = $Matches[1].Trim()
            $manifestDigest = [string] $releaseManifest.image_digest
            if (
                -not [string]::IsNullOrWhiteSpace($envDigest) -and
                -not [string]::IsNullOrWhiteSpace($manifestDigest) -and
                $envDigest -ne $manifestDigest
            ) {
                throw ".env.example image digest '$envDigest' does not match release-manifest.v1.json image digest '$manifestDigest'."
            }
        }
    }
}

function Test-TowerScoutAssetReleaseMatch {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $AssetManifestPath,

        [string] $AssetZipPath = ""
    )

    $controlManifestPath = Join-Path $RootPath "webapp\asset_manifest.v1.json"
    if (-not (Test-Path -LiteralPath $controlManifestPath -PathType Leaf)) {
        throw "Control package asset manifest was not found: $controlManifestPath"
    }

    $controlHash = Get-TowerScoutSha256FileHash -Path $controlManifestPath
    $assetHash = Get-TowerScoutSha256FileHash -Path $AssetManifestPath
    if ($controlHash -ne $assetHash) {
        throw "Asset package manifest does not match the control package manifest. Use the Model & Data Package from the same release."
    }

    if (-not [string]::IsNullOrWhiteSpace($AssetZipPath)) {
        $releaseVersion = Get-TowerScoutReleaseVersion -RootPath $RootPath
        $assetManifest = Get-TowerScoutJsonFile -Path $AssetManifestPath
        $assetVersion = [string] $assetManifest.manifest_version
        if (-not [string]::IsNullOrWhiteSpace($releaseVersion) -and -not [string]::IsNullOrWhiteSpace($assetVersion)) {
            $expectedName = "towerscout-$releaseVersion-assets-$assetVersion.zip"
            $actualName = [System.IO.Path]::GetFileName($AssetZipPath)
            if ($actualName -ne $expectedName) {
                throw "Asset ZIP filename '$actualName' does not match expected release artifact '$expectedName'."
            }
        }
    }
}

function Test-TowerScoutAssetZipReleaseMatch {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $ZipPath
    )

    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $tempManifestPath = [System.IO.Path]::GetTempFileName()
    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        $manifestEntry = $null
        foreach ($entry in $zip.Entries) {
            $normalized = Test-TowerScoutZipEntryName -EntryName $entry.FullName
            if ($normalized -eq "asset_manifest.v1.json") {
                $manifestEntry = $entry
                break
            }
        }

        if ($null -eq $manifestEntry) {
            throw "Asset ZIP is missing asset_manifest.v1.json at the ZIP root."
        }

        $sourceStream = $manifestEntry.Open()
        try {
            $targetStream = [System.IO.File]::Create($tempManifestPath)
            try {
                $sourceStream.CopyTo($targetStream)
            }
            finally {
                $targetStream.Close()
            }
        }
        finally {
            $sourceStream.Close()
        }

        Test-TowerScoutAssetReleaseMatch -RootPath $RootPath -AssetManifestPath $tempManifestPath -AssetZipPath $ZipPath
    }
    finally {
        $zip.Dispose()
        if (Test-Path -LiteralPath $tempManifestPath) {
            Remove-Item -LiteralPath $tempManifestPath -Force -ErrorAction SilentlyContinue
        }
    }
}

function Expand-TowerScoutAssetZip {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $ZipPath,

        [Parameter(Mandatory = $true)]
        [string] $AssetsPath,

        [switch] $ReplaceExisting
    )

    if (-not (Test-TowerScoutBootstrapChildPath -Parent $RootPath -Child $AssetsPath)) {
        throw "For safety, bootstrap asset extraction must target a folder inside the TowerScout package: $AssetsPath"
    }

    Test-TowerScoutAssetZipLayout -ZipPath $ZipPath | Out-Null

    if (-not (Test-Path -LiteralPath $AssetsPath -PathType Container)) {
        New-Item -ItemType Directory -Path $AssetsPath | Out-Null
    }

    if (-not $ReplaceExisting) {
        foreach ($existing in @("model_params", "data", "asset_manifest.v1.json")) {
            $existingPath = Join-Path $AssetsPath $existing
            if (Test-Path -LiteralPath $existingPath) {
                throw "Assets folder already contains '$existing' but the complete staged layout did not validate. Remove or repair the staged assets before re-running setup; valid staged assets are reused automatically."
            }
        }
    }

    $stagingPath = Join-Path $AssetsPath (".staging-" + [guid]::NewGuid().ToString("N"))
    $movedPaths = New-Object System.Collections.Generic.List[string]

    try {
        New-Item -ItemType Directory -Path $stagingPath | Out-Null

        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
        try {
            foreach ($entry in $zip.Entries) {
                $normalized = Test-TowerScoutZipEntryName -EntryName $entry.FullName
                $destination = Join-Path $stagingPath ($normalized.Replace("/", [System.IO.Path]::DirectorySeparatorChar))
                $destinationFull = [System.IO.Path]::GetFullPath($destination)
                if (-not (Test-TowerScoutBootstrapChildPath -Parent $stagingPath -Child $destinationFull)) {
                    throw "Refusing to extract asset ZIP entry outside the temporary staging folder: $($entry.FullName)"
                }

                if ($normalized.EndsWith("/")) {
                    if (-not (Test-Path -LiteralPath $destinationFull -PathType Container)) {
                        New-Item -ItemType Directory -Path $destinationFull | Out-Null
                    }
                    continue
                }

                $destinationDir = Split-Path -Parent $destinationFull
                if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
                    New-Item -ItemType Directory -Path $destinationDir | Out-Null
                }

                $sourceStream = $entry.Open()
                try {
                    $targetStream = [System.IO.File]::Create($destinationFull)
                    try {
                        $sourceStream.CopyTo($targetStream)
                    }
                    finally {
                        $targetStream.Close()
                    }
                }
                finally {
                    $sourceStream.Close()
                }
            }
        }
        finally {
            $zip.Dispose()
        }

        $assetManifestPath = Join-Path $stagingPath "asset_manifest.v1.json"
        Test-TowerScoutAssetReleaseMatch -RootPath $RootPath -AssetManifestPath $assetManifestPath -AssetZipPath $ZipPath
        Test-TowerScoutStagedAssets -RootPath $RootPath -AssetsPath $stagingPath | Out-Null

        if ($ReplaceExisting) {
            foreach ($existing in @("model_params", "data", "asset_manifest.v1.json")) {
                $existingPath = Join-Path $AssetsPath $existing
                if (Test-Path -LiteralPath $existingPath) {
                    Remove-Item -LiteralPath $existingPath -Recurse -Force -ErrorAction Stop
                }
            }
        }
        else {
            foreach ($existing in @("model_params", "data", "asset_manifest.v1.json")) {
                $existingPath = Join-Path $AssetsPath $existing
                if (Test-Path -LiteralPath $existingPath) {
                    throw "Assets folder already contains '$existing' but the complete staged layout did not validate. Remove or repair the staged assets before re-running setup; valid staged assets are reused automatically."
                }
            }
        }

        foreach ($assetEntry in @("model_params", "data", "asset_manifest.v1.json")) {
            $sourcePath = Join-Path $stagingPath $assetEntry
            $destinationPath = Join-Path $AssetsPath $assetEntry
            Move-Item -LiteralPath $sourcePath -Destination $destinationPath -ErrorAction Stop
            $movedPaths.Add($destinationPath) | Out-Null
        }
    }
    catch {
        for ($i = $movedPaths.Count - 1; $i -ge 0; $i--) {
            $movedPath = $movedPaths[$i]
            if (Test-Path -LiteralPath $movedPath) {
                Remove-Item -LiteralPath $movedPath -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        throw
    }
    finally {
        if (Test-Path -LiteralPath $stagingPath) {
            Remove-Item -LiteralPath $stagingPath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    Write-Host "Asset ZIP validated in temporary staging and staged into $AssetsPath."
}

function Test-TowerScoutStagedAssets {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $AssetsPath,

        [switch] $AllowRepair
    )

    if (-not (Test-Path -LiteralPath $AssetsPath -PathType Container)) {
        return $false
    }

    $nestedAssets = Join-Path $AssetsPath "assets"
    $modelSource = Join-Path $AssetsPath "model_params"
    $dataSource = Join-Path $AssetsPath "data"
    $manifestSource = Join-Path $AssetsPath "asset_manifest.v1.json"

    $hasDirectLayout = (
        (Test-Path -LiteralPath $modelSource -PathType Container) -and
        (Test-Path -LiteralPath $dataSource -PathType Container) -and
        (Test-Path -LiteralPath $manifestSource -PathType Leaf)
    )

    if ((Test-Path -LiteralPath $nestedAssets -PathType Container) -and -not $hasDirectLayout) {
        throw "Assets folder contains a nested assets directory. Move model_params, data, and asset_manifest.v1.json directly into $AssetsPath."
    }

    if ((Test-Path -LiteralPath $nestedAssets -PathType Container) -and $hasDirectLayout) {
        throw "Assets folder has both direct assets and a nested assets directory. This layout is ambiguous; ask support before importing."
    }

    if (-not $hasDirectLayout) {
        return $false
    }

    try {
        Test-TowerScoutAssetReleaseMatch -RootPath $RootPath -AssetManifestPath $manifestSource
        Test-TowerScoutStagedAssetFiles -AssetsPath $AssetsPath -AssetManifestPath $manifestSource
    }
    catch {
        if ($AllowRepair) {
            Write-Warning "Existing staged assets are incomplete or corrupt and will be replaced from the verified Model & Data Package ZIP. $($_.Exception.Message)"
            return $false
        }
        throw
    }

    Write-Host "Asset layout check: staged assets are present, complete, and match the control manifest."
    return $true
}

function Test-TowerScoutStagedAssetFiles {
    param(
        [Parameter(Mandatory = $true)]
        [string] $AssetsPath,

        [Parameter(Mandatory = $true)]
        [string] $AssetManifestPath
    )

    $manifest = Get-TowerScoutJsonFile -Path $AssetManifestPath
    $assets = @($manifest.assets)
    foreach ($asset in $assets) {
        $assetId = [string] $asset.id
        if ([string]::IsNullOrWhiteSpace($assetId)) {
            $assetId = [string] $asset.path
        }

        $relativePath = ([string] $asset.path).Trim()
        if ([string]::IsNullOrWhiteSpace($relativePath)) {
            throw "Asset manifest entry '$assetId' does not identify a relative path."
        }
        if ([System.IO.Path]::IsPathRooted($relativePath)) {
            throw "Asset manifest entry '$assetId' uses an absolute path; asset paths must be relative."
        }

        $normalizedRelativePath = $relativePath.Replace("/", [System.IO.Path]::DirectorySeparatorChar)
        $assetPath = [System.IO.Path]::GetFullPath((Join-Path $AssetsPath $normalizedRelativePath))
        if (-not (Test-TowerScoutBootstrapChildPath -Parent $AssetsPath -Child $assetPath)) {
            throw "Asset manifest entry '$assetId' resolves outside the assets folder."
        }

        $required = $true
        if ($asset.PSObject.Properties.Name -contains "required") {
            $required = [bool] $asset.required
        }

        if (-not (Test-Path -LiteralPath $assetPath -PathType Leaf)) {
            if ($required) {
                throw "Staged assets are missing required asset '$assetId' at $relativePath."
            }
            continue
        }

        if ($asset.PSObject.Properties.Name -contains "bytes" -and $null -ne $asset.bytes) {
            $expectedBytes = [Int64] $asset.bytes
            $actualBytes = (Get-Item -LiteralPath $assetPath).Length
            if ($actualBytes -ne $expectedBytes) {
                throw "Staged asset '$assetId' has $actualBytes bytes, expected $expectedBytes."
            }
        }

        $expectedSha256 = ""
        if ($asset.PSObject.Properties.Name -contains "sha256") {
            $expectedSha256 = ([string] $asset.sha256).Trim()
        }
        if (-not [string]::IsNullOrWhiteSpace($expectedSha256)) {
            $actualSha256 = Get-TowerScoutSha256FileHash -Path $assetPath
            if ($actualSha256.ToLowerInvariant() -ne $expectedSha256.ToLowerInvariant()) {
                throw "Staged asset '$assetId' failed SHA-256 verification."
            }
        }
    }
}

function Get-TowerScoutReadinessGuidance {
    param(
        [Parameter(Mandatory = $true)]
        [string] $State
    )

    switch ($State) {
        "setup_required" { return "TowerScout is running, but provider setup is not complete. Open Setup Wizard or Settings and save one valid Google Maps or Azure Maps provider key." }
        "degraded" { return "TowerScout is running with a recoverable issue. Follow the readiness recovery hints, most commonly importing the Model & Data Package assets." }
        "ready" { return "TowerScout is ready. Provider setup and required assets are available." }
        "fatal" { return "TowerScout cannot safely serve normal workflows. Stop validation and collect support evidence with scripts\status.cmd and scripts\logs.cmd." }
        default { return "TowerScout returned readiness state '$State'. Keep the PowerShell window open while startup continues, or ask support if the state does not change." }
    }
}
