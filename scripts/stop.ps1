param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

Invoke-TowerScoutCompose -Engine $Engine -ComposeArguments @("down", "--remove-orphans")
exit $script:TowerScoutComposeExitCode
