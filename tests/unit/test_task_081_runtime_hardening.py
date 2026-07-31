"""Task-081 runtime and launcher hardening coverage."""

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "compose.yaml"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
PACKAGE_SCRIPT = REPO_ROOT / "scripts" / "package-release.ps1"
COMPOSE_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutCompose.ps1"
LAUNCH_SCRIPT = REPO_ROOT / "scripts" / "launch.ps1"
IMPORT_ASSETS_SCRIPT = REPO_ROOT / "scripts" / "import-assets.ps1"
STOP_SCRIPT = REPO_ROOT / "scripts" / "stop.ps1"
STATUS_SCRIPT = REPO_ROOT / "scripts" / "status.ps1"
PROVIDER_CATALOG = REPO_ROOT / "scripts" / "podman-compose-providers.v1.json"
PROVIDER_INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install-podman-compose-provider.ps1"


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


def _write_podman_compose_provider(path: Path, version: str = "1.5.0"):
    path.write_text(
        "@echo off\r\n"
        "if \"%1\"==\"version\" (\r\n"
        f"  echo podman-compose version {version}\r\n"
        "  exit /b 0\r\n"
        ")\r\n"
        "echo podman-compose %*\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )


def test_compose_defaults_use_cpu_tag_restart_and_runtime_guards():
    compose = COMPOSE_FILE.read_text(encoding="utf-8")
    env_example = ENV_EXAMPLE.read_text(encoding="utf-8")
    package_script = PACKAGE_SCRIPT.read_text(encoding="utf-8")

    assert "ghcr.io/j-schulein/towerscout:latest-cpu" in compose
    assert "ghcr.io/j-schulein/towerscout:latest-cpu" in env_example
    assert 'ghcr.io/j-schulein/towerscout:latest-cpu' in package_script
    assert "ghcr.io/j-schulein/towerscout:latest}" not in compose
    assert "TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout:latest\n" not in env_example
    assert "restart: always" in compose
    assert "TOWERSCOUT_GPU_MODE: ${TOWERSCOUT_GPU_MODE:-off}" in compose
    assert "TOWERSCOUT_PILOT_MAX_TILES: ${TOWERSCOUT_PILOT_MAX_TILES:-100}" in compose
    assert "PODMAN_COMPOSE_PROVIDER=" in env_example
    assert "auto-detect exactly one" in env_example
    assert "install-podman-compose-provider.cmd -Apply" in env_example


def test_podman_compose_provider_installer_uses_isolated_venv_and_pinned_deps():
    installer = PROVIDER_INSTALL_SCRIPT.read_text(encoding="utf-8")
    catalog = json.loads(PROVIDER_CATALOG.read_text(encoding="utf-8"))
    provider = next(
        item for item in catalog["providers"] if item["id"] == "podman-compose-pypi-1.5.0"
    )

    requirements = {dependency["requirement"] for dependency in provider["dependencies"]}
    assert provider["requires_python"] == ">=3.9"
    assert requirements == {"python-dotenv==1.1.1", "PyYAML==6.0.2"}
    assert "Join-Path $InstallDir \".venv\"" in installer
    assert "@(\"-m\", \"venv\", $venvDir)" in installer
    assert "\"pip\"" in installer
    assert "\"install\"" in installer
    assert "--only-binary" in installer
    assert "foreach ($dependency in @($provider.dependencies))" in installer
    assert "\"%~dp0.venv\\Scripts\\podman-compose.exe\" %*" in installer
    assert "System.IO.Compression.ZipFile" not in installer
    assert "podman_compose.py" not in installer


def test_import_assets_uses_shared_copy_fallback_and_sets_gpu_environment():
    import_assets = IMPORT_ASSETS_SCRIPT.read_text(encoding="utf-8")
    helper = COMPOSE_LIB.read_text(encoding="utf-8")

    assert "Set-TowerScoutGpuEnvironment -Gpu $Gpu -Build:$Build" in import_assets
    assert "Copy-TowerScoutContainerPath" in import_assets
    assert "podman cp $LocalPath" in helper
    assert "Get-TowerScoutPodmanServiceContainerId" in helper
    assert "io.podman.compose.project" in helper
    assert "com.docker.compose.project" in helper
    assert '"NVIDIA_VISIBLE_DEVICES"' in helper
    assert '"NVIDIA_DRIVER_CAPABILITIES"' in helper
    assert "$env:TOWERSCOUT_CONTAINER_ENGINE = $effectiveEngine" in helper
    assert "Initialize-TowerScoutPodmanComposeProvider" in helper
    assert "Assert-TowerScoutPodmanComposeProviderAllowed" in helper


def test_launch_gpu_on_requires_cuda_readiness():
    launch = LAUNCH_SCRIPT.read_text(encoding="utf-8")

    assert "function Test-TowerScoutCudaSelected" in launch
    assert '$GpuMode -eq "on" -and -not (Test-TowerScoutCudaSelected -Readiness $readiness)' in launch
    assert "selected_device=cuda" in launch
    assert "Runtime: engine={0} device_policy={1} selected_device={2} pytorch_flavor={3}" in launch


def test_stop_script_uses_down_without_deleting_named_volumes():
    stop_script = STOP_SCRIPT.read_text(encoding="utf-8")
    compose_line = next(line for line in stop_script.splitlines() if "Invoke-TowerScoutCompose" in line)

    assert '@("down", "--remove-orphans")' in stop_script
    assert '@("stop")' not in stop_script
    assert "--volumes" not in compose_line
    assert "-v" not in compose_line


def test_status_script_reports_engine_image_identity_and_fails_on_mismatch():
    status_script = STATUS_SCRIPT.read_text(encoding="utf-8")

    assert 'Initialize-TowerScoutEnvFile -RootPath $repoRoot' in status_script
    assert "Test-TowerScoutRunningImageMatchesPackage" in status_script
    assert "Running image:" in status_script
    assert "Running image digest:" in status_script
    assert '$imageIdentityCheck.Reason -eq "mismatch"' in status_script
    assert '$imageIdentityCheck.Reason -eq "container_not_found"' in status_script
    assert "No running TowerScout container found for this package." in status_script
    assert "Running container image does not match this package's pinned identity." in status_script
    assert "exit 1" in status_script


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_status_script_preserves_down_state_when_container_is_missing():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task088-status-down-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    lib_dir = temp_root / "lib"
    lib_dir.mkdir(parents=True)
    status_copy = temp_root / "status.ps1"
    status_copy.write_text(STATUS_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    (temp_root / ".env.example").write_text(
        "TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout:v0.1.1-cpu@sha256:" + ("1" * 64) + "\n",
        encoding="utf-8",
    )
    (temp_root / "release-manifest.v1.json").write_text(
        json.dumps({"release_version": "v0.1.1-cpu", "pytorch_flavor": "cpu"}),
        encoding="utf-8",
    )
    stub_lib = lib_dir / "TowerScoutCompose.ps1"
    stub_lib.write_text(
        "function Get-TowerScoutRepoRoot { return \"" + str(temp_root).replace("\\", "\\\\") + "\" }\n"
        "function Initialize-TowerScoutEnvFile { param([string] $RootPath) }\n"
        "function Write-TowerScoutComposeProviderSummary { param([string] $Engine) }\n"
        "function Invoke-TowerScoutCompose { param([string] $Engine, [string[]] $ComposeArguments) $script:TowerScoutComposeExitCode = 0 }\n"
        "function Test-TowerScoutRunningImageMatchesPackage { param([string] $Engine) return [pscustomobject]@{ Checked = $true; Matches = $false; Reason = \"container_not_found\"; ExpectedImage = \"\"; ExpectedDigest = \"\"; Identity = $null } }\n",
        encoding="utf-8",
    )

    try:
        result = subprocess.run(
            [_powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(status_copy), "-Port", "5999"],
            cwd=temp_root,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 2, result.stdout + result.stderr
        combined = result.stdout + result.stderr
        assert "No running TowerScout container found for this package." in combined
        assert "Running container image does not match this package's pinned identity." not in combined
        assert "TowerScout readiness endpoint is not reachable" in combined
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_auto_engine_selection_prefers_reachable_podman_when_docker_is_down():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-auto-provider-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    provider = temp_root / "podman-compose.cmd"
    _write_podman_compose_provider(provider)

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        $env:Path = "{temp_root}"
        $env:PODMAN_COMPOSE_PROVIDER = ""
        . "{COMPOSE_LIB}"

        function Test-TowerScoutCommand {{
            param([string] $Name)
            return $Name -in @("docker", "podman")
        }}

        function Test-TowerScoutEngineReady {{
            param([string] $EngineName)
            return $EngineName -eq "podman"
        }}

        $command = Get-TowerScoutComposeCommand -Engine auto
        if ($command["Executable"] -ne "podman") {{
            throw "Expected automatic engine selection to choose reachable Podman."
        }}
        if ($command["Arguments"][0] -ne "compose") {{
            throw "Expected Podman compose arguments."
        }}
        if ($env:PODMAN_COMPOSE_PROVIDER -ne "{provider}") {{
            throw "Expected provider auto-detection to set the approved provider."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_compose_invocation_allows_successful_provider_stderr_banner():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{COMPOSE_LIB}"
    $stubDir = Join-Path "{REPO_ROOT}" ".agent_work\\pytest-temp"
    New-Item -ItemType Directory -Force -Path $stubDir | Out-Null
    $stubPath = Join-Path $stubDir "task081-provider-stderr.ps1"
    $stubScript = @(
        "[Console]::Error.WriteLine('provider banner')",
        "Write-Output 'abc123'",
        "exit 0"
    ) -join "; "
    Set-Content -LiteralPath $stubPath -Encoding UTF8 -Value $stubScript

    function Get-TowerScoutRepoRoot {{
        return "{REPO_ROOT}"
    }}

    function Get-TowerScoutComposeCommand {{
        param([string] $Engine)
        return @{{
            Executable = "powershell.exe"
            Arguments = @(
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                $stubPath
            )
        }}
    }}

    function Test-TowerScoutUseGpuOverlay {{
        return $false
    }}

    function Set-TowerScoutGpuEnvironment {{
        param(
            [string] $Gpu,
            [switch] $Build
        )
    }}

    $containerIds = @(Get-TowerScoutComposeServiceContainerIds -Engine podman)
    if ($containerIds.Count -ne 1 -or $containerIds[0] -ne "abc123") {{
        throw "Expected compose ps to return abc123 despite provider stderr banner."
    }}

    Invoke-TowerScoutCompose -Engine podman -ComposeArguments @("up", "-d")
    if ($script:TowerScoutComposeExitCode -ne 0) {{
        throw "Expected provider command to exit 0, got $script:TowerScoutComposeExitCode"
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_running_image_identity_check_matches_pinned_digest_from_engine_inspect():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task088-image-identity-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    digest = "sha256:" + ("4" * 64)
    expected_image = f"ghcr.io/j-schulein/towerscout:v0.1.1-cpu@{digest}"
    (temp_root / "release-manifest.v1.json").write_text(
        json.dumps({"release_version": "v0.1.1-cpu", "pytorch_flavor": "cpu"}),
        encoding="utf-8",
    )
    (temp_root / ".env").write_text(
        "\n".join(
            [
                f"TOWERSCOUT_IMAGE={expected_image}",
                f"TOWERSCOUT_IMAGE_DIGEST={digest}",
            ]
        ),
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"

        function Get-TowerScoutRepoRoot {{
            return "{temp_root}"
        }}

        function Get-TowerScoutRunningImageIdentity {{
            param([string] $Engine, [string] $ServiceName)
            return [pscustomobject]@{{
                EngineName = "docker"
                ContainerId = "container-123"
                ConfigImage = "{expected_image}"
                ImageId = "sha256:imageid123"
                RepoDigests = @("{expected_image}")
                ActualDigest = "{digest}"
            }}
        }}

        $result = Test-TowerScoutRunningImageMatchesPackage -Engine docker -RootPath "{temp_root}"
        if (-not $result.Checked) {{
            throw "Expected running image identity check to run."
        }}
        if (-not $result.Matches) {{
            throw "Expected running image identity check to match the pinned digest."
        }}
        if ($result.Identity.ConfigImage -ne "{expected_image}") {{
            throw "Expected Config.Image to match the pinned image."
        }}
        if ($result.Identity.ActualDigest -ne "{digest}") {{
            throw "Expected actual digest to match the pinned digest."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_get_running_image_identity_uses_engine_inspect_successfully():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task088-engine-inspect-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    digest = "sha256:" + ("5" * 64)
    expected_image = f"ghcr.io/j-schulein/towerscout:v0.1.2-cpu@{digest}"
    (temp_root / "release-manifest.v1.json").write_text(
        json.dumps({"release_version": "v0.1.2-cpu", "pytorch_flavor": "cpu"}),
        encoding="utf-8",
    )
    (temp_root / ".env").write_text(
        "\n".join(
            [
                f"TOWERSCOUT_IMAGE={expected_image}",
                f"TOWERSCOUT_IMAGE_DIGEST={digest}",
            ]
        ),
        encoding="utf-8",
    )
    shim_dir = temp_root / "bin"
    shim_dir.mkdir(parents=True)
    docker_cmd = shim_dir / "docker.cmd"
    docker_cmd.write_text(
        "@echo off\r\n"
        "if \"%1\"==\"compose\" (\r\n"
        "  if \"%2\"==\"ps\" echo container-123&& exit /b 0\r\n"
        ")\r\n"
        "if \"%1\"==\"inspect\" (\r\n"
        "  if \"%5\"==\"{{.Image}}\" echo sha256:imageid123&& exit /b 0\r\n"
        f"  if \"%5\"==\"{{.Config.Image}}\" echo {expected_image}&& exit /b 0\r\n"
        f"  if \"%5\"==\"{{json .RepoDigests}}\" echo [\"ghcr.io/j-schulein/towerscout@{digest}\"]&& exit /b 0\r\n"
        ")\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        $env:PATH = "{shim_dir};$env:PATH"
        . "{COMPOSE_LIB}"

        function Get-TowerScoutRepoRoot {{
            return "{temp_root}"
        }}

        function Get-TowerScoutComposeServiceContainerIds {{
            param([string] $Engine, [string] $ServiceName)
            return @("container-123")
        }}

        $identity = Get-TowerScoutRunningImageIdentity -Engine docker -ServiceName "towerscout"
        if ($null -eq $identity) {{
            throw "Expected engine inspect to produce a running image identity."
        }}
        if ($identity.ImageId -ne "sha256:imageid123") {{
            throw "Expected image identity helper to preserve the inspected image ID."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_podman_copy_uses_direct_podman_cp_without_provider_cp_noise():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-podman-copy-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    local_asset = temp_root / "asset.txt"
    local_asset.write_text("asset", encoding="utf-8")

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"
        $podmanShimDir = Join-Path "{temp_root}" "bin"
        New-Item -ItemType Directory -Force -Path $podmanShimDir | Out-Null
        $podmanShimPath = Join-Path $podmanShimDir "podman.cmd"
        $podmanCallsPath = Join-Path "{temp_root}" "podman-calls.txt"
        $podmanShim = @(
            '@echo off',
            ('echo %*>> "' + $podmanCallsPath + '"'),
            'if "%1"=="compose" echo compose-provider-id&& exit /b 0',
            'if "%1"=="ps" echo direct-container-id&& exit /b 0',
            'if "%1"=="cp" exit /b 0',
            'exit /b 1'
        ) -join "`r`n"
        Set-Content -LiteralPath $podmanShimPath -Encoding ASCII -Value $podmanShim
        $env:PATH = "$podmanShimDir;$env:PATH"

        function Get-TowerScoutRepoRoot {{
            return "{temp_root}"
        }}
        function Get-TowerScoutComposeCommand {{
            param([string] $Engine)
            if ($Engine -ne "podman") {{
                throw "Expected podman engine, got $Engine"
            }}
            return @{{
                Executable = "podman"
                Arguments = @("compose")
            }}
        }}
        function Invoke-TowerScoutCompose {{
            throw "Podman copy should use direct podman cp, not compose cp."
        }}

        $env:COMPOSE_PROJECT_NAME = "task084-project"
        Copy-TowerScoutContainerPath `
            -Engine podman `
            -LocalPath "{local_asset}" `
            -ContainerPath "/app/model_params/asset.txt"

        if ($script:TowerScoutComposeExitCode -ne 0) {{
            throw "Expected direct podman cp exit 0, got $script:TowerScoutComposeExitCode"
        }}
        $joinedCalls = Get-Content -LiteralPath $podmanCallsPath -Raw
        if ($joinedCalls -notmatch "compose .* ps -a -q towerscout") {{
            throw "Expected provider compose ps lookup, got $joinedCalls"
        }}
        if ($joinedCalls -match "ps .*io\\.podman\\.compose\\.project=task084-project") {{
            throw "Expected compose ps to avoid label fallback, got $joinedCalls"
        }}
        if ($joinedCalls -notmatch "cp .*compose-provider-id:/app/model_params/asset.txt") {{
            throw "Expected direct podman cp call, got $joinedCalls"
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        os.environ.pop("COMPOSE_PROJECT_NAME", None)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_podman_compose_provider_override_uses_env_file_and_rejects_docker_desktop():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task083-provider-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    provider = temp_root / "podman-compose.cmd"
    _write_podman_compose_provider(provider)
    (temp_root / ".env").write_text(
        f"PODMAN_COMPOSE_PROVIDER={provider}\n",
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"
        function Get-TowerScoutRepoRoot {{
            return "{temp_root}"
        }}

        $env:PODMAN_COMPOSE_PROVIDER = ""
        $resolved = Initialize-TowerScoutPodmanComposeProvider
        if ($resolved -ne "{provider}") {{
            throw "Expected provider from .env, got $resolved"
        }}
        if ($env:PODMAN_COMPOSE_PROVIDER -ne "{provider}") {{
            throw "Expected environment override to be set for podman compose."
        }}

        $env:PODMAN_COMPOSE_PROVIDER = "C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker-compose.exe"
        try {{
            Initialize-TowerScoutPodmanComposeProvider | Out-Null
            throw "Docker Desktop provider override was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "Docker Desktop") {{
                throw
            }}
        }}

        try {{
            $dockerDesktopProviderLine = (
                '>>>> Executing external compose provider ' +
                '"C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker-compose.exe"'
            )
            $dockerDesktopEscapedProviderLine = (
                '>>>> Executing external compose provider ' +
                '"C:\\\\Program Files\\\\Docker\\\\Docker\\\\resources\\\\bin\\\\docker-compose.exe". <<<<'
            )
            if (-not (Test-TowerScoutDockerDesktopComposeProvider -Value $dockerDesktopEscapedProviderLine)) {{
                throw "Docker Desktop provider output with escaped backslashes was not detected."
            }}
            Assert-TowerScoutPodmanComposeProviderAllowed -Lines @(
                $dockerDesktopProviderLine,
                $dockerDesktopEscapedProviderLine
            )
            throw "Docker Desktop provider output was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "Docker Desktop") {{
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


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_podman_compose_provider_requires_single_approved_provider():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-provider-policy-{uuid.uuid4().hex}"
    empty_path_root = temp_root / "empty-path"
    provider_a_root = temp_root / "provider-a"
    provider_b_root = temp_root / "provider-b"
    empty_path_root.mkdir(parents=True)
    provider_a_root.mkdir(parents=True)
    provider_b_root.mkdir(parents=True)
    _write_podman_compose_provider(provider_a_root / "podman-compose.cmd")
    _write_podman_compose_provider(provider_b_root / "podman-compose.cmd")

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"

        $env:PODMAN_COMPOSE_PROVIDER = ""
        $env:Path = "{empty_path_root}"
        try {{
            Initialize-TowerScoutPodmanComposeProvider | Out-Null
            throw "Missing provider was accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "No approved Podman Compose provider") {{
                throw
            }}
        }}

        $env:PODMAN_COMPOSE_PROVIDER = ""
        $env:Path = "{provider_a_root};{provider_b_root}"
        try {{
            Initialize-TowerScoutPodmanComposeProvider | Out-Null
            throw "Ambiguous providers were accepted."
        }}
        catch {{
            if ($_.Exception.Message -notmatch "Multiple approved Podman Compose providers") {{
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


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_podman_compose_provider_env_apply_preserves_existing_settings():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-provider-apply-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    provider = temp_root / "podman-compose.cmd"
    _write_podman_compose_provider(provider)
    env_file = temp_root / ".env"
    env_file.write_text(
        "TOWERSCOUT_PORT=5005\n"
        "PODMAN_COMPOSE_PROVIDER=old-provider\n"
        "TOWERSCOUT_GPU_MODE=off\n",
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{REPO_ROOT}\\scripts\\lib\\TowerScoutPodmanComposeProvider.ps1"

        $preview = Set-TowerScoutPodmanComposeProviderEnv -ProviderPath "{provider}" -RootPath "{temp_root}"
        if ($preview.Applied) {{
            throw "Preview mode should not apply .env changes."
        }}
        $before = Get-Content -LiteralPath "{env_file}" -Raw
        if ($before -notmatch "PODMAN_COMPOSE_PROVIDER=old-provider") {{
            throw "Preview mode changed .env."
        }}

        $applied = Set-TowerScoutPodmanComposeProviderEnv -ProviderPath "{provider}" -RootPath "{temp_root}" -Apply
        if (-not $applied.Applied) {{
            throw "Apply mode did not report an applied update."
        }}
        if (-not (Test-Path -LiteralPath $applied.BackupPath -PathType Leaf)) {{
            throw "Apply mode did not create a backup."
        }}
        $after = Get-Content -LiteralPath "{env_file}" -Raw
        if ($after -notmatch [regex]::Escape("PODMAN_COMPOSE_PROVIDER={provider}")) {{
            throw "Apply mode did not set the provider path."
        }}
        if ($after -notmatch "TOWERSCOUT_PORT=5005" -or $after -notmatch "TOWERSCOUT_GPU_MODE=off") {{
            throw "Apply mode did not preserve existing settings."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_podman_command_timeout_and_cp_fallback_use_compose_ps():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-podman-command-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    podman_cmd = temp_root / "podman.cmd"
    podman_cmd.write_text(
        "@echo off\r\n"
        "if \"%1\"==\"sleep\" (\r\n"
        "  ping -n 6 127.0.0.1 > nul\r\n"
        "  exit /b 0\r\n"
        ")\r\n"
        "echo podman %*\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        $env:Path = "{temp_root};" + $env:Path
        . "{COMPOSE_LIB}"

        $timeout = Invoke-TowerScoutPodmanCommand -Arguments @("sleep") -TimeoutSeconds 1
        if ($timeout.ExitCode -ne 124 -or -not $timeout.TimedOut) {{
            throw "Expected timeout exit 124, got $($timeout.ExitCode) timedOut=$($timeout.TimedOut)"
        }}
        if ($timeout.StdErr -notmatch "timed out") {{
            throw "Expected timeout stderr guidance, got $($timeout.StdErr)"
        }}

        function Get-TowerScoutComposeServiceContainerIds {{
            param([string] $Engine, [string] $ServiceName)
            if ($Engine -ne "podman" -or $ServiceName -ne "towerscout") {{
                throw "Unexpected compose ps lookup: $Engine $ServiceName"
            }}
            return @("compose-provider-id")
        }}

        $containerId = Get-TowerScoutPodmanServiceContainerId -ServiceName "towerscout"
        if ($containerId -ne "compose-provider-id") {{
            throw "Expected compose ps container id, got $containerId"
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_compose_project_name_sanitizes_release_package_folder_dots():
    package_root = REPO_ROOT / ".agent_work" / "pytest-temp" / "towerscout-v0.1.0-rc6-cpu"
    package_root.mkdir(parents=True, exist_ok=True)
    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"
        function Get-TowerScoutRepoRoot {{
            return "{package_root}"
        }}

        $env:COMPOSE_PROJECT_NAME = ""
        $projectName = Get-TowerScoutComposeProjectName
        if ($projectName -ne "towerscout-v010-rc6-cpu") {{
            throw "Expected sanitized package project name, got $projectName"
        }}

        Set-Content -LiteralPath "{package_root / ".env"}" -Encoding UTF8 -Value "COMPOSE_PROJECT_NAME=env-file-project"
        $envFileProjectName = Get-TowerScoutComposeProjectName
        if ($envFileProjectName -ne "env-file-project") {{
            throw "Expected .env COMPOSE_PROJECT_NAME to win over folder fallback, got $envFileProjectName"
        }}

        $env:COMPOSE_PROJECT_NAME = "explicit-project"
        $explicit = Get-TowerScoutComposeProjectName
        if ($explicit -ne "explicit-project") {{
            throw "Expected explicit COMPOSE_PROJECT_NAME to win, got $explicit"
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(package_root, ignore_errors=True)
        os.environ.pop("COMPOSE_PROJECT_NAME", None)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_podman_gpu_gate_uses_configured_machine_from_env_file():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task083-podman-machine-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    (temp_root / ".env").write_text(
        "TOWERSCOUT_PODMAN_MACHINE=towerscout-gpu-machine\n",
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{COMPOSE_LIB}"

        function Get-TowerScoutRepoRoot {{
            return "{temp_root}"
        }}

        function Test-TowerScoutUseGpuOverlay {{
            return $true
        }}

        function Test-TowerScoutPodmanGpuReady {{
            param([string] $MachineName)
            $script:CapturedMachineName = $MachineName
            return [pscustomobject]@{{
                Ready = $true
                FailedRung = -1
                Message = "ready"
            }}
        }}

        $env:TOWERSCOUT_PODMAN_MACHINE = ""
        $resolved = Get-TowerScoutConfiguredPodmanMachineName
        if ($resolved -ne "towerscout-gpu-machine") {{
            throw "Expected .env Podman machine, got $resolved"
        }}

        $overlay = Resolve-TowerScoutGpuComposeOverlay -EngineName podman -Gpu on
        if ($overlay -ne "compose.gpu.podman.yaml") {{
            throw "Expected Podman GPU overlay, got $overlay"
        }}
        if ($script:CapturedMachineName -ne "towerscout-gpu-machine") {{
            throw "Expected GPU readiness check to use configured machine, got $script:CapturedMachineName"
        }}

        $explicit = Get-TowerScoutConfiguredPodmanMachineName -MachineName "explicit-machine"
        if ($explicit -ne "explicit-machine") {{
            throw "Explicit Podman machine should win, got $explicit"
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_stale_container_plan_restarts_on_gpu_or_device_mismatch():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{COMPOSE_LIB}"
    $now = [datetime]"2026-06-12T12:00:00Z"

    $cpuContainer = [pscustomobject]@{{
        Id = "cpu"
        Name = "towerscout"
        StateStatus = "running"
        HealthStatus = "healthy"
        CreatedAt = $now.AddHours(-1)
        GpuMode = "off"
        DevicePolicy = "cpu"
    }}
    $gpuPlan = Get-TowerScoutContainerSessionPlan `
        -Containers @($cpuContainer) `
        -SessionMaxHours 12 `
        -ExpectedGpuMode "on" `
        -ExpectedDevicePolicy "cuda" `
        -Now $now
    if ($gpuPlan.Action -ne "restart" -or $gpuPlan.Reason -notmatch "different GPU mode") {{
        throw "Expected GPU mode mismatch restart, got $($gpuPlan.Action): $($gpuPlan.Reason)"
    }}

    $wrongDeviceContainer = [pscustomobject]@{{
        Id = "wrong-device"
        Name = "towerscout"
        StateStatus = "running"
        HealthStatus = "healthy"
        CreatedAt = $now.AddHours(-1)
        GpuMode = "on"
        DevicePolicy = "cpu"
    }}
    $devicePlan = Get-TowerScoutContainerSessionPlan `
        -Containers @($wrongDeviceContainer) `
        -SessionMaxHours 12 `
        -ExpectedGpuMode "on" `
        -ExpectedDevicePolicy "cuda" `
        -Now $now
    if ($devicePlan.Action -ne "restart" -or $devicePlan.Reason -notmatch "different ML device policy") {{
        throw "Expected device policy mismatch restart, got $($devicePlan.Action): $($devicePlan.Reason)"
    }}

    $matchingContainer = [pscustomobject]@{{
        Id = "matching"
        Name = "towerscout"
        StateStatus = "running"
        HealthStatus = "healthy"
        CreatedAt = $now.AddHours(-1)
        GpuMode = "on"
        DevicePolicy = "cuda"
        ContainerEngine = "podman"
        Image = "ghcr.io/j-schulein/towerscout:latest-cpu"
        HostPort = "5000"
    }}
    $reusePlan = Get-TowerScoutContainerSessionPlan `
        -Containers @($matchingContainer) `
        -SessionMaxHours 12 `
        -ExpectedGpuMode "on" `
        -ExpectedDevicePolicy "cuda" `
        -ExpectedContainerEngine "podman" `
        -ExpectedImage "ghcr.io/j-schulein/towerscout:latest-cpu" `
        -ExpectedHostPort "5000" `
        -Now $now
    if ($reusePlan.Action -ne "reuse") {{
        throw "Expected matching launch settings to reuse, got $($reusePlan.Action): $($reusePlan.Reason)"
    }}

    $imagePlan = Get-TowerScoutContainerSessionPlan `
        -Containers @($matchingContainer) `
        -SessionMaxHours 12 `
        -ExpectedGpuMode "on" `
        -ExpectedDevicePolicy "cuda" `
        -ExpectedContainerEngine "podman" `
        -ExpectedImage "ghcr.io/j-schulein/towerscout:v0.1.0-rc3-cpu" `
        -ExpectedHostPort "5000" `
        -Now $now
    if ($imagePlan.Action -ne "restart" -or $imagePlan.Reason -notmatch "different image reference") {{
        throw "Expected image mismatch restart, got $($imagePlan.Action): $($imagePlan.Reason)"
    }}

    $portPlan = Get-TowerScoutContainerSessionPlan `
        -Containers @($matchingContainer) `
        -SessionMaxHours 12 `
        -ExpectedGpuMode "on" `
        -ExpectedDevicePolicy "cuda" `
        -ExpectedContainerEngine "podman" `
        -ExpectedImage "ghcr.io/j-schulein/towerscout:latest-cpu" `
        -ExpectedHostPort "5001" `
        -Now $now
    if ($portPlan.Action -ne "restart" -or $portPlan.Reason -notmatch "different host port") {{
        throw "Expected port mismatch restart, got $($portPlan.Action): $($portPlan.Reason)"
    }}

    $enginePlan = Get-TowerScoutContainerSessionPlan `
        -Containers @($matchingContainer) `
        -SessionMaxHours 12 `
        -ExpectedGpuMode "on" `
        -ExpectedDevicePolicy "cuda" `
        -ExpectedContainerEngine "docker" `
        -ExpectedImage "ghcr.io/j-schulein/towerscout:latest-cpu" `
        -ExpectedHostPort "5000" `
        -Now $now
    if ($enginePlan.Action -ne "restart" -or $enginePlan.Reason -notmatch "different container engine") {{
        throw "Expected container engine mismatch restart, got $($enginePlan.Action): $($enginePlan.Reason)"
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout
