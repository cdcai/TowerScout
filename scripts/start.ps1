param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [switch] $Build
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

$composeArgs = @("up", "-d")
if ($Build) {
    $composeArgs += "--build"
}

Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments $composeArgs
exit $script:TowerScoutComposeExitCode
