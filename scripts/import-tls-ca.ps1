param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [switch] $Build,

    [string] $Thumbprint = "",

    [string] $CertificatePath = "",

    [string] $ContainerCertificateName = "local-ca.pem",

    [string] $BundleName = "towerscout-ca-bundle.pem"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"

if ([string]::IsNullOrWhiteSpace($Thumbprint) -and [string]::IsNullOrWhiteSpace($CertificatePath)) {
    throw "Specify either -Thumbprint for a Windows certificate store entry or -CertificatePath for a PEM/CER/CRT file."
}
if (-not [string]::IsNullOrWhiteSpace($Thumbprint) -and -not [string]::IsNullOrWhiteSpace($CertificatePath)) {
    throw "Specify only one of -Thumbprint or -CertificatePath."
}

function Convert-CertificateToPem {
    param(
        [Parameter(Mandatory = $true)]
        [byte[]] $RawData
    )

    $base64 = [Convert]::ToBase64String($RawData)
    $builder = [System.Text.StringBuilder]::new()
    [void] $builder.AppendLine("-----BEGIN CERTIFICATE-----")
    for ($index = 0; $index -lt $base64.Length; $index += 64) {
        $length = [Math]::Min(64, $base64.Length - $index)
        [void] $builder.AppendLine($base64.Substring($index, $length))
    }
    [void] $builder.AppendLine("-----END CERTIFICATE-----")
    return $builder.ToString()
}

function Get-CertificateFromStore {
    param(
        [Parameter(Mandatory = $true)]
        [string] $CertificateThumbprint
    )

    $normalizedThumbprint = ($CertificateThumbprint -replace "[^A-Fa-f0-9]", "").ToUpperInvariant()
    if ($normalizedThumbprint.Length -eq 0) {
        throw "Certificate thumbprint is empty after normalization."
    }

    $storePaths = @(
        "Cert:\CurrentUser\Root",
        "Cert:\CurrentUser\CA",
        "Cert:\LocalMachine\Root",
        "Cert:\LocalMachine\CA"
    )

    $matches = foreach ($storePath in $storePaths) {
        Get-ChildItem -Path $storePath -ErrorAction SilentlyContinue |
            Where-Object { ($_.Thumbprint -replace "[^A-Fa-f0-9]", "").ToUpperInvariant() -eq $normalizedThumbprint }
    }

    if ($null -eq $matches -or @($matches).Count -eq 0) {
        throw "No Windows certificate store entry found for thumbprint $CertificateThumbprint."
    }
    if (@($matches).Count -gt 1) {
        Write-Host "Multiple matching certificates found; using the first match."
    }

    return @($matches)[0]
}

function Get-PemFromFile {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    $resolvedPath = Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue
    if ($null -eq $resolvedPath) {
        throw "Certificate file not found: $Path"
    }

    $text = Get-Content -LiteralPath $resolvedPath.Path -Raw -ErrorAction SilentlyContinue
    if ($text -match "-----BEGIN CERTIFICATE-----") {
        return $text
    }

    $certificate = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($resolvedPath.Path)
    return Convert-CertificateToPem -RawData $certificate.RawData
}

$pemText = ""
$sourceDescription = ""
if (-not [string]::IsNullOrWhiteSpace($Thumbprint)) {
    $certificate = Get-CertificateFromStore -CertificateThumbprint $Thumbprint
    $chain = [System.Security.Cryptography.X509Certificates.X509Chain]::new()
    $chain.ChainPolicy.RevocationMode = [System.Security.Cryptography.X509Certificates.X509RevocationMode]::NoCheck
    [void] $chain.Build($certificate)

    $seenThumbprints = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $pemParts = [System.Collections.Generic.List[string]]::new()
    foreach ($element in $chain.ChainElements) {
        $chainCertificate = $element.Certificate
        if ($seenThumbprints.Add($chainCertificate.Thumbprint)) {
            $pemParts.Add((Convert-CertificateToPem -RawData $chainCertificate.RawData))
        }
    }

    $pemText = ($pemParts -join [Environment]::NewLine)
    $sourceDescription = "$($certificate.Subject) [$($certificate.Thumbprint)] plus Windows chain"
}
else {
    $pemText = Get-PemFromFile -Path $CertificatePath
    $sourceDescription = (Resolve-Path -LiteralPath $CertificatePath).Path
}

$tempPem = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-ca-{0}.pem" -f ([Guid]::NewGuid().ToString("N")))
Set-Content -LiteralPath $tempPem -Value $pemText -Encoding ASCII

$containerCertDir = "/app/webapp/config/certs"
$containerCertPath = "$containerCertDir/$ContainerCertificateName"
$containerBundlePath = "$containerCertDir/$BundleName"

try {
    Write-Host "Starting TowerScout container so the persistent config volume is available..."
    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @("up", "-d", "towerscout")
    if ($script:TowerScoutComposeExitCode -ne 0) {
        exit $script:TowerScoutComposeExitCode
    }

    Write-Host "Creating container certificate directory..."
    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @(
        "exec",
        "-T",
        "towerscout",
        "mkdir",
        "-p",
        $containerCertDir
    )
    if ($script:TowerScoutComposeExitCode -ne 0) {
        exit $script:TowerScoutComposeExitCode
    }

    Write-Host "Importing TLS CA certificate from $sourceDescription..."
    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @(
        "cp",
        $tempPem,
        "towerscout:$containerCertPath"
    )
    if ($script:TowerScoutComposeExitCode -ne 0) {
        exit $script:TowerScoutComposeExitCode
    }

    $bundleScript = "cat /etc/ssl/certs/ca-certificates.crt '$containerCertPath' > '$containerBundlePath' && chmod 0644 '$containerCertPath' '$containerBundlePath'"
    Write-Host "Building combined CA bundle at $containerBundlePath..."
    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @(
        "exec",
        "-T",
        "towerscout",
        "sh",
        "-c",
        $bundleScript
    )
    if ($script:TowerScoutComposeExitCode -ne 0) {
        exit $script:TowerScoutComposeExitCode
    }

    $pythonVerify = "import requests; r=requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=test&key=invalid', timeout=10); print('google_tls_status=' + str(r.status_code)); print('google_tls_body=' + r.text[:80].replace(chr(10), ' ')); raise SystemExit(0 if r.status_code == 200 else 1)"
    Write-Host "Verifying Google TLS through the combined CA bundle..."
    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -ComposeArguments @(
        "exec",
        "-T",
        "towerscout",
        "env",
        "REQUESTS_CA_BUNDLE=$containerBundlePath",
        "SSL_CERT_FILE=$containerBundlePath",
        "python",
        "-c",
        $pythonVerify
    )
    if ($script:TowerScoutComposeExitCode -ne 0) {
        exit $script:TowerScoutComposeExitCode
    }

    Write-Host "Imported CA bundle:"
    Write-Host "  REQUESTS_CA_BUNDLE=$containerBundlePath"
    Write-Host "  SSL_CERT_FILE=$containerBundlePath"
}
finally {
    if (Test-Path -LiteralPath $tempPem) {
        Remove-Item -LiteralPath $tempPem -Force
    }
}

exit $script:TowerScoutComposeExitCode
