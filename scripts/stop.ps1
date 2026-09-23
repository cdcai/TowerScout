param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto"
)

$ErrorActionPreference = "Stop"
$hostHelperReviewEnabled = (
    ([string] $env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED).Trim().ToLowerInvariant() -in
    @("1", "true", "yes", "on")
)
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"
. "$PSScriptRoot\lib\TowerScoutHostHelperState.ps1"
if ($hostHelperReviewEnabled) {
    . "$PSScriptRoot\lib\TowerScoutHostHelper.ps1"
}

$helperControlledOperation = [string]::Equals(
    [string] $env:TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION,
    "1",
    [System.StringComparison]::Ordinal
) -and $hostHelperReviewEnabled

if (-not $helperControlledOperation) {
    try {
        $helperCleanup = Clear-TowerScoutHostHelperSession -RootPath (Get-TowerScoutRepoRoot)
        if ($helperCleanup.cleared -gt 0) {
            Write-Host "Invalidated TowerScout host helper session metadata."
        }
    }
    catch {
        Write-Host "Could not invalidate TowerScout host helper session metadata: $($_.Exception.Message)"
    }
    Clear-TowerScoutHostHelperBridgeEnvironment
}
else {
    Write-Host "Deferred TowerScout host helper session invalidation for controlled operation."
}

Invoke-TowerScoutCompose -Engine $Engine -ComposeArguments @("down", "--remove-orphans")
exit $script:TowerScoutComposeExitCode
