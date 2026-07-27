"""Task-074 bootstrap/preflight coverage."""

import hashlib
import json
import os
import shutil
import subprocess
import uuid
import zipfile
import hashlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_SCRIPT = REPO_ROOT / "scripts" / "bootstrap.ps1"
SETUP_SCRIPT = REPO_ROOT / "scripts" / "setup-towerscout.ps1"
BOOTSTRAP_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutBootstrap.ps1"
COMPOSE_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutCompose.ps1"
PACKAGE_SCRIPT = REPO_ROOT / "scripts" / "package-release.ps1"
LAUNCH_SCRIPT = REPO_ROOT / "scripts" / "launch.ps1"
IMPORT_ASSETS_SCRIPT = REPO_ROOT / "scripts" / "import-assets.ps1"


def _powershell_executable():
    return shutil.which("powershell.exe") or shutil.which("pwsh")


def _run_powershell(command: str):
    powershell = _powershell_executable()
    if powershell is None:
        pytest.skip("PowerShell executable not found")

    return subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_bootstrap_entrypoint_is_packaged_and_reuses_validated_scripts():
    bootstrap_cmd = (REPO_ROOT / "bootstrap.cmd").read_text(encoding="utf-8")
    setup_cmd = (REPO_ROOT / "setup-towerscout.cmd").read_text(encoding="utf-8")
    setup = SETUP_SCRIPT.read_text(encoding="utf-8")
    bootstrap = BOOTSTRAP_SCRIPT.read_text(encoding="utf-8")
    launch = LAUNCH_SCRIPT.read_text(encoding="utf-8")
    import_assets = IMPORT_ASSETS_SCRIPT.read_text(encoding="utf-8")
    package_script = PACKAGE_SCRIPT.read_text(encoding="utf-8")

    assert "scripts\\bootstrap.ps1" in bootstrap_cmd
    assert "scripts\\setup-towerscout.ps1" in setup_cmd
    assert 'ValidateSet("docker", "podman")' in setup
    assert '[string] $Engine = "docker"' in setup
    assert '[string] $Gpu = "off"' in setup
    assert "Find-TowerScoutSetupAssetZip" in setup
    assert "Find-TowerScoutSetupPackageZip" in setup
    assert "bootstrap.ps1" in setup
    assert "$bootstrapParams" in setup
    assert "@bootstrapParams" in setup
    assert "@bootstrapArgs" not in setup
    assert 'ValidateSet("auto", "docker", "podman")' in bootstrap
    assert 'ValidateSet("off", "auto", "on")' in bootstrap
    assert "[switch] $VerifyOnly" in bootstrap
    assert "import-assets.ps1" in bootstrap
    assert "-VerifyHashes" in bootstrap
    assert "SessionMaxHours = $SessionMaxHours" in setup
    assert "-SessionMaxHours $SessionMaxHours" in bootstrap
    assert "Invoke-TowerScoutStaleContainerGuard" in launch
    assert "Invoke-TowerScoutStaleContainerGuard" in import_assets
    assert "Write-TowerScoutImagePullReadiness" in bootstrap
    assert "launch.ps1" in bootstrap
    assert "-NoBrowser:$NoBrowser" in bootstrap
    assert "@launchArgs" not in bootstrap
    assert '"setup-towerscout.cmd"' in package_script
    assert '"bootstrap.cmd"' in package_script
    assert '"scripts\\setup-towerscout.ps1"' in package_script
    assert '"scripts\\bootstrap.ps1"' in package_script
    assert '"scripts\\lib\\TowerScoutBootstrap.ps1"' in package_script


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_setup_zip_discovery_finds_uat_downloads_and_requires_sidecars():
    uat_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task080-setup-{uuid.uuid4().hex}"
    app_root = uat_root / "towerscout-v0.1.0-rc1"
    app_root.mkdir(parents=True)
    (app_root / "release-manifest.v1.json").write_text(
        json.dumps({"release_version": "v0.1.0-rc1"}),
        encoding="utf-8",
    )
    asset_zip = uat_root / "towerscout-v0.1.0-rc1-assets-windows.zip"
    package_zip = uat_root / "towerscout-v0.1.0-rc1.zip"
    asset_sidecar = asset_zip.with_suffix(".zip.sha256")
    package_sidecar = package_zip.with_suffix(".zip.sha256")
    asset_zip.write_bytes(b"asset package")
    package_zip.write_bytes(b"application package")
    asset_sidecar.write_text("hash  towerscout-v0.1.0-rc1-assets-windows.zip\n", encoding="utf-8")
    package_sidecar.write_text("hash  towerscout-v0.1.0-rc1.zip\n", encoding="utf-8")

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        $asset = Find-TowerScoutSetupAssetZip -RootPath "{app_root}"
        if ($asset -ne "{asset_zip}") {{
            throw "Wrong asset ZIP discovered: $asset"
        }}
        $package = Find-TowerScoutSetupPackageZip -RootPath "{app_root}"
        if ($package -ne "{package_zip}") {{
            throw "Wrong package ZIP discovered: $package"
        }}
        $explicitAsset = Find-TowerScoutSetupAssetZip -RootPath "{app_root}" -AssetZip "{asset_zip}"
        if ($explicitAsset -ne "{asset_zip}") {{
            throw "Wrong explicit asset ZIP resolved: $explicitAsset"
        }}
        $explicitPackage = Find-TowerScoutSetupPackageZip -RootPath "{app_root}" -PackageZip "{package_zip}"
        if ($explicitPackage -ne "{package_zip}") {{
            throw "Wrong explicit package ZIP resolved: $explicitPackage"
        }}
        Remove-Item -LiteralPath "{asset_sidecar}"
        try {{
            Find-TowerScoutSetupAssetZip -RootPath "{app_root}" | Out-Null
            throw "Missing asset sidecar was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "checksum sidecar") {{
                throw
            }}
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(uat_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_setup_zip_discovery_uses_manifest_asset_bundle_for_variant_package():
    uat_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-setup-{uuid.uuid4().hex}"
    app_root = uat_root / "towerscout-v0.1.0-ga-cpu"
    app_root.mkdir(parents=True)
    shared_asset_zip = uat_root / "towerscout-v0.1.0-ga-assets-task084-test-assets.zip"
    flavor_asset_zip = uat_root / "towerscout-v0.1.0-ga-cpu-assets-task084-test-assets.zip"
    package_zip = uat_root / "towerscout-v0.1.0-ga-cpu.zip"
    (app_root / "release-manifest.v1.json").write_text(
        json.dumps(
            {
                "release_version": "v0.1.0-ga-cpu",
                "release_artifacts": {
                    "asset_bundle": shared_asset_zip.name,
                },
            }
        ),
        encoding="utf-8",
    )
    shared_asset_zip.write_bytes(b"shared asset package")
    flavor_asset_zip.write_bytes(b"wrong flavor-specific asset package")
    package_zip.write_bytes(b"application package")
    shared_asset_zip.with_suffix(".zip.sha256").write_text(
        f"hash  {shared_asset_zip.name}\n",
        encoding="utf-8",
    )
    flavor_asset_zip.with_suffix(".zip.sha256").write_text(
        f"hash  {flavor_asset_zip.name}\n",
        encoding="utf-8",
    )
    package_zip.with_suffix(".zip.sha256").write_text(
        f"hash  {package_zip.name}\n",
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        $asset = Find-TowerScoutSetupAssetZip -RootPath "{app_root}"
        if ($asset -ne "{shared_asset_zip}") {{
            throw "Wrong asset ZIP discovered: $asset"
        }}
        $package = Find-TowerScoutSetupPackageZip -RootPath "{app_root}"
        if ($package -ne "{package_zip}") {{
            throw "Wrong package ZIP discovered: $package"
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(uat_root, ignore_errors=True)


def test_bootstrap_verify_only_does_not_stage_asset_zip_before_exit():
    bootstrap = BOOTSTRAP_SCRIPT.read_text(encoding="utf-8")
    helper = BOOTSTRAP_LIB.read_text(encoding="utf-8")

    assert "Test-TowerScoutAssetZipReleaseMatch" in helper
    assert "Test-TowerScoutAssetZipReleaseMatch -RootPath $repoRoot -ZipPath $resolvedAssetZip" in bootstrap
    assert bootstrap.index("Resolve-TowerScoutBootstrapEngine") < bootstrap.index("if ($VerifyOnly)")
    assert bootstrap.index("if ($VerifyOnly)") < bootstrap.index("Expand-TowerScoutAssetZip")


def test_bootstrap_reuses_valid_staged_assets_before_extracting_asset_zip():
    bootstrap = BOOTSTRAP_SCRIPT.read_text(encoding="utf-8")

    assert "$hasExistingStagedAssets = Test-TowerScoutStagedAssets" in bootstrap
    assert "if ($hasExistingStagedAssets)" in bootstrap
    assert "Reusing the staged assets and continuing with engine import." in bootstrap
    assert bootstrap.index("$hasExistingStagedAssets = Test-TowerScoutStagedAssets") < bootstrap.index("if ($VerifyOnly)")
    assert bootstrap.index("if ($hasExistingStagedAssets)") < bootstrap.index("Expand-TowerScoutAssetZip")


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_compose_helper_initializes_env_from_package_template_without_overwrite():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task074-env-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    env_example = temp_root / ".env.example"
    env_path = temp_root / ".env"
    env_example.write_text(
        "TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda126\n",
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"
        Initialize-TowerScoutEnvFile -RootPath "{temp_root}"
        if (-not (Test-Path -LiteralPath "{env_path}" -PathType Leaf)) {{
            throw "Expected .env to be created from .env.example."
        }}
        Set-Content -LiteralPath "{env_path}" -Value "TOWERSCOUT_IMAGE=custom" -Encoding ASCII
        Initialize-TowerScoutEnvFile -RootPath "{temp_root}"
        $envText = Get-Content -LiteralPath "{env_path}" -Raw
        if ($envText -notmatch "TOWERSCOUT_IMAGE=custom") {{
            throw "Existing .env was overwritten."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_release_package_env_sync_overrides_stale_process_values():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task074-env-sync-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    digest = "sha256:" + ("3" * 64)
    expected_image = f"ghcr.io/j-schulein/towerscout:v0.1.0-ga-cpu@{digest}"
    (temp_root / "release-manifest.v1.json").write_text(
        json.dumps(
            {
                "release_version": "v0.1.0-ga-cpu",
                "pytorch_flavor": "cpu",
            }
        ),
        encoding="utf-8",
    )
    (temp_root / ".env.example").write_text(
        "\n".join(
            [
                f"TOWERSCOUT_IMAGE={expected_image}",
                f"TOWERSCOUT_IMAGE_DIGEST={digest}",
                "REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt",
                "SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt",
                "TOWERSCOUT_CONTAINER_ENGINE=",
            ]
        ),
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"

        $env:TOWERSCOUT_IMAGE = "towerscout:local"
        $env:TOWERSCOUT_IMAGE_DIGEST = "sha256:{'9' * 64}"
        $env:REQUESTS_CA_BUNDLE = "C:/bad/certs.pem"
        $env:SSL_CERT_FILE = "C:/bad/certs.pem"
        $env:TOWERSCOUT_CONTAINER_ENGINE = "docker"

        Initialize-TowerScoutEnvFile -RootPath "{temp_root}"

        if ($env:TOWERSCOUT_IMAGE -ne "{expected_image}") {{
            throw "Expected TOWERSCOUT_IMAGE to sync from package .env."
        }}
        if ($env:TOWERSCOUT_IMAGE_DIGEST -ne "{digest}") {{
            throw "Expected TOWERSCOUT_IMAGE_DIGEST to sync from package .env."
        }}
        if ($env:REQUESTS_CA_BUNDLE -ne "/etc/ssl/certs/ca-certificates.crt") {{
            throw "Expected REQUESTS_CA_BUNDLE to sync from package .env."
        }}
        if ($env:SSL_CERT_FILE -ne "/etc/ssl/certs/ca-certificates.crt") {{
            throw "Expected SSL_CERT_FILE to sync from package .env."
        }}
        if (-not [string]::IsNullOrEmpty($env:TOWERSCOUT_CONTAINER_ENGINE)) {{
            throw "Expected blank package TOWERSCOUT_CONTAINER_ENGINE to clear the stale process value."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_package_env_image_mismatch_fails_closed_without_overwrite():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-env-mismatch-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    digest = "sha256:" + ("8" * 64)
    expected_image = f"ghcr.io/j-schulein/towerscout:v0.1.0-ga-cpu@{digest}"
    (temp_root / "release-manifest.v1.json").write_text(
        json.dumps(
            {
                "release_version": "v0.1.0-ga-cpu",
                "pytorch_flavor": "cpu",
            }
        ),
        encoding="utf-8",
    )
    (temp_root / ".env.example").write_text(
        "\n".join(
            [
                f"TOWERSCOUT_IMAGE={expected_image}",
                f"TOWERSCOUT_IMAGE_DIGEST={digest}",
                "PODMAN_COMPOSE_PROVIDER=",
            ]
        ),
        encoding="utf-8",
    )
    (temp_root / ".env").write_text(
        "\n".join(
            [
                "TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout:old-cuda126",
                "TOWERSCOUT_IMAGE_DIGEST=sha256:9999999999999999999999999999999999999999999999999999999999999999",
                "PODMAN_COMPOSE_PROVIDER=C:\\Tools\\podman-compose.exe",
            ]
        ),
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"

        try {{
            Initialize-TowerScoutEnvFile -RootPath "{temp_root}"
            throw "Package image mismatch was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "Package image mismatch") {{
                throw
            }}
            if ($_.Exception.Message -notmatch "TOWERSCOUT_IMAGE_DIGEST") {{
                throw "Mismatch message did not include digest detail."
            }}
        }}

        $envText = Get-Content -LiteralPath "{temp_root / '.env'}" -Raw
        if ($envText -notmatch "old-cuda126" -or $envText -notmatch "PODMAN_COMPOSE_PROVIDER") {{
            throw "Existing .env was overwritten instead of failing closed."
        }}

        Set-Content -LiteralPath "{temp_root / '.env'}" -Encoding ASCII -Value @(
            "TOWERSCOUT_IMAGE={expected_image}",
            "TOWERSCOUT_IMAGE_DIGEST={digest}",
            "PODMAN_COMPOSE_PROVIDER=C:\\Tools\\podman-compose.exe"
        )
        Initialize-TowerScoutEnvFile -RootPath "{temp_root}"
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_helpers_verify_checksum_and_readiness_guidance():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task074-checksum-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    artifact = temp_root / "artifact.zip"
    artifact.write_bytes(b"tower scout artifact")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    artifact.with_suffix(".zip.sha256").write_text(
        f"{digest}  artifact.zip\n",
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        $hash = Test-TowerScoutChecksumSidecar -ArtifactPath "{artifact}"
        if ($hash -ne "{digest}") {{
            throw "Checksum helper returned wrong hash."
        }}
        function Test-TowerScoutBootstrapCommand {{
            param([string] $Name)
            return $false
        }}
        $fallbackHash = Get-TowerScoutSha256FileHash -Path "{artifact}"
        if ($fallbackHash -ne "{digest}") {{
            throw "Fallback checksum helper returned wrong hash."
        }}
        $fatal = Get-TowerScoutReadinessGuidance -State fatal
        if ($fatal -notmatch "support evidence") {{
            throw "Fatal readiness guidance did not include support evidence."
        }}
        $setup = Get-TowerScoutReadinessGuidance -State setup_required
        if ($setup -notmatch "provider setup") {{
            throw "Setup guidance did not explain provider setup."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_asset_zip_layout_accepts_expected_roots_and_rejects_nested_assets():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task074-zip-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    good_zip = temp_root / "good-assets.zip"
    nested_zip = temp_root / "nested-assets.zip"

    with zipfile.ZipFile(good_zip, "w") as package:
        package.writestr("model_params/yolov5/newest.pt", b"weights")
        package.writestr("data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp", b"shape")
        package.writestr("asset_manifest.v1.json", "{}")

    with zipfile.ZipFile(nested_zip, "w") as package:
        package.writestr("assets/model_params/yolov5/newest.pt", b"weights")
        package.writestr("assets/data/file.txt", b"data")
        package.writestr("assets/asset_manifest.v1.json", "{}")

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        Test-TowerScoutAssetZipLayout -ZipPath "{good_zip}" | Out-Null
        try {{
            Test-TowerScoutAssetZipLayout -ZipPath "{nested_zip}" | Out-Null
            throw "Nested layout was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "nested assets directory") {{
                throw
            }}
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_asset_zip_uses_temporary_staging_and_cleans_failed_extract():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task074-stage-{uuid.uuid4().hex}"
    good_root = temp_root / "good"
    bad_root = temp_root / "bad"
    good_assets = good_root / "assets"
    bad_assets = bad_root / "assets"
    good_control = good_root / "webapp" / "asset_manifest.v1.json"
    bad_control = bad_root / "webapp" / "asset_manifest.v1.json"
    good_zip = temp_root / "good-assets.zip"
    bad_zip = temp_root / "bad-assets.zip"

    manifest = {
        "schema_version": 1,
        "manifest_version": "task074-test-assets",
        "assets": [],
    }
    manifest_text = json.dumps(manifest, sort_keys=True)
    mismatched_manifest_text = json.dumps(
        {
            "schema_version": 1,
            "manifest_version": "wrong-assets",
            "assets": [],
        },
        sort_keys=True,
    )

    good_control.parent.mkdir(parents=True)
    bad_control.parent.mkdir(parents=True)
    good_control.write_text(manifest_text, encoding="utf-8")
    bad_control.write_text(manifest_text, encoding="utf-8")

    with zipfile.ZipFile(good_zip, "w") as package:
        package.writestr("model_params/yolov5/newest.pt", b"weights")
        package.writestr("data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp", b"shape")
        package.writestr("asset_manifest.v1.json", manifest_text)

    with zipfile.ZipFile(bad_zip, "w") as package:
        package.writestr("model_params/yolov5/newest.pt", b"weights")
        package.writestr("data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp", b"shape")
        package.writestr("asset_manifest.v1.json", mismatched_manifest_text)

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        Test-TowerScoutAssetZipReleaseMatch -RootPath "{good_root}" -ZipPath "{good_zip}"
        Expand-TowerScoutAssetZip -RootPath "{good_root}" -ZipPath "{good_zip}" -AssetsPath "{good_assets}"
        if (-not (Test-Path -LiteralPath "{good_assets / "model_params" / "yolov5" / "newest.pt"}" -PathType Leaf)) {{
            throw "Expected model file was not moved into final assets."
        }}
        if ((Get-ChildItem -LiteralPath "{good_assets}" -Directory -Filter ".staging-*" | Measure-Object).Count -ne 0) {{
            throw "Temporary staging folder was not removed after successful extraction."
        }}

        try {{
            Test-TowerScoutAssetZipReleaseMatch -RootPath "{bad_root}" -ZipPath "{bad_zip}"
            throw "Mismatched asset ZIP manifest was accepted before extraction."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "does not match the control package manifest") {{
                throw
            }}
        }}

        try {{
            Expand-TowerScoutAssetZip -RootPath "{bad_root}" -ZipPath "{bad_zip}" -AssetsPath "{bad_assets}"
            throw "Mismatched asset manifest was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "does not match the control package manifest") {{
                throw
            }}
        }}

        foreach ($entry in @("model_params", "data", "asset_manifest.v1.json")) {{
            if (Test-Path -LiteralPath (Join-Path "{bad_assets}" $entry)) {{
                throw "Failed extraction left final asset entry behind: $entry"
            }}
        }}
        if (
            (Test-Path -LiteralPath "{bad_assets}") -and
            ((Get-ChildItem -LiteralPath "{bad_assets}" -Directory -Filter ".staging-*" | Measure-Object).Count -ne 0)
        ) {{
            throw "Temporary staging folder was not removed after failed extraction."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_asset_zip_release_match_uses_manifest_asset_bundle_name():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-assets-{uuid.uuid4().hex}"
    package_root = temp_root / "towerscout-v0.1.0-ga-cpu"
    control_manifest = package_root / "webapp" / "asset_manifest.v1.json"
    expected_zip = temp_root / "towerscout-v0.1.0-ga-assets-task084-test-assets.zip"
    wrong_zip = temp_root / "towerscout-v0.1.0-ga-cpu-assets-task084-test-assets.zip"
    asset_manifest = {
        "schema_version": 1,
        "manifest_version": "task084-test-assets",
        "assets": [],
    }
    asset_manifest_text = json.dumps(asset_manifest, sort_keys=True)
    release_manifest = {
        "release_version": "v0.1.0-ga-cpu",
        "release_artifacts": {
            "asset_bundle": expected_zip.name,
        },
    }

    control_manifest.parent.mkdir(parents=True)
    control_manifest.write_text(asset_manifest_text, encoding="utf-8")
    (package_root / "release-manifest.v1.json").write_text(
        json.dumps(release_manifest, sort_keys=True),
        encoding="utf-8",
    )

    for zip_path in [expected_zip, wrong_zip]:
        with zipfile.ZipFile(zip_path, "w") as package:
            package.writestr("model_params/yolov5/newest.pt", b"weights")
            package.writestr("data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp", b"shape")
            package.writestr("asset_manifest.v1.json", asset_manifest_text)

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        Test-TowerScoutAssetZipReleaseMatch -RootPath "{package_root}" -ZipPath "{expected_zip}"
        try {{
            Test-TowerScoutAssetZipReleaseMatch -RootPath "{package_root}" -ZipPath "{wrong_zip}"
            throw "Flavor-specific asset ZIP name was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "expected release artifact") {{
                throw
            }}
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_staged_assets_must_match_control_manifest():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task074-assets-{uuid.uuid4().hex}"
    assets = temp_root / "assets"
    control_manifest = temp_root / "webapp" / "asset_manifest.v1.json"
    control_manifest.parent.mkdir(parents=True)
    assets.mkdir(parents=True)
    (assets / "model_params").mkdir()
    (assets / "data").mkdir()

    manifest = {
        "schema_version": 1,
        "manifest_version": "task074-test-assets",
        "assets": [],
    }
    manifest_text = json.dumps(manifest, sort_keys=True)
    control_manifest.write_text(manifest_text, encoding="utf-8")
    (assets / "asset_manifest.v1.json").write_text(manifest_text, encoding="utf-8")

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        $hasAssets = Test-TowerScoutStagedAssets -RootPath "{temp_root}" -AssetsPath "{assets}"
        if (-not $hasAssets) {{
            throw "Expected staged assets to be detected."
        }}
        Set-Content -LiteralPath "{assets / "asset_manifest.v1.json"}" -Value '{{"manifest_version":"wrong"}}' -Encoding ASCII
        try {{
            Test-TowerScoutStagedAssets -RootPath "{temp_root}" -AssetsPath "{assets}" | Out-Null
            throw "Mismatched manifest was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "does not match the control package manifest") {{
                throw
            }}
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_staged_assets_verify_files_before_reuse_and_zip_can_repair():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task083-staged-repair-{uuid.uuid4().hex}"
    assets = temp_root / "assets"
    control_manifest = temp_root / "webapp" / "asset_manifest.v1.json"
    asset_zip = temp_root / "towerscout-v0.0.0-assets-task083-test-assets.zip"
    good_payload = b"known-good-model"
    bad_payload = b"X" * len(good_payload)
    control_manifest.parent.mkdir(parents=True)
    (assets / "model_params" / "yolov5").mkdir(parents=True)
    (assets / "data").mkdir(parents=True)

    manifest = {
        "schema_version": 1,
        "manifest_version": "task083-test-assets",
        "assets": [
            {
                "id": "required-model",
                "path": "model_params/yolov5/newest.pt",
                "required": True,
                "bytes": len(good_payload),
                "sha256": hashlib.sha256(good_payload).hexdigest().upper(),
            }
        ],
    }
    manifest_text = json.dumps(manifest, sort_keys=True)
    control_manifest.write_text(manifest_text, encoding="utf-8")
    (assets / "asset_manifest.v1.json").write_text(manifest_text, encoding="utf-8")
    (assets / "model_params" / "yolov5" / "newest.pt").write_bytes(bad_payload)

    with zipfile.ZipFile(asset_zip, "w") as package:
        package.writestr("model_params/yolov5/newest.pt", good_payload)
        package.writestr("data/tiny.dat", b"x")
        package.writestr("asset_manifest.v1.json", manifest_text)

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"

        try {{
            Test-TowerScoutStagedAssets -RootPath "{temp_root}" -AssetsPath "{assets}" | Out-Null
            throw "Corrupt staged assets were accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "SHA-256") {{
                throw
            }}
        }}

        $repairable = Test-TowerScoutStagedAssets `
            -RootPath "{temp_root}" `
            -AssetsPath "{assets}" `
            -AllowRepair
        if ($repairable) {{
            throw "Corrupt staged assets should not be reused when repair is allowed."
        }}

        Expand-TowerScoutAssetZip `
            -RootPath "{temp_root}" `
            -ZipPath "{asset_zip}" `
            -AssetsPath "{assets}" `
            -ReplaceExisting
        $repaired = Test-TowerScoutStagedAssets -RootPath "{temp_root}" -AssetsPath "{assets}"
        if (-not $repaired) {{
            throw "Expected repaired staged assets to validate."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_partial_staged_assets_fail_with_rerun_guidance():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task083-partial-assets-{uuid.uuid4().hex}"
    assets = temp_root / "assets"
    control_manifest = temp_root / "webapp" / "asset_manifest.v1.json"
    asset_zip = temp_root / "assets.zip"
    control_manifest.parent.mkdir(parents=True)
    assets.mkdir(parents=True)
    (assets / "model_params").mkdir()

    manifest = {
        "schema_version": 1,
        "manifest_version": "task083-test-assets",
        "assets": [],
    }
    manifest_text = json.dumps(manifest, sort_keys=True)
    control_manifest.write_text(manifest_text, encoding="utf-8")

    with zipfile.ZipFile(asset_zip, "w") as package:
        package.writestr("model_params/yolov5/newest.pt", b"weights")
        package.writestr("data/tl_2025_us_zcta520/tl_2025_us_zcta520.shp", b"shape")
        package.writestr("asset_manifest.v1.json", manifest_text)

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        try {{
            Expand-TowerScoutAssetZip -RootPath "{temp_root}" -ZipPath "{asset_zip}" -AssetsPath "{assets}"
            throw "Partial staged assets were accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "valid staged assets are reused automatically") {{
                throw
            }}
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_image_reference_uses_digest_pin_from_env_example():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task074-image-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    digest = "sha256:" + ("a" * 64)
    (temp_root / ".env.example").write_text(
        "\n".join(
            [
                "TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda126",
                f"TOWERSCOUT_IMAGE_DIGEST={digest}",
            ]
        ),
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{BOOTSTRAP_LIB}"
        $image = Get-TowerScoutBootstrapImageReference -RootPath "{temp_root}"
        if ($image -ne "ghcr.io/j-schulein/towerscout:v0.1.0-rc1-cuda126@{digest}") {{
            throw "Image digest was not appended correctly: $image"
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_bootstrap_image_inspect_uses_small_formatted_output():
    helper = BOOTSTRAP_LIB.read_text(encoding="utf-8")

    assert '"image", "inspect", $image, "--format", "{{.Id}}"' in helper
    assert '"image", "inspect", $image)' not in helper


def test_stale_container_guard_does_not_remove_named_volumes():
    compose_helper = COMPOSE_LIB.read_text(encoding="utf-8")

    assert "Invoke-TowerScoutStaleContainerGuard" in compose_helper
    assert "container rm" in compose_helper
    assert "down -v" not in compose_helper
    assert "volume rm" not in compose_helper
    assert "docker volume" not in compose_helper
    assert "podman volume" not in compose_helper


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_stale_container_session_plan_covers_uat_lifetime_decisions():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{COMPOSE_LIB}"
    $now = [datetime]"2026-06-09T12:00:00Z"

    $start = Get-TowerScoutContainerSessionPlan -Containers @() -SessionMaxHours 12 -Now $now
    if ($start.Action -ne "start") {{
        throw "Expected no-container plan to start, got $($start.Action)"
    }}

    $young = [pscustomobject]@{{
        Id = "young"
        Name = "towerscout"
        StateStatus = "running"
        HealthStatus = "healthy"
        CreatedAt = $now.AddHours(-2)
    }}
    $reuse = Get-TowerScoutContainerSessionPlan -Containers @($young) -SessionMaxHours 12 -Now $now
    if ($reuse.Action -ne "reuse") {{
        throw "Expected young healthy container to be reused, got $($reuse.Action)"
    }}

    $old = [pscustomobject]@{{
        Id = "old"
        Name = "towerscout"
        StateStatus = "running"
        HealthStatus = "healthy"
        CreatedAt = $now.AddHours(-13)
    }}
    $restartOld = Get-TowerScoutContainerSessionPlan -Containers @($old) -SessionMaxHours 12 -Now $now
    if ($restartOld.Action -ne "restart" -or $restartOld.Reason -notmatch "older than 12") {{
        throw "Expected old container to restart, got $($restartOld.Action): $($restartOld.Reason)"
    }}

    $override = Get-TowerScoutContainerSessionPlan -Containers @($old) -SessionMaxHours 24 -Now $now
    if ($override.Action -ne "reuse") {{
        throw "Expected longer support TTL to reuse, got $($override.Action)"
    }}

    $stopped = [pscustomobject]@{{
        Id = "stopped"
        Name = "towerscout"
        StateStatus = "exited"
        HealthStatus = ""
        CreatedAt = $now.AddHours(-1)
    }}
    $restartStopped = Get-TowerScoutContainerSessionPlan -Containers @($stopped) -SessionMaxHours 12 -Now $now
    if ($restartStopped.Action -ne "restart" -or $restartStopped.Reason -notmatch "not running") {{
        throw "Expected stopped container to restart, got $($restartStopped.Action): $($restartStopped.Reason)"
    }}

    $unhealthy = [pscustomobject]@{{
        Id = "unhealthy"
        Name = "towerscout"
        StateStatus = "running"
        HealthStatus = "unhealthy"
        CreatedAt = $now.AddHours(-1)
    }}
    $restartUnhealthy = Get-TowerScoutContainerSessionPlan -Containers @($unhealthy) -SessionMaxHours 12 -Now $now
    if ($restartUnhealthy.Action -ne "restart" -or $restartUnhealthy.Reason -notmatch "unhealthy") {{
        throw "Expected unhealthy container to restart, got $($restartUnhealthy.Action): $($restartUnhealthy.Reason)"
    }}

    try {{
        Get-TowerScoutContainerSessionPlan -Containers @($young) -SessionMaxHours -1 -Now $now | Out-Null
        throw "Negative session lifetime was accepted."
    }}
    catch {{
        if ($_.Exception.Message -notmatch "SessionMaxHours") {{
            throw
        }}
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_readiness_probe_rejects_non_towerscout_payloads():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{BOOTSTRAP_LIB}"
    $readyPayload = '{{"state":"ready","components":{{}},"runtime":{{}},"recovery":[]}}'
    if (-not (Test-TowerScoutReadinessPayload -Body $readyPayload)) {{
        throw "Expected TowerScout readiness payload to be accepted."
    }}
    $fatalPayload = '{{"state":"fatal","components":{{}},"runtime":{{}},"recovery":["collect support evidence"]}}'
    if (-not (Test-TowerScoutReadinessPayload -Body $fatalPayload)) {{
        throw "Expected fatal TowerScout readiness payload to be accepted."
    }}
    foreach ($body in @(
        '<html>not found</html>',
        '{{"state":"ready"}}',
        '{{"state":"ok","components":{{}},"runtime":{{}},"recovery":[]}}'
    )) {{
        if (Test-TowerScoutReadinessPayload -Body $body) {{
            throw "Expected non-TowerScout payload to be rejected: $body"
        }}
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell bootstrap helpers are Windows-only")
def test_bootstrap_port_mapping_conflict_detects_stale_container():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{BOOTSTRAP_LIB}"
    $conflict = Get-TowerScoutPortMappingConflict -Port 5000 -Lines @(
        "towerscout-towerscout-1 Created 0.0.0.0:5000->5000/tcp",
        "other Up 2 minutes 0.0.0.0:5001->5000/tcp"
    )
    if ($conflict -notmatch "Created") {{
        throw "Expected stale created container to be detected."
    }}
    $conflicts = @(Get-TowerScoutPortMappingConflicts -Port 5000 -Lines @(
        "first Created 0.0.0.0:5000->5000/tcp",
        "second Exited (0) 127.0.0.1:5000->5000/tcp",
        "running Up 2 minutes 0.0.0.0:5000->5000/tcp"
    ))
    if ($conflicts.Count -ne 2) {{
        throw "Expected two stale conflicts, got $($conflicts.Count): $($conflicts -join '; ')"
    }}
    $allowed = Get-TowerScoutPortMappingConflict -Port 5000 -Lines @(
        "towerscout-towerscout-1 Up 2 minutes 0.0.0.0:5000->5000/tcp"
    )
    if (-not [string]::IsNullOrWhiteSpace($allowed)) {{
        throw "Expected running mapping to be allowed."
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout
