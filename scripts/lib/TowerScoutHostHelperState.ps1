Set-StrictMode -Version Latest

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
