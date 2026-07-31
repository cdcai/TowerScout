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

    [string] $PackageRoot = "",

    [int] $MutexWaitMilliseconds = 5000,

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
    $stopRoot = if ([string]::IsNullOrWhiteSpace($PackageRoot)) {
        (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
    }
    else {
        (Resolve-Path -LiteralPath $PackageRoot).Path
    }
    $result = Clear-TowerScoutHostHelperSession -RootPath $stopRoot
    Write-Host "TowerScout host helper sessions invalidated: $($result.cleared)"
    exit 0
}

$token = New-TowerScoutHostHelperToken
$resolvedPackageRoot = if ([string]::IsNullOrWhiteSpace($PackageRoot)) {
    (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
}
else {
    (Resolve-Path -LiteralPath $PackageRoot).Path
}
$profile = New-TowerScoutHostHelperRuntimeProfile `
    -Engine $Engine `
    -Gpu $Gpu `
    -AppPort $AppPort `
    -PackageRoot $resolvedPackageRoot `
    -PackageFlavor $PackageFlavor `
    -HelperPort $HelperPort `
    -HelperSessionId $HelperSessionId `
    -BrowserAuthorizationKey ([string] $env:TOWERSCOUT_HOST_HELPER_SESSION_KEY) `
    -ProviderTlsRepairEnabled:$false

Write-Host "TowerScout host helper review transport is starting on loopback only."
Write-Host "Helper token generated and stored in the package-local helper secret file."
Write-Host "Helper session metadata recorded without token material."
Write-Host "The public repair capability and browser-triggered mutation remain disabled."
try {
    $Host.UI.RawUI.WindowTitle = "TowerScout host helper - keep this window open"
}
catch {}
try {
    Start-TowerScoutHostHelper `
        -Profile $profile `
        -Token $token `
        -HelperPort $HelperPort `
        -MaxRequests $MaxRequests `
        -ExecutionEnabled:$false `
        -MutexWaitMilliseconds $MutexWaitMilliseconds
}
finally {
    Clear-TowerScoutHostHelperSession `
        -RootPath $resolvedPackageRoot `
        -SessionId $profile.HelperSessionId | Out-Null
}
