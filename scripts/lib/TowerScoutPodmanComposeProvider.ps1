Set-StrictMode -Version Latest

function Get-TowerScoutProviderRepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Get-TowerScoutProviderCatalogPath {
    return (Join-Path (Get-TowerScoutProviderRepoRoot) "scripts\podman-compose-providers.v1.json")
}

function Get-TowerScoutPodmanComposeProviderCatalog {
    $catalogPath = Get-TowerScoutProviderCatalogPath
    if (-not (Test-Path -LiteralPath $catalogPath -PathType Leaf)) {
        throw "Podman Compose provider catalog was not found: $catalogPath"
    }

    return (Get-Content -LiteralPath $catalogPath -Raw | ConvertFrom-Json)
}

function Get-TowerScoutProviderObjectValue {
    param(
        [object] $InputObject,

        [string] $Name
    )

    if ($null -eq $InputObject) {
        return ""
    }
    if ($InputObject.PSObject.Properties.Name -notcontains $Name) {
        return ""
    }

    return [string] $InputObject.PSObject.Properties[$Name].Value
}

function Resolve-TowerScoutProviderCandidatePath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Value
    )

    if (Test-Path -LiteralPath $Value -PathType Leaf) {
        return (Resolve-Path -LiteralPath $Value).Path
    }

    $command = Get-Command $Value -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        return ""
    }

    if ($command.PSObject.Properties.Name -contains "Source" -and -not [string]::IsNullOrWhiteSpace([string] $command.Source)) {
        return [string] $command.Source
    }
    if ($command.PSObject.Properties.Name -contains "Path" -and -not [string]::IsNullOrWhiteSpace([string] $command.Path)) {
        return [string] $command.Path
    }

    return [string] $command.Name
}

function Test-TowerScoutProviderPathDisallowed {
    param(
        [string] $ProviderPath = "",

        [object] $Provider
    )

    if ([string]::IsNullOrWhiteSpace($ProviderPath)) {
        return $true
    }

    $normalized = ([string] $ProviderPath).Replace("/", "\")
    $normalized = $normalized -replace '\\{2,}', '\'
    foreach ($pattern in @($Provider.disallowed_path_patterns)) {
        if ($normalized -match ([string] $pattern)) {
            return $true
        }
    }

    return $false
}

function Invoke-TowerScoutProviderCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ProviderPath,

        [string[]] $Arguments = @()
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & $ProviderPath @Arguments 2>&1
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            Output = [string]::Join([Environment]::NewLine, @($output))
        }
    }
    catch {
        return [pscustomobject]@{
            ExitCode = 127
            Output = $_.Exception.Message
        }
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Test-TowerScoutApprovedPodmanComposeProvider {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ProviderPath,

        [Parameter(Mandatory = $true)]
        [object] $Provider
    )

    $resolvedPath = Resolve-TowerScoutProviderCandidatePath -Value $ProviderPath
    if ([string]::IsNullOrWhiteSpace($resolvedPath)) {
        return [pscustomobject]@{
            Accepted = $false
            Reason = "provider path was not found"
            Path = $ProviderPath
            Provider = $Provider
        }
    }

    $leafName = [System.IO.Path]::GetFileName($resolvedPath)
    $allowedNames = @($Provider.allowed_executable_names | ForEach-Object { ([string] $_).ToLowerInvariant() })
    if ($allowedNames -notcontains $leafName.ToLowerInvariant()) {
        return [pscustomobject]@{
            Accepted = $false
            Reason = "executable name '$leafName' is not allowlisted for $($Provider.id)"
            Path = $resolvedPath
            Provider = $Provider
        }
    }

    if (Test-TowerScoutProviderPathDisallowed -ProviderPath $resolvedPath -Provider $Provider) {
        return [pscustomobject]@{
            Accepted = $false
            Reason = "provider path is disallowed"
            Path = $resolvedPath
            Provider = $Provider
        }
    }

    $expectedSha256 = (Get-TowerScoutProviderObjectValue -InputObject $Provider -Name "windows_amd64_sha256").Trim().ToLowerInvariant()
    if (-not [string]::IsNullOrWhiteSpace($expectedSha256)) {
        $actualSha256 = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualSha256 -ne $expectedSha256) {
            return [pscustomobject]@{
                Accepted = $false
                Reason = "provider SHA-256 did not match the allowlist"
                Path = $resolvedPath
                Provider = $Provider
            }
        }
    }

    foreach ($requiredCommand in @($Provider.required_commands)) {
        $arguments = @($requiredCommand.arguments | ForEach-Object { [string] $_ })
        $result = Invoke-TowerScoutProviderCommand -ProviderPath $resolvedPath -Arguments $arguments
        if ($result.ExitCode -ne 0) {
            return [pscustomobject]@{
                Accepted = $false
                Reason = "required command '$($arguments -join ' ')' failed"
                Path = $resolvedPath
                Provider = $Provider
            }
        }

        $expectedPattern = [string] $requiredCommand.expected_output_pattern
        if (-not [string]::IsNullOrWhiteSpace($expectedPattern) -and $result.Output -notmatch $expectedPattern) {
            return [pscustomobject]@{
                Accepted = $false
                Reason = "required command output did not match $($Provider.display_name)"
                Path = $resolvedPath
                Provider = $Provider
            }
        }
    }

    return [pscustomobject]@{
        Accepted = $true
        Reason = "approved"
        Path = $resolvedPath
        Provider = $Provider
    }
}

