param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [int] $Port = $(if ($env:TOWERSCOUT_PORT) { [int] $env:TOWERSCOUT_PORT } else { 5000 })
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

Invoke-TowerScoutCompose -Engine $Engine -ComposeArguments @("ps")
$composeExitCode = $script:TowerScoutComposeExitCode
if ($composeExitCode -ne 0) {
    exit $composeExitCode
}

$readinessUrl = "http://127.0.0.1:$Port/api/readiness"
try {
    $request = [System.Net.HttpWebRequest]::Create($readinessUrl)
    $request.Timeout = 5000
    try {
        $response = $request.GetResponse()
    }
    catch [System.Net.WebException] {
        if ($_.Exception.Response -eq $null) {
            throw
        }
        $response = $_.Exception.Response
    }

    $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
    try {
        $body = $reader.ReadToEnd()
    }
    finally {
        $reader.Close()
        $response.Close()
    }

    $readiness = $body | ConvertFrom-Json
    $readiness | ConvertTo-Json -Depth 8
    if ($readiness.state -eq "fatal") {
        exit 1
    }
    exit 0
}
catch {
    Write-Warning "TowerScout readiness endpoint is not reachable at $readinessUrl."
    exit 2
}
