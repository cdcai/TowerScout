Set-StrictMode -Version Latest

. (Join-Path $PSScriptRoot "TowerScoutHostHelperState.ps1")

$script:TowerScoutHostHelperVersion = "0.4.0-gate3-review"
$script:TowerScoutHostHelperReadTimeoutMs = 5000
$script:TowerScoutHostHelperMaxRequestLineLength = 4096
$script:TowerScoutHostHelperMaxHeaderLines = 64
$script:TowerScoutHostHelperMaxHeaderBytes = 16384
$script:TowerScoutHostHelperMaxBodyBytes = 4096
$script:TowerScoutHostHelperProviderTlsRepairConfirmation = "repair_tls_and_restart"
$script:TowerScoutHostHelperOperationTimeoutSeconds = 900
$script:TowerScoutHostHelperOperationStatusRetentionSeconds = 3600
$script:TowerScoutHostHelperReplayRetentionSeconds = 900
$script:TowerScoutHostHelperSessionTtlSeconds = 43200
$script:TowerScoutHostHelperHeartbeatIntervalSeconds = 2
$script:TowerScoutHostHelperHeartbeatStaleSeconds = 10
$script:TowerScoutHostHelperPackageMutexWaitMilliseconds = 5000
$script:TowerScoutHostHelperLauncherReadinessTimeoutSeconds = 15
$script:TowerScoutHostHelperOperationAuthorizationPattern = "^(?:[A-Za-z0-9_-]{32,128}|v1\.[A-Za-z0-9_-]{80,768}\.[A-Za-z0-9_-]{43})$"
$script:TowerScoutHostHelperSignedAuthorizationPattern = "^v1\.[A-Za-z0-9_-]{80,768}\.[A-Za-z0-9_-]{43}$"
$script:TowerScoutHostHelperBrowserAuthorizationAudience = "towerscout-host-helper"
$script:TowerScoutHostHelperBrowserAuthorizationMaxTtlSeconds = 900
$script:TowerScoutHostHelperBrowserAuthorizationClockSkewSeconds = 300
$script:TowerScoutHostHelperExecutionEnabledByDefault = $false
$script:TowerScoutHostHelperLaunchReadinessTimeoutSeconds = 180
$script:TowerScoutHostHelperStartTimeoutHeadroomSeconds = 60
$script:TowerScoutHostHelperProcessTreeCleanupTimeoutMs = 10000
$script:TowerScoutHostHelperProcessOutputDrainTimeoutMs = 5000
$script:TowerScoutHostHelperOperationStepTimeoutSeconds = @{
    repair = 300
    stop = 120
    start = ($script:TowerScoutHostHelperLaunchReadinessTimeoutSeconds + $script:TowerScoutHostHelperStartTimeoutHeadroomSeconds)
}
$script:TowerScoutHostHelperOperationCommandScripts = @{
    repair = "scripts\repair-provider-tls.cmd"
    stop = "scripts\stop.cmd"
    start = "start.bat"
}

function New-TowerScoutHostHelperToken {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $rng.GetBytes($bytes)
    }
    finally {
        $rng.Dispose()
    }

    return ([Convert]::ToBase64String($bytes).TrimEnd("=") -replace "\+", "-" -replace "/", "_")
}

function ConvertFrom-TowerScoutHostHelperBase64Url {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Value
    )

    $normalized = $Value.Replace("-", "+").Replace("_", "/")
    switch ($normalized.Length % 4) {
        0 {}
        2 { $normalized += "==" }
        3 { $normalized += "=" }
        default { throw "Invalid base64url value." }
    }
    return [Convert]::FromBase64String($normalized)
}

function ConvertTo-TowerScoutHostHelperBase64Url {
    param(
        [byte[]] $Value = @()
    )

    return ([Convert]::ToBase64String($Value).TrimEnd("=") -replace "\+", "-" -replace "/", "_")
}

function Test-TowerScoutHostHelperFixedTimeEquals {
    param(
        [byte[]] $Expected = @(),

        [byte[]] $Actual = @()
    )

    if ($Expected.Length -ne $Actual.Length) {
        return $false
    }

    [int] $difference = 0
    for ($index = 0; $index -lt $Expected.Length; $index++) {
        $difference = $difference -bor ($Expected[$index] -bxor $Actual[$index])
    }
    return $difference -eq 0
}

function Test-TowerScoutHostHelperFixedTimeStringEquals {
    param(
        [string] $Expected = "",

        [string] $Actual = ""
    )

    $encoding = [System.Text.Encoding]::UTF8
    return Test-TowerScoutHostHelperFixedTimeEquals `
        -Expected $encoding.GetBytes($Expected) `
        -Actual $encoding.GetBytes($Actual)
}

function Resolve-TowerScoutHostHelperBrowserAuthorization {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [string] $Authorization = "",

        [Parameter(Mandatory = $true)]
        [ValidateSet("helper_probe", "provider_tls_repair", "operation_status")]
        [string] $ExpectedScope,

        [string] $ExpectedProvider = "",

        [string] $ExpectedOperationId = ""
    )

    $rejected = [pscustomobject]@{
        Accepted = $false
        State = "rejected_operation_authorization"
        Provider = ""
        Scope = ""
        OperationId = ""
    }
    if ($Authorization -notmatch $script:TowerScoutHostHelperSignedAuthorizationPattern) {
        return $rejected
    }

    $authorizationKey = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "BrowserAuthorizationKey"
    if ($authorizationKey -notmatch "^[A-Za-z0-9_-]{43}$") {
        return $rejected
    }

    try {
        $segments = $Authorization.Split(".")
        if ($segments.Count -ne 3 -or $segments[0] -ne "v1") {
            return $rejected
        }

        $keyBytes = ConvertFrom-TowerScoutHostHelperBase64Url -Value $authorizationKey
        if ($keyBytes.Length -ne 32) {
            return $rejected
        }
        $signingInput = [System.Text.Encoding]::ASCII.GetBytes("v1.$($segments[1])")
        $hmac = New-Object System.Security.Cryptography.HMACSHA256(,$keyBytes)
        try {
            $expectedSignature = $hmac.ComputeHash($signingInput)
        }
        finally {
            $hmac.Dispose()
        }
        $actualSignature = ConvertFrom-TowerScoutHostHelperBase64Url -Value $segments[2]
        if (-not (Test-TowerScoutHostHelperFixedTimeEquals -Expected $expectedSignature -Actual $actualSignature)) {
            return $rejected
        }

        $payloadBytes = ConvertFrom-TowerScoutHostHelperBase64Url -Value $segments[1]
        if (-not (Test-TowerScoutHostHelperAsciiBytes -Bytes $payloadBytes)) {
            return $rejected
        }
        $payload = [System.Text.Encoding]::ASCII.GetString($payloadBytes) | ConvertFrom-Json -ErrorAction Stop
        $audience = Get-TowerScoutHostHelperObjectValue -InputObject $payload -Name "aud"
        $scope = Get-TowerScoutHostHelperObjectValue -InputObject $payload -Name "scope"
        $provider = (Get-TowerScoutHostHelperObjectValue -InputObject $payload -Name "provider").Trim().ToLowerInvariant()
        $sessionId = Get-TowerScoutHostHelperObjectValue -InputObject $payload -Name "session_id"
        $operationId = (Get-TowerScoutHostHelperObjectValue -InputObject $payload -Name "operation_id").Trim().ToLowerInvariant()
        $version = Get-TowerScoutHostHelperObjectValue -InputObject $payload -Name "v"
        [long] $issuedAt = 0
        [long] $expiresAt = 0
        if (-not [long]::TryParse((Get-TowerScoutHostHelperObjectValue -InputObject $payload -Name "iat"), [ref] $issuedAt)) {
            return $rejected
        }
        if (-not [long]::TryParse((Get-TowerScoutHostHelperObjectValue -InputObject $payload -Name "exp"), [ref] $expiresAt)) {
            return $rejected
        }

        if ($version -ne "1" -or $audience -ne $script:TowerScoutHostHelperBrowserAuthorizationAudience) {
            return $rejected
        }
        if ($scope -ne $ExpectedScope -or $provider -notin @("google", "azure")) {
            return $rejected
        }
        if (-not [string]::IsNullOrWhiteSpace($ExpectedProvider) -and $provider -ne $ExpectedProvider.Trim().ToLowerInvariant()) {
            return $rejected
        }
        if ($sessionId -ne (Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "HelperSessionId")) {
            return $rejected
        }
        if ($operationId -and $operationId -notmatch "^[a-f0-9]{32}$") {
            return $rejected
        }
        if ($ExpectedScope -eq "operation_status") {
            if ([string]::IsNullOrWhiteSpace($ExpectedOperationId) -or $operationId -ne $ExpectedOperationId.Trim().ToLowerInvariant()) {
                return $rejected
            }
        }
        elseif (-not [string]::IsNullOrWhiteSpace($operationId)) {
            return $rejected
        }

        $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        if ($issuedAt -gt ($now + $script:TowerScoutHostHelperBrowserAuthorizationClockSkewSeconds)) {
            return $rejected
        }
        if (
            $expiresAt -le (
                $now - $script:TowerScoutHostHelperBrowserAuthorizationClockSkewSeconds
            )
        ) {
            return [pscustomobject]@{
                Accepted = $false
                State = "rejected_expired_authorization"
                Provider = $provider
                Scope = $scope
                OperationId = $operationId
            }
        }
        $ttl = $expiresAt - $issuedAt
        if ($ttl -lt 1 -or $ttl -gt $script:TowerScoutHostHelperBrowserAuthorizationMaxTtlSeconds) {
            return $rejected
        }

        return [pscustomobject]@{
            Accepted = $true
            State = "authorized"
            Provider = $provider
            Scope = $scope
            OperationId = $operationId
            IssuedAtUnix = $issuedAt
            ExpiresAtUnix = $expiresAt
        }
    }
    catch {
        return $rejected
    }
}

function New-TowerScoutHostHelperBrowserAuthorization {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [ValidateSet("operation_status")]
        [string] $Scope,

        [Parameter(Mandatory = $true)]
        [ValidateSet("google", "azure")]
        [string] $Provider,

        [Parameter(Mandatory = $true)]
        [string] $OperationId,

        [int] $TtlSeconds = $script:TowerScoutHostHelperBrowserAuthorizationMaxTtlSeconds
    )

    $authorizationKey = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "BrowserAuthorizationKey"
    if ($authorizationKey -notmatch "^[A-Za-z0-9_-]{43}$") {
        throw "The helper browser authorization key is unavailable."
    }
    $normalizedOperationId = Resolve-TowerScoutHostHelperSessionId -SessionId $OperationId
    if ($TtlSeconds -lt 1 -or $TtlSeconds -gt $script:TowerScoutHostHelperBrowserAuthorizationMaxTtlSeconds) {
        throw "The helper browser authorization TTL is outside the allowed range."
    }

    $issuedAt = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $expiresAt = $issuedAt + $TtlSeconds
    $payload = [ordered]@{
        aud = $script:TowerScoutHostHelperBrowserAuthorizationAudience
        exp = $expiresAt
        iat = $issuedAt
        nonce = New-TowerScoutHostHelperToken
        operation_id = $normalizedOperationId
        provider = $Provider
        scope = $Scope
        session_id = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "HelperSessionId"
        v = 1
    }
    $payloadBytes = [System.Text.Encoding]::ASCII.GetBytes(
        ($payload | ConvertTo-Json -Compress)
    )
    $payloadSegment = ConvertTo-TowerScoutHostHelperBase64Url -Value $payloadBytes
    $signingInput = [System.Text.Encoding]::ASCII.GetBytes("v1.$payloadSegment")
    $keyBytes = ConvertFrom-TowerScoutHostHelperBase64Url -Value $authorizationKey
    $hmac = New-Object System.Security.Cryptography.HMACSHA256(,$keyBytes)
    try {
        $signature = $hmac.ComputeHash($signingInput)
    }
    finally {
        $hmac.Dispose()
    }

    return [pscustomobject]@{
        operation_type = "provider_tls_repair"
        scope = $Scope
        expires_at = [DateTimeOffset]::FromUnixTimeSeconds($expiresAt).UtcDateTime.ToString("o")
        authorization = "v1.$payloadSegment.$(ConvertTo-TowerScoutHostHelperBase64Url -Value $signature)"
    }
}

function Get-TowerScoutHostHelperValueFingerprint {
    param(
        [string] $Value = ""
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ""
    }

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash($bytes)
    }
    finally {
        $sha256.Dispose()
    }

    return (($hashBytes | ForEach-Object { $_.ToString("x2") }) -join "")
}

function Get-TowerScoutHostHelperObjectValue {
    param(
        [object] $InputObject,

        [string] $Name
    )

    if ($null -eq $InputObject) {
        return ""
    }
    $property = $InputObject.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return ""
    }

    return [string] $property.Value
}

function Set-TowerScoutHostHelperObjectValue {
    param(
        [Parameter(Mandatory = $true)]
        [object] $InputObject,

        [Parameter(Mandatory = $true)]
        [string] $Name,

        [object] $Value
    )

    $InputObject | Add-Member -NotePropertyName $Name -NotePropertyValue $Value -Force
}

function New-TowerScoutHostHelperSessionId {
    return [guid]::NewGuid().ToString("N")
}

function Resolve-TowerScoutHostHelperSessionId {
    param(
        [string] $SessionId = ""
    )

    if ([string]::IsNullOrWhiteSpace($SessionId)) {
        return New-TowerScoutHostHelperSessionId
    }

    $normalized = $SessionId.Trim().ToLowerInvariant()
    if ($normalized -notmatch "^[a-f0-9]{32}$") {
        throw "HelperSessionId must be a 32-character hexadecimal value."
    }

    return $normalized
}

function Get-TowerScoutHostHelperPackageRootIdentity {
    param(
        [Parameter(Mandatory = $true)]
        [string] $PackageRoot
    )

    $normalizedRoot = ([System.IO.Path]::GetFullPath($PackageRoot)).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    ).ToLowerInvariant()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalizedRoot)
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash($bytes)
    }
    finally {
        $sha256.Dispose()
    }

    return (($hashBytes | ForEach-Object { $_.ToString("x2") }) -join "").Substring(0, 16)
}

function Get-TowerScoutHostHelperStateDirectory {
    param(
        [string] $RootPath = $(Resolve-Path (Join-Path $PSScriptRoot "..\.."))
    )

    $resolvedRoot = (Resolve-Path -LiteralPath $RootPath).Path
    return (Join-Path $resolvedRoot ".towerscout-runtime\host-helper")
}

function Protect-TowerScoutHostHelperStatePath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,

        [switch] $Directory
    )

    if ($env:OS -ne "Windows_NT") {
        return
    }

    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $security = if ($Directory) {
        New-Object System.Security.AccessControl.DirectorySecurity
    }
    else {
        New-Object System.Security.AccessControl.FileSecurity
    }
    $security.SetAccessRuleProtection($true, $false)
    $inheritance = if ($Directory) {
        [System.Security.AccessControl.InheritanceFlags]"ContainerInherit, ObjectInherit"
    }
    else {
        [System.Security.AccessControl.InheritanceFlags]::None
    }
    $propagation = [System.Security.AccessControl.PropagationFlags]::None
    $rights = [System.Security.AccessControl.FileSystemRights]::FullControl
    $allow = [System.Security.AccessControl.AccessControlType]::Allow
    $principals = @(
        $identity.User,
        (New-Object System.Security.Principal.SecurityIdentifier(
            [System.Security.Principal.WellKnownSidType]::LocalSystemSid,
            $null
        )),
        (New-Object System.Security.Principal.SecurityIdentifier(
            [System.Security.Principal.WellKnownSidType]::BuiltinAdministratorsSid,
            $null
        ))
    )
    foreach ($principal in $principals) {
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            $principal,
            $rights,
            $inheritance,
            $propagation,
            $allow
        )
        $security.AddAccessRule($rule)
    }

    # Set-Acl remains available in both Windows PowerShell 5.1 and PowerShell 7.
    # The static System.IO SetAccessControl methods are not exposed by every
    # .NET runtime used by pwsh.
    Set-Acl -LiteralPath $Path -AclObject $security -ErrorAction Stop
}

function Initialize-TowerScoutHostHelperStateDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $stateDirectory = Get-TowerScoutHostHelperStateDirectory -RootPath $RootPath
    New-Item -ItemType Directory -Path $stateDirectory -Force | Out-Null
    Protect-TowerScoutHostHelperStatePath -Path $stateDirectory -Directory
    return $stateDirectory
}

