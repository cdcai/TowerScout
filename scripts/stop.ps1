param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

Invoke-TowerScoutCompose -Engine $Engine -ComposeArguments @("stop")
exit $script:TowerScoutComposeExitCode
