param(
    [string] $Version = "local",

    [string] $OutputDir = "dist",

    [string] $Image = "",

    [string] $ImageDigest = "",

    [switch] $AllowMutableImage,

    [switch] $AllowMissingSourceRef,

    [switch] $AllowDirtySource,

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

$digestPattern = "sha256:[0-9a-f]{64}"
if ([string]::IsNullOrWhiteSpace($ImageDigest) -and $Image -match "@($digestPattern)$") {
    $ImageDigest = $Matches[1]
}

if ([string]::IsNullOrWhiteSpace($ImageDigest)) {
    if (-not $AllowMutableImage) {
        throw "Release packaging requires -ImageDigest with sha256:<64 lowercase hex>. Use -AllowMutableImage only for local validation packages."
    }
}
elseif ($ImageDigest -notmatch "^$digestPattern$") {
    throw "ImageDigest must match sha256:<64 lowercase hex>."
}

if (($Image -match "@($digestPattern)$") -and -not [string]::IsNullOrWhiteSpace($ImageDigest) -and $Matches[1] -ne $ImageDigest) {
    throw "Image already contains digest $($Matches[1]), which does not match -ImageDigest $ImageDigest."
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$sourceRef = ""
try {
    $gitOutput = & git -C $repoRoot rev-parse HEAD 2>$null
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($gitOutput)) {
        $sourceRef = ($gitOutput | Select-Object -First 1).Trim()
    }
}
catch {
    $sourceRef = ""
}

if ([string]::IsNullOrWhiteSpace($sourceRef)) {
    if (-not $AllowMissingSourceRef) {
        throw "Release packaging requires a git source ref. Use -AllowMissingSourceRef only for local validation packages."
    }
    Write-Warning "Creating a local-validation package without a source ref. Do not use this package as a release artifact."
}

$gitStatusChecked = $false
$dirtyEntries = @()
try {
    $gitStatusOutput = & git -C $repoRoot status --porcelain 2>$null
    if ($LASTEXITCODE -eq 0) {
        $gitStatusChecked = $true
        $dirtyEntries = @($gitStatusOutput | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    }
}
catch {
    $gitStatusChecked = $false
}

if (-not $gitStatusChecked) {
    if (-not $AllowDirtySource) {
        throw "Release packaging requires git working-tree status. Use -AllowDirtySource only for local validation packages."
    }
    Write-Warning "Creating a local-validation package without git dirty-tree verification."
}
elseif ($dirtyEntries.Count -gt 0) {
    if (-not $AllowDirtySource) {
        throw "Release packaging requires a clean git working tree. Commit or stash changes, or use -AllowDirtySource only for local validation packages."
    }
    Write-Warning "Creating a local-validation package from a dirty working tree. Do not use this package as a release artifact."
}

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
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "MODEL_LICENSES.md",
    "DATA_LICENSES.md",
    "PROVIDER_TERMS.md",
    "docs\oci-quick-start.md",
    "docs\oci-runtime-contract.md",
    "docs\release-asset-bundle-contract.md",
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
assets\asset_manifest.v1.json

Then run:

scripts\import-assets.cmd -Source assets

For release-candidate or support validation, use:

scripts\import-assets.cmd -Source assets -VerifyHashes

YOLO detector weights are treated as YOLO-derived/AGPL-governed for this
release track unless separate written model terms say otherwise. See
MODEL_LICENSES.md, DATA_LICENSES.md, and THIRD_PARTY_NOTICES.md.
"@ | Set-Content -LiteralPath (Join-Path $assetDir "README.txt") -Encoding ASCII

$effectiveImage = $Image
if (-not [string]::IsNullOrWhiteSpace($ImageDigest)) {
    if ($Image -notmatch "@sha256:") {
        $effectiveImage = "$Image@$ImageDigest"
    }
    else {
        $effectiveImage = $Image
    }
}
elseif ($AllowMutableImage) {
    Write-Warning "Creating a local-validation package with a mutable image reference. Do not use this package as a release artifact."
}

@"
TowerScout release image

Version: $Version
Image: $effectiveImage
Image digest: $ImageDigest
Generated UTC: $((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))

Release packages pin TOWERSCOUT_IMAGE to an immutable digest reference.
If Image digest is blank, this package was generated with -AllowMutableImage and is suitable for local validation only.
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

@"
TowerScout corresponding source notice

Version: $Version
Release track: agpl-yolo
Source ref: $sourceRef
Generated UTC: $((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))

The YOLO-enabled release package and image must have matching corresponding
source available for the exact release ref. The source must include:

- TowerScout source code.
- Vendored Ultralytics YOLOv5 source under webapp/vendor/yolov5_local/.
- TowerScout local YOLO patches and loader code.
- Dockerfile, Compose files, launcher scripts, packaging scripts, requirements,
  and asset import helpers.
- Build, package, asset import, and run instructions.

If the source ref is blank, this package was generated with
-AllowMissingSourceRef and is suitable for local validation only.
"@ | Set-Content -LiteralPath (Join-Path $stagePath "SOURCE.txt") -Encoding ASCII

@"
TowerScout SBOM reference

Version: $Version
Release track: agpl-yolo
Image: $effectiveImage
Generated UTC: $((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))

Attach or publish an SBOM for the exact release package and container image.
At minimum, the SBOM should cover Python packages from webapp/requirements.txt,
frontend packages from package-lock.json, OS packages in the image, and the
vendored YOLOv5 source snapshot.

This file is a release-package reference, not the generated SBOM itself.
"@ | Set-Content -LiteralPath (Join-Path $stagePath "SBOM.txt") -Encoding ASCII

$manifest = [ordered]@{
    schema_version = 1
    track = "agpl-yolo"
    release_version = $Version
    release_statement = "TowerScout-authored code may be Apache-2.0 where confirmed, but the YOLO-enabled package/image is distributed with AGPL-3.0 obligations."
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    image = $effectiveImage
    image_digest = $ImageDigest
    asset_manifest = "webapp/asset_manifest.v1.json"
    compliance_files = @(
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_NOTICES.md",
        "MODEL_LICENSES.md",
        "DATA_LICENSES.md",
        "PROVIDER_TERMS.md",
        "SOURCE.txt",
        "SBOM.txt",
        "IMAGE.txt",
        "SHA256SUMS.txt"
    )
    release_artifacts = [ordered]@{
        control_zip = if ($NoZip) { "" } else { "$packageName.zip" }
        control_zip_sha256 = ""
        image = $effectiveImage
        image_digest = $ImageDigest
        asset_manifest = "webapp/asset_manifest.v1.json"
        asset_bundle_sha256 = ""
    }
    corresponding_source = [ordered]@{
        source_ref = $sourceRef
        source_offer = "See SOURCE.txt."
        required_paths = @(
            "webapp/vendor/yolov5_local/",
            "webapp/ts_yolov5_local.py",
            "webapp/ts_yolov5.py",
            "Dockerfile",
            "compose.yaml",
            "scripts/",
            "webapp/requirements.txt",
            "package-lock.json"
        )
    }
    runtime_components = [ordered]@{
        yolo = [ordered]@{
            name = "Ultralytics YOLOv5"
            license = "AGPL-3.0"
            vendored_path = "webapp/vendor/yolov5_local"
            validated_upstream_commit = "1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c"
        }
    }
    sbom = [ordered]@{
        reference = "SBOM.txt"
        status = "Release SBOM must be generated or attached for each release candidate."
    }
    revocation = [ordered]@{
        notes = "Revoke and replace the release if the ZIP, image digest, model/data assets, source ref, SBOM, or notices are defective."
    }
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $stagePath "release-manifest.v1.json") -Encoding ASCII

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