function Write-TowerScoutHostHelperJsonAtomic {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,

        [Parameter(Mandatory = $true)]
        [object] $Value
    )

    $uniqueSuffix = "{0}.{1}" -f $PID, ([guid]::NewGuid().ToString("N"))
    $temporaryPath = "{0}.{1}.tmp" -f $Path, $uniqueSuffix
    $backupPath = "{0}.{1}.bak" -f $Path, $uniqueSuffix
    try {
        $json = $Value | ConvertTo-Json -Depth 10
        [System.IO.File]::WriteAllText(
            $temporaryPath,
            $json,
            [System.Text.Encoding]::ASCII
        )
        Protect-TowerScoutHostHelperStatePath -Path $temporaryPath
        Install-TowerScoutHostHelperJsonDocument `
            -TemporaryPath $temporaryPath `
            -DestinationPath $Path `
            -BackupPath $backupPath
        Remove-Item -LiteralPath $backupPath -Force -ErrorAction SilentlyContinue
    }
    finally {
        if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) {
            Remove-Item -LiteralPath $temporaryPath -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path -LiteralPath $backupPath -PathType Leaf) {
            Remove-Item -LiteralPath $backupPath -Force -ErrorAction SilentlyContinue
        }
    }
}

function Write-TowerScoutHostHelperSecret {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,

        [Parameter(Mandatory = $true)]
        [string] $Value
    )

    $bytes = [System.Text.Encoding]::ASCII.GetBytes($Value)
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::Create,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    }
    finally {
        $stream.Dispose()
    }
    Protect-TowerScoutHostHelperStatePath -Path $Path
}

function Enter-TowerScoutHostHelperPackageMutex {
    param(
        [Parameter(Mandatory = $true)]
        [string] $PackageRoot,

        [int] $WaitMilliseconds = 10000
    )

    $rootIdentity = Get-TowerScoutHostHelperPackageRootIdentity -PackageRoot $PackageRoot
    $prefix = if ($env:OS -eq "Windows_NT") { "Local\" } else { "" }
    $mutex = New-Object System.Threading.Mutex(
        $false,
        ("{0}TowerScoutHostHelper-{1}" -f $prefix, $rootIdentity)
    )
    try {
        $acquired = $mutex.WaitOne($WaitMilliseconds)
    }
    catch [System.Threading.AbandonedMutexException] {
        $acquired = $true
    }
    if (-not $acquired) {
        $mutex.Dispose()
        throw "Another TowerScout host helper is already active for this package."
    }
    return $mutex
}

function Save-TowerScoutHostHelperLaunchProfile {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $Engine,

        [Parameter(Mandatory = $true)]
        [ValidateSet("off", "auto", "on")]
        [string] $Gpu,

        [Parameter(Mandatory = $true)]
        [int] $AppPort,

        [string] $RootPath = $(Resolve-Path (Join-Path $PSScriptRoot "..\..")),

        [string] $PackageFlavor = "source"
    )

    if ($AppPort -lt 1 -or $AppPort -gt 65535) {
        throw "AppPort must be between 1 and 65535."
    }

    $resolvedRoot = (Resolve-Path -LiteralPath $RootPath).Path
    $stateDirectory = Initialize-TowerScoutHostHelperStateDirectory -RootPath $resolvedRoot

    $profilePath = Join-Path $stateDirectory "launch-profile.json"
    $launchProfile = [pscustomobject]@{
        helper_version = $script:TowerScoutHostHelperVersion
        created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        engine = $Engine
        gpu = $Gpu
        app_port = $AppPort
        base_url = "http://localhost:$AppPort"
        package_flavor = $PackageFlavor
        package_root_identity = Get-TowerScoutHostHelperPackageRootIdentity -PackageRoot $resolvedRoot
        state = "profile_captured"
    }

    Write-TowerScoutHostHelperJsonAtomic -Path $profilePath -Value $launchProfile
    return $profilePath
}

function Save-TowerScoutHostHelperSession {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [string] $RootPath = "",

        [string] $Token = ""
    )

    $resolvedRootPath = if ([string]::IsNullOrWhiteSpace($RootPath)) {
        Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "PackageRoot"
    }
    else {
        $RootPath
    }
    if ([string]::IsNullOrWhiteSpace($resolvedRootPath)) {
        $resolvedRootPath = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
    }
    $stateDirectory = Initialize-TowerScoutHostHelperStateDirectory -RootPath $resolvedRootPath

    $sessionPath = Join-Path $stateDirectory ("session-{0}.json" -f $Profile.HelperSessionId)
    $tokenFileName = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "TokenFileName"
    if (-not [string]::IsNullOrWhiteSpace($Token)) {
        $tokenFileName = "token-{0}.secret" -f $Profile.HelperSessionId
        $tokenPath = Join-Path $stateDirectory $tokenFileName
        Write-TowerScoutHostHelperSecret -Path $tokenPath -Value $Token
        Set-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "TokenFileName" -Value $tokenFileName
        Set-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "TokenPath" -Value $tokenPath
    }

    $createdAtUtc = [datetime]::Parse([string] $Profile.CreatedAtUtc).ToUniversalTime()
    $leaseExpiresAtUtc = $createdAtUtc.AddSeconds($script:TowerScoutHostHelperSessionTtlSeconds)
    $process = Get-Process -Id $PID -ErrorAction Stop
    $session = [pscustomobject]@{
        helper_version = [string] $Profile.HelperVersion
        helper_session_id = [string] $Profile.HelperSessionId
        created_at_utc = [string] $Profile.CreatedAtUtc
        engine = [string] $Profile.Engine
        gpu = [string] $Profile.Gpu
        app_port = [int] $Profile.AppPort
        helper_port = [int] $Profile.HelperPort
        package_flavor = [string] $Profile.PackageFlavor
        package_root_identity = Get-TowerScoutHostHelperPackageRootIdentity -PackageRoot $Profile.PackageRoot
        token_file = $tokenFileName
        process_id = $PID
        process_start_time_utc = $process.StartTime.ToUniversalTime().ToString("o")
        last_heartbeat_utc = (Get-Date).ToUniversalTime().ToString("o")
        lease_expires_at_utc = $leaseExpiresAtUtc.ToString("o")
        state = "active"
    }

    Write-TowerScoutHostHelperJsonAtomic -Path $sessionPath -Value $session
    $Profile | Add-Member -NotePropertyName "SessionPath" -NotePropertyValue $sessionPath -Force
    return $sessionPath
}

function Clear-TowerScoutHostHelperSession {
    param(
        [string] $RootPath = $(Resolve-Path (Join-Path $PSScriptRoot "..\..")),

        [string] $SessionId = ""
    )

    $stateDirectory = Get-TowerScoutHostHelperStateDirectory -RootPath $RootPath
    if (-not (Test-Path -LiteralPath $stateDirectory -PathType Container)) {
        return [pscustomobject]@{
            cleared = 0
            state = "no_sessions"
        }
    }

    $normalizedSessionId = if ([string]::IsNullOrWhiteSpace($SessionId)) { "" } else { Resolve-TowerScoutHostHelperSessionId -SessionId $SessionId }
    $sessionFilter = if ([string]::IsNullOrWhiteSpace($normalizedSessionId)) { "session-*.json" } else { "session-$normalizedSessionId.json" }
    $tokenFilter = if ([string]::IsNullOrWhiteSpace($normalizedSessionId)) { "token-*.secret" } else { "token-$normalizedSessionId.secret" }
    $operationFilter = "operation-*.json"
    $sessionFiles = @(Get-ChildItem -LiteralPath $stateDirectory -Filter $sessionFilter -File -ErrorAction SilentlyContinue)
    $tokenFiles = @(Get-ChildItem -LiteralPath $stateDirectory -Filter $tokenFilter -File -ErrorAction SilentlyContinue)
    $operationFiles = @(
        if (
            [string]::IsNullOrWhiteSpace($normalizedSessionId) -or
            $sessionFiles.Count -gt 0
        ) {
            Get-ChildItem -LiteralPath $stateDirectory -Filter $operationFilter -File -ErrorAction SilentlyContinue
        }
    )
    foreach ($file in @($sessionFiles + $tokenFiles + $operationFiles)) {
        Remove-Item -LiteralPath $file.FullName -Force -ErrorAction SilentlyContinue
    }

    return [pscustomobject]@{
        cleared = $sessionFiles.Count
        token_files_cleared = $tokenFiles.Count
        operation_files_cleared = $operationFiles.Count
        state = "invalidated"
    }
}

function Test-TowerScoutHostHelperReviewEnabled {
    $value = ([string] $env:TOWERSCOUT_HOST_HELPER_REVIEW_ENABLED).Trim().ToLowerInvariant()
    return $value -in @("1", "true", "yes", "on")
}

function Clear-TowerScoutHostHelperBridgeEnvironment {
    $env:TOWERSCOUT_HOST_HELPER_ENABLED = "0"
    Remove-Item Env:TOWERSCOUT_HOST_HELPER_PORT -ErrorAction SilentlyContinue
    Remove-Item Env:TOWERSCOUT_HOST_HELPER_SESSION_ID -ErrorAction SilentlyContinue
    Remove-Item Env:TOWERSCOUT_HOST_HELPER_SESSION_KEY -ErrorAction SilentlyContinue
}

function Get-TowerScoutHostHelperSessionMetadata {
    param(
        [Parameter(Mandatory = $true)]
        [string] $SessionId,

        [Parameter(Mandatory = $true)]
        [string] $RootPath
    )

    $stateDirectory = Get-TowerScoutHostHelperStateDirectory -RootPath $RootPath
    $sessionPath = Join-Path $stateDirectory ("session-{0}.json" -f $SessionId)
    if (-not (Test-Path -LiteralPath $sessionPath -PathType Leaf)) {
        return $null
    }
    try {
        return Get-TowerScoutHostHelperJsonDocument -Path $sessionPath
    }
    catch {
        return $null
    }
}

function Test-TowerScoutHostHelperSessionMetadataMatchesProfile {
    param(
        [object] $Metadata,

        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $EngineName,

        [Parameter(Mandatory = $true)]
        [ValidateSet("off", "auto", "on")]
        [string] $GpuMode,

        [Parameter(Mandatory = $true)]
        [int] $AppPort,

        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $PackageFlavor
    )

    if ($null -eq $Metadata) {
        return $false
    }

    [int] $metadataAppPort = 0
    [int] $metadataHelperPort = 0
    $expectedRootIdentity = Get-TowerScoutHostHelperPackageRootIdentity -PackageRoot $RootPath
    return (
        (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "state") -eq "active" -and
        (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "helper_version") -eq $script:TowerScoutHostHelperVersion -and
        (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "engine") -eq $EngineName -and
        (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "gpu") -eq $GpuMode -and
        [int]::TryParse(
            ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "app_port")),
            [ref] $metadataAppPort
        ) -and
        $metadataAppPort -eq $AppPort -and
        [int]::TryParse(
            ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "helper_port")),
            [ref] $metadataHelperPort
        ) -and
        $metadataHelperPort -ge 1 -and
        $metadataHelperPort -le 65535 -and
        (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "package_flavor") -eq $PackageFlavor -and
        (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "package_root_identity") -eq $expectedRootIdentity
    )
}

function Test-TowerScoutHostHelperSessionLiveness {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Metadata,

        [Parameter(Mandatory = $true)]
        [string] $SessionId,

        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [int] $AppPort
    )

    [int] $processId = 0
    [int] $helperPort = 0
    [datetime] $expectedStartUtc = [datetime]::MinValue
    [datetime] $leaseExpiresUtc = [datetime]::MinValue
    [datetime] $heartbeatUtc = [datetime]::MinValue
    if (
        -not [int]::TryParse(
            ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "process_id")),
            [ref] $processId
        ) -or
        -not [int]::TryParse(
            ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "helper_port")),
            [ref] $helperPort
        ) -or
        -not [datetime]::TryParse(
            ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "process_start_time_utc")),
            [ref] $expectedStartUtc
        ) -or
        -not [datetime]::TryParse(
            ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "lease_expires_at_utc")),
            [ref] $leaseExpiresUtc
        ) -or
        -not [datetime]::TryParse(
            ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "last_heartbeat_utc")),
            [ref] $heartbeatUtc
        )
    ) {
        return $false
    }

    $nowUtc = (Get-Date).ToUniversalTime()
    if (
        $leaseExpiresUtc.ToUniversalTime() -le $nowUtc -or
        $heartbeatUtc.ToUniversalTime() -lt $nowUtc.AddSeconds(-$script:TowerScoutHostHelperHeartbeatStaleSeconds)
    ) {
        return $false
    }

    try {
        $process = Get-Process -Id $processId -ErrorAction Stop
        if (
            [Math]::Abs(
                ($process.StartTime.ToUniversalTime() - $expectedStartUtc.ToUniversalTime()).TotalSeconds
            ) -gt 2
        ) {
            return $false
        }
    }
    catch {
        return $false
    }

    $tokenFileName = [string] (
        Get-TowerScoutHostHelperObjectValue -InputObject $Metadata -Name "token_file"
    )
    if ($tokenFileName -ne ("token-{0}.secret" -f $SessionId)) {
        return $false
    }
    $tokenPath = Join-Path `
        (Get-TowerScoutHostHelperStateDirectory -RootPath $RootPath) `
        $tokenFileName
    if (-not (Test-Path -LiteralPath $tokenPath -PathType Leaf)) {
        return $false
    }

    try {
        $token = (Get-Content -LiteralPath $tokenPath -Raw).Trim()
        $request = [System.Net.HttpWebRequest]::Create(
            "http://127.0.0.1:$helperPort/runtime-profile"
        )
        $request.Method = "GET"
        $request.Timeout = 2000
        $request.Headers.Add("X-TowerScout-Helper-Token", $token)
        $request.Headers.Add("Origin", "http://localhost:$AppPort")
        $response = $request.GetResponse()
        try {
            $reader = New-Object System.IO.StreamReader(
                $response.GetResponseStream()
            )
            try {
                $profile = $reader.ReadToEnd() | ConvertFrom-Json
            }
            finally {
                $reader.Dispose()
            }
        }
        finally {
            $response.Dispose()
        }
        return (
            (Get-TowerScoutHostHelperObjectValue -InputObject $profile -Name "state") -eq "ready"
        )
    }
    catch {
        return $false
    }
}

function Start-TowerScoutHostHelperReviewProcess {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $EngineName,

        [Parameter(Mandatory = $true)]
        [ValidateSet("off", "auto", "on")]
        [string] $GpuMode,

        [Parameter(Mandatory = $true)]
        [int] $AppPort,

        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $PackageFlavor,

        [Parameter(Mandatory = $true)]
        [string] $SessionId,

        [int] $MutexWaitMilliseconds = $script:TowerScoutHostHelperPackageMutexWaitMilliseconds
    )

    $resolvedHelperScript = (
        Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\host-helper.ps1")
    ).Path
    $resolvedPowerShell = [string] (
        Get-Command "powershell.exe" -CommandType Application -ErrorAction Stop
    ).Source
    $resolvedRoot = (Resolve-Path -LiteralPath $RootPath).Path
    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $resolvedHelperScript,
        "-Engine",
        $EngineName,
        "-Gpu",
        $GpuMode,
        "-AppPort",
        "$AppPort",
        "-PackageFlavor",
        $PackageFlavor,
        "-HelperSessionId",
        $SessionId,
        "-PackageRoot",
        $resolvedRoot,
        "-MutexWaitMilliseconds",
        "$MutexWaitMilliseconds"
    )
    $argumentLine = [string]::Join(
        " ",
        @($arguments | ForEach-Object {
            ConvertTo-TowerScoutHostHelperCmdArgument -Value ([string] $_)
        })
    )

    return Start-Process `
        -FilePath $resolvedPowerShell `
        -ArgumentList $argumentLine `
        -WorkingDirectory $resolvedRoot `
        -WindowStyle Normal `
        -PassThru
}

function Stop-TowerScoutHostHelperReviewSession {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [string] $SessionId = "",

        [System.Diagnostics.Process] $Process = $null
    )

    Clear-TowerScoutHostHelperSession -RootPath $RootPath -SessionId $SessionId | Out-Null
    Clear-TowerScoutHostHelperBridgeEnvironment
    try {
        if ($null -ne $Process) {
            Stop-TowerScoutHostHelperProcessTree -Process $Process -RequireExit | Out-Null
        }
    }
    finally {
        # A late-starting helper can publish state between cooperative
        # invalidation and verified process exit, so clear the exact session
        # again after the termination attempt.
        Clear-TowerScoutHostHelperSession -RootPath $RootPath -SessionId $SessionId | Out-Null
        Clear-TowerScoutHostHelperBridgeEnvironment
    }
}