function Test-TowerScoutAnyApprovedPodmanComposeProvider {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ProviderPath
    )

    $catalog = Get-TowerScoutPodmanComposeProviderCatalog
    $rejections = New-Object System.Collections.Generic.List[string]
    foreach ($provider in @($catalog.providers)) {
        $check = Test-TowerScoutApprovedPodmanComposeProvider -ProviderPath $ProviderPath -Provider $provider
        if ($check.Accepted) {
            return $check
        }
        [void] $rejections.Add("$($provider.id): $($check.Reason)")
    }

    return [pscustomobject]@{
        Accepted = $false
        Reason = ([string]::Join("; ", @($rejections)))
        Path = $ProviderPath
        Provider = $null
    }
}

function Find-TowerScoutApprovedPodmanComposeProviders {
    $catalog = Get-TowerScoutPodmanComposeProviderCatalog
    $results = New-Object System.Collections.Generic.List[object]
    $seen = @{}

    foreach ($provider in @($catalog.providers)) {
        foreach ($name in @($provider.allowed_executable_names)) {
            foreach ($command in @(Get-Command ([string] $name) -All -ErrorAction SilentlyContinue)) {
                $candidateValue = ""
                if ($command.PSObject.Properties.Name -contains "Source" -and -not [string]::IsNullOrWhiteSpace([string] $command.Source)) {
                    $candidateValue = [string] $command.Source
                }
                elseif ($command.PSObject.Properties.Name -contains "Path" -and -not [string]::IsNullOrWhiteSpace([string] $command.Path)) {
                    $candidateValue = [string] $command.Path
                }
                else {
                    $candidateValue = [string] $command.Name
                }

                $candidatePath = Resolve-TowerScoutProviderCandidatePath -Value $candidateValue
                if ([string]::IsNullOrWhiteSpace($candidatePath)) {
                    continue
                }
                $key = $candidatePath.ToLowerInvariant()
                if ($seen.ContainsKey($key)) {
                    continue
                }
                $seen[$key] = $true

                $check = Test-TowerScoutApprovedPodmanComposeProvider -ProviderPath $candidatePath -Provider $provider
                if ($check.Accepted) {
                    [void] $results.Add($check)
                }
            }
        }
    }

    foreach ($result in $results) {
        $result
    }
}

function Set-TowerScoutEnvSetting {
    param(
        [Parameter(Mandatory = $true)]
        [string] $EnvPath,

        [Parameter(Mandatory = $true)]
        [string] $Name,

        [Parameter(Mandatory = $true)]
        [string] $Value
    )

    $lines = @()
    if (Test-Path -LiteralPath $EnvPath -PathType Leaf) {
        $lines = @(Get-Content -LiteralPath $EnvPath)
    }

    $pattern = "^\s*" + [regex]::Escape($Name) + "\s*="
    $updated = $false
    $output = foreach ($line in $lines) {
        if (-not $updated -and ([string] $line) -match $pattern) {
            $updated = $true
            "$Name=$Value"
        }
        else {
            $line
        }
    }

    if (-not $updated) {
        $output += "$Name=$Value"
    }

    $output | Set-Content -LiteralPath $EnvPath -Encoding ASCII
}

function Set-TowerScoutPodmanComposeProviderEnv {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ProviderPath,

        [string] $RootPath = $(Get-TowerScoutProviderRepoRoot),

        [switch] $Apply
    )

    $resolvedPath = Resolve-TowerScoutProviderCandidatePath -Value $ProviderPath
    if ([string]::IsNullOrWhiteSpace($resolvedPath)) {
        throw "Provider path was not found: $ProviderPath"
    }

    $envPath = Join-Path $RootPath ".env"
    if (-not $Apply) {
        Write-Host "Set this value in .env after review:"
        Write-Host "PODMAN_COMPOSE_PROVIDER=$resolvedPath"
        return [pscustomobject]@{
            Applied = $false
            EnvPath = $envPath
            ProviderPath = $resolvedPath
        }
    }

    if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
        $templatePath = Join-Path $RootPath ".env.example"
        if (Test-Path -LiteralPath $templatePath -PathType Leaf) {
            Copy-Item -LiteralPath $templatePath -Destination $envPath
        }
        else {
            New-Item -ItemType File -Path $envPath | Out-Null
        }
    }

    $backupPath = "$envPath.backup.$((Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss'))"
    Copy-Item -LiteralPath $envPath -Destination $backupPath
    Set-TowerScoutEnvSetting -EnvPath $envPath -Name "PODMAN_COMPOSE_PROVIDER" -Value $resolvedPath
    Write-Host "Updated PODMAN_COMPOSE_PROVIDER in .env."
    Write-Host "Backup: $backupPath"

    return [pscustomobject]@{
        Applied = $true
        EnvPath = $envPath
        BackupPath = $backupPath
        ProviderPath = $resolvedPath
    }
}
