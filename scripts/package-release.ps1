param(
    [string] $Version = "local",

    [string] $OutputDir = "dist",

    [string] $Image = "",

    [string] $ImageDigest = "",

    [switch] $NoZip,

    [switch] $Force
)

$ErrorActionPreference = "Stop"

if ($Version -notmatch "^[A-Za-z0-9][A-Za-z0-9._-]*$") {
    throw "Version must contain only letters, numbers, dots, underscores, and hyphens, and must start with a letter or number."
}

if ([string]::IsNullOrWhiteSpace($Image)) {
    $Image = $env:TOWERSCOUT_IMAGE
}
if ([string]::IsNullOrWhiteSpace($Image)) {
    $Image = "ghcr.io/j-schulein/towerscout:latest"
}
if ([string]::IsNullOrWhiteSpace($ImageDigest)) {
    $ImageDigest = $env:TOWERSCOUT_IMAGE_DIGEST
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$outputPath = Join-Path $repoRoot $OutputDir
if (-not (Test-Path -LiteralPath $outputPath -PathType Container)) {
    New-Item -ItemType Directory -Path $outputPath | Out-Null
}

$outputRoot = (Resolve-Path -LiteralPath $outputPath).Path
$packageName = "towerscout-$Version"
$stagePath = Join-Path $outputRoot $packageName
$zipPath = Join-Path $outputRoot "$packageName.zip"

function Test-ChildPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Parent,

        [Parameter(Mandatory = $true)]
        [string] $Child
    )

    $parentFull = [System.IO.Path]::GetFullPath($Parent).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $childFull = [System.IO.Path]::GetFullPath($Child)
    return $childFull.StartsWith($parentFull + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

if (Test-Path -LiteralPath $stagePath) {
    if (-not $Force) {
        throw "Package staging directory already exists: $stagePath. Use -Force or choose a different -Version/-OutputDir."
    }
    if (-not (Test-ChildPath -Parent $outputRoot -Child $stagePath)) {
        throw "Refusing to remove staging directory outside the output root: $stagePath"
    }
    Remove-Item -LiteralPath $stagePath -Recurse -Force
}

if ((Test-Path -LiteralPath $zipPath) -and -not $NoZip) {
    if (-not $Force) {
        throw "Package zip already exists: $zipPath. Use -Force or choose a different -Version/-OutputDir."
    }
    if (-not (Test-ChildPath -Parent $outputRoot -Child $zipPath)) {
        throw "Refusing to remove zip outside the output root: $zipPath"
    }
    Remove-Item -LiteralPath $zipPath -Force
}

New-Item -ItemType Directory -Path $stagePath | Out-Null

function Copy-ReleaseItem {
    param(
        [Parameter(Mandatory = $true)]
        [string] $RelativePath
    )

    $source = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Required release file not found: $RelativePath"
    }

    $destination = Join-Path $stagePath $RelativePath
    $destinationDir = Split-Path -Parent $destination
    if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationDir | Out-Null
    }
    Copy-Item -LiteralPath $source -Destination $destination
}

$releaseFiles = @(
    "start.bat",
    "compose.yaml",
    ".env.example",
    "docs\oci-quick-start.md",
    "docs\oci-runtime-contract.md",
    "webapp\asset_manifest.v1.json",
    "scripts\lib\TowerScoutCompose.ps1",
    "scripts\launch.ps1",
    "scripts\start.cmd",
    "scripts\start.ps1",
    "scripts\stop.cmd",
    "scripts\stop.ps1",
    "scripts\logs.cmd",
    "scripts\logs.ps1",
    "scripts\status.cmd",
    "scripts\status.ps1",
    "scripts\import-assets.cmd",
    "scripts\import-assets.ps1",
    "scripts\import-tls-ca.cmd",
    "scripts\import-tls-ca.ps1"
)

foreach ($file in $releaseFiles) {
    Copy-ReleaseItem -RelativePath $file
}

$assetDir = Join-Path $stagePath "assets"
New-Item -ItemType Directory -Path $assetDir | Out-Null
@"
TowerScout assets are distributed separately from the release control package.

Place the asset bundle here before running scripts\import-assets.cmd:

assets\model_params\
assets\data\

Then run:

scripts\import-assets.cmd -Source assets -VerifyHashes
"@ | Set-Content -LiteralPath (Join-Path $assetDir "README.txt") -Encoding ASCII

$effectiveImage = $Image
if (-not [string]::IsNullOrWhiteSpace($ImageDigest)) {
    if ($Image -notmatch "@sha256:") {
        $effectiveImage = "$Image@$ImageDigest"
    }
}

@"
TowerScout release image

Version: $Version
Image: $effectiveImage
Image digest: $ImageDigest
Generated UTC: $((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))

Release packages should pin TOWERSCOUT_IMAGE to an immutable digest reference.
If Image digest is blank, this package is suitable for local validation only.
"@ | Set-Content -LiteralPath (Join-Path $stagePath "IMAGE.txt") -Encoding ASCII

$envSource = Join-Path $stagePath ".env.example"
$envLines = Get-Content -LiteralPath $envSource
$envLines = $envLines | ForEach-Object {
    if ($_ -match "^TOWERSCOUT_IMAGE=") {
        "TOWERSCOUT_IMAGE=$effectiveImage"
    }
    elseif ($_ -match "^TOWERSCOUT_IMAGE_DIGEST=") {
        "TOWERSCOUT_IMAGE_DIGEST=$ImageDigest"
    }
    else {
        $_
    }
}
$envLines | Set-Content -LiteralPath $envSource -Encoding ASCII

$checksumPath = Join-Path $stagePath "SHA256SUMS.txt"
$stageFullPath = [System.IO.Path]::GetFullPath($stagePath).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
$filesToHash = Get-ChildItem -LiteralPath $stagePath -Recurse -File |
    Where-Object { $_.FullName -ne $checksumPath } |
    Sort-Object FullName

$checksumLines = foreach ($file in $filesToHash) {
    $relative = [System.IO.Path]::GetFullPath($file.FullName).Substring($stageFullPath.Length).Replace("\", "/")
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $relative"
}
$checksumLines | Set-Content -LiteralPath $checksumPath -Encoding ASCII

if (-not $NoZip) {
    Compress-Archive -Path (Join-Path $stagePath "*") -DestinationPath $zipPath
    $zipHash = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()
    "$zipHash  $packageName.zip" | Set-Content -LiteralPath (Join-Path $outputRoot "$packageName.zip.sha256") -Encoding ASCII
}

Write-Host "Package staged at: $stagePath"
if (-not $NoZip) {
    Write-Host "Package zip: $zipPath"
}
Write-Host "Image: $effectiveImage"
