param(
    [string] $MachineName = $(if ($env:TOWERSCOUT_PODMAN_MACHINE) { [string] $env:TOWERSCOUT_PODMAN_MACHINE } else { "podman-machine-default" }),

    [string] $Image = "",

    [string] $EvidenceDir = "",

    [switch] $DryRun,

    [switch] $VerifyOnly,

    [switch] $Force
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutPodmanGpu.ps1"

try {
    Invoke-TowerScoutPodmanGpuEnablement `
        -MachineName $MachineName `
        -Image $Image `
        -EvidenceDir $EvidenceDir `
        -DryRun:$DryRun `
        -VerifyOnly:$VerifyOnly `
        -Force:$Force | Out-Null
}
catch {
    Write-Host "Podman GPU enablement failed: $($_.Exception.Message)"
    exit 1
}