function Initialize-TowerScoutHostHelperReviewSession {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $EngineName,

        [Parameter(Mandatory = $true)]
        [ValidateSet("off", "auto", "on")]
        [string] $GpuMode,

        [Parameter(Mandatory = $true)]
        [int] $AppPort,

        [Parameter(Mandatory = $true)]
        [string] $RootPath,

        [Parameter(Mandatory = $true)]
        [string] $PackageFlavor,

        [int] $ReadinessTimeoutSeconds = $script:TowerScoutHostHelperLauncherReadinessTimeoutSeconds,

        [int] $MutexWaitMilliseconds = $script:TowerScoutHostHelperPackageMutexWaitMilliseconds
    )

    if ($ReadinessTimeoutSeconds -lt 1) {
        throw "ReadinessTimeoutSeconds must be at least 1."
    }
    if ($MutexWaitMilliseconds -lt 1) {
        throw "MutexWaitMilliseconds must be at least 1."
    }

    if (-not (Test-TowerScoutHostHelperReviewEnabled)) {
        Stop-TowerScoutHostHelperReviewSession -RootPath $RootPath
        return $null
    }

    $existingSessionId = ([string] $env:TOWERSCOUT_HOST_HELPER_SESSION_ID).Trim().ToLowerInvariant()
    $existingSessionKey = ([string] $env:TOWERSCOUT_HOST_HELPER_SESSION_KEY).Trim()
    if (
        $existingSessionId -match "^[a-f0-9]{32}$" -and
        $existingSessionKey -match "^[A-Za-z0-9_-]{43}$"
    ) {
        $existingMetadata = Get-TowerScoutHostHelperSessionMetadata `
            -SessionId $existingSessionId `
            -RootPath $RootPath
        [int] $existingProcessId = 0
        if (
            (Test-TowerScoutHostHelperSessionMetadataMatchesProfile `
                -Metadata $existingMetadata `
                -EngineName $EngineName `
                -GpuMode $GpuMode `
                -AppPort $AppPort `
                -RootPath $RootPath `
                -PackageFlavor $PackageFlavor) -and
            [int]::TryParse(
                ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $existingMetadata -Name "process_id")),
                [ref] $existingProcessId
            ) -and
            (Test-TowerScoutHostHelperSessionLiveness `
                -Metadata $existingMetadata `
                -SessionId $existingSessionId `
                -RootPath $RootPath `
                -AppPort $AppPort)
        ) {
            # The process can exit after the authenticated liveness probe. If
            # that happens, fall through to exact stale-session cleanup and a
            # new helper instead of aborting the launcher.
            $existingProcess = Get-Process `
                -Id $existingProcessId `
                -ErrorAction SilentlyContinue
            if ($null -ne $existingProcess) {
                $env:TOWERSCOUT_HOST_HELPER_ENABLED = "1"
                $env:TOWERSCOUT_HOST_HELPER_PORT = [string] (
                    Get-TowerScoutHostHelperObjectValue -InputObject $existingMetadata -Name "helper_port"
                )
                Write-Host "Reusing the active TowerScout host helper review session."
                return [pscustomobject]@{
                    SessionId = $existingSessionId
                    Process = $existingProcess
                    StartedNewProcess = $false
                }
            }
        }
    }

    Stop-TowerScoutHostHelperReviewSession -RootPath $RootPath

    $sessionId = New-TowerScoutHostHelperSessionId
    $sessionKey = New-TowerScoutHostHelperToken
    $env:TOWERSCOUT_HOST_HELPER_SESSION_ID = $sessionId
    $env:TOWERSCOUT_HOST_HELPER_SESSION_KEY = $sessionKey
    $env:TOWERSCOUT_HOST_HELPER_ENABLED = "1"
    $helperProcess = $null

    try {
        $helperProcess = Start-TowerScoutHostHelperReviewProcess `
            -EngineName $EngineName `
            -GpuMode $GpuMode `
            -AppPort $AppPort `
            -RootPath $RootPath `
            -PackageFlavor $PackageFlavor `
            -SessionId $sessionId `
            -MutexWaitMilliseconds $MutexWaitMilliseconds

        $deadline = (Get-Date).AddSeconds($ReadinessTimeoutSeconds)
        while ((Get-Date) -lt $deadline) {
            if ($helperProcess.HasExited) {
                throw "The TowerScout host helper review process exited before it became ready."
            }

            $metadata = Get-TowerScoutHostHelperSessionMetadata `
                -SessionId $sessionId `
                -RootPath $RootPath
            [int] $helperPort = 0
            [int] $metadataProcessId = 0
            if (
                (Test-TowerScoutHostHelperSessionMetadataMatchesProfile `
                    -Metadata $metadata `
                    -EngineName $EngineName `
                    -GpuMode $GpuMode `
                    -AppPort $AppPort `
                    -RootPath $RootPath `
                    -PackageFlavor $PackageFlavor) -and
                [int]::TryParse(
                    ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $metadata -Name "helper_port")),
                    [ref] $helperPort
                ) -and
                [int]::TryParse(
                    ([string] (Get-TowerScoutHostHelperObjectValue -InputObject $metadata -Name "process_id")),
                    [ref] $metadataProcessId
                ) -and
                $metadataProcessId -eq $helperProcess.Id -and
                (Test-TowerScoutHostHelperSessionLiveness `
                    -Metadata $metadata `
                    -SessionId $sessionId `
                    -RootPath $RootPath `
                    -AppPort $AppPort)
            ) {
                $env:TOWERSCOUT_HOST_HELPER_PORT = "$helperPort"
                Write-Host "TowerScout host helper review session is ready."
                return [pscustomobject]@{
                    SessionId = $sessionId
                    Process = $helperProcess
                    StartedNewProcess = $true
                }
            }
            Start-Sleep -Milliseconds 200
        }

        throw "The TowerScout host helper review session did not become ready."
    }
    catch {
        $initializationError = $_
        $cleanupError = $null
        try {
            Stop-TowerScoutHostHelperReviewSession `
                -RootPath $RootPath `
                -SessionId $sessionId `
                -Process $helperProcess
        }
        catch {
            $cleanupError = $_
        }
        finally {
            if ($null -ne $helperProcess) {
                $helperProcess.Dispose()
            }
        }
        if ($null -ne $cleanupError) {
            throw $cleanupError
        }
        throw $initializationError
    }
}

function Test-TowerScoutHostHelperSessionActive {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [switch] $IgnoreHeartbeatStaleness
    )

    $sessionPath = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "SessionPath"
    if ([string]::IsNullOrWhiteSpace($sessionPath)) {
        return $true
    }

    if (-not (Test-Path -LiteralPath $sessionPath -PathType Leaf)) {
        return $false
    }

    try {
        $session = Get-TowerScoutHostHelperJsonDocument -Path $sessionPath
        if ($null -eq $session) {
            return $false
        }
        [int] $processId = 0
        [datetime] $processStartTimeUtc = [datetime]::MinValue
        [datetime] $lastHeartbeatUtc = [datetime]::MinValue
        [datetime] $leaseExpiresAtUtc = [datetime]::MinValue
        if (
            (Get-TowerScoutHostHelperObjectValue -InputObject $session -Name "state") -ne "active" -or
            (Get-TowerScoutHostHelperObjectValue -InputObject $session -Name "helper_session_id") -ne
                (Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "HelperSessionId") -or
            (Get-TowerScoutHostHelperObjectValue -InputObject $session -Name "package_root_identity") -ne
                (Get-TowerScoutHostHelperPackageRootIdentity -PackageRoot $Profile.PackageRoot) -or
            -not [int]::TryParse(
                (Get-TowerScoutHostHelperObjectValue -InputObject $session -Name "process_id"),
                [ref] $processId
            ) -or
            -not [datetime]::TryParse(
                (Get-TowerScoutHostHelperObjectValue -InputObject $session -Name "process_start_time_utc"),
                [ref] $processStartTimeUtc
            ) -or
            -not [datetime]::TryParse(
                (Get-TowerScoutHostHelperObjectValue -InputObject $session -Name "last_heartbeat_utc"),
                [ref] $lastHeartbeatUtc
            ) -or
            -not [datetime]::TryParse(
                (Get-TowerScoutHostHelperObjectValue -InputObject $session -Name "lease_expires_at_utc"),
                [ref] $leaseExpiresAtUtc
            )
        ) {
            return $false
        }
        $nowUtc = (Get-Date).ToUniversalTime()
        if (
            $leaseExpiresAtUtc.ToUniversalTime() -le $nowUtc -or
            (
                -not $IgnoreHeartbeatStaleness -and
                $lastHeartbeatUtc.ToUniversalTime() -lt
                $nowUtc.AddSeconds(-$script:TowerScoutHostHelperHeartbeatStaleSeconds)
            )
        ) {
            return $false
        }

        $process = Get-Process -Id $processId -ErrorAction Stop
        return [Math]::Abs(
            (
                $process.StartTime.ToUniversalTime() -
                $processStartTimeUtc.ToUniversalTime()
            ).TotalSeconds
        ) -le 2
    }
    catch {
        return $false
    }
}

function Update-TowerScoutHostHelperSessionHeartbeat {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile
    )

    $sessionPath = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "SessionPath"
    if ([string]::IsNullOrWhiteSpace($sessionPath) -or -not (Test-Path -LiteralPath $sessionPath -PathType Leaf)) {
        return $false
    }
    try {
        $session = Get-TowerScoutHostHelperJsonDocument -Path $sessionPath
        if ($null -eq $session) {
            return $false
        }
        Set-TowerScoutHostHelperObjectValue `
            -InputObject $session `
            -Name "last_heartbeat_utc" `
            -Value ((Get-Date).ToUniversalTime().ToString("o"))
        Write-TowerScoutHostHelperJsonAtomic -Path $sessionPath -Value $session
        return $true
    }
    catch {
        return $false
    }
}

function New-TowerScoutHostHelperRuntimeProfile {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("docker", "podman")]
        [string] $Engine,

        [Parameter(Mandatory = $true)]
        [ValidateSet("off", "auto", "on")]
        [string] $Gpu,

        [Parameter(Mandatory = $true)]
        [int] $AppPort,

        [string] $PackageRoot = $(Resolve-Path (Join-Path $PSScriptRoot "..\..")),

        [string] $PackageFlavor = "source",

        [string[]] $AllowedOrigins = @(),

        [int] $HelperPort = 0,

        [string] $HelperSessionId = "",

        [string] $BrowserAuthorizationKey = "",

        [bool] $ProviderTlsRepairEnabled = $false
    )

    if ($AppPort -lt 1 -or $AppPort -gt 65535) {
        throw "AppPort must be between 1 and 65535."
    }
    if ($HelperPort -lt 0 -or $HelperPort -gt 65535) {
        throw "HelperPort must be 0 or between 1 and 65535."
    }
    if (-not [string]::IsNullOrWhiteSpace($BrowserAuthorizationKey) -and $BrowserAuthorizationKey -notmatch "^[A-Za-z0-9_-]{43}$") {
        throw "BrowserAuthorizationKey must be a 32-byte base64url value."
    }

    $resolvedRoot = (Resolve-Path -LiteralPath $PackageRoot).Path
    if ($AllowedOrigins.Count -eq 0) {
        $AllowedOrigins = @(
            "http://localhost:$AppPort",
            "http://127.0.0.1:$AppPort"
        )
    }
    $resolvedSessionId = Resolve-TowerScoutHostHelperSessionId -SessionId $HelperSessionId

    return [pscustomobject]@{
        HelperVersion = $script:TowerScoutHostHelperVersion
        HelperSessionId = $resolvedSessionId
        CreatedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        Engine = $Engine
        Gpu = $Gpu
        AppPort = $AppPort
        BaseUrl = "http://localhost:$AppPort"
        PackageRoot = $resolvedRoot
        PackageFlavor = $PackageFlavor
        AllowedOrigins = @($AllowedOrigins)
        HelperPort = $HelperPort
        BrowserAuthorizationKey = $BrowserAuthorizationKey
        ProviderTlsRepairEnabled = $ProviderTlsRepairEnabled
    }
}

function ConvertTo-TowerScoutHostHelperPublicRuntimeProfile {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile
    )

    [bool] $providerTlsRepairEnabled = $false
    [bool]::TryParse(
        (Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "ProviderTlsRepairEnabled"),
        [ref] $providerTlsRepairEnabled
    ) | Out-Null
    return [pscustomobject]@{
        helper_version = [string] $Profile.HelperVersion
        state = "ready"
        runtime = [pscustomobject]@{
            engine = [string] $Profile.Engine
            gpu = [string] $Profile.Gpu
            app_port = [int] $Profile.AppPort
            package_flavor = [string] $Profile.PackageFlavor
        }
        capabilities = [pscustomobject]@{
            provider_tls_repair = $providerTlsRepairEnabled
            podman_provider_repair = $false
            max_active_operations = 1
        }
    }
}

function Get-TowerScoutHostHelperOperationStatePolicy {
    param(
        [string] $State = ""
    )

    switch ($State) {
        "planned" {
            return [pscustomobject]@{
                Classification = "pending"
                Terminal = $false
                NextAction = "await_controlled_execution"
            }
        }
        "operation_busy" {
            return [pscustomobject]@{
                Classification = "active"
                Terminal = $false
                NextAction = "poll_existing_operation"
            }
        }
        "tls_repair_running" {
            return [pscustomobject]@{
                Classification = "active"
                Terminal = $false
                NextAction = "poll_existing_operation"
            }
        }
        "runtime_stopping" {
            return [pscustomobject]@{
                Classification = "active"
                Terminal = $false
                NextAction = "poll_existing_operation"
            }
        }
        "runtime_starting" {
            return [pscustomobject]@{
                Classification = "active"
                Terminal = $false
                NextAction = "poll_existing_operation"
            }
        }
        "tls_repair_completed" {
            return [pscustomobject]@{
                Classification = "intermediate_success"
                Terminal = $false
                NextAction = "continue_to_runtime_stop"
            }
        }
        "runtime_stopped" {
            return [pscustomobject]@{
                Classification = "intermediate_success"
                Terminal = $false
                NextAction = "continue_to_runtime_start"
            }
        }
        "ready" {
            return [pscustomobject]@{
                Classification = "terminal_success"
                Terminal = $true
                NextAction = "retry_provider_validation"
            }
        }
        "runtime_stop_failed" {
            return [pscustomobject]@{
                Classification = "retryable_failure_with_support_review"
                Terminal = $true
                NextAction = "review_runtime_state_before_retry"
            }
        }
        "readiness_timeout" {
            return [pscustomobject]@{
                Classification = "terminal_timeout"
                Terminal = $true
                NextAction = "use_startup_fallback_guidance"
            }
        }
        "operation_timeout" {
            return [pscustomobject]@{
                Classification = "terminal_timeout"
                Terminal = $true
                NextAction = "clear_or_reauthorize_after_timeout"
            }
        }
        "tls_repair_selection_required" {
            return [pscustomobject]@{
                Classification = "terminal_support_escalation"
                Terminal = $true
                NextAction = "use_manual_dry_run_support_selection"
            }
        }
        "tls_repair_failed" {
            return [pscustomobject]@{
                Classification = "terminal_support_escalation"
                Terminal = $true
                NextAction = "use_manual_tls_repair_fallback"
            }
        }
        "runtime_start_failed" {
            return [pscustomobject]@{
                Classification = "terminal_support_escalation"
                Terminal = $true
                NextAction = "use_manual_start_fallback"
            }
        }
        "readiness_failed" {
            return [pscustomobject]@{
                Classification = "terminal_support_escalation"
                Terminal = $true
                NextAction = "use_status_and_log_guidance"
            }
        }
        "operation_expired" {
            return [pscustomobject]@{
                Classification = "terminal_timeout"
                Terminal = $true
                NextAction = "new_authorization_required"
            }
        }
        "rejected_expired_authorization" {
            return [pscustomobject]@{
                Classification = "rejected"
                Terminal = $true
                NextAction = "new_authorization_required"
            }
        }
        "rejected_operation_authorization" {
            return [pscustomobject]@{
                Classification = "rejected"
                Terminal = $true
                NextAction = "new_authorization_required"
            }
        }
        "capability_disabled" {
            return [pscustomobject]@{
                Classification = "rejected"
                Terminal = $true
                NextAction = "support_review_required"
            }
        }
        "rejected_replayed_authorization" {
            return [pscustomobject]@{
                Classification = "rejected"
                Terminal = $true
                NextAction = "new_authorization_required"
            }
        }
        default {
            $classification = if ($State -like "rejected_*" -or $State -eq "unsupported_runtime") { "rejected" } else { "unknown" }
            return [pscustomobject]@{
                Classification = $classification
                Terminal = $true
                NextAction = "support_review_required"
            }
        }
    }
}

function New-TowerScoutHostHelperPublicOperationStatus {
    param(
        [string] $State,

        [string] $OperationType = "provider_tls_repair",

        [string] $OperationId = "",

        [string] $Provider = "",

        [string] $Engine = "",

        [string] $Gpu = "",

        [int] $AppPort = 0,

        [bool] $Accepted = $false,

        [bool] $ExistingOperation = $false,

        [bool] $ExecutionEnabled = $false,

        [string] $Step = "",

        [string] $Classification = "",

        [bool] $Terminal = $false,

        [string] $NextAction = ""
    )

    $policy = Get-TowerScoutHostHelperOperationStatePolicy -State $State
    if ([string]::IsNullOrWhiteSpace($Classification)) {
        $Classification = [string] $policy.Classification
    }
    if ([string]::IsNullOrWhiteSpace($NextAction)) {
        $NextAction = [string] $policy.NextAction
    }
    if (-not $Terminal) {
        $Terminal = [bool] $policy.Terminal
    }
    if ([string]::IsNullOrWhiteSpace($Step)) {
        $Step = if ($State -eq "planned") { "planned" } else { "" }
    }

    return [pscustomobject]@{
        state = $State
        operation_id = $OperationId
        operation_type = $OperationType
        provider = $Provider
        accepted = $Accepted
        existing_operation = $ExistingOperation
        execution_enabled = $ExecutionEnabled
        current_step = $Step
        classification = $Classification
        terminal = $Terminal
        next_action = $NextAction
        runtime = [pscustomobject]@{
            engine = $Engine
            gpu = $Gpu
            app_port = $AppPort
        }
        steps = @("repair_tls", "stop_runtime", "start_runtime", "readiness_wait")
        timeout_seconds = $script:TowerScoutHostHelperOperationTimeoutSeconds
    }
}

function New-TowerScoutHostHelperHttpResult {
    param(
        [int] $StatusCode,

        [string] $Reason,

        [object] $Body = @{}
    )

    return [pscustomobject]@{
        StatusCode = $StatusCode
        Reason = $Reason
        Body = $Body
    }
}

function Get-TowerScoutHostHelperJsonValue {
    param(
        [object] $InputObject,

        [string] $Name
    )

    if ($null -eq $InputObject) {
        return ""
    }

    foreach ($property in @($InputObject.PSObject.Properties)) {
        if ([string]::Equals([string] $property.Name, $Name, [System.StringComparison]::OrdinalIgnoreCase)) {
            return [string] $property.Value
        }
    }

    return ""
}

function ConvertTo-TowerScoutHostHelperOperationStatusFromLock {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Lock,

        [string] $State = "",

        [bool] $ExistingOperation = $false
    )

    [int] $appPort = 0
    [int]::TryParse((Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "app_port"), [ref] $appPort) | Out-Null
    $stateOverrideProvided = -not [string]::IsNullOrWhiteSpace($State)
    $operationState = if (-not $stateOverrideProvided) {
        Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "state"
    }
    else {
        $State
    }
    $step = Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "current_step"
    $classification = Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "classification"
    $nextAction = Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "next_action"
    $terminalText = Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "terminal"
    [bool] $terminal = $false
    [bool]::TryParse($terminalText, [ref] $terminal) | Out-Null
    if ($stateOverrideProvided) {
        $overridePolicy = Get-TowerScoutHostHelperOperationStatePolicy -State $operationState
        $classification = [string] $overridePolicy.Classification
        $nextAction = [string] $overridePolicy.NextAction
        $terminal = [bool] $overridePolicy.Terminal
    }
    $executionEnabledText = Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "execution_enabled"
    [bool] $executionEnabled = $false
    [bool]::TryParse($executionEnabledText, [ref] $executionEnabled) | Out-Null

    return New-TowerScoutHostHelperPublicOperationStatus `
        -State $operationState `
        -OperationId (Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "operation_id") `
        -OperationType (Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "operation_type") `
        -Provider (Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "provider") `
        -Engine (Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "engine") `
        -Gpu (Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "gpu") `
        -AppPort $appPort `
        -Accepted:$true `
        -ExistingOperation:$ExistingOperation `
        -ExecutionEnabled:$executionEnabled `
        -Step $step `
        -Classification $classification `
        -Terminal:$terminal `
        -NextAction $nextAction
}

function New-TowerScoutHostHelperRejectedOperationPlan {
    param(
        [Parameter(Mandatory = $true)]
        [string] $State,

        [Parameter(Mandatory = $true)]
        [string] $Reason,

        [string] $Provider = "",

        [object] $Profile = $null
    )

    $engine = ""
    $gpu = ""
    [int] $appPort = 0
    if ($null -ne $Profile) {
        $engine = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "Engine"
        $gpu = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "Gpu"
        $appPortText = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "AppPort"
        [int]::TryParse($appPortText, [ref] $appPort) | Out-Null
    }
    $publicProvider = ([string] $Provider).Trim().ToLowerInvariant()
    if ($publicProvider -notin @("google", "azure")) {
        $publicProvider = "unknown"
    }

    return [pscustomobject]@{
        Accepted = $false
        State = $State
        Reason = $Reason
        OperationId = ""
        OperationType = "provider_tls_repair"
        Provider = $publicProvider
        PublicStatus = (New-TowerScoutHostHelperPublicOperationStatus `
            -State $State `
            -Provider $publicProvider `
            -Engine $engine `
            -Gpu $gpu `
            -AppPort $appPort)
    }
}

