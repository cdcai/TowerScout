param(
    [ValidateSet("auto", "docker", "podman")]
    [string] $Engine = "auto",

    [ValidateSet("off", "auto", "on")]
    [string] $Gpu = "off",

    [ValidateRange(1, 65535)]
    [Nullable[int]] $Port = $null,

    [switch] $Build,

    [string] $Thumbprint = "",

    [string] $CertificatePath = "",

    [switch] $RefreshExisting,

    [string] $ContainerCertificateName = "local-ca.pem",

    [string] $BundleName = "towerscout-ca-bundle.pem",

    [ValidateSet("auto", "google", "azure", "none")]
    [string] $VerifyProvider = "auto"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\lib\TowerScoutCompose.ps1"
. "$PSScriptRoot\lib\TowerScoutCertificateStore.ps1"

$repoRoot = Get-TowerScoutRepoRoot
$portWasSpecified = $PSBoundParameters.ContainsKey("Port")

if ($RefreshExisting -and ($Thumbprint -or $CertificatePath)) {
    throw "Use -RefreshExisting alone to reuse previously approved container CA material."
}
foreach ($name in @($ContainerCertificateName, $BundleName)) {
    if ($name -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,100}\.pem$') {
        throw "Certificate and bundle names must be simple PEM filenames."
    }
}
if (-not $RefreshExisting -and [string]::IsNullOrWhiteSpace($Thumbprint) -and [string]::IsNullOrWhiteSpace($CertificatePath)) {
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
    $certificate = Get-TowerScoutCertificateFromStore -CertificateThumbprint $Thumbprint
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
elseif (-not $RefreshExisting) {
    $pemText = Get-PemFromFile -Path $CertificatePath
    $sourceDescription = (Resolve-Path -LiteralPath $CertificatePath).Path
}

$tempPem = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-ca-{0}.pem" -f ([Guid]::NewGuid().ToString("N")))
Set-Content -LiteralPath $tempPem -Value $pemText -Encoding ASCII

$containerCertDir = "/app/webapp/config/certs"
$containerCertPath = "$containerCertDir/$ContainerCertificateName"
$candidateId = [Guid]::NewGuid().ToString("N")
if (-not $RefreshExisting) {
    $containerCertPath = "$containerCertDir/$candidateId-$ContainerCertificateName"
}
$containerBundlePath = "$containerCertDir/$candidateId-$BundleName"
$containerStagingPath = "/tmp/towerscout-ca-$candidateId.pem"
$trustPromoted = $false
$stagingCopied = $false

function Set-TowerScoutEnvFileValues {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [hashtable] $Values
    )

    $envPath = Join-Path $RootPath ".env"
    if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
        throw "Expected .env to exist after initialization: $envPath"
    }

    $lines = [System.Collections.Generic.List[string]]::new()
    foreach ($line in Get-Content -LiteralPath $envPath) {
        $lines.Add([string] $line)
    }

    $updated = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    for ($index = 0; $index -lt $lines.Count; $index += 1) {
        $lineText = [string] $lines[$index]
        if ($lineText.TrimStart().StartsWith("#")) {
            continue
        }

        foreach ($name in $Values.Keys) {
            $pattern = "^\s*" + [regex]::Escape([string] $name) + "\s*="
            if ($lineText -match $pattern) {
                if ($updated.Add([string] $name)) {
                    $lines[$index] = "$name=$($Values[$name])"
                }
                else {
                    # Keep one authoritative entry; later duplicates can override it.
                    $lines.RemoveAt($index)
                    $index -= 1
                }
                break
            }
        }
    }

    foreach ($name in $Values.Keys) {
        if (-not $updated.Contains([string] $name)) {
            $lines.Add("$name=$($Values[$name])")
        }
    }

    $candidateEnv = "$envPath.tls-$candidateId"
    $backupEnv = "$envPath.backup.tls-$candidateId"
    try {
        [System.IO.File]::WriteAllLines($candidateEnv, $lines, [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::Replace($candidateEnv, $envPath, $backupEnv)
    }
    finally {
        if (Test-Path -LiteralPath $candidateEnv) { Remove-Item -LiteralPath $candidateEnv -Force }
    }
}

function Resolve-TowerScoutTlsVerifyProvider {
    if ($VerifyProvider -ne "auto") {
        return $VerifyProvider
    }

    $defaultProvider = $env:DEFAULT_MAP_PROVIDER
    if ([string]::IsNullOrWhiteSpace($defaultProvider)) {
        $envPath = Join-Path (Get-TowerScoutRepoRoot) ".env"
        if (Test-Path -LiteralPath $envPath -PathType Leaf) {
            $providerLine = Get-Content -LiteralPath $envPath |
                Where-Object { $_ -match "^\s*DEFAULT_MAP_PROVIDER\s*=" } |
                Select-Object -Last 1
            if (-not [string]::IsNullOrWhiteSpace($providerLine)) {
                $defaultProvider = ($providerLine -replace "^\s*DEFAULT_MAP_PROVIDER\s*=", "").Trim()
            }
        }
    }

    if ($defaultProvider -match "^(?i:azure)$") {
        return "azure"
    }

    return "google"
}

function Get-TowerScoutTlsVerificationScript {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("google", "azure")]
        [string] $Provider
    )

    if ($Provider -eq "azure") {
        return @'
import requests
try:
    r = requests.get("https://atlas.microsoft.com/map/attribution", params={"api-version": "2024-04-01"}, timeout=10)
    ok = r.status_code in (200, 400, 401, 403)
    print("azure_tls_status=" + str(r.status_code))
    print("azure_tls_category=" + ("tls_ok" if ok else "provider_http_error"))
    raise SystemExit(0 if ok else 1)
except requests.exceptions.SSLError:
    print("azure_tls_status=unavailable")
    print("azure_tls_category=tls_certificate_error")
    raise SystemExit(1)
except requests.exceptions.RequestException:
    print("azure_tls_status=unavailable")
    print("azure_tls_category=network_error")
    raise SystemExit(1)
'@
    }

    return @'
