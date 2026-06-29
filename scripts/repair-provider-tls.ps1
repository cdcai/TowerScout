param(
    [ValidateSet("google", "azure")]
    [string] $Provider = "google",

    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [ValidateSet("off", "auto", "on")]
    [string] $Gpu = "off",

    [switch] $Build,

    [switch] $Apply,

    [string] $Thumbprint = "",

    [string] $CertificatePath = ""
)

$ErrorActionPreference = "Stop"

function Get-TowerScoutProviderTlsHost {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("google", "azure")]
        [string] $Name
    )

    if ($Name -eq "azure") {
        return "atlas.microsoft.com"
    }
    return "maps.googleapis.com"
}

function Normalize-TowerScoutThumbprint {
    param([string] $Value)
    return (($Value -replace "[^A-Fa-f0-9]", "").ToUpperInvariant())
}

function Test-TowerScoutCertificateIsCa {
    param(
        [Parameter(Mandatory = $true)]
        [System.Security.Cryptography.X509Certificates.X509Certificate2] $Certificate
    )

    foreach ($extension in $Certificate.Extensions) {
        if ($extension.Oid.Value -eq "2.5.29.19") {
            $basic = [System.Security.Cryptography.X509Certificates.X509BasicConstraintsExtension]::new($extension, $false)
            return [bool] $basic.CertificateAuthority
        }
    }
    return $false
}

function Test-TowerScoutCertificateCanSign {
    param(
        [Parameter(Mandatory = $true)]
        [System.Security.Cryptography.X509Certificates.X509Certificate2] $Certificate
    )

    foreach ($extension in $Certificate.Extensions) {
        if ($extension.Oid.Value -eq "2.5.29.15") {
            $keyUsage = [System.Security.Cryptography.X509Certificates.X509KeyUsageExtension]::new($extension, $false)
            return (($keyUsage.KeyUsages -band [System.Security.Cryptography.X509Certificates.X509KeyUsageFlags]::KeyCertSign) -ne 0)
        }
    }
    return $true
}