function New-TowerScoutProviderTlsRepairOperationPlan {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $Provider,

        [Parameter(Mandatory = $true)]
        [string] $Confirmation
    )

    $providerValue = ([string] $Provider).Trim().ToLowerInvariant()
    if ($providerValue -notin @("google", "azure")) {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_unknown_provider" `
            -Reason "provider_not_allowlisted" `
            -Provider $providerValue `
            -Profile $Profile
    }

    if (-not [string]::Equals([string] $Confirmation, $script:TowerScoutHostHelperProviderTlsRepairConfirmation, [System.StringComparison]::Ordinal)) {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_confirmation" `
            -Reason "confirmation_required" `
            -Provider $providerValue `
            -Profile $Profile
    }

    $engine = (Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "Engine").Trim().ToLowerInvariant()
    $gpu = (Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "Gpu").Trim().ToLowerInvariant()
    $appPortText = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "AppPort"
    [int] $appPort = 0
    if (-not [int]::TryParse($appPortText, [ref] $appPort) -or $appPort -lt 1 -or $appPort -gt 65535) {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_runtime_profile" `
            -Reason "invalid_app_port" `
            -Provider $providerValue `
            -Profile $Profile
    }

    if ($engine -ne "docker") {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "unsupported_runtime" `
            -Reason "docker_only_first_slice" `
            -Provider $providerValue `
            -Profile $Profile
    }
    if ($gpu -notin @("off", "auto", "on")) {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_runtime_profile" `
            -Reason "invalid_gpu_mode" `
            -Provider $providerValue `
            -Profile $Profile
    }

    $operationId = New-TowerScoutHostHelperSessionId
    $publicStatus = New-TowerScoutHostHelperPublicOperationStatus `
        -State "planned" `
        -OperationId $operationId `
        -Provider $providerValue `
        -Engine $engine `
        -Gpu $gpu `
        -AppPort $appPort `
        -Accepted:$true

    return [pscustomobject]@{
        Accepted = $true
        State = "planned"
        Reason = ""
        OperationId = $operationId
        OperationType = "provider_tls_repair"
        Provider = $providerValue
        Engine = $engine
        Gpu = $gpu
        AppPort = $appPort
        TimeoutSeconds = $script:TowerScoutHostHelperOperationTimeoutSeconds
        Confirmation = $script:TowerScoutHostHelperProviderTlsRepairConfirmation
        InternalCommands = [pscustomobject]@{
            Repair = [pscustomobject]@{
                Script = "scripts\repair-provider-tls.cmd"
                Arguments = @("-Provider", $providerValue, "-Engine", "docker", "-Gpu", $gpu, "-Apply")
            }
            Stop = [pscustomobject]@{
                Script = "scripts\stop.cmd"
                Arguments = @("-Engine", "docker")
            }
            Start = [pscustomobject]@{
                Script = "start.bat"
                Arguments = @("-Engine", "docker", "-Gpu", $gpu, "-Port", "$appPort", "-NoBrowser", "-TimeoutSeconds", "180")
            }
        }
        PublicStatus = $publicStatus
    }
}

function Get-TowerScoutHostHelperOperationLockPath {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile
    )

    $packageRoot = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "PackageRoot"
    $stateDirectory = Initialize-TowerScoutHostHelperStateDirectory -RootPath $packageRoot
    return (Join-Path $stateDirectory "operation-active.json")
}

function Get-TowerScoutHostHelperOperationStatusPath {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $OperationId
    )

    $packageRoot = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "PackageRoot"
    $stateDirectory = Initialize-TowerScoutHostHelperStateDirectory -RootPath $packageRoot
    $normalizedOperationId = Resolve-TowerScoutHostHelperSessionId -SessionId $OperationId
    return (Join-Path $stateDirectory ("operation-status-{0}.json" -f $normalizedOperationId))
}

function Get-TowerScoutHostHelperOperationWorkerPath {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $OperationId
    )

    $packageRoot = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "PackageRoot"
    $stateDirectory = Initialize-TowerScoutHostHelperStateDirectory -RootPath $packageRoot
    $normalizedOperationId = Resolve-TowerScoutHostHelperSessionId -SessionId $OperationId
    return (Join-Path $stateDirectory ("operation-worker-{0}.json" -f $normalizedOperationId))
}

function Save-TowerScoutHostHelperOperationWorkerIdentity {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $OperationId,

        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process] $Process
    )

    $workerPath = Get-TowerScoutHostHelperOperationWorkerPath `
        -Profile $Profile `
        -OperationId $OperationId
    $identity = [pscustomobject]@{
        operation_id = Resolve-TowerScoutHostHelperSessionId -SessionId $OperationId
        process_id = [int] $Process.Id
        process_start_time_utc = $Process.StartTime.ToUniversalTime().ToString("o")
    }
    Write-TowerScoutHostHelperJsonAtomic -Path $workerPath -Value $identity
    return $workerPath
}

function Test-TowerScoutHostHelperOperationWorkerActive {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $OperationId
    )

    $workerPath = Get-TowerScoutHostHelperOperationWorkerPath `
        -Profile $Profile `
        -OperationId $OperationId
    if (-not (Test-Path -LiteralPath $workerPath -PathType Leaf)) {
        return $null
    }
    $identity = Get-TowerScoutHostHelperJsonDocument -Path $workerPath
    [int] $processId = 0
    [datetime] $expectedStartUtc = [datetime]::MinValue
    if (
        $null -eq $identity -or
        -not [int]::TryParse(
            (Get-TowerScoutHostHelperObjectValue -InputObject $identity -Name "process_id"),
            [ref] $processId
        ) -or
        -not [datetime]::TryParse(
            (Get-TowerScoutHostHelperObjectValue -InputObject $identity -Name "process_start_time_utc"),
            [ref] $expectedStartUtc
        )
    ) {
        return $false
    }
    try {
        $process = Get-Process -Id $processId -ErrorAction Stop
        return (
            [Math]::Abs(
                ($process.StartTime.ToUniversalTime() - $expectedStartUtc.ToUniversalTime()).TotalSeconds
            ) -le 2
        )
    }
    catch {
        return $false
    }
}

function Clear-TowerScoutHostHelperOperationWorkerIdentity {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $OperationId
    )

    $workerPath = Get-TowerScoutHostHelperOperationWorkerPath `
        -Profile $Profile `
        -OperationId $OperationId
    Remove-Item -LiteralPath $workerPath -Force -ErrorAction SilentlyContinue
}

function Get-TowerScoutHostHelperOperationStatusRecord {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $OperationId
    )

    $statusPath = Get-TowerScoutHostHelperOperationStatusPath `
        -Profile $Profile `
        -OperationId $OperationId
    if (-not (Test-Path -LiteralPath $statusPath -PathType Leaf)) {
        return $null
    }
    try {
        return (Get-TowerScoutHostHelperJsonDocument -Path $statusPath)
    }
    catch {
        return $null
    }
}

function Find-TowerScoutHostHelperOperationByNonceFingerprint {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $NonceFingerprint
    )

    if ([string]::IsNullOrWhiteSpace($NonceFingerprint)) {
        return $null
    }
    $packageRoot = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "PackageRoot"
    $stateDirectory = Initialize-TowerScoutHostHelperStateDirectory -RootPath $packageRoot
    foreach ($file in @(Get-ChildItem -LiteralPath $stateDirectory -Filter "operation-status-*.json" -File -ErrorAction SilentlyContinue)) {
        try {
            $record = Get-TowerScoutHostHelperJsonDocument -Path $file.FullName
            if ($null -eq $record) {
                continue
            }
            $recordFingerprint = Get-TowerScoutHostHelperObjectValue -InputObject $record -Name "nonce_fingerprint"
            [datetime] $replayExpiresAtUtc = [datetime]::MinValue
            $replayExpiresText = Get-TowerScoutHostHelperObjectValue -InputObject $record -Name "replay_expires_at_utc"
            if (
                [string]::Equals($recordFingerprint, $NonceFingerprint, [System.StringComparison]::Ordinal) -and
                [datetime]::TryParse($replayExpiresText, [ref] $replayExpiresAtUtc) -and
                $replayExpiresAtUtc.ToUniversalTime() -gt (Get-Date).ToUniversalTime()
            ) {
                return $record
            }
        }
        catch {
            continue
        }
    }
    return $null
}

function Get-TowerScoutHostHelperOperationLock {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile
    )

    $lockPath = Get-TowerScoutHostHelperOperationLockPath -Profile $Profile
    if (-not (Test-Path -LiteralPath $lockPath -PathType Leaf)) {
        return $null
    }

    try {
        return (Get-TowerScoutHostHelperJsonDocument -Path $lockPath)
    }
    catch {
        return $null
    }
}

function Test-TowerScoutHostHelperOperationLockActive {
    param(
        [object] $Lock
    )

    if ($null -eq $Lock) {
        return $false
    }

    [datetime] $expiresAtUtc = [datetime]::MinValue
    $expiresText = Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "expires_at_utc"
    if (-not [datetime]::TryParse($expiresText, [ref] $expiresAtUtc)) {
        return $false
    }

    return ($expiresAtUtc.ToUniversalTime() -gt (Get-Date).ToUniversalTime())
}

function New-TowerScoutHostHelperOperationBusyResult {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Lock
    )

    return [pscustomobject]@{
        Acquired = $false
        State = "operation_busy"
        OperationId = Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "operation_id"
        PublicStatus = (ConvertTo-TowerScoutHostHelperOperationStatusFromLock `
            -Lock $Lock `
            -State "operation_busy" `
            -ExistingOperation:$true)
    }
}

function New-TowerScoutHostHelperOperationExistingResult {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Lock
    )

    return [pscustomobject]@{
        Acquired = $false
        State = "operation_exists"
        OperationId = Get-TowerScoutHostHelperObjectValue -InputObject $Lock -Name "operation_id"
        PublicStatus = (ConvertTo-TowerScoutHostHelperOperationStatusFromLock `
            -Lock $Lock `
            -ExistingOperation:$true)
    }
}

function New-TowerScoutHostHelperOperationLock {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [object] $Plan,

        [string] $OperationNonce = ""
    )

    if (-not [bool] $Plan.Accepted) {
        return [pscustomobject]@{
            Acquired = $false
            State = [string] $Plan.State
            OperationId = ""
            PublicStatus = $Plan.PublicStatus
        }
    }

    $nonceFingerprint = Get-TowerScoutHostHelperValueFingerprint -Value $OperationNonce
    $replayedOperation = Find-TowerScoutHostHelperOperationByNonceFingerprint `
        -Profile $Profile `
        -NonceFingerprint $nonceFingerprint
    if ($null -ne $replayedOperation) {
        if (-not [bool] $replayedOperation.terminal) {
            return New-TowerScoutHostHelperOperationExistingResult -Lock $replayedOperation
        }
        $replayedStatus = ConvertTo-TowerScoutHostHelperOperationStatusFromLock `
            -Lock $replayedOperation `
            -ExistingOperation:$true
        return [pscustomobject]@{
            Acquired = $false
            State = "rejected_replayed_authorization"
            OperationId = Get-TowerScoutHostHelperObjectValue -InputObject $replayedOperation -Name "operation_id"
            PublicStatus = $replayedStatus
        }
    }
    $lockPath = Get-TowerScoutHostHelperOperationLockPath -Profile $Profile
    $existingLock = Get-TowerScoutHostHelperOperationLock -Profile $Profile
    if (Test-TowerScoutHostHelperOperationLockActive -Lock $existingLock) {
        $existingFingerprint = Get-TowerScoutHostHelperObjectValue -InputObject $existingLock -Name "nonce_fingerprint"
        if (-not [string]::IsNullOrWhiteSpace($nonceFingerprint) -and [string]::Equals($existingFingerprint, $nonceFingerprint, [System.StringComparison]::Ordinal)) {
            return New-TowerScoutHostHelperOperationExistingResult -Lock $existingLock
        }
        return New-TowerScoutHostHelperOperationBusyResult -Lock $existingLock
    }
    if ($null -ne $existingLock -and (Test-Path -LiteralPath $lockPath -PathType Leaf)) {
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    }

    $createdAtUtc = (Get-Date).ToUniversalTime()
    $expiresAtUtc = $createdAtUtc.AddSeconds($script:TowerScoutHostHelperOperationTimeoutSeconds)
    $policy = Get-TowerScoutHostHelperOperationStatePolicy -State "planned"
    $lock = [pscustomobject]@{
        operation_id = [string] $Plan.OperationId
        operation_type = [string] $Plan.OperationType
        state = "planned"
        current_step = "planned"
        classification = [string] $policy.Classification
        terminal = [bool] $policy.Terminal
        next_action = [string] $policy.NextAction
        execution_enabled = $false
        provider = [string] $Plan.Provider
        engine = [string] $Plan.Engine
        gpu = [string] $Plan.Gpu
        app_port = [int] $Plan.AppPort
        created_at_utc = $createdAtUtc.ToString("o")
        expires_at_utc = $expiresAtUtc.ToString("o")
        status_expires_at_utc = $createdAtUtc.AddSeconds(
            $script:TowerScoutHostHelperOperationStatusRetentionSeconds
        ).ToString("o")
        replay_expires_at_utc = $createdAtUtc.AddSeconds(
            $script:TowerScoutHostHelperReplayRetentionSeconds
        ).ToString("o")
        nonce_fingerprint = $nonceFingerprint
    }
    $json = $lock | ConvertTo-Json -Depth 8
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($json)

    $stream = $null
    try {
        $stream = [System.IO.File]::Open($lockPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    }
    catch [System.IO.IOException] {
        $raceLock = Get-TowerScoutHostHelperOperationLock -Profile $Profile
        if (Test-TowerScoutHostHelperOperationLockActive -Lock $raceLock) {
            $raceFingerprint = Get-TowerScoutHostHelperObjectValue -InputObject $raceLock -Name "nonce_fingerprint"
            if (-not [string]::IsNullOrWhiteSpace($nonceFingerprint) -and [string]::Equals($raceFingerprint, $nonceFingerprint, [System.StringComparison]::Ordinal)) {
                return New-TowerScoutHostHelperOperationExistingResult -Lock $raceLock
            }
            return New-TowerScoutHostHelperOperationBusyResult -Lock $raceLock
        }
        throw
    }
    finally {
        if ($null -ne $stream) {
            $stream.Dispose()
        }
    }
    Protect-TowerScoutHostHelperStatePath -Path $lockPath
    $statusPath = Get-TowerScoutHostHelperOperationStatusPath `
        -Profile $Profile `
        -OperationId ([string] $Plan.OperationId)
    Write-TowerScoutHostHelperJsonAtomic -Path $statusPath -Value $lock

    return [pscustomobject]@{
        Acquired = $true
        State = "operation_locked"
        OperationId = [string] $Plan.OperationId
        PublicStatus = (ConvertTo-TowerScoutHostHelperOperationStatusFromLock -Lock $lock)
    }
}