import requests
try:
    r = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params={"address": "test"}, timeout=10)
    ok = r.status_code in (200, 400, 401, 403)
    print("google_tls_status=" + str(r.status_code))
    print("google_tls_category=" + ("tls_ok" if ok else "provider_http_error"))
    raise SystemExit(0 if ok else 1)
except requests.exceptions.SSLError:
    print("google_tls_status=unavailable")
    print("google_tls_category=tls_certificate_error")
    raise SystemExit(1)
except requests.exceptions.RequestException:
    print("google_tls_status=unavailable")
    print("google_tls_category=network_error")
    raise SystemExit(1)
'@
}

function Copy-TowerScoutFileIntoContainer {
    param(
        [Parameter(Mandatory = $true)]
        [string] $LocalPath,

        [Parameter(Mandatory = $true)]
        [string] $ContainerPath
    )

    Copy-TowerScoutContainerPath `
        -Engine $Engine `
        -LocalPath $LocalPath `
        -ContainerPath $ContainerPath `
        -Build:$Build `
        -Gpu $Gpu
}

function Invoke-TowerScoutTlsProviderVerification {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("google", "azure")]
        [string] $Provider,

        [Parameter(Mandatory = $true)]
        [string] $ContainerBundlePath
    )

    $pythonVerify = Get-TowerScoutTlsVerificationScript -Provider $Provider
    $verifyId = [Guid]::NewGuid().ToString("N")
    $localVerifyPath = Join-Path ([System.IO.Path]::GetTempPath()) "towerscout-tls-verify-$verifyId.py"
    $containerVerifyPath = "/tmp/towerscout-tls-verify-$verifyId.py"
    $copiedVerifyScript = $false

    Set-Content -LiteralPath $localVerifyPath -Value $pythonVerify -Encoding ASCII

    try {
        Copy-TowerScoutFileIntoContainer -LocalPath $localVerifyPath -ContainerPath $containerVerifyPath
        if ($script:TowerScoutComposeExitCode -ne 0) {
            return
        }
        $copiedVerifyScript = $true

        Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
            "exec",
            "-T",
            "towerscout",
            "env",
            "REQUESTS_CA_BUNDLE=$ContainerBundlePath",
            "SSL_CERT_FILE=$ContainerBundlePath",
            "python",
            $containerVerifyPath
        )
    }
    finally {
        if (Test-Path -LiteralPath $localVerifyPath) {
            Remove-Item -LiteralPath $localVerifyPath -Force
        }

        if ($copiedVerifyScript) {
            $verificationExitCode = $script:TowerScoutComposeExitCode
            try {
                Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
                    "exec",
                    "-T",
                    "towerscout",
                    "rm",
                    "-f",
                    $containerVerifyPath
                )
            }
            catch {
                Write-Host "Warning: could not remove temporary TLS verification script from the container."
            }
            $script:TowerScoutComposeExitCode = $verificationExitCode
        }
    }
}

$trustLock = $null
try {
    $trustLock = [System.IO.File]::Open((Join-Path $repoRoot ".tls-import.lock"), [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    Initialize-TowerScoutEnvFile -RootPath $repoRoot
    if ($portWasSpecified) {
        Set-TowerScoutPortEnvironment -Port $Port | Out-Null
    }
    else {
        Set-TowerScoutPortEnvironment | Out-Null
    }
    if ($RefreshExisting -and -not $PSBoundParameters.ContainsKey("ContainerCertificateName")) {
        $recordedCa = Get-TowerScoutEnvFileValueFromPath -Path (Join-Path $repoRoot ".env") -Name "TOWERSCOUT_TLS_APPROVED_CA"
        if ($recordedCa) {
            if ($recordedCa -notmatch '^/app/webapp/config/certs/[A-Za-z0-9][A-Za-z0-9._-]{0,150}\.pem$') {
                throw "Recorded approved CA path is invalid; select the approved CA explicitly."
            }
            $containerCertPath = $recordedCa
        }
    }
    Write-Host "Starting TowerScout container so the persistent config volume is available..."
    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @("up", "-d", "towerscout")
    if ($script:TowerScoutComposeExitCode -ne 0) {
        exit $script:TowerScoutComposeExitCode
    }

    Write-Host "Creating container certificate directory..."
    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
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

    if (-not $RefreshExisting) {
        Write-Host "Importing approved TLS CA certificate into a new candidate file..."
        $stagingCopied = $true
        Copy-TowerScoutFileIntoContainer -LocalPath $tempPem -ContainerPath $containerStagingPath
        if ($script:TowerScoutComposeExitCode -ne 0) {
            exit $script:TowerScoutComposeExitCode
        }
    }

    $approvedInputPath = if ($RefreshExisting) { $containerCertPath } else { $containerStagingPath }

    Write-Host "Building combined CA bundle at $containerBundlePath..."
    Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
        "exec",
        "-T",
        "towerscout",
        "python",
        "/app/webapp/ts_trust.py",
        "--approved-ca", $approvedInputPath,
        "--destination", $containerBundlePath
    )
    if ($script:TowerScoutComposeExitCode -ne 0) {
        exit $script:TowerScoutComposeExitCode
    }

    $resolvedVerifyProvider = Resolve-TowerScoutTlsVerifyProvider
    if ($resolvedVerifyProvider -eq "none") {
        Write-Host "Skipping remote TLS verification by request."
    }
    else {
        Write-Host "Verifying $resolvedVerifyProvider TLS through the combined CA bundle..."
        Invoke-TowerScoutTlsProviderVerification -Provider $resolvedVerifyProvider -ContainerBundlePath $containerBundlePath
        if ($script:TowerScoutComposeExitCode -ne 0) {
            Write-Host "Provider TLS verification failed; .env was not updated."
            Write-Host "Re-run scripts\repair-provider-tls.cmd in dry-run mode and use the selected CA, or provide a full PEM CA chain with -CertificatePath."
            exit $script:TowerScoutComposeExitCode
        }
    }

    if (-not $RefreshExisting) {
        # Only validated CA-only bytes enter persistent storage.
        Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments @(
            "exec", "-T", "towerscout", "cp", "--", $containerStagingPath, $containerCertPath
        )
        if ($script:TowerScoutComposeExitCode -ne 0) { exit $script:TowerScoutComposeExitCode }
    }
    Set-TowerScoutEnvFileValues -RootPath $repoRoot -Values @{
        REQUESTS_CA_BUNDLE = $containerBundlePath
        SSL_CERT_FILE = $containerBundlePath
        TOWERSCOUT_TLS_APPROVED_CA = $containerCertPath
    }
    $trustPromoted = $true

    Write-Host "Imported CA bundle:"
    Write-Host "  REQUESTS_CA_BUNDLE=$containerBundlePath"
    Write-Host "  SSL_CERT_FILE=$containerBundlePath"
    Write-Host "Updated .env so future TowerScout starts use the combined CA bundle."
    Write-Host "Restart TowerScout for the updated TLS settings to take effect."
}
finally {
    $savedExitCode = $script:TowerScoutComposeExitCode
    try {
        $ownedCandidates = @()
        if ($stagingCopied) { $ownedCandidates += $containerStagingPath }
        if (-not $trustPromoted) {
            $ownedCandidates += $containerBundlePath
            if (-not $RefreshExisting) { $ownedCandidates += $containerCertPath }
        }
        if ($ownedCandidates.Count -gt 0) {
            Invoke-TowerScoutCompose -Engine $Engine -Build:$Build -Gpu $Gpu -ComposeArguments (
                @("exec", "-T", "towerscout", "rm", "-f", "--") + $ownedCandidates
            )
        }
    }
    catch { Write-Host "Warning: could not remove newly owned TLS staging files; preserve active trust and retry cleanup." }
    $script:TowerScoutComposeExitCode = $savedExitCode
    if ($null -ne $trustLock) { $trustLock.Dispose() }
    if (Test-Path -LiteralPath $tempPem) {
        Remove-Item -LiteralPath $tempPem -Force
    }
}

exit $script:TowerScoutComposeExitCode
