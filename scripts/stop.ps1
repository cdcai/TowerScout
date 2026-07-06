param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"
. "$PSScriptRoot\lib\TowerScoutHostHelper.ps1"

$helperControlledOperation = [string]::Equals(
    [string] $env:TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION,
    "1",
    [System.StringComparison]::Ordinal
)

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
}
else {
    Write-Host "Deferred TowerScout host helper session invalidation for controlled operation."
}

Invoke-TowerScoutCompose -Engine $Engine -ComposeArguments @("down", "--remove-orphans")
exit $script:TowerScoutComposeExitCode