function Get-TowerScoutHostHelperOperationStatus {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $OperationId
    )

    $normalizedOperationId = ""
    try {
        $normalizedOperationId = Resolve-TowerScoutHostHelperSessionId -SessionId $OperationId
    }
    catch {
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode 404 `
            -Reason "Not Found" `
            -Body @{ state = "rejected_unknown_operation" }
    }

    $lock = Get-TowerScoutHostHelperOperationStatusRecord `
        -Profile $Profile `
        -OperationId $normalizedOperationId
    if ($null -eq $lock) {
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode 404 `
            -Reason "Not Found" `
            -Body @{ state = "rejected_unknown_operation" }
    }

    [datetime] $statusExpiresAtUtc = [datetime]::MinValue
    $statusExpiresText = Get-TowerScoutHostHelperObjectValue -InputObject $lock -Name "status_expires_at_utc"
    if (
        -not [datetime]::TryParse($statusExpiresText, [ref] $statusExpiresAtUtc) -or
        $statusExpiresAtUtc.ToUniversalTime() -le (Get-Date).ToUniversalTime()
    ) {
        $statusPath = Get-TowerScoutHostHelperOperationStatusPath `
            -Profile $Profile `
            -OperationId $normalizedOperationId
        Remove-Item -LiteralPath $statusPath -Force -ErrorAction SilentlyContinue
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode 410 `
            -Reason "Gone" `
            -Body (ConvertTo-TowerScoutHostHelperOperationStatusFromLock `
                -Lock $lock `
                -State "operation_expired")
    }

    $publicStatus = Complete-TowerScoutHostHelperExpiredOperation `
        -Profile $Profile `
        -Record $lock `
        -OperationId $normalizedOperationId
    if ($null -eq $publicStatus) {
        [bool] $terminal = $false
        [bool]::TryParse(
            (Get-TowerScoutHostHelperObjectValue -InputObject $lock -Name "terminal"),
            [ref] $terminal
        ) | Out-Null
        [bool] $executionEnabled = $false
        [bool]::TryParse(
            (Get-TowerScoutHostHelperObjectValue -InputObject $lock -Name "execution_enabled"),
            [ref] $executionEnabled
        ) | Out-Null
        $workerActive = Test-TowerScoutHostHelperOperationWorkerActive `
            -Profile $Profile `
            -OperationId $normalizedOperationId
        if (-not $terminal -and $executionEnabled -and $workerActive -eq $false) {
            try {
                $publicStatus = Set-TowerScoutHostHelperOperationLockState `
                    -Profile $Profile `
                    -OperationId $normalizedOperationId `
                    -State "runtime_start_failed" `
                    -Step "worker_exit" `
                    -ExecutionEnabled:$true
            }
            catch {
                $lock = Get-TowerScoutHostHelperOperationStatusRecord `
                    -Profile $Profile `
                    -OperationId $normalizedOperationId
            }
        }
    }
    if ($null -eq $publicStatus) {
        $publicStatus = ConvertTo-TowerScoutHostHelperOperationStatusFromLock -Lock $lock
    }
    return New-TowerScoutHostHelperHttpResult `
        -StatusCode 200 `
        -Reason "OK" `
        -Body $publicStatus
}

function ConvertTo-TowerScoutHostHelperScriptExitState {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("repair", "stop", "start", "readiness")]
        [string] $Step,

        [int] $ExitCode = 0,

        [bool] $TimedOut = $false
    )

    if ($TimedOut) {
        return "operation_timeout"
    }

    switch ($Step) {
        "repair" {
            if ($ExitCode -eq 0) { return "tls_repair_completed" }
            if ($ExitCode -eq 2) { return "tls_repair_selection_required" }
            return "tls_repair_failed"
        }
        "stop" {
            if ($ExitCode -eq 0) { return "runtime_stopped" }
            return "runtime_stop_failed"
        }
        "start" {
            if ($ExitCode -eq 0) { return "ready" }
            if ($ExitCode -eq 2) { return "readiness_timeout" }
            return "runtime_start_failed"
        }
        "readiness" {
            if ($ExitCode -eq 0) { return "ready" }
            if ($ExitCode -eq 2) { return "readiness_timeout" }
            return "readiness_failed"
        }
    }
}

function Get-TowerScoutHostHelperStepTimeoutSeconds {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("repair", "stop", "start")]
        [string] $Step
    )

    return [int] $script:TowerScoutHostHelperOperationStepTimeoutSeconds[$Step]
}

function Get-TowerScoutHostHelperBatchInterpreterPath {
    $systemDirectory = [string] [System.Environment]::SystemDirectory
    if ([string]::IsNullOrWhiteSpace($systemDirectory)) {
        throw "Windows system directory could not be resolved for the helper command interpreter."
    }

    $cmdPath = Join-Path $systemDirectory "cmd.exe"
    if (-not (Test-Path -LiteralPath $cmdPath -PathType Leaf)) {
        throw "The fixed Windows command interpreter was not found."
    }

    return (Resolve-Path -LiteralPath $cmdPath).Path
}

function Get-TowerScoutHostHelperTaskkillPath {
    $systemDirectory = [string] [System.Environment]::SystemDirectory
    if ([string]::IsNullOrWhiteSpace($systemDirectory)) {
        throw "Windows system directory could not be resolved for helper process-tree cleanup."
    }

    $taskkillPath = Join-Path $systemDirectory "taskkill.exe"
    if (-not (Test-Path -LiteralPath $taskkillPath -PathType Leaf)) {
        throw "The fixed Windows taskkill utility was not found."
    }

    return (Resolve-Path -LiteralPath $taskkillPath).Path
}

function ConvertTo-TowerScoutHostHelperCmdArgument {
    param(
        [string] $Value = ""
    )

    return '"' + (([string] $Value).Replace('"', '\"')) + '"'
}

function Assert-TowerScoutHostHelperExpectedArguments {
    param(
        [string[]] $Actual = @(),

        [string[]] $Expected = @()
    )

    if ($Actual.Count -ne $Expected.Count) {
        throw "The helper operation plan arguments did not match the controlled runner contract."
    }

    for ($index = 0; $index -lt $Expected.Count; $index += 1) {
        if (-not [string]::Equals([string] $Actual[$index], [string] $Expected[$index], [System.StringComparison]::Ordinal)) {
            throw "The helper operation plan arguments did not match the controlled runner contract."
        }
    }
}

function Resolve-TowerScoutHostHelperPackageCommandPath {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $RelativeScriptPath
    )

    if ([System.IO.Path]::IsPathRooted($RelativeScriptPath)) {
        throw "The helper operation plan selected a rooted command path."
    }

    $packageRoot = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "PackageRoot"
    if ([string]::IsNullOrWhiteSpace($packageRoot)) {
        throw "The helper runtime profile did not include a package root."
    }

    $resolvedRoot = (Resolve-Path -LiteralPath $packageRoot).Path
    $rootFullPath = [System.IO.Path]::GetFullPath($resolvedRoot).TrimEnd(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $candidatePath = [System.IO.Path]::GetFullPath((Join-Path $rootFullPath $RelativeScriptPath))
    $rootPrefix = $rootFullPath + [System.IO.Path]::DirectorySeparatorChar
    if (-not $candidatePath.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "The helper operation plan selected a command path outside the package root."
    }
    if (-not (Test-Path -LiteralPath $candidatePath -PathType Leaf)) {
        throw "The helper operation plan selected a missing package-local command wrapper."
    }

    return (Resolve-Path -LiteralPath $candidatePath).Path
}

function Resolve-TowerScoutHostHelperControlledCommand {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [object] $Plan,

        [Parameter(Mandatory = $true)]
        [ValidateSet("repair", "stop", "start")]
        [string] $Step
    )

    if (-not [bool] $Plan.Accepted) {
        throw "The helper controlled runner requires an accepted operation plan."
    }
    if ([string] $Plan.Engine -ne "docker") {
        throw "The helper controlled runner is Docker-only for this slice."
    }
    if ([string] $Plan.Provider -notin @("google", "azure")) {
        throw "The helper controlled runner rejected a non-allowlisted provider."
    }
    if ([string] $Plan.Gpu -notin @("off", "auto", "on")) {
        throw "The helper controlled runner rejected an invalid GPU mode."
    }
    if ([int] $Plan.AppPort -lt 1 -or [int] $Plan.AppPort -gt 65535) {
        throw "The helper controlled runner rejected an invalid app port."
    }

    $command = switch ($Step) {
        "repair" { $Plan.InternalCommands.Repair }
        "stop" { $Plan.InternalCommands.Stop }
        "start" { $Plan.InternalCommands.Start }
    }
    $expectedScript = [string] $script:TowerScoutHostHelperOperationCommandScripts[$Step]
    if (-not [string]::Equals([string] $command.Script, $expectedScript, [System.StringComparison]::Ordinal)) {
        throw "The helper operation plan selected a non-allowlisted command wrapper."
    }

    $expectedArguments = switch ($Step) {
        "repair" { @("-Provider", [string] $Plan.Provider, "-Engine", "docker", "-Gpu", [string] $Plan.Gpu, "-Apply") }
        "stop" { @("-Engine", "docker") }
        "start" { @("-Engine", "docker", "-Gpu", [string] $Plan.Gpu, "-Port", "$([int] $Plan.AppPort)", "-NoBrowser", "-TimeoutSeconds", "180") }
    }
    Assert-TowerScoutHostHelperExpectedArguments -Actual @($command.Arguments) -Expected $expectedArguments

    $scriptPath = Resolve-TowerScoutHostHelperPackageCommandPath -Profile $Profile -RelativeScriptPath $expectedScript
    $interpreterPath = Get-TowerScoutHostHelperBatchInterpreterPath
    $environmentVariables = @{}
    if ($Step -in @("stop", "start")) {
        # The controlled stop/start sequence must preserve its supervising
        # helper. Both wrappers can otherwise re-enter normal launcher cleanup
        # through inherited review-session environment values.
        $environmentVariables["TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION"] = "1"
    }

    return [pscustomobject]@{
        Step = $Step
        Script = $expectedScript
        ScriptPath = $scriptPath
        Arguments = @($expectedArguments)
        Interpreter = "cmd.exe"
        InterpreterPath = $interpreterPath
        InterpreterArguments = @("/d", "/s", "/c")
        WorkingDirectory = (Resolve-Path -LiteralPath (Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "PackageRoot")).Path
        TimeoutSeconds = (Get-TowerScoutHostHelperStepTimeoutSeconds -Step $Step)
        EnvironmentVariables = $environmentVariables
    }
}

function Test-TowerScoutHostHelperRealWrapperContract {
    param(
        [string] $RootPath = $(Resolve-Path (Join-Path $PSScriptRoot "..\..")),

        [ValidateSet("google", "azure")]
        [string] $Provider = "google",

        [ValidateSet("off", "auto", "on")]
        [string] $Gpu = "off",

        [int] $AppPort = 5000
    )

    $resolvedRoot = (Resolve-Path -LiteralPath $RootPath).Path
    $profile = New-TowerScoutHostHelperRuntimeProfile `
        -Engine "docker" `
        -Gpu $Gpu `
        -AppPort $AppPort `
        -PackageRoot $resolvedRoot `
        -PackageFlavor "real-wrapper-contract"
    $plan = New-TowerScoutProviderTlsRepairOperationPlan `
        -Profile $profile `
        -Provider $Provider `
        -Confirmation $script:TowerScoutHostHelperProviderTlsRepairConfirmation
    if (-not [bool] $plan.Accepted) {
        throw "The real-wrapper contract check could not create an accepted provider TLS repair plan."
    }

    $validatedSteps = @()
    foreach ($step in @("repair", "stop", "start")) {
        $command = Resolve-TowerScoutHostHelperControlledCommand `
            -Profile $profile `
            -Plan $plan `
            -Step $step
        $expectedScript = [string] $script:TowerScoutHostHelperOperationCommandScripts[$step]
        $expectedLeaf = [System.IO.Path]::GetFileName($expectedScript)
        $actualLeaf = [System.IO.Path]::GetFileName([string] $command.ScriptPath)
        if (-not [string]::Equals($actualLeaf, $expectedLeaf, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "The real-wrapper contract check resolved an unexpected command wrapper."
        }
        if (-not [string]::Equals([string] $command.Interpreter, "cmd.exe", [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "The real-wrapper contract check resolved an unexpected command interpreter."
        }
        if ([string]::Join(" ", @($command.InterpreterArguments)) -ne "/d /s /c") {
            throw "The real-wrapper contract check resolved unexpected command interpreter arguments."
        }
        if (-not [string]::Equals([string] $command.WorkingDirectory, $resolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "The real-wrapper contract check resolved an unexpected working directory."
        }

        $validatedSteps += [pscustomobject]@{
            step = $step
            argument_count = @($command.Arguments).Count
            timeout_seconds = [int] $command.TimeoutSeconds
        }
    }

    return [pscustomobject]@{
        state = "real_wrapper_contract_validated"
        operation_type = "provider_tls_repair"
        provider = $Provider
        execution_enabled = $false
        executed = $false
        runtime = [pscustomobject]@{
            engine = "docker"
            gpu = $Gpu
            app_port = $AppPort
        }
        step_count = $validatedSteps.Count
        steps = @($validatedSteps)
    }
}

function Stop-TowerScoutHostHelperProcessTree {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process] $Process,

        [int] $CleanupTimeoutMs = $script:TowerScoutHostHelperProcessTreeCleanupTimeoutMs,

        [switch] $RequireExit
    )

    if ($CleanupTimeoutMs -lt 1) {
        throw "CleanupTimeoutMs must be at least 1."
    }

    if ($Process.HasExited) {
        return [pscustomobject]@{
            Exited = $true
            TaskkillExitCode = $null
            FallbackAttempted = $false
        }
    }

    $taskkillExitCode = $null
    $fallbackAttempted = $false
    try {
        if ($env:OS -eq "Windows_NT") {
            $taskkillPath = Get-TowerScoutHostHelperTaskkillPath
            & $taskkillPath /PID $Process.Id /T /F 2>$null | Out-Null
            $taskkillExitCode = $LASTEXITCODE
        }
        else {
            try {
                $Process.Kill($true)
            }
            catch {
                $Process.Kill()
            }
        }
    }
    catch {
        $fallbackAttempted = $true
    }

    try {
        $Process.Refresh()
    }
    catch {
        # The final exit check below is authoritative.
    }
    if (
        -not $Process.HasExited -and
        ($fallbackAttempted -or $env:OS -eq "Windows_NT")
    ) {
        $fallbackAttempted = $true
        try {
            $Process.Kill()
        }
        catch {
            # The verified wait below decides whether cleanup succeeded.
        }
    }

    $exited = $Process.HasExited
    try {
        if (-not $exited) {
            $exited = $Process.WaitForExit($CleanupTimeoutMs)
        }
    }
    catch {
        $exited = $false
    }
    if (-not $exited) {
        try {
            $Process.Refresh()
            $exited = $Process.HasExited
        }
        catch {
            $exited = $false
        }
    }

    if ($RequireExit -and -not $exited) {
        throw "The TowerScout host helper process tree did not exit within the cleanup timeout."
    }

    return [pscustomobject]@{
        Exited = [bool] $exited
        TaskkillExitCode = $taskkillExitCode
        FallbackAttempted = [bool] $fallbackAttempted
    }
}

function Wait-TowerScoutHostHelperOutputTask {
    param(
        [Parameter(Mandatory = $true)]
        [System.Threading.Tasks.Task] $Task,

        [int] $TimeoutMs = $script:TowerScoutHostHelperProcessOutputDrainTimeoutMs
    )

    try {
        if ($Task.Wait($TimeoutMs)) {
            return [string] $Task.Result
        }
    }
    catch {
        return ""
    }

    return ""
}

function Invoke-TowerScoutHostHelperProcessCommand {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Command,

        [object] $Profile = $null
    )

    $process = New-Object System.Diagnostics.Process
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = [string] $Command.InterpreterPath
    $scriptAndArguments = @(
        (ConvertTo-TowerScoutHostHelperCmdArgument -Value ([string] $Command.ScriptPath))
    ) + @($Command.Arguments | ForEach-Object { ConvertTo-TowerScoutHostHelperCmdArgument -Value ([string] $_) })
    $commandLine = [string]::Join(" ", $scriptAndArguments)
    $startInfo.Arguments = ([string]::Join(" ", @($Command.InterpreterArguments))) + ' "' + $commandLine + '"'
    $startInfo.WorkingDirectory = [string] $Command.WorkingDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true
    $commandEnvironmentVariables = $null
    if ($Command.PSObject.Properties.Name -contains "EnvironmentVariables") {
        $commandEnvironmentVariables = $Command.PSObject.Properties["EnvironmentVariables"].Value
    }
    if ($commandEnvironmentVariables -is [System.Collections.IDictionary]) {
        $controlledOperationMarker = [string] $commandEnvironmentVariables["TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION"]
        if ([string]::Equals($controlledOperationMarker, "1", [System.StringComparison]::Ordinal)) {
            $startInfo.EnvironmentVariables.Set_Item("TOWERSCOUT_HOST_HELPER_CONTROLLED_OPERATION", "1")
        }
    }
    $process.StartInfo = $startInfo

    $started = $process.Start()
    if (-not $started) {
        throw "The helper controlled runner could not start the fixed command interpreter."
    }

    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $deadline = (Get-Date).AddSeconds([int] $Command.TimeoutSeconds)
    $timedOut = $false
    $cancelled = $false
    while (-not $process.WaitForExit(250)) {
        if ($null -ne $Profile -and -not (Test-TowerScoutHostHelperSessionActive -Profile $Profile)) {
            # A host sleep/resume or bounded request read can temporarily age
            # the listener heartbeat. Give the listener one full request
            # deadline to refresh before terminating a restart command.
            $sessionRecoveryDeadline = (Get-Date).AddMilliseconds(
                $script:TowerScoutHostHelperReadTimeoutMs + 1000
            )
            while (
                -not $process.HasExited -and
                (Get-Date) -lt $sessionRecoveryDeadline -and
                -not (Test-TowerScoutHostHelperSessionActive -Profile $Profile)
            ) {
                Start-Sleep -Milliseconds 250
            }
            if (
                -not $process.HasExited -and
                -not (Test-TowerScoutHostHelperSessionActive -Profile $Profile)
            ) {
                $cancelled = $true
                break
            }
        }
        if ((Get-Date) -ge $deadline) {
            $timedOut = $true
            break
        }
    }
    if ($timedOut -or $cancelled) {
        try {
            Stop-TowerScoutHostHelperProcessTree -Process $process -RequireExit | Out-Null
        }
        catch {
            $process.Dispose()
            throw
        }
    }
    else {
        $process.WaitForExit()
    }

    $stdout = Wait-TowerScoutHostHelperOutputTask -Task $stdoutTask
    $stderr = Wait-TowerScoutHostHelperOutputTask -Task $stderrTask
    $exitCode = if ($timedOut -or $cancelled) { 1 } else { [int] $process.ExitCode }
    $process.Dispose()

    return [pscustomobject]@{
        ExitCode = $exitCode
        TimedOut = $timedOut
        Cancelled = $cancelled
        StdoutByteCount = [System.Text.Encoding]::UTF8.GetByteCount($stdout)
        StderrByteCount = [System.Text.Encoding]::UTF8.GetByteCount($stderr)
    }
}

