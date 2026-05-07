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
