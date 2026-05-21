param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [ValidateSet("off", "auto", "on")]
    [string] $Gpu = "off",

    [switch] $Build
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

$composeArgs = @("up", "-d")
if ($Build) {
    $composeArgs += "--build"
}

Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments $composeArgs
exit $script:TowerScoutComposeExitCode