function Set-TowerScoutHostHelperOperationLockState {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $OperationId,

        [Parameter(Mandatory = $true)]
        [string] $State,

        [string] $Step = "",

        [bool] $ExecutionEnabled = $false
    )

    $lockPath = Get-TowerScoutHostHelperOperationLockPath -Profile $Profile
    $activeLock = Get-TowerScoutHostHelperOperationLock -Profile $Profile
    $lock = Get-TowerScoutHostHelperOperationStatusRecord `
        -Profile $Profile `
        -OperationId $OperationId
    if (
        $null -eq $lock -or
        $null -eq $activeLock -or
        -not [string]::Equals(
            (Get-TowerScoutHostHelperObjectValue -InputObject $activeLock -Name "operation_id"),
            $OperationId,
            [System.StringComparison]::Ordinal
        )
    ) {
        throw "The helper operation lock was not available for status update."
    }

    $policy = Get-TowerScoutHostHelperOperationStatePolicy -State $State
    Set-TowerScoutHostHelperObjectValue -InputObject $lock -Name "state" -Value $State
    Set-TowerScoutHostHelperObjectValue -InputObject $lock -Name "current_step" -Value $Step
    Set-TowerScoutHostHelperObjectValue -InputObject $lock -Name "classification" -Value ([string] $policy.Classification)
    Set-TowerScoutHostHelperObjectValue -InputObject $lock -Name "terminal" -Value ([bool] $policy.Terminal)
    Set-TowerScoutHostHelperObjectValue -InputObject $lock -Name "next_action" -Value ([string] $policy.NextAction)
    Set-TowerScoutHostHelperObjectValue -InputObject $lock -Name "execution_enabled" -Value $ExecutionEnabled
    Set-TowerScoutHostHelperObjectValue -InputObject $lock -Name "updated_at_utc" -Value ((Get-Date).ToUniversalTime().ToString("o"))
    if ([bool] $policy.Terminal) {
        Set-TowerScoutHostHelperObjectValue -InputObject $lock -Name "completed_at_utc" -Value ((Get-Date).ToUniversalTime().ToString("o"))
    }
    $statusPath = Get-TowerScoutHostHelperOperationStatusPath `
        -Profile $Profile `
        -OperationId $OperationId
    Write-TowerScoutHostHelperJsonAtomic -Path $statusPath -Value $lock
    if ([bool] $policy.Terminal) {
        $currentActive = Get-TowerScoutHostHelperOperationLock -Profile $Profile
        if (
            $null -ne $currentActive -and
            [string]::Equals(
                (Get-TowerScoutHostHelperObjectValue -InputObject $currentActive -Name "operation_id"),
                $OperationId,
                [System.StringComparison]::Ordinal
            )
        ) {
            Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
        }
        Clear-TowerScoutHostHelperOperationWorkerIdentity `
            -Profile $Profile `
            -OperationId $OperationId
    }
    else {
        Write-TowerScoutHostHelperJsonAtomic -Path $lockPath -Value $lock
    }
    return ConvertTo-TowerScoutHostHelperOperationStatusFromLock -Lock $lock
}

function Invoke-TowerScoutHostHelperControlledCommand {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [object] $Plan,

        [Parameter(Mandatory = $true)]
        [ValidateSet("repair", "stop", "start")]
        [string] $Step,

        [scriptblock] $CommandInvoker = $null
    )

    $command = Resolve-TowerScoutHostHelperControlledCommand -Profile $Profile -Plan $Plan -Step $Step
    $processResult = if ($null -ne $CommandInvoker) {
        & $CommandInvoker $command
    }
    else {
        Invoke-TowerScoutHostHelperProcessCommand -Command $command -Profile $Profile
    }
    $timedOutText = Get-TowerScoutHostHelperObjectValue -InputObject $processResult -Name "TimedOut"
    [bool] $timedOut = $false
    [bool]::TryParse($timedOutText, [ref] $timedOut) | Out-Null
    [int] $exitCode = 1
    [int]::TryParse((Get-TowerScoutHostHelperObjectValue -InputObject $processResult -Name "ExitCode"), [ref] $exitCode) | Out-Null
    $state = ConvertTo-TowerScoutHostHelperScriptExitState -Step $Step -ExitCode $exitCode -TimedOut:$timedOut
    $policy = Get-TowerScoutHostHelperOperationStatePolicy -State $state

    return [pscustomobject]@{
        Step = $Step
        State = $state
        Classification = [string] $policy.Classification
        Terminal = [bool] $policy.Terminal
        NextAction = [string] $policy.NextAction
        TimedOut = $timedOut
        ExitCode = $exitCode
    }
}

function Invoke-TowerScoutProviderTlsRepairControlledExecution {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [object] $Plan,

        [bool] $ExecutionEnabled = $script:TowerScoutHostHelperExecutionEnabledByDefault,

        [scriptblock] $CommandInvoker = $null
    )

    if (-not $ExecutionEnabled) {
        return Set-TowerScoutHostHelperOperationLockState `
            -Profile $Profile `
            -OperationId ([string] $Plan.OperationId) `
            -State "planned" `
            -Step "planned" `
            -ExecutionEnabled:$false
    }

    $lastStatus = $null
    foreach ($step in @("repair", "stop", "start")) {
        $runningState = switch ($step) {
            "repair" { "tls_repair_running" }
            "stop" { "runtime_stopping" }
            "start" { "runtime_starting" }
        }
        Set-TowerScoutHostHelperOperationLockState `
            -Profile $Profile `
            -OperationId ([string] $Plan.OperationId) `
            -State $runningState `
            -Step $step `
            -ExecutionEnabled:$true | Out-Null
        try {
            $result = Invoke-TowerScoutHostHelperControlledCommand `
                -Profile $Profile `
                -Plan $Plan `
                -Step $step `
                -CommandInvoker $CommandInvoker
        }
        catch {
            $failureState = switch ($step) {
                "repair" { "tls_repair_failed" }
                "stop" { "runtime_stop_failed" }
                "start" { "runtime_start_failed" }
            }
            return Set-TowerScoutHostHelperOperationLockState `
                -Profile $Profile `
                -OperationId ([string] $Plan.OperationId) `
                -State $failureState `
                -Step $step `
                -ExecutionEnabled:$true
        }
        $lastStatus = Set-TowerScoutHostHelperOperationLockState `
            -Profile $Profile `
            -OperationId ([string] $Plan.OperationId) `
            -State ([string] $result.State) `
            -Step $step `
            -ExecutionEnabled:$true
        if ([bool] $result.Terminal) {
            return $lastStatus
        }
    }

    return $lastStatus
}

function Read-TowerScoutProviderTlsRepairRequestBody {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Request,

        [Parameter(Mandatory = $true)]
        [object] $Profile
    )

    $contentType = [string] $Request.Headers["content-type"]
    $contentTypeBase = if ([string]::IsNullOrWhiteSpace($contentType)) { "" } else { $contentType.Split([char[]] @(";"), 2)[0].Trim().ToLowerInvariant() }
    if ($contentTypeBase -ne "application/json") {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_content_type" `
            -Reason "json_required" `
            -Profile $Profile
    }

    $bodyText = [string] $Request.BodyText
    if ([string]::IsNullOrWhiteSpace($bodyText)) {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_bad_request" `
            -Reason "json_body_required" `
            -Profile $Profile
    }
    if ([System.Text.Encoding]::UTF8.GetByteCount($bodyText) -gt $script:TowerScoutHostHelperMaxBodyBytes) {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_bad_request" `
            -Reason "json_body_too_large" `
            -Profile $Profile
    }

    try {
        $payload = $bodyText | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_bad_json" `
            -Reason "json_parse_failed" `
            -Profile $Profile
    }

    if ($null -eq $payload -or $payload -is [array]) {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_bad_json" `
            -Reason "json_object_required" `
            -Profile $Profile
    }

    $allowedProperties = @("provider", "confirmation", "operation_authorization")
    foreach ($property in @($payload.PSObject.Properties)) {
        $propertyName = ([string] $property.Name).Trim().ToLowerInvariant()
        if ($propertyName -notin $allowedProperties) {
            return New-TowerScoutHostHelperRejectedOperationPlan `
                -State "rejected_unexpected_field" `
                -Reason "unexpected_field" `
                -Profile $Profile
        }
    }

    $operationAuthorization = Get-TowerScoutHostHelperJsonValue -InputObject $payload -Name "operation_authorization"
    if ([string]::IsNullOrWhiteSpace($operationAuthorization) -or $operationAuthorization -notmatch $script:TowerScoutHostHelperOperationAuthorizationPattern) {
        return New-TowerScoutHostHelperRejectedOperationPlan `
            -State "rejected_operation_authorization" `
            -Reason "operation_authorization_required" `
            -Profile $Profile
    }

    return [pscustomobject]@{
        Accepted = $true
        Provider = Get-TowerScoutHostHelperJsonValue -InputObject $payload -Name "provider"
        Confirmation = Get-TowerScoutHostHelperJsonValue -InputObject $payload -Name "confirmation"
        OperationAuthorization = $operationAuthorization
    }
}

function Add-TowerScoutHostHelperStatusAuthorization {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [object] $PublicStatus
    )

    $operationId = Get-TowerScoutHostHelperObjectValue -InputObject $PublicStatus -Name "operation_id"
    $provider = Get-TowerScoutHostHelperObjectValue -InputObject $PublicStatus -Name "provider"
    $authorizationKey = Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "BrowserAuthorizationKey"
    if (
        $operationId -notmatch "^[a-f0-9]{32}$" -or
        $provider -notin @("google", "azure") -or
        $authorizationKey -notmatch "^[A-Za-z0-9_-]{43}$"
    ) {
        return $PublicStatus
    }
    $statusAuthorization = New-TowerScoutHostHelperBrowserAuthorization `
        -Profile $Profile `
        -Scope "operation_status" `
        -Provider $provider `
        -OperationId $operationId
    Set-TowerScoutHostHelperObjectValue `
        -InputObject $PublicStatus `
        -Name "status_authorization" `
        -Value $statusAuthorization
    return $PublicStatus
}

