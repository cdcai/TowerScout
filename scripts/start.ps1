param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [ValidateSet("off", "auto", "on")]
    [string] $Gpu = "off",

    [string] $PodmanMachineName = "",

    [switch] $Build
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

$repoRoot = Get-TowerScoutRepoRoot
Initialize-TowerScoutEnvFile -RootPath $repoRoot

$composeArgs = @("up", "-d")
if ($Build) {
    $composeArgs += "--build"
}

Invoke-TowerScoutCompose `
    -Engine $Engine `
    -Build:$Build `
    -Gpu $Gpu `
    -PodmanMachineName $PodmanMachineName `
    -ComposeArguments $composeArgs
exit $script:TowerScoutComposeExitCode
