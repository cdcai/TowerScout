"""Task-081 runtime and launcher hardening coverage."""

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
    assert "Docker-Desktop-free Podman validation" in env_example


def test_import_assets_uses_shared_copy_fallback_and_sets_gpu_environment():
    import_assets = IMPORT_ASSETS_SCRIPT.read_text(encoding="utf-8")
    helper = COMPOSE_LIB.read_text(encoding="utf-8")

    assert "Set-TowerScoutGpuEnvironment -Gpu $Gpu -Build:$Build" in import_assets
    assert "Copy-TowerScoutContainerPath" in import_assets
    assert "Compose provider did not support cp; falling back to direct podman cp." in helper
    assert "Get-TowerScoutPodmanServiceContainerId" in helper
    assert "io.podman.compose.project" in helper
    assert "com.docker.compose.project" in helper
    assert "$env:TOWERSCOUT_CONTAINER_ENGINE = $effectiveEngine" in helper
    assert "Initialize-TowerScoutPodmanComposeProvider" in helper
    assert "Assert-TowerScoutPodmanComposeProviderAllowed" in helper


def test_launch_gpu_on_requires_cuda_readiness():
    launch = LAUNCH_SCRIPT.read_text(encoding="utf-8")

    assert "function Test-TowerScoutCudaSelected" in launch
    assert '$Gpu -eq "on" -and -not (Test-TowerScoutCudaSelected -Readiness $readiness)' in launch
    assert "selected_device=cuda" in launch
    assert "Runtime: engine={0} device_policy={1} selected_device={2} pytorch_flavor={3}" in launch


def test_stop_script_uses_down_without_deleting_named_volumes():
    stop_script = STOP_SCRIPT.read_text(encoding="utf-8")
    compose_line = next(line for line in stop_script.splitlines() if "Invoke-TowerScoutCompose" in line)

    assert '@("down", "--remove-orphans")' in stop_script
    assert '@("stop")' not in stop_script
    assert "--volumes" not in compose_line
    assert "-v" not in compose_line


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_auto_engine_selection_prefers_reachable_podman_when_docker_is_down():
    command = f"""
    $ErrorActionPreference = "Stop"
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
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


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
def test_podman_compose_provider_override_uses_env_file_and_rejects_docker_desktop():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task083-provider-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    provider = temp_root / "podman-compose.exe"
    provider.write_text("stub provider", encoding="utf-8")
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