function Start-TowerScoutHostHelperOperationWorker {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [object] $Plan
    )

    $workerPath = Join-Path ([string] $Profile.PackageRoot) "scripts\host-helper-worker.ps1"
    if (-not (Test-Path -LiteralPath $workerPath -PathType Leaf)) {
        throw "The fixed TowerScout host-helper worker script is unavailable."
    }
    $powerShell = Get-Command "powershell.exe" -CommandType Application -ErrorAction Stop
    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        (ConvertTo-TowerScoutHostHelperCmdArgument -Value $workerPath),
        "-Engine",
        ([string] $Profile.Engine),
        "-Gpu",
        ([string] $Profile.Gpu),
        "-AppPort",
        ([string] $Profile.AppPort),
        "-PackageFlavor",
        (ConvertTo-TowerScoutHostHelperCmdArgument -Value ([string] $Profile.PackageFlavor)),
        "-HelperSessionId",
        ([string] $Profile.HelperSessionId),
        "-OperationId",
        ([string] $Plan.OperationId),
        "-Provider",
        ([string] $Plan.Provider)
    )
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = [string] $powerShell.Source
    $startInfo.Arguments = [string]::Join(" ", $arguments)
    $startInfo.WorkingDirectory = [string] $Profile.PackageRoot
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw "The fixed TowerScout host-helper worker could not be started."
    }
    try {
        Save-TowerScoutHostHelperOperationWorkerIdentity `
            -Profile $Profile `
            -OperationId ([string] $Plan.OperationId) `
            -Process $process | Out-Null
        return $process.Id
    }
    catch {
        Stop-TowerScoutHostHelperProcessTree -Process $process -RequireExit | Out-Null
        throw
    }
    finally {
        $process.Dispose()
    }
}

function New-TowerScoutProviderTlsRepairOperationPlanResponse {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [object] $Request,

        [bool] $ExecutionEnabled = $script:TowerScoutHostHelperExecutionEnabledByDefault,

        [scriptblock] $CommandInvoker = $null,

        [bool] $RequireSignedAuthorization = $false,

        [scriptblock] $WorkerStarter = $null
    )

    [bool] $providerTlsRepairEnabled = $false
    [bool]::TryParse(
        (Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "ProviderTlsRepairEnabled"),
        [ref] $providerTlsRepairEnabled
    ) | Out-Null
    if (-not $providerTlsRepairEnabled) {
        $disabledStatus = New-TowerScoutHostHelperPublicOperationStatus `
            -State "capability_disabled"
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode 403 `
            -Reason "Forbidden" `
            -Body $disabledStatus
    }

    $payload = Read-TowerScoutProviderTlsRepairRequestBody -Request $Request -Profile $Profile
    if (-not [bool] $payload.Accepted) {
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode 400 `
            -Reason "Bad Request" `
            -Body $payload.PublicStatus
    }

    if ($RequireSignedAuthorization) {
        $authorization = Resolve-TowerScoutHostHelperBrowserAuthorization `
            -Profile $Profile `
            -Authorization $payload.OperationAuthorization `
            -ExpectedScope "provider_tls_repair" `
            -ExpectedProvider $payload.Provider
        if (-not [bool] $authorization.Accepted) {
            $rejectedStatus = New-TowerScoutHostHelperPublicOperationStatus `
                -State ([string] $authorization.State) `
                -Provider ([string] $authorization.Provider)
            return New-TowerScoutHostHelperHttpResult `
                -StatusCode 401 `
                -Reason "Unauthorized" `
                -Body $rejectedStatus
        }
    }

    $plan = New-TowerScoutProviderTlsRepairOperationPlan `
        -Profile $Profile `
        -Provider $payload.Provider `
        -Confirmation $payload.Confirmation
    if (-not [bool] $plan.Accepted) {
        $statusCode = if ($plan.State -eq "unsupported_runtime") { 409 } else { 400 }
        $reason = if ($statusCode -eq 409) { "Conflict" } else { "Bad Request" }
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode $statusCode `
            -Reason $reason `
            -Body $plan.PublicStatus
    }

    $lockResult = New-TowerScoutHostHelperOperationLock `
        -Profile $Profile `
        -Plan $plan `
        -OperationNonce $payload.OperationAuthorization
    if ($lockResult.State -eq "operation_busy") {
        $busyStatus = Add-TowerScoutHostHelperStatusAuthorization `
            -Profile $Profile `
            -PublicStatus $lockResult.PublicStatus
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode 409 `
            -Reason "Conflict" `
            -Body $busyStatus
    }
    if ($lockResult.State -eq "rejected_replayed_authorization") {
        $replayedStatus = Add-TowerScoutHostHelperStatusAuthorization `
            -Profile $Profile `
            -PublicStatus $lockResult.PublicStatus
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode 409 `
            -Reason "Conflict" `
            -Body $replayedStatus
    }

    if ([bool] $lockResult.Acquired -and $ExecutionEnabled) {
        if ($null -ne $CommandInvoker) {
            # Unit-only hook: production listener execution always uses the
            # fixed detached worker so status polling remains responsive.
            $executionStatus = Invoke-TowerScoutProviderTlsRepairControlledExecution `
                -Profile $Profile `
                -Plan $plan `
                -ExecutionEnabled:$true `
                -CommandInvoker $CommandInvoker
        }
        else {
            try {
                $executionStatus = Set-TowerScoutHostHelperOperationLockState `
                    -Profile $Profile `
                    -OperationId ([string] $plan.OperationId) `
                    -State "planned" `
                    -Step "worker_start" `
                    -ExecutionEnabled:$true
                if ($null -ne $WorkerStarter) {
                    & $WorkerStarter $Profile $plan | Out-Null
                }
                else {
                    Start-TowerScoutHostHelperOperationWorker `
                        -Profile $Profile `
                        -Plan $plan | Out-Null
                }
            }
            catch {
                $executionStatus = Set-TowerScoutHostHelperOperationLockState `
                    -Profile $Profile `
                    -OperationId ([string] $plan.OperationId) `
                    -State "runtime_start_failed" `
                    -Step "worker_start" `
                    -ExecutionEnabled:$true
            }
        }
        $executionStatus = Add-TowerScoutHostHelperStatusAuthorization `
            -Profile $Profile `
            -PublicStatus $executionStatus
        return New-TowerScoutHostHelperHttpResult `
            -StatusCode 202 `
            -Reason "Accepted" `
            -Body $executionStatus
    }

    $publicStatus = Add-TowerScoutHostHelperStatusAuthorization `
        -Profile $Profile `
        -PublicStatus $lockResult.PublicStatus
    return New-TowerScoutHostHelperHttpResult `
        -StatusCode 202 `
        -Reason "Accepted" `
        -Body $publicStatus
}

function Clear-TowerScoutHostHelperOperationLock {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile
    )

    $lockPath = Get-TowerScoutHostHelperOperationLockPath -Profile $Profile
    $cleared = 0
    if (Test-Path -LiteralPath $lockPath -PathType Leaf) {
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
        $cleared = 1
    }

    return [pscustomobject]@{
        cleared = $cleared
        state = "operation_lock_cleared"
    }
}

function Test-TowerScoutHostHelperOrigin {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [string] $Origin = ""
    )

    if ([string]::IsNullOrWhiteSpace($Origin)) {
        return $false
    }

    foreach ($allowedOrigin in @($Profile.AllowedOrigins)) {
        if ([string]::Equals($Origin, [string] $allowedOrigin, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }

    return $false
}

function Test-TowerScoutHostHelperAsciiBytes {
    param(
        [byte[]] $Bytes = @()
    )

    foreach ($value in $Bytes) {
        if ($value -gt 127) {
            return $false
        }
    }

    return $true
}

function Get-TowerScoutHostHelperAllowedMethodsForPath {
    param(
        [string] $Path = ""
    )

    if ($Path -in @("/health", "/runtime-profile")) {
        return "GET, OPTIONS"
    }
    if ($Path -eq "/operations/provider-tls-repair") {
        return "POST, OPTIONS"
    }
    if ($Path -match "^/operations/[a-f0-9]{32}$") {
        return "GET, OPTIONS"
    }

    return ""
}

function Test-TowerScoutHostHelperMethodAllowed {
    param(
        [string] $AllowedMethods = "",

        [string] $Method = ""
    )

    if ([string]::IsNullOrWhiteSpace($AllowedMethods) -or [string]::IsNullOrWhiteSpace($Method)) {
        return $false
    }

    $normalizedMethod = $Method.Trim().ToUpperInvariant()
    foreach ($allowedMethod in $AllowedMethods.Split([char[]] @(","), [System.StringSplitOptions]::RemoveEmptyEntries)) {
        if ([string]::Equals($allowedMethod.Trim().ToUpperInvariant(), $normalizedMethod, [System.StringComparison]::Ordinal)) {
            return $true
        }
    }

    return $false
}

function Read-TowerScoutHostHelperRequest {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Stream] $Stream,

        [datetime] $DeadlineUtc = (
            (Get-Date).ToUniversalTime().AddMilliseconds(
                $script:TowerScoutHostHelperReadTimeoutMs
            )
        )
    )

    $headerStream = New-Object System.IO.MemoryStream
    while ($true) {
        $remainingMilliseconds = [int] [Math]::Ceiling(
            ($DeadlineUtc - (Get-Date).ToUniversalTime()).TotalMilliseconds
        )
        if ($remainingMilliseconds -le 0) {
            throw "The helper request exceeded its total read deadline."
        }
        if ($Stream.CanTimeout) {
            $Stream.ReadTimeout = [Math]::Max(
                1,
                [Math]::Min(
                    $script:TowerScoutHostHelperReadTimeoutMs,
                    $remainingMilliseconds
                )
            )
        }
        $value = $Stream.ReadByte()
        if ($value -lt 0) {
            throw "The helper request headers ended early."
        }
        $headerStream.WriteByte([byte] $value)
        if ($headerStream.Length -gt $script:TowerScoutHostHelperMaxHeaderBytes) {
            throw "The helper request headers were too large."
        }

        if ($headerStream.Length -ge 4) {
            $headerBuffer = $headerStream.ToArray()
            $lastIndex = $headerBuffer.Length - 1
            if ($headerBuffer[$lastIndex - 3] -eq 13 -and $headerBuffer[$lastIndex - 2] -eq 10 -and $headerBuffer[$lastIndex - 1] -eq 13 -and $headerBuffer[$lastIndex] -eq 10) {
                break
            }
        }
    }

    $rawHeaderBytes = $headerStream.ToArray()
    $headerByteCount = $rawHeaderBytes.Length - 4
    if ($headerByteCount -le 0) {
        throw "The helper request was empty."
    }
    $headerBytes = New-Object byte[] $headerByteCount
    [System.Array]::Copy($rawHeaderBytes, 0, $headerBytes, 0, $headerByteCount)
    if (-not (Test-TowerScoutHostHelperAsciiBytes -Bytes $headerBytes)) {
        throw "The helper request headers must be ASCII."
    }

    $headerText = [System.Text.Encoding]::ASCII.GetString($headerBytes)
    $headerLines = @($headerText -split "`r`n")
    if ($headerLines.Count -lt 1 -or $headerLines.Count -gt ($script:TowerScoutHostHelperMaxHeaderLines + 1)) {
        throw "The helper request header count was invalid."
    }

    $requestLine = [string] $headerLines[0]
    if ([string]::IsNullOrWhiteSpace($requestLine)) {
        throw "The helper request was empty."
    }
    if ($requestLine.Length -gt $script:TowerScoutHostHelperMaxRequestLineLength) {
        throw "The helper request line was too large."
    }

    $parts = $requestLine.Split([char[]] @(" "), [System.StringSplitOptions]::RemoveEmptyEntries)
    if ($parts.Count -lt 3) {
        throw "The helper request line was invalid."
    }
    $method = ([string] $parts[0]).ToUpperInvariant()

    $headers = @{}
    foreach ($line in @($headerLines | Select-Object -Skip 1)) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        $separatorIndex = $line.IndexOf(":")
        if ($separatorIndex -le 0) {
            continue
        }

        $name = $line.Substring(0, $separatorIndex).Trim().ToLowerInvariant()
        $value = $line.Substring($separatorIndex + 1).Trim()
        $headers[$name] = $value
    }

    $bodyText = ""
    $contentLengthText = [string] $headers["content-length"]
    [int] $contentLength = 0
    if (-not [string]::IsNullOrWhiteSpace($contentLengthText)) {
        if (-not [int]::TryParse($contentLengthText, [ref] $contentLength) -or $contentLength -lt 0) {
            throw "The helper request content length was invalid."
        }
        if ($contentLength -gt $script:TowerScoutHostHelperMaxBodyBytes) {
            throw "The helper request body was too large."
        }
    }

    if ($method -eq "POST") {
        if ([string]::IsNullOrWhiteSpace($contentLengthText)) {
            throw "The helper POST request did not include a content length."
        }
        if ($contentLength -gt 0) {
            $buffer = New-Object byte[] $contentLength
            $totalRead = 0
            while ($totalRead -lt $contentLength) {
                $remainingMilliseconds = [int] [Math]::Ceiling(
                    ($DeadlineUtc - (Get-Date).ToUniversalTime()).TotalMilliseconds
                )
                if ($remainingMilliseconds -le 0) {
                    throw "The helper request exceeded its total read deadline."
                }
                if ($Stream.CanTimeout) {
                    $Stream.ReadTimeout = [Math]::Max(
                        1,
                        [Math]::Min(
                            $script:TowerScoutHostHelperReadTimeoutMs,
                            $remainingMilliseconds
                        )
                    )
                }
                $read = $Stream.Read($buffer, $totalRead, $contentLength - $totalRead)
                if ($read -le 0) {
                    throw "The helper request body ended early."
                }
                $totalRead += $read
            }
            if (-not (Test-TowerScoutHostHelperAsciiBytes -Bytes $buffer)) {
                throw "The helper request body must be ASCII."
            }
            $bodyText = [System.Text.Encoding]::ASCII.GetString($buffer)
        }
    }
    elseif ($contentLength -gt 0) {
        throw "The helper request method does not accept a body."
    }

    return [pscustomobject]@{
        Method = $method
        Path = [string] $parts[1]
        Headers = $headers
        BodyText = $bodyText
    }
}

function Write-TowerScoutHostHelperResponse {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Stream] $Stream,

        [Parameter(Mandatory = $true)]
        [int] $StatusCode,

        [Parameter(Mandatory = $true)]
        [string] $Reason,

        [object] $Body = @{},

        [string] $AccessControlAllowOrigin = "",

        [string] $AccessControlAllowMethods = "GET, OPTIONS"
    )

    $json = ($Body | ConvertTo-Json -Depth 8 -Compress)
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $lines = @(
        "HTTP/1.1 $StatusCode $Reason",
        "Content-Type: application/json; charset=utf-8",
        "Content-Length: $($bodyBytes.Length)",
        "Cache-Control: no-store",
        "Pragma: no-cache",
        "X-Content-Type-Options: nosniff",
        "Connection: close"
    )
    if (-not [string]::IsNullOrWhiteSpace($AccessControlAllowOrigin)) {
        $lines += @(
            "Access-Control-Allow-Origin: $AccessControlAllowOrigin",
            "Access-Control-Allow-Headers: X-TowerScout-Helper-Token, X-TowerScout-Operation-Authorization, Content-Type",
            "Access-Control-Allow-Methods: $AccessControlAllowMethods",
            "Vary: Origin"
        )
    }

    $headerText = ([string]::Join("`r`n", $lines)) + "`r`n`r`n"
    $headerBytes = [System.Text.Encoding]::ASCII.GetBytes($headerText)
    $Stream.Write($headerBytes, 0, $headerBytes.Length)
    $Stream.Write($bodyBytes, 0, $bodyBytes.Length)
    $Stream.Flush()
}

function Invoke-TowerScoutHostHelperRequest {
    param(
        [Parameter(Mandatory = $true)]
        [System.Net.Sockets.TcpClient] $Client,

        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $Token,

        [bool] $ExecutionEnabled = $script:TowerScoutHostHelperExecutionEnabledByDefault,

        [scriptblock] $WorkerStarter = $null
    )

    try {
        $Client.ReceiveTimeout = $script:TowerScoutHostHelperReadTimeoutMs
        $Client.SendTimeout = $script:TowerScoutHostHelperReadTimeoutMs
        $stream = $Client.GetStream()
        $remoteEndpoint = $Client.Client.RemoteEndPoint
        if ($null -eq $remoteEndpoint -or -not [System.Net.IPAddress]::IsLoopback($remoteEndpoint.Address)) {
            Write-TowerScoutHostHelperResponse `
                -Stream $stream `
                -StatusCode 403 `
                -Reason "Forbidden" `
                -Body @{ state = "rejected_non_loopback" }
            return
        }

        try {
            $request = Read-TowerScoutHostHelperRequest -Stream $stream
        }
        catch {
            Write-TowerScoutHostHelperResponse `
                -Stream $stream `
                -StatusCode 400 `
                -Reason "Bad Request" `
                -Body @{ state = "rejected_bad_request" }
            return
        }

        $path = ([string] $request.Path).Split([char[]] @("?"), 2)[0]
        $operationStatusPathPattern = "^/operations/([a-f0-9]{32})$"
        $allowedMethods = Get-TowerScoutHostHelperAllowedMethodsForPath -Path $path
        $origin = [string] $request.Headers["origin"]
        $originAllowed = Test-TowerScoutHostHelperOrigin -Profile $Profile -Origin $origin
        $corsOrigin = if ($originAllowed) { $origin } else { "" }

        if (-not $originAllowed) {
            Write-TowerScoutHostHelperResponse `
                -Stream $stream `
                -StatusCode 403 `
                -Reason "Forbidden" `
                -Body @{ state = "rejected_origin" }
            return
        }

        if (-not (Test-TowerScoutHostHelperSessionActive -Profile $Profile)) {
            Write-TowerScoutHostHelperResponse `
                -Stream $stream `
                -StatusCode 410 `
                -Reason "Gone" `
                -Body @{ state = "session_invalidated" } `
                -AccessControlAllowOrigin $corsOrigin `
                -AccessControlAllowMethods $allowedMethods
            return
        }

        if ($request.Method -eq "OPTIONS") {
            if ([string]::IsNullOrWhiteSpace($allowedMethods)) {
                Write-TowerScoutHostHelperResponse `
                    -Stream $stream `
                    -StatusCode 404 `
                    -Reason "Not Found" `
                    -Body @{ state = "rejected_unknown_endpoint" }
                return
            }

            $preflightMethod = [string] $request.Headers["access-control-request-method"]
            if (-not (Test-TowerScoutHostHelperMethodAllowed -AllowedMethods $allowedMethods -Method $preflightMethod)) {
                Write-TowerScoutHostHelperResponse `
                    -Stream $stream `
                    -StatusCode 405 `
                    -Reason "Method Not Allowed" `
                    -Body @{ state = "rejected_method" } `
                    -AccessControlAllowOrigin $corsOrigin `
                    -AccessControlAllowMethods $allowedMethods
                return
            }

            Write-TowerScoutHostHelperResponse `
                -Stream $stream `
                -StatusCode 200 `
                -Reason "OK" `
                -Body @{ state = "cors_preflight_ok" } `
                -AccessControlAllowOrigin $corsOrigin `
                -AccessControlAllowMethods $allowedMethods
            return
        }

        $providedToken = [string] $request.Headers["x-towerscout-helper-token"]
        $durableTokenAuthorized = (
            -not [string]::IsNullOrWhiteSpace($providedToken) -and
            (Test-TowerScoutHostHelperFixedTimeStringEquals `
                -Expected $Token `
                -Actual $providedToken)
        )
        $browserAuthorizationHeader = [string] $request.Headers["x-towerscout-operation-authorization"]
        if (-not [string]::IsNullOrWhiteSpace($providedToken) -and -not $durableTokenAuthorized) {
            Write-TowerScoutHostHelperResponse `
                -Stream $stream `
                -StatusCode 401 `
                -Reason "Unauthorized" `
                -Body @{ state = "rejected_token" } `
                -AccessControlAllowOrigin $corsOrigin `
                -AccessControlAllowMethods $allowedMethods
            return
        }

        if ($request.Method -eq "POST") {
            if ($path -ne "/operations/provider-tls-repair") {
                $statusCode = if ([string]::IsNullOrWhiteSpace($allowedMethods)) { 404 } else { 405 }
                $reason = if ($statusCode -eq 404) { "Not Found" } else { "Method Not Allowed" }
                $state = if ($statusCode -eq 404) { "rejected_unknown_endpoint" } else { "rejected_method" }
                Write-TowerScoutHostHelperResponse `
                    -Stream $stream `
                    -StatusCode $statusCode `
                    -Reason $reason `
                    -Body @{ state = $state } `
                    -AccessControlAllowOrigin $corsOrigin `
                    -AccessControlAllowMethods $allowedMethods
                return
            }

            $operationResult = New-TowerScoutProviderTlsRepairOperationPlanResponse `
                -Profile $Profile `
                -Request $request `
                -ExecutionEnabled:$ExecutionEnabled `
                -RequireSignedAuthorization:(-not $durableTokenAuthorized) `
                -WorkerStarter $WorkerStarter
            Write-TowerScoutHostHelperResponse `
                -Stream $stream `
                -StatusCode $operationResult.StatusCode `
                -Reason $operationResult.Reason `
                -Body $operationResult.Body `
                -AccessControlAllowOrigin $corsOrigin `
                -AccessControlAllowMethods $allowedMethods
            return
        }

        if ($request.Method -ne "GET") {
            Write-TowerScoutHostHelperResponse `
                -Stream $stream `
                -StatusCode 405 `
                -Reason "Method Not Allowed" `
                -Body @{ state = "rejected_method" } `
                -AccessControlAllowOrigin $corsOrigin `
                -AccessControlAllowMethods $allowedMethods
            return
        }

        switch ($path) {
            "/health" {
                if (-not $durableTokenAuthorized) {
                    $probeAuthorization = Resolve-TowerScoutHostHelperBrowserAuthorization `
                        -Profile $Profile `
                        -Authorization $browserAuthorizationHeader `
                        -ExpectedScope "helper_probe"
                    if (-not [bool] $probeAuthorization.Accepted) {
                        Write-TowerScoutHostHelperResponse `
                            -Stream $stream `
                            -StatusCode 401 `
                            -Reason "Unauthorized" `
                            -Body @{ state = [string] $probeAuthorization.State } `
                            -AccessControlAllowOrigin $corsOrigin `
                            -AccessControlAllowMethods $allowedMethods
                        return
                    }
                }
                Write-TowerScoutHostHelperResponse `
                    -Stream $stream `
                    -StatusCode 200 `
                    -Reason "OK" `
                    -Body (ConvertTo-TowerScoutHostHelperPublicRuntimeProfile -Profile $Profile) `
                    -AccessControlAllowOrigin $corsOrigin `
                    -AccessControlAllowMethods $allowedMethods
                return
            }
            "/runtime-profile" {
                if (-not $durableTokenAuthorized) {
                    Write-TowerScoutHostHelperResponse `
                        -Stream $stream `
                        -StatusCode 401 `
                        -Reason "Unauthorized" `
                        -Body @{ state = "rejected_token" } `
                        -AccessControlAllowOrigin $corsOrigin `
                        -AccessControlAllowMethods $allowedMethods
                    return
                }
                Write-TowerScoutHostHelperResponse `
                    -Stream $stream `
                    -StatusCode 200 `
                    -Reason "OK" `
                    -Body (ConvertTo-TowerScoutHostHelperPublicRuntimeProfile -Profile $Profile) `
                    -AccessControlAllowOrigin $corsOrigin `
                    -AccessControlAllowMethods $allowedMethods
                return
            }
            default {
                if ($path -match $operationStatusPathPattern) {
                    $operationId = [string] $Matches[1]
                    $statusAuthorization = $null
                    if (-not $durableTokenAuthorized) {
                        $statusAuthorization = Resolve-TowerScoutHostHelperBrowserAuthorization `
                            -Profile $Profile `
                            -Authorization $browserAuthorizationHeader `
                            -ExpectedScope "operation_status" `
                            -ExpectedOperationId $operationId
                        if (-not [bool] $statusAuthorization.Accepted) {
                            Write-TowerScoutHostHelperResponse `
                                -Stream $stream `
                                -StatusCode 401 `
                                -Reason "Unauthorized" `
                                -Body @{ state = [string] $statusAuthorization.State } `
                                -AccessControlAllowOrigin $corsOrigin `
                                -AccessControlAllowMethods $allowedMethods
                            return
                        }
                    }
                    $operationResult = Get-TowerScoutHostHelperOperationStatus `
                        -Profile $Profile `
                        -OperationId $operationId
                    $operationProvider = Get-TowerScoutHostHelperObjectValue `
                        -InputObject $operationResult.Body `
                        -Name "provider"
                    if (
                        -not $durableTokenAuthorized -and
                        $null -ne $operationResult.Body -and
                        -not [string]::IsNullOrWhiteSpace($operationProvider) -and
                        -not [string]::Equals(
                            $operationProvider,
                            ([string] $statusAuthorization.Provider),
                            [System.StringComparison]::Ordinal
                        )
                    ) {
                        Write-TowerScoutHostHelperResponse `
                            -Stream $stream `
                            -StatusCode 401 `
                            -Reason "Unauthorized" `
                            -Body @{ state = "rejected_operation_authorization" } `
                            -AccessControlAllowOrigin $corsOrigin `
                            -AccessControlAllowMethods $allowedMethods
                        return
                    }
                    Write-TowerScoutHostHelperResponse `
                        -Stream $stream `
                        -StatusCode $operationResult.StatusCode `
                        -Reason $operationResult.Reason `
                        -Body $operationResult.Body `
                        -AccessControlAllowOrigin $corsOrigin `
                        -AccessControlAllowMethods $allowedMethods
                    return
                }

                if (-not $durableTokenAuthorized) {
                    Write-TowerScoutHostHelperResponse `
                        -Stream $stream `
                        -StatusCode 401 `
                        -Reason "Unauthorized" `
                        -Body @{ state = "rejected_token" } `
                        -AccessControlAllowOrigin $corsOrigin `
                        -AccessControlAllowMethods $allowedMethods
                    return
                }
                Write-TowerScoutHostHelperResponse `
                    -Stream $stream `
                    -StatusCode 404 `
                    -Reason "Not Found" `
                    -Body @{ state = "rejected_unknown_endpoint" } `
                    -AccessControlAllowOrigin $corsOrigin `
                    -AccessControlAllowMethods $allowedMethods
            }
        }
    }
    finally {
        $Client.Close()
    }
}

function Start-TowerScoutHostHelper {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $Token,

        [int] $HelperPort = 0,

        [int] $MaxRequests = 0,

        [bool] $ExecutionEnabled = $script:TowerScoutHostHelperExecutionEnabledByDefault,

        [scriptblock] $WorkerStarter = $null,

        [int] $MutexWaitMilliseconds = $script:TowerScoutHostHelperPackageMutexWaitMilliseconds
    )

    if ($HelperPort -lt 0 -or $HelperPort -gt 65535) {
        throw "HelperPort must be 0 or between 1 and 65535."
    }
    if ($MaxRequests -lt 0) {
        throw "MaxRequests must be 0 or greater."
    }
    if ($MutexWaitMilliseconds -lt 1) {
        throw "MutexWaitMilliseconds must be at least 1."
    }

    $address = [System.Net.IPAddress]::Parse("127.0.0.1")
    $listener = New-Object System.Net.Sockets.TcpListener($address, $HelperPort)
    $handled = 0
    $packageMutex = $null
    try {
        $packageMutex = Enter-TowerScoutHostHelperPackageMutex `
            -PackageRoot ([string] $Profile.PackageRoot) `
            -WaitMilliseconds $MutexWaitMilliseconds
        $listener.Start()
        $boundPort = ([System.Net.IPEndPoint] $listener.LocalEndpoint).Port
        Set-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "HelperPort" -Value $boundPort
        if ([string]::IsNullOrWhiteSpace((Get-TowerScoutHostHelperObjectValue -InputObject $Profile -Name "SessionPath"))) {
            Save-TowerScoutHostHelperSession -Profile $Profile -Token $Token | Out-Null
        }
        else {
            Save-TowerScoutHostHelperSession -Profile $Profile | Out-Null
        }

        $nextHeartbeat = (Get-Date)
        while (
            ($MaxRequests -eq 0 -or $handled -lt $MaxRequests) -and
            (Test-TowerScoutHostHelperSessionActive `
                -Profile $Profile `
                -IgnoreHeartbeatStaleness)
        ) {
            if ((Get-Date) -ge $nextHeartbeat) {
                if (-not (Update-TowerScoutHostHelperSessionHeartbeat -Profile $Profile)) {
                    if (-not (Test-TowerScoutHostHelperSessionActive -Profile $Profile)) {
                        break
                    }
                }
                $nextHeartbeat = (Get-Date).AddSeconds(
                    $script:TowerScoutHostHelperHeartbeatIntervalSeconds
                )
            }
            if (-not $listener.Pending()) {
                Start-Sleep -Milliseconds 200
                continue
            }

            $client = $listener.AcceptTcpClient()
            Invoke-TowerScoutHostHelperRequest `
                -Client $client `
                -Profile $Profile `
                -Token $Token `
                -ExecutionEnabled:$ExecutionEnabled `
                -WorkerStarter $WorkerStarter
            $handled += 1
        }
    }
    finally {
        $listener.Stop()
        if ($null -ne $packageMutex) {
            try {
                $packageMutex.ReleaseMutex()
            }
            catch {}
            $packageMutex.Dispose()
        }
    }
}

