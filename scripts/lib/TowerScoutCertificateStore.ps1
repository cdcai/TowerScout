function Normalize-TowerScoutThumbprint {
    param([string] $Value)

    return (($Value -replace "[^A-Fa-f0-9]", "").ToUpperInvariant())
}

function Get-TowerScoutCertificateStorePaths {
    return @(
        "Cert:\LocalMachine\Root",
        "Cert:\CurrentUser\Root",
        "Cert:\LocalMachine\CA",
        "Cert:\CurrentUser\CA"
    )
}

function Get-TowerScoutCertificateStoreMatches {
    param(
        [Parameter(Mandatory = $true)]
        [System.Security.Cryptography.X509Certificates.X509Certificate2] $Certificate
    )

    $thumbprint = Normalize-TowerScoutThumbprint $Certificate.Thumbprint
    foreach ($storePath in Get-TowerScoutCertificateStorePaths) {
        Get-ChildItem -Path $storePath -ErrorAction SilentlyContinue |
            Where-Object { (Normalize-TowerScoutThumbprint $_.Thumbprint) -eq $thumbprint } |
            ForEach-Object {
                [PSCustomObject]@{
                    StorePath = $storePath
                    Certificate = $_
                }
            }
    }
}

function Get-TowerScoutCertificateFromStore {
    param(
        [Parameter(Mandatory = $true)]
        [string] $CertificateThumbprint
    )

    $normalizedThumbprint = Normalize-TowerScoutThumbprint $CertificateThumbprint
    if ($normalizedThumbprint.Length -eq 0) {
        throw "Certificate thumbprint is empty after normalization."
    }

    $matches = foreach ($storePath in Get-TowerScoutCertificateStorePaths) {
        Get-ChildItem -Path $storePath -ErrorAction SilentlyContinue |
            Where-Object { (Normalize-TowerScoutThumbprint $_.Thumbprint) -eq $normalizedThumbprint }
    }

    if ($null -eq $matches -or @($matches).Count -eq 0) {
        throw "No Windows certificate store entry found for thumbprint $CertificateThumbprint."
    }
    if (@($matches).Count -gt 1) {
        Write-Host "Multiple matching certificates found; using the first match."
    }

    return @($matches)[0]
}