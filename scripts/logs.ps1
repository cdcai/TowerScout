param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [int] $Tail = 200,

    [switch] $Follow
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

$composeArgs = @("logs", "--tail", "$Tail")
if ($Follow) {
    $composeArgs += "-f"
}

Invoke-TowerScoutCompose -Engine $Engine -ComposeArguments $composeArgs
exit $script:TowerScoutComposeExitCode