function Invoke-TowerScoutHostHelperSelfTestRequest {
    param(
        [Parameter(Mandatory = $true)]
        [System.Net.Sockets.TcpListener] $Listener,

        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [string] $ServerToken,

        [string] $RequestToken = "",

        [string] $BrowserAuthorization = "",

        [string] $Origin = "http://localhost:5000",

        [string] $Path = "/health",

        [ValidateSet("GET", "POST", "OPTIONS")]
        [string] $Method = "GET",

        [string] $Body = "",

        [string] $ContentType = "application/json",

        [ValidateSet("GET", "POST")]
        [string] $PreflightMethod = "GET",

        [bool] $ExecutionEnabled = $script:TowerScoutHostHelperExecutionEnabledByDefault,

        [scriptblock] $WorkerStarter = $null
    )

    $port = ([System.Net.IPEndPoint] $Listener.LocalEndpoint).Port
    $accept = $Listener.BeginAcceptTcpClient($null, $null)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $client.Connect([System.Net.IPAddress]::Loopback, $port)
        $stream = $client.GetStream()
        $lines = @(
            "$Method $Path HTTP/1.1",
            "Host: 127.0.0.1",
            "Origin: $Origin",
            "Connection: close"
        )
        if (-not [string]::IsNullOrWhiteSpace($RequestToken)) {
            $lines += "X-TowerScout-Helper-Token: $RequestToken"
        }
        if (-not [string]::IsNullOrWhiteSpace($BrowserAuthorization)) {
            $lines += "X-TowerScout-Operation-Authorization: $BrowserAuthorization"
        }
        if ($Method -eq "OPTIONS") {
            $lines += "Access-Control-Request-Method: $PreflightMethod"
            $lines += "Access-Control-Request-Headers: X-TowerScout-Helper-Token, X-TowerScout-Operation-Authorization"
        }
        if ($Method -eq "POST") {
            $bodyBytes = [System.Text.Encoding]::ASCII.GetBytes($Body)
            if (-not [string]::IsNullOrWhiteSpace($ContentType)) {
                $lines += "Content-Type: $ContentType"
            }
            $lines += "Content-Length: $($bodyBytes.Length)"
        }

        $requestText = ([string]::Join("`r`n", $lines)) + "`r`n`r`n"
        $requestBytes = [System.Text.Encoding]::ASCII.GetBytes($requestText)
        $stream.Write($requestBytes, 0, $requestBytes.Length)
        if ($Method -eq "POST" -and $bodyBytes.Length -gt 0) {
            $stream.Write($bodyBytes, 0, $bodyBytes.Length)
        }
        $stream.Flush()

        $serverClient = $Listener.EndAcceptTcpClient($accept)
        Invoke-TowerScoutHostHelperRequest `
            -Client $serverClient `
            -Profile $Profile `
            -Token $ServerToken `
            -ExecutionEnabled:$ExecutionEnabled `
            -WorkerStarter $WorkerStarter

        $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::UTF8)
        $raw = $reader.ReadToEnd()
    }
    finally {
        $client.Close()
    }

    $statusCode = 0
    if ($raw -match "^HTTP/\d\.\d\s+(\d{3})") {
        $statusCode = [int] $Matches[1]
    }

    $headers = @{}
    $headerEnd = $raw.IndexOf("`r`n`r`n")
    if ($headerEnd -ge 0) {
        $headerText = $raw.Substring(0, $headerEnd)
        foreach ($line in @($headerText -split "`r`n" | Select-Object -Skip 1)) {
            $separatorIndex = ([string] $line).IndexOf(":")
            if ($separatorIndex -le 0) {
                continue
            }
            $name = ([string] $line).Substring(0, $separatorIndex).Trim().ToLowerInvariant()
            $value = ([string] $line).Substring($separatorIndex + 1).Trim()
            $headers[$name] = $value
        }
    }

    $responseBody = $null
    $bodyStart = $raw.IndexOf("`r`n`r`n")
    if ($bodyStart -ge 0) {
        $bodyText = $raw.Substring($bodyStart + 4)
        if (-not [string]::IsNullOrWhiteSpace($bodyText)) {
            try {
                $responseBody = $bodyText | ConvertFrom-Json
            }
            catch {
                $responseBody = $null
            }
        }
    }

    return [pscustomobject]@{
        StatusCode = $statusCode
        Headers = $headers
        Body = $responseBody
    }
}

function Invoke-TowerScoutHostHelperSelfTest {
    $token = New-TowerScoutHostHelperToken
    $profile = New-TowerScoutHostHelperRuntimeProfile `
        -Engine "docker" `
        -Gpu "off" `
        -AppPort 5000 `
        -PackageFlavor "self-test"
    $invalidatedProfile = New-TowerScoutHostHelperRuntimeProfile `
        -Engine "docker" `
        -Gpu "off" `
        -AppPort 5000 `
        -PackageFlavor "self-test"
    Set-TowerScoutHostHelperObjectValue `
        -InputObject $invalidatedProfile `
        -Name "SessionPath" `
        -Value (Join-Path (Get-TowerScoutHostHelperStateDirectory) "missing-session.json")

    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("towerscout-host-helper-selftest-{0}" -f (New-TowerScoutHostHelperSessionId))
    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
    $listener = $null
    try {
        $operationProfile = New-TowerScoutHostHelperRuntimeProfile `
            -Engine "docker" `
            -Gpu "off" `
            -AppPort 5000 `
            -PackageRoot $tempRoot `
            -PackageFlavor "self-test"
        $podmanProfile = New-TowerScoutHostHelperRuntimeProfile `
            -Engine "podman" `
            -Gpu "off" `
            -AppPort 5000 `
            -PackageRoot $tempRoot `
            -PackageFlavor "self-test"

        $acceptedPlan = New-TowerScoutProviderTlsRepairOperationPlan `
            -Profile $operationProfile `
            -Provider "google" `
            -Confirmation $script:TowerScoutHostHelperProviderTlsRepairConfirmation
        $podmanPlan = New-TowerScoutProviderTlsRepairOperationPlan `
            -Profile $podmanProfile `
            -Provider "google" `
            -Confirmation $script:TowerScoutHostHelperProviderTlsRepairConfirmation
        $badConfirmationPlan = New-TowerScoutProviderTlsRepairOperationPlan `
            -Profile $operationProfile `
            -Provider "google" `
            -Confirmation "restart_now"
        $badProviderPlan = New-TowerScoutProviderTlsRepairOperationPlan `
            -Profile $operationProfile `
            -Provider "google;process-start" `
            -Confirmation $script:TowerScoutHostHelperProviderTlsRepairConfirmation
        $realWrapperContract = Test-TowerScoutHostHelperRealWrapperContract `
            -Provider "google" `
            -Gpu "off" `
            -AppPort 5000

        $lockResult = New-TowerScoutHostHelperOperationLock `
            -Profile $operationProfile `
            -Plan $acceptedPlan `
            -OperationNonce (New-TowerScoutHostHelperToken)
        $duplicateLockResult = New-TowerScoutHostHelperOperationLock `
            -Profile $operationProfile `
            -Plan $acceptedPlan `
            -OperationNonce (New-TowerScoutHostHelperToken)

        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Parse("127.0.0.1"), 0)
        $listener.Start()
        $results = @(
            [pscustomobject]@{
                Scenario = "authorized_health"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $profile -ServerToken $token -RequestToken $token)
                Expected = 200
            },
            [pscustomobject]@{
                Scenario = "wrong_token"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $profile -ServerToken $token -RequestToken "wrong-token")
                Expected = 401
            },
            [pscustomobject]@{
                Scenario = "wrong_origin"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $profile -ServerToken $token -RequestToken $token -Origin "http://example.invalid")
                Expected = 403
            },
            [pscustomobject]@{
                Scenario = "unknown_endpoint"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $profile -ServerToken $token -RequestToken $token -Path "/unknown")
                Expected = 404
            },
            [pscustomobject]@{
                Scenario = "cors_preflight"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $profile -ServerToken $token -Method "OPTIONS")
                Expected = 200
            },
            [pscustomobject]@{
                Scenario = "cors_preflight_post_endpoint"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $profile -ServerToken $token -Path "/operations/provider-tls-repair" -Method "OPTIONS" -PreflightMethod "POST")
                Expected = 200
            },
            [pscustomobject]@{
                Scenario = "cors_preflight_status_endpoint"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $profile -ServerToken $token -Path "/operations/$($acceptedPlan.OperationId)" -Method "OPTIONS" -PreflightMethod "GET")
                Expected = 200
            },
            [pscustomobject]@{
                Scenario = "cors_preflight_wrong_method"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $profile -ServerToken $token -Path "/operations/provider-tls-repair" -Method "OPTIONS" -PreflightMethod "GET")
                Expected = 405
            },
            [pscustomobject]@{
                Scenario = "invalidated_session"
                Response = (Invoke-TowerScoutHostHelperSelfTestRequest -Listener $listener -Profile $invalidatedProfile -ServerToken $token -RequestToken $token)
                Expected = 410
            }
        )

        foreach ($result in $results) {
            if ($result.Response.StatusCode -ne $result.Expected) {
                throw "Host helper self-test scenario '$($result.Scenario)' returned $($result.Response.StatusCode); expected $($result.Expected)."
            }
        }
        $corsPreflight = @($results | Where-Object { $_.Scenario -eq "cors_preflight" } | Select-Object -First 1)
        if ($corsPreflight.Count -ne 1 -or [string] $corsPreflight[0].Response.Headers["access-control-allow-methods"] -ne "GET, OPTIONS") {
            throw "Host helper self-test did not return the expected health CORS method policy."
        }
        $expectedCorsMethods = @{
            cors_preflight = "GET, OPTIONS"
            cors_preflight_post_endpoint = "POST, OPTIONS"
            cors_preflight_status_endpoint = "GET, OPTIONS"
            cors_preflight_wrong_method = "POST, OPTIONS"
        }
        foreach ($entry in $expectedCorsMethods.GetEnumerator()) {
            $scenarioResult = @($results | Where-Object { $_.Scenario -eq $entry.Key } | Select-Object -First 1)
            if ($scenarioResult.Count -ne 1 -or [string] $scenarioResult[0].Response.Headers["access-control-allow-methods"] -ne [string] $entry.Value) {
                throw "Host helper self-test returned unexpected CORS methods for '$($entry.Key)'."
            }
        }

        if (-not $acceptedPlan.Accepted -or $acceptedPlan.State -ne "planned") {
            throw "Host helper operation plan did not accept the Docker provider TLS repair case."
        }
        if ([string] $acceptedPlan.InternalCommands.Repair.Script -ne "scripts\repair-provider-tls.cmd") {
            throw "Host helper operation plan did not select the allowlisted TLS repair wrapper."
        }
        $expectedRepairArguments = @("-Provider", "google", "-Engine", "docker", "-Gpu", "off", "-Apply")
        if ([string]::Join(" ", $acceptedPlan.InternalCommands.Repair.Arguments) -ne [string]::Join(" ", $expectedRepairArguments)) {
            throw "Host helper operation plan did not use the expected repair arguments."
        }
        if ([string]::Join(" ", $acceptedPlan.InternalCommands.Start.Arguments) -notmatch "-NoBrowser") {
            throw "Host helper operation plan did not preserve the no-browser restart guard."
        }
        if ($podmanPlan.State -ne "unsupported_runtime") {
            throw "Host helper operation plan accepted Podman in the Docker-only first slice."
        }
        if ($badConfirmationPlan.State -ne "rejected_confirmation") {
            throw "Host helper operation plan accepted a missing fixed confirmation value."
        }
        if ($badProviderPlan.State -ne "rejected_unknown_provider") {
            throw "Host helper operation plan accepted a non-allowlisted provider."
        }
        if ($badProviderPlan.PublicStatus.provider -ne "unknown") {
            throw "Host helper operation plan reflected caller-supplied invalid provider text."
        }
        if (-not $lockResult.Acquired -or $lockResult.State -ne "operation_locked") {
            throw "Host helper operation lock was not acquired for the first operation."
        }
        if ($duplicateLockResult.Acquired -or $duplicateLockResult.State -ne "operation_busy") {
            throw "Host helper operation lock did not reject a duplicate active operation."
        }

        $publicOperationJson = $acceptedPlan.PublicStatus | ConvertTo-Json -Depth 8 -Compress
        if ($publicOperationJson -match "repair-provider-tls|scripts\\\\|start\.bat|stop\.cmd|token|secret|thumbprint|certificate") {
            throw "Host helper public operation status exposed support-sensitive command or credential details."
        }
        $badProviderPublicJson = $badProviderPlan.PublicStatus | ConvertTo-Json -Depth 8 -Compress
        if ($badProviderPublicJson -match "google;|process-start") {
            throw "Host helper rejected-provider status exposed caller-supplied invalid provider text."
        }

        Clear-TowerScoutHostHelperOperationLock -Profile $operationProfile | Out-Null

        return [pscustomobject]@{
            result = "passed"
            helper_version = $script:TowerScoutHostHelperVersion
            listener = "loopback"
            scenarios = @($results | ForEach-Object {
                [pscustomobject]@{
                    name = $_.Scenario
                    status_code = $_.Response.StatusCode
                    state = if ($null -ne $_.Response.Body) { Get-TowerScoutHostHelperObjectValue -InputObject $_.Response.Body -Name "state" } else { "" }
                }
            })
            operation_scenarios = @(
                [pscustomobject]@{
                    name = "provider_tls_repair_docker_plan"
                    state = [string] $acceptedPlan.PublicStatus.state
                    provider = [string] $acceptedPlan.PublicStatus.provider
                    runtime = [string] $acceptedPlan.PublicStatus.runtime.engine
                },
                [pscustomobject]@{
                    name = "provider_tls_repair_podman_blocked"
                    state = [string] $podmanPlan.PublicStatus.state
                },
                [pscustomobject]@{
                    name = "provider_tls_repair_confirmation_required"
                    state = [string] $badConfirmationPlan.PublicStatus.state
                },
                [pscustomobject]@{
                    name = "provider_tls_repair_provider_allowlist"
                    state = [string] $badProviderPlan.PublicStatus.state
                    provider = [string] $badProviderPlan.PublicStatus.provider
                },
                [pscustomobject]@{
                    name = "provider_tls_repair_single_operation_lock"
                    state = [string] $duplicateLockResult.PublicStatus.state
                },
                [pscustomobject]@{
                    name = "provider_tls_repair_real_wrapper_contract"
                    state = [string] $realWrapperContract.state
                    executed = [bool] $realWrapperContract.executed
                }
            )
            redaction_check = "no tokens, operation authorizations, helper listener ports, local paths, provider keys, certificate details, raw subprocess output, or command paths returned"
        }
    }
    finally {
        if ($null -ne $listener) {
            $listener.Stop()
        }
        if (Test-Path -LiteralPath $tempRoot) {
            Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}
