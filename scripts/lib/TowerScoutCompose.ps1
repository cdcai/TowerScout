Set-StrictMode -Version Latest
$script:TowerScoutComposeExitCode = 0

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

function Invoke-TowerScoutCompose {
    param(
        [ValidateSet("auto", "docker", "podman")]
        [string] $Engine = "auto",

        [string[]] $ComposeArguments = @(),

        [switch] $Build
    )

    $repoRoot = Get-TowerScoutRepoRoot
    $command = Get-TowerScoutComposeCommand -Engine $Engine
    $composeFiles = @("-f", (Join-Path $repoRoot "compose.yaml"))
    if ($Build) {
        $composeFiles += @("-f", (Join-Path $repoRoot "compose.build.yaml"))
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
