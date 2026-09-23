Set-StrictMode -Version Latest

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

function Get-TowerScoutHostHelperStateDirectory {
    param(
        [string] $RootPath = $(Resolve-Path (Join-Path $PSScriptRoot "..\.."))
    )

    $resolvedRoot = (Resolve-Path -LiteralPath $RootPath).Path
    return (Join-Path $resolvedRoot ".towerscout-runtime\host-helper")
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

function Clear-TowerScoutHostHelperBridgeEnvironment {
    $env:TOWERSCOUT_HOST_HELPER_ENABLED = "0"
    Remove-Item Env:TOWERSCOUT_HOST_HELPER_PORT -ErrorAction SilentlyContinue
    Remove-Item Env:TOWERSCOUT_HOST_HELPER_SESSION_ID -ErrorAction SilentlyContinue
    Remove-Item Env:TOWERSCOUT_HOST_HELPER_SESSION_KEY -ErrorAction SilentlyContinue
}

function Get-TowerScoutHostHelperJsonDocument {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,

        [ValidateRange(1, 10)]
        [int] $MaximumAttempts = 4
    )

    for ($attempt = 1; $attempt -le $MaximumAttempts; $attempt++) {
        $json = Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
        if (-not [string]::IsNullOrWhiteSpace($json)) {
            $document = $null
            try {
                $document = $json | ConvertFrom-Json -ErrorAction Stop
            }
            catch {
                # Atomic replacement can expose a transient read/open race.
                # Malformed or incomplete JSON is retried below.
                $document = $null
            }
            if ($null -ne $document) {
                return $document
            }
        }
        if ($attempt -lt $MaximumAttempts) {
            Start-Sleep -Milliseconds 25
        }
    }
    return $null
}

function Install-TowerScoutHostHelperJsonDocument {
    param(
        [Parameter(Mandatory = $true)]
        [string] $TemporaryPath,

        [Parameter(Mandatory = $true)]
        [string] $DestinationPath,

        [Parameter(Mandatory = $true)]
        [string] $BackupPath,

        [ValidateRange(1, 10)]
        [int] $MaximumAttempts = 6
    )

    for ($attempt = 1; $attempt -le $MaximumAttempts; $attempt++) {
        try {
            if (Test-Path -LiteralPath $DestinationPath -PathType Leaf) {
                [System.IO.File]::Replace($TemporaryPath, $DestinationPath, $BackupPath)
            }
            else {
                [System.IO.File]::Move($TemporaryPath, $DestinationPath)
            }
            return
        }
        catch {
            if ($attempt -ge $MaximumAttempts) {
                throw
            }
            Start-Sleep -Milliseconds 25
        }
    }
}

function Complete-TowerScoutHostHelperExpiredOperation {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Profile,

        [Parameter(Mandatory = $true)]
        [object] $Record,

        [Parameter(Mandatory = $true)]
        [string] $OperationId
    )

    [bool] $terminal = $false
    [bool]::TryParse(
        (Get-TowerScoutHostHelperObjectValue -InputObject $Record -Name "terminal"),
        [ref] $terminal
    ) | Out-Null
    [datetime] $expiresAtUtc = [datetime]::MinValue
    if (
        $terminal -or
        -not [datetime]::TryParse(
            (Get-TowerScoutHostHelperObjectValue -InputObject $Record -Name "expires_at_utc"),
            [ref] $expiresAtUtc
        ) -or
        $expiresAtUtc.ToUniversalTime() -gt (Get-Date).ToUniversalTime()
    ) {
        return $null
    }

    $activeRecord = Get-TowerScoutHostHelperOperationLock -Profile $Profile
    if (
        $null -ne $activeRecord -and
        [string]::Equals(
            (Get-TowerScoutHostHelperObjectValue -InputObject $activeRecord -Name "operation_id"),
            $OperationId,
            [System.StringComparison]::Ordinal
        )
    ) {
        try {
            return Set-TowerScoutHostHelperOperationLockState `
                -Profile $Profile `
                -OperationId $OperationId `
                -State "operation_timeout" `
                -Step "operation_timeout" `
                -ExecutionEnabled:$false
        }
        catch {
            # A new operation may have replaced the stale active record.
        }
    }

    $policy = Get-TowerScoutHostHelperOperationStatePolicy -State "operation_timeout"
    Set-TowerScoutHostHelperObjectValue -InputObject $Record -Name "state" -Value "operation_timeout"
    Set-TowerScoutHostHelperObjectValue -InputObject $Record -Name "current_step" -Value "operation_timeout"
    Set-TowerScoutHostHelperObjectValue -InputObject $Record -Name "classification" -Value ([string] $policy.Classification)
    Set-TowerScoutHostHelperObjectValue -InputObject $Record -Name "terminal" -Value $true
    Set-TowerScoutHostHelperObjectValue -InputObject $Record -Name "next_action" -Value ([string] $policy.NextAction)
    Set-TowerScoutHostHelperObjectValue -InputObject $Record -Name "execution_enabled" -Value $false
    Set-TowerScoutHostHelperObjectValue -InputObject $Record -Name "completed_at_utc" -Value ((Get-Date).ToUniversalTime().ToString("o"))
    Set-TowerScoutHostHelperObjectValue -InputObject $Record -Name "updated_at_utc" -Value ((Get-Date).ToUniversalTime().ToString("o"))
    $statusPath = Get-TowerScoutHostHelperOperationStatusPath `
        -Profile $Profile `
        -OperationId $OperationId
    Write-TowerScoutHostHelperJsonAtomic -Path $statusPath -Value $Record
    return ConvertTo-TowerScoutHostHelperOperationStatusFromLock -Lock $Record
}
