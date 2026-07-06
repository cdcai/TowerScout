param(
    [ValidateSet("docker", "podman")]
    [string] $Engine = "docker",

    [ValidateSet("off", "auto", "on")]
    [string] $Gpu = "off",

    [int] $AppPort = $(if ($env:TOWERSCOUT_PORT) { [int] $env:TOWERSCOUT_PORT } else { 5000 }),

    [int] $HelperPort = 0,

    [int] $MaxRequests = 0,

    [string] $PackageFlavor = "source",

    [string] $HelperSessionId = "",

    [switch] $SelfTest,

    [switch] $Stop
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutHostHelper.ps1"

if ($SelfTest) {
    Invoke-TowerScoutHostHelperSelfTest | ConvertTo-Json -Depth 8
    exit 0
}

if ($Stop) {
    $result = Clear-TowerScoutHostHelperSession
    Write-Host "TowerScout host helper sessions invalidated: $($result.cleared)"
    exit 0
}

$token = New-TowerScoutHostHelperToken
$profile = New-TowerScoutHostHelperRuntimeProfile `
    -Engine $Engine `
    -Gpu $Gpu `
    -AppPort $AppPort `
    -PackageFlavor $PackageFlavor `
    -HelperPort $HelperPort `
    -HelperSessionId $HelperSessionId
Save-TowerScoutHostHelperSession -Profile $profile -Token $token | Out-Null

Write-Host "TowerScout host helper proof is starting on loopback only."
Write-Host "Helper token generated and stored in the package-local helper secret file."
Write-Host "Helper session metadata recorded without token material."
Write-Host "This Gate 1 entry point is not yet wired into product UI or restart orchestration."
try {
    Start-TowerScoutHostHelper -Profile $profile -Token $token -HelperPort $HelperPort -MaxRequests $MaxRequests
}
finally {
    Clear-TowerScoutHostHelperSession -SessionId $profile.HelperSessionId | Out-Null
}
