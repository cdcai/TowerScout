param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [int] $Port = $(if ($env:TOWERSCOUT_PORT) { [int] $env:TOWERSCOUT_PORT } else { 5000 }),

    [int] $TimeoutSeconds = 180,

    [switch] $Build,

    [switch] $NoBrowser
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

$repoRoot = Get-TowerScoutRepoRoot
$appUrl = "http://127.0.0.1:$Port"
$readinessUrl = "$appUrl/api/readiness"

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

function Get-TowerScoutReadiness {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Url
    )

    try {
        $request = [System.Net.HttpWebRequest]::Create($Url)
        $request.Timeout = 5000
        try {
            $response = $request.GetResponse()
        }
        catch [System.Net.WebException] {
            if ($_.Exception.Response -eq $null) {
                throw
            }
            $response = $_.Exception.Response
        }

        $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
        try {
            $body = $reader.ReadToEnd()
        }
        finally {
            $reader.Close()
            $response.Close()
        }

        $payload = $body | ConvertFrom-Json
        return [pscustomobject]@{
            Reachable = $true
            State = [string] $payload.state
            Payload = $payload
            Error = $null
        }
    }
    catch {
        return [pscustomobject]@{
            Reachable = $false
            State = "unreachable"
            Payload = $null
            Error = $_.Exception.Message
        }
    }
}

function Write-TowerScoutReadinessSummary {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Readiness
    )

    if (-not $Readiness.Reachable) {
        Write-Host "TowerScout is not reachable yet. The container may still be starting."
        return
    }

    $payload = $Readiness.Payload
    Write-Host "TowerScout readiness state: $($Readiness.State)"
    if ($payload.components -and $payload.components.assets -and $payload.components.assets.status) {
        Write-Host "Asset status: $($payload.components.assets.status)"
    }
    if ($payload.components -and $payload.components.config -and $payload.components.config.status) {
        Write-Host "Config status: $($payload.components.config.status)"
    }
    if ($payload.recovery) {
        foreach ($item in $payload.recovery) {
            Write-Host "Recovery: $item"
        }
    }
}

function Write-TowerScoutHostDiagnostics {
    param(
        [Parameter(Mandatory = $true)]
        [string] $EngineName
    )

    if ($env:OS -ne "Windows_NT") {
        return
    }

    Write-Host ""
    Write-Host "Windows container runtime diagnostics:"

    $wslCommand = Get-Command "wsl.exe" -ErrorAction SilentlyContinue
    if ($null -eq $wslCommand) {
        Write-Host "- wsl.exe was not found. Docker Desktop or Podman on Windows usually needs WSL2 or Hyper-V/virtualization support."
    }
    else {
        Write-Host "- wsl.exe found at $($wslCommand.Source)."
        try {
            $wslStatus = & wsl.exe --status 2>&1
            foreach ($line in $wslStatus) {
                $normalizedLine = ([string] $line).Replace([string][char]0, "")
                if (-not [string]::IsNullOrWhiteSpace($normalizedLine)) {
                    Write-Host "  $normalizedLine"
                }
            }
        }
        catch {
            Write-Host "  Could not read WSL status: $($_.Exception.Message)"
        }
    }

    if ($EngineName -eq "podman") {
        Write-Host "- For Podman, check the machine state with: podman machine list"
        try {
            $podmanMachine = & podman machine list 2>&1
            foreach ($line in $podmanMachine) {
                $normalizedLine = ([string] $line).Replace([string][char]0, "")
                if (-not [string]::IsNullOrWhiteSpace($normalizedLine)) {
                    Write-Host "  $normalizedLine"
                }
            }
        }
        catch {
            Write-Host "  Could not read Podman machine state: $($_.Exception.Message)"
        }
    }

    if ($EngineName -eq "docker") {
        Write-Host "- For Docker Desktop, confirm Docker Desktop is running and that its WSL2 or Hyper-V backend is healthy."
    }

    Write-Host "- If the engine is managed by local IT, confirm virtualization, WSL2/Hyper-V, endpoint policy, and Compose provider access are approved."
}

if ($TimeoutSeconds -lt 5) {
    throw "TimeoutSeconds must be at least 5."
}

Initialize-TowerScoutEnvFile -RootPath $repoRoot

$composeCommand = Get-TowerScoutComposeCommand -Engine $Engine
$effectiveEngine = [string] $composeCommand["Executable"]
$env:TOWERSCOUT_CONTAINER_ENGINE = $effectiveEngine
$env:TOWERSCOUT_PORT = "$Port"

Write-Host "Starting TowerScout with $effectiveEngine on $appUrl..."

$composeArgs = @("up", "-d")
if ($Build) {
    $composeArgs += "--build"
}
Invoke-TowerScoutCompose -Engine $effectiveEngine -Build:$Build -ComposeArguments $composeArgs
if ($script:TowerScoutComposeExitCode -ne 0) {
    Write-Host "TowerScout container startup failed. Check the selected engine, Compose provider, and local permissions."
    Write-TowerScoutHostDiagnostics -EngineName $effectiveEngine
    exit $script:TowerScoutComposeExitCode
}

Write-Host "Waiting for TowerScout readiness at $readinessUrl..."
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$lastState = ""
$lastReadiness = $null

while ((Get-Date) -lt $deadline) {
    $readiness = Get-TowerScoutReadiness -Url $readinessUrl
    $lastReadiness = $readiness

    if ($readiness.Reachable) {
        if ($readiness.State -in @("setup_required", "degraded", "ready")) {
            Write-TowerScoutReadinessSummary -Readiness $readiness
            if (-not $NoBrowser) {
                Write-Host "Opening TowerScout in your browser..."
                Start-Process $appUrl
            }
            else {
                Write-Host "Browser launch skipped. Open $appUrl when ready."
            }
            exit 0
        }

        if ($readiness.State -eq "fatal") {
            Write-TowerScoutReadinessSummary -Readiness $readiness
            Write-Host "Run scripts\logs.cmd for container logs or scripts\status.cmd for the current readiness payload."
            exit 1
        }
    }

    if ($readiness.State -ne $lastState) {
        Write-TowerScoutReadinessSummary -Readiness $readiness
        $lastState = $readiness.State
    }

    Start-Sleep -Seconds 2
}

Write-Warning "Timed out after $TimeoutSeconds seconds waiting for TowerScout readiness."
if ($lastReadiness -ne $null) {
    Write-TowerScoutReadinessSummary -Readiness $lastReadiness
}
Write-Host "Use scripts\status.cmd to inspect readiness, scripts\logs.cmd -Tail 200 for logs, or scripts\stop.cmd to stop TowerScout."
exit 2