function Get-TowerScoutCertificateStoreMatches {
    param(
        [Parameter(Mandatory = $true)]
        [System.Security.Cryptography.X509Certificates.X509Certificate2] $Certificate
    )

    $thumbprint = Normalize-TowerScoutThumbprint $Certificate.Thumbprint
    $storePaths = @(
        "Cert:\LocalMachine\Root",
        "Cert:\CurrentUser\Root",
        "Cert:\LocalMachine\CA",
        "Cert:\CurrentUser\CA"
    )

    foreach ($storePath in $storePaths) {
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

function Get-TowerScoutStoreScore {
    param([string] $StorePath)

    switch -Regex ($StorePath) {
        "LocalMachine\\Root$" { return 100 }
        "CurrentUser\\Root$" { return 90 }
        "LocalMachine\\CA$" { return 70 }
        "CurrentUser\\CA$" { return 60 }
        default { return 10 }
    }
}

function Get-TowerScoutRemoteCertificateChain {
    param(
        [Parameter(Mandatory = $true)]
        [string] $HostName
    )

    $tcpClient = [System.Net.Sockets.TcpClient]::new()
    $callbackChainElements = [System.Collections.Generic.List[object]]::new()
    try {
        $tcpClient.Connect($HostName, 443)
        $validationCallback = {
            param($sender, $certificate, $chain, $sslPolicyErrors)

            $callbackChainElements.Clear()
            if ($null -ne $chain) {
                for ($index = 0; $index -lt $chain.ChainElements.Count; $index += 1) {
                    $chainCertificate = $chain.ChainElements[$index].Certificate
                    $callbackChainElements.Add([PSCustomObject]@{
                        Index = $index
                        Certificate = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($chainCertificate.RawData)
                    })
                }
            }

            return $true
        }
        $sslStream = [System.Net.Security.SslStream]::new(
            $tcpClient.GetStream(),
            $false,
            $validationCallback
        )
        try {
            $sslStream.AuthenticateAsClient($HostName)
            if ($null -eq $sslStream.RemoteCertificate) {
                throw "Remote host did not provide a certificate."
            }

            if ($callbackChainElements.Count -gt 0) {
                return $callbackChainElements
            }

            $leaf = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($sslStream.RemoteCertificate)
            $chain = [System.Security.Cryptography.X509Certificates.X509Chain]::new()
            $chain.ChainPolicy.RevocationMode = [System.Security.Cryptography.X509Certificates.X509RevocationMode]::NoCheck
            $chain.ChainPolicy.VerificationFlags = [System.Security.Cryptography.X509Certificates.X509VerificationFlags]::AllowUnknownCertificateAuthority
            [void] $chain.Build($leaf)

            $elements = [System.Collections.Generic.List[object]]::new()
            for ($index = 0; $index -lt $chain.ChainElements.Count; $index += 1) {
                $elements.Add([PSCustomObject]@{
                    Index = $index
                    Certificate = $chain.ChainElements[$index].Certificate
                })
            }
            return $elements
        }
        finally {
            $sslStream.Dispose()
        }
    }
    finally {
        $tcpClient.Dispose()
    }
}

function Select-TowerScoutTlsCaCandidate {
    param(
        [Parameter(Mandatory = $true)]
        [object[]] $ChainElements
    )

    $candidates = foreach ($element in $ChainElements) {
        $certificate = $element.Certificate
        if ($element.Index -eq 0) {
            continue
        }
        if (-not (Test-TowerScoutCertificateIsCa -Certificate $certificate)) {
            continue
        }

        $storeMatches = @(Get-TowerScoutCertificateStoreMatches -Certificate $certificate)
        $storePath = if ($storeMatches.Count -gt 0) { $storeMatches[0].StorePath } else { "" }
        $storeScore = if ($storePath) { Get-TowerScoutStoreScore -StorePath $storePath } else { 10 }
        $signingScore = if (Test-TowerScoutCertificateCanSign -Certificate $certificate) { 5 } else { 0 }
        $chainDepthScore = [int] $element.Index

        [PSCustomObject]@{
            Thumbprint = $certificate.Thumbprint
            Subject = $certificate.Subject
            Issuer = $certificate.Issuer
            NotAfter = $certificate.NotAfter
            StorePath = $storePath
            Score = $storeScore + $signingScore + $chainDepthScore
        }
    }

    return @($candidates | Sort-Object -Property Score -Descending)
}

function Format-TowerScoutImportCommand {
    param(
        [string] $SelectedThumbprint,
        [string] $SelectedCertificatePath
    )

    $parts = @(
        "scripts\import-tls-ca.cmd",
        "-Engine", $Engine,
        "-Gpu", $Gpu,
        "-VerifyProvider", $Provider
    )
    if ($Build) {
        $parts += "-Build"
    }
    if (-not [string]::IsNullOrWhiteSpace($SelectedThumbprint)) {
        $parts += @("-Thumbprint", $SelectedThumbprint)
    }
    if (-not [string]::IsNullOrWhiteSpace($SelectedCertificatePath)) {
        $parts += @("-CertificatePath", "`"$SelectedCertificatePath`"")
    }
    return ($parts -join " ")
}

function Format-TowerScoutRepairCommand {
    param(
        [string] $SelectedThumbprint,
        [string] $SelectedCertificatePath
    )

    $parts = @(
        "scripts\repair-provider-tls.cmd",
        "-Provider", $Provider,
        "-Engine", $Engine,
        "-Gpu", $Gpu,
        "-Apply"
    )
    if ($Build) {
        $parts += "-Build"
    }
    if (-not [string]::IsNullOrWhiteSpace($SelectedThumbprint)) {
        $parts += @("-Thumbprint", $SelectedThumbprint)
    }
    if (-not [string]::IsNullOrWhiteSpace($SelectedCertificatePath)) {
        $parts += @("-CertificatePath", "`"$SelectedCertificatePath`"")
    }
    return ($parts -join " ")
}

function Invoke-TowerScoutImport {
    param(
        [string] $SelectedThumbprint,
        [string] $SelectedCertificatePath
    )

    $importCommand = Join-Path $PSScriptRoot "import-tls-ca.cmd"
    $arguments = @(
        "-Engine",
        $Engine,
        "-Gpu",
        $Gpu,
        "-VerifyProvider",
        $Provider
    )
    if ($Build) {
        $arguments += "-Build"
    }
    if (-not [string]::IsNullOrWhiteSpace($SelectedThumbprint)) {
        $arguments += @("-Thumbprint", $SelectedThumbprint)
    }
    if (-not [string]::IsNullOrWhiteSpace($SelectedCertificatePath)) {
        $arguments += @("-CertificatePath", $SelectedCertificatePath)
    }

    & $importCommand @arguments
    return $LASTEXITCODE
}

if (-not [string]::IsNullOrWhiteSpace($Thumbprint) -and -not [string]::IsNullOrWhiteSpace($CertificatePath)) {
    throw "Specify only one of -Thumbprint or -CertificatePath."
}

$hostName = Get-TowerScoutProviderTlsHost -Name $Provider
$selectedThumbprint = Normalize-TowerScoutThumbprint $Thumbprint
$selectedCertificatePath = $CertificatePath

Write-Host "TowerScout provider TLS repair"
Write-Host "  provider=$Provider"
Write-Host "  host=$hostName"
Write-Host "  engine=$Engine"
Write-Host "  gpu=$Gpu"
Write-Host "  mode=$(if ($Apply) { 'apply' } else { 'dry-run' })"
Write-Host "No API keys or provider response bodies are used by this repair wrapper."
Write-Host "Support-sensitive local output: certificate subjects and thumbprints can identify your organization. Do not paste dry-run output into public issue comments or public release evidence."

if ([string]::IsNullOrWhiteSpace($selectedThumbprint) -and [string]::IsNullOrWhiteSpace($selectedCertificatePath)) {
    Write-Host "Inspecting Windows TLS certificate chain for $hostName..."
    $chainElements = @(Get-TowerScoutRemoteCertificateChain -HostName $hostName)
    foreach ($element in $chainElements) {
        $certificate = $element.Certificate
        Write-Host ("  chain[{0}] subject={1}" -f $element.Index, $certificate.Subject)
        Write-Host ("           issuer={0}" -f $certificate.Issuer)
        Write-Host ("           thumbprint={0}" -f $certificate.Thumbprint)
    }

    $candidates = @(Select-TowerScoutTlsCaCandidate -ChainElements $chainElements)
    if ($candidates.Count -eq 0) {
        Write-Host "No CA certificate candidate was found in the remote Windows chain."
        Write-Host "Provide a CA certificate explicitly with -Thumbprint or -CertificatePath."
        exit 2
    }

    Write-Host "CA candidates:"
    foreach ($candidate in $candidates) {
        $store = if ($candidate.StorePath) { $candidate.StorePath } else { "not found in searched stores" }
        Write-Host ("  score={0} thumbprint={1}" -f $candidate.Score, $candidate.Thumbprint)
        Write-Host ("       store={0}" -f $store)
        Write-Host ("       subject={0}" -f $candidate.Subject)
    }

    $topCandidate = $candidates[0]
    if ($candidates.Count -gt 1 -and $candidates[0].Score -eq $candidates[1].Score) {
        Write-Host "Multiple CA candidates have the same score. Re-run with -Thumbprint for the intended organization/root CA."
        exit 2
    }

    $selectedThumbprint = Normalize-TowerScoutThumbprint $topCandidate.Thumbprint
    Write-Host "Selected CA thumbprint: $selectedThumbprint"
}

$importCommand = Format-TowerScoutImportCommand -SelectedThumbprint $selectedThumbprint -SelectedCertificatePath $selectedCertificatePath
$repairCommand = Format-TowerScoutRepairCommand -SelectedThumbprint $selectedThumbprint -SelectedCertificatePath $selectedCertificatePath
if (-not $Apply) {
    Write-Host "Dry run only. To apply the repair, run:"
    Write-Host "  $repairCommand"
    Write-Host "The apply path imports the selected CA into the TowerScout container bundle and verifies provider TLS without printing response bodies."
    exit 0
}

Write-Host "Applying TLS CA repair with:"
Write-Host "  $importCommand"
$exitCode = Invoke-TowerScoutImport -SelectedThumbprint $selectedThumbprint -SelectedCertificatePath $selectedCertificatePath
exit $exitCode
