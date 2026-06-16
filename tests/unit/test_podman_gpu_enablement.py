"""Task-083 Podman GPU CDI gating and provisioner coverage."""

import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutCompose.ps1"
PODMAN_GPU_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutPodmanGpu.ps1"
PACKAGE_SCRIPT = REPO_ROOT / "scripts" / "package-release.ps1"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
PODMAN_GPU_OVERLAY = REPO_ROOT / "compose.gpu.podman.yaml"


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


def test_podman_gpu_overlay_and_release_package_entries_exist():
    overlay = PODMAN_GPU_OVERLAY.read_text(encoding="utf-8")
    env_example = ENV_EXAMPLE.read_text(encoding="utf-8")
    package_script = PACKAGE_SCRIPT.read_text(encoding="utf-8")

    assert "nvidia.com/gpu=all" in overlay
    assert "security_opt:" in overlay
    assert "label=disable" in overlay
    assert "TOWERSCOUT_PODMAN_GPU_OVERLAY=0" in env_example
    assert "TOWERSCOUT_PODMAN_MACHINE=podman-machine-default" in env_example
    assert '"compose.gpu.podman.yaml"' in package_script
    assert '"scripts\\enable-podman-gpu.ps1"' in package_script
    assert '"scripts\\lib\\TowerScoutPodmanGpu.ps1"' in package_script


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_podman_gpu_overlay_decision_matrix():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{COMPOSE_LIB}"

    function Test-TowerScoutPodmanGpuReady {{
        param([string] $MachineName)
        return [pscustomobject]@{{
            Ready = $true
            FailedRung = -1
            Message = "ready"
        }}
    }}

    $env:TOWERSCOUT_GPU_AUTO_OVERLAY = "0"
    $env:TOWERSCOUT_PODMAN_GPU_OVERLAY = "0"
    if (Resolve-TowerScoutGpuComposeOverlay -EngineName docker -Gpu off) {{
        throw "Expected -Gpu off to skip all overlays."
    }}
    if (Test-TowerScoutUseGpuOverlay -EngineName podman -Gpu auto) {{
        throw "Expected podman auto to skip overlay when gate is off."
    }}

    $env:TOWERSCOUT_GPU_AUTO_OVERLAY = "1"
    if ((Resolve-TowerScoutGpuComposeOverlay -EngineName docker -Gpu auto) -ne "compose.gpu.yaml") {{
        throw "Expected docker auto gate to select compose.gpu.yaml."
    }}

    $env:TOWERSCOUT_PODMAN_GPU_OVERLAY = "1"
    if ((Resolve-TowerScoutGpuComposeOverlay -EngineName podman -Gpu auto) -ne "compose.gpu.podman.yaml") {{
        throw "Expected podman auto gate and ready CDI to select compose.gpu.podman.yaml."
    }}
    if ((Resolve-TowerScoutGpuComposeOverlay -EngineName podman -Gpu on) -ne "compose.gpu.podman.yaml") {{
        throw "Expected podman -Gpu on and ready CDI to select compose.gpu.podman.yaml."
    }}

    function Test-TowerScoutPodmanGpuReady {{
        param([string] $MachineName)
        return [pscustomobject]@{{
            Ready = $false
            FailedRung = 3
            Message = "CDI spec missing"
        }}
    }}

    try {{
        Resolve-TowerScoutGpuComposeOverlay -EngineName podman -Gpu on | Out-Null
        throw "Expected podman -Gpu on to fail closed when CDI is missing."
    }}
    catch {{
        if ($_.Exception.Message -notmatch "enable-podman-gpu.ps1") {{
            throw
        }}
    }}

    $autoFallback = Resolve-TowerScoutGpuComposeOverlay -EngineName podman -Gpu auto
    if (-not [string]::IsNullOrWhiteSpace($autoFallback)) {{
        throw "Expected podman -Gpu auto to fall back to CPU when CDI is missing."
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_podman_gpu_preflight_ladder_reports_ready_and_cdi_missing():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{COMPOSE_LIB}"
    $machineInspectJson = (
        '[{{"Name":"podman-machine-default","State":"running","ConfigDir":' +
        '{{"Path":"C:\\\\Users\\\\tester\\\\.config\\\\containers\\\\podman\\\\machine\\\\wsl"}}}}]'
    )

    function Test-TowerScoutCommand {{
        param([string] $Name)
        return $Name -eq "podman"
    }}
    function Test-TowerScoutHostNvidiaSmi {{
        return $true
    }}
    function Invoke-TowerScoutPodmanCommand {{
        param([string[]] $Arguments, [int] $TimeoutSeconds)
        $text = [string]::Join(" ", $Arguments)
        if ($text -match "version") {{
            return [pscustomobject]@{{ ExitCode = 0; StdOut = "5.8.2"; StdErr = "" }}
        }}
        if ($text -match "machine inspect") {{
            return [pscustomobject]@{{
                ExitCode = 0
                StdOut = $machineInspectJson
                StdErr = ""
            }}
        }}
        if ($text -match "nvidia-smi") {{
            return [pscustomobject]@{{ ExitCode = 0; StdOut = "GPU 0: NVIDIA T1000 8GB"; StdErr = "" }}
        }}
        if ($text -match "nvidia-ctk cdi list") {{
            return [pscustomobject]@{{ ExitCode = 0; StdOut = "nvidia.com/gpu=all"; StdErr = "" }}
        }}
        throw "Unexpected command $text"
    }}

    $ready = Test-TowerScoutPodmanGpuReady -MachineName "podman-machine-default"
    if (-not $ready.Ready) {{
        throw "Expected GPU preflight to be ready: $($ready.Message)"
    }}

    function Invoke-TowerScoutPodmanCommand {{
        param([string[]] $Arguments, [int] $TimeoutSeconds)
        $text = [string]::Join(" ", $Arguments)
        if ($text -match "version") {{
            return [pscustomobject]@{{ ExitCode = 0; StdOut = "5.8.2"; StdErr = "" }}
        }}
        if ($text -match "machine inspect") {{
            return [pscustomobject]@{{
                ExitCode = 0
                StdOut = $machineInspectJson
                StdErr = ""
            }}
        }}
        if ($text -match "nvidia-smi") {{
            return [pscustomobject]@{{ ExitCode = 0; StdOut = "GPU 0: NVIDIA T1000 8GB"; StdErr = "" }}
        }}
        if ($text -match "nvidia-ctk cdi list") {{
            return [pscustomobject]@{{ ExitCode = 1; StdOut = ""; StdErr = "missing CDI" }}
        }}
        throw "Unexpected command $text"
    }}

    $missing = Test-TowerScoutPodmanGpuReady -MachineName "podman-machine-default"
    if ($missing.Ready -or $missing.FailedRung -ne 3 -or $missing.Message -notmatch "enable-podman-gpu.ps1") {{
        throw "Expected rung 3 CDI failure, got $($missing.FailedRung): $($missing.Message)"
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell provisioner helpers are Windows-only")
def test_podman_gpu_provisioner_dry_run_and_verify_only_are_non_mutating():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{PODMAN_GPU_LIB}"
    $machineInspectJson = (
        '[{{"Name":"podman-machine-default","State":"running","ConfigDir":' +
        '{{"Path":"C:\\\\Users\\\\tester\\\\.config\\\\containers\\\\podman\\\\machine\\\\wsl"}}}}]'
    )

    $script:Calls = @()
    function Invoke-TowerScoutPodmanGpuCommand {{
        param([string] $FileName, [string[]] $Arguments, [int] $TimeoutSeconds)
        $script:Calls += [string]::Join(" ", $Arguments)
        throw "Dry run should not execute commands."
    }}

    $dryRun = Invoke-TowerScoutPodmanGpuEnablement -DryRun -MachineName "podman-machine-default" -Image "test:image"
    if (-not $dryRun.Success -or $script:Calls.Count -ne 0) {{
        throw "Dry run executed commands or failed."
    }}

    function Invoke-TowerScoutPodmanGpuCommand {{
        param([string] $FileName, [string[]] $Arguments, [int] $TimeoutSeconds)
        $text = [string]::Join(" ", $Arguments)
        $script:Calls += $text
        if ($text -match "machine inspect") {{
            return [pscustomobject]@{{
                ExitCode = 0
                StdOut = $machineInspectJson
                StdErr = ""
            }}
        }}
        if ($text -match "nvidia-smi") {{
            return [pscustomobject]@{{ ExitCode = 0; StdOut = "GPU 0: NVIDIA T1000 8GB"; StdErr = "" }}
        }}
        if ($text -match "nvidia-ctk cdi list") {{
            return [pscustomobject]@{{ ExitCode = 0; StdOut = ""; StdErr = "" }}
        }}
        throw "VerifyOnly attempted mutating command: $text"
    }}

    $script:Calls = @()
    try {{
        Invoke-TowerScoutPodmanGpuEnablement -VerifyOnly -MachineName "podman-machine-default" -Image "test:image" | Out-Null
        throw "Expected VerifyOnly to fail when CDI is missing."
    }}
    catch {{
        if ($_.Exception.Message -notmatch "CDI spec does not list") {{
            throw
        }}
    }}
    if (($script:Calls -join " ") -match "dnf install|cdi generate|podman run") {{
        throw "VerifyOnly executed a mutating command: $($script:Calls -join '; ')"
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell provisioner helpers are Windows-only")
def test_podman_gpu_provisioner_recovers_stale_cdi_once():
    evidence_dir = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task083-podman-gpu-{uuid.uuid4().hex}"
    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{PODMAN_GPU_LIB}"
        $machineInspectJson = (
            '[{{"Name":"podman-machine-default","State":"running","ConfigDir":' +
            '{{"Path":"C:\\\\Users\\\\tester\\\\.config\\\\containers\\\\podman\\\\machine\\\\wsl"}}}}]'
        )

        $script:GenerateCount = 0
        $script:SmokeCount = 0
        function Invoke-TowerScoutPodmanGpuCommand {{
            param([string] $FileName, [string[]] $Arguments, [int] $TimeoutSeconds)
            $text = [string]::Join(" ", $Arguments)
            if ($text -match "machine inspect") {{
                return [pscustomobject]@{{
                    ExitCode = 0
                    StdOut = $machineInspectJson
                    StdErr = ""
                }}
            }}
            if ($text -match "/usr/lib/wsl/lib/nvidia-smi") {{
                return [pscustomobject]@{{ ExitCode = 0; StdOut = "GPU 0: NVIDIA T1000 8GB"; StdErr = "" }}
            }}
            if ($text -match "nvidia-container-toolkit") {{
                return [pscustomobject]@{{ ExitCode = 0; StdOut = "nvidia-container-toolkit-1.19.1"; StdErr = "" }}
            }}
            if ($text -match "nvidia-ctk cdi generate") {{
                $script:GenerateCount += 1
                return [pscustomobject]@{{ ExitCode = 0; StdOut = "generated"; StdErr = "" }}
            }}
            if ($text -match "nvidia-ctk cdi list") {{
                return [pscustomobject]@{{ ExitCode = 0; StdOut = "nvidia.com/gpu=all"; StdErr = "" }}
            }}
            if ($text -match "^run --rm --device") {{
                $script:SmokeCount += 1
                if ($script:SmokeCount -eq 1) {{
                    return [pscustomobject]@{{
                        ExitCode = 1
                        StdOut = ""
                        StdErr = "unresolvable CDI devices nvidia.com/gpu=all"
                    }}
                }}
                return [pscustomobject]@{{ ExitCode = 0; StdOut = "GPU 0: NVIDIA T1000 8GB"; StdErr = "" }}
            }}
            throw "Unexpected command: $text"
        }}

        $result = Invoke-TowerScoutPodmanGpuEnablement `
            -MachineName "podman-machine-default" `
            -Image "test:image" `
            -EvidenceDir "{evidence_dir}"
        if (-not $result.Success) {{
            throw "Expected provisioner success."
        }}
        if ($script:GenerateCount -ne 2) {{
            throw "Expected initial CDI generation plus one stale-CDI regeneration, got $script:GenerateCount."
        }}
        if ($script:SmokeCount -ne 2) {{
            throw "Expected one smoke retry, got $script:SmokeCount."
        }}
        if (-not (Test-Path -LiteralPath "{evidence_dir / 'runtime-versions.json'}" -PathType Leaf)) {{
            throw "Expected runtime-versions evidence to be written."
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(evidence_dir, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell provisioner helpers are Windows-only")
def test_podman_gpu_image_uses_package_template_digest_before_env_exists():
    temp_root = REPO_ROOT / ".agent_work" / "pytest-temp" / f"task084-podman-image-{uuid.uuid4().hex}"
    temp_root.mkdir(parents=True)
    digest = "sha256:" + ("b" * 64)
    (temp_root / ".env.example").write_text(
        "\n".join(
            [
                "TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout:v0.1.0-ga-cuda121",
                f"TOWERSCOUT_IMAGE_DIGEST={digest}",
            ]
        ),
        encoding="utf-8",
    )

    try:
        command = f"""
        $ErrorActionPreference = "Stop"
        . "{PODMAN_GPU_LIB}"

        function Get-TowerScoutPodmanGpuRepoRoot {{
            return "{temp_root}"
        }}

        $env:TOWERSCOUT_IMAGE = ""
        $env:TOWERSCOUT_IMAGE_DIGEST = ""
        $resolved = Get-TowerScoutPodmanGpuImage
        $expected = "ghcr.io/j-schulein/towerscout:v0.1.0-ga-cuda121@{digest}"
        if ($resolved -ne $expected) {{
            throw "Expected package template image '$expected', got '$resolved'"
        }}

        Set-Content -LiteralPath "{temp_root / '.env'}" -Encoding ASCII -Value @(
            "TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout:local-cuda121",
            "TOWERSCOUT_IMAGE_DIGEST="
        )
        $resolvedEnvWithoutDigest = Get-TowerScoutPodmanGpuImage
        if ($resolvedEnvWithoutDigest -ne "ghcr.io/j-schulein/towerscout:local-cuda121") {{
            throw ".env image should not append .env.example digest: $resolvedEnvWithoutDigest"
        }}

        Set-Content -LiteralPath "{temp_root / '.env'}" -Encoding ASCII -Value @(
            "TOWERSCOUT_IMAGE=ghcr.io/j-schulein/towerscout:local-cuda121@{digest}",
            "TOWERSCOUT_IMAGE_DIGEST=sha256:{'c' * 64}"
        )
        $resolvedEnv = Get-TowerScoutPodmanGpuImage
        if ($resolvedEnv -ne "ghcr.io/j-schulein/towerscout:local-cuda121@{digest}") {{
            throw ".env should win and should not append a second digest: $resolvedEnv"
        }}

        $env:TOWERSCOUT_IMAGE = "ghcr.io/j-schulein/towerscout:process-cuda121"
        $env:TOWERSCOUT_IMAGE_DIGEST = "sha256:{'d' * 64}"
        $resolvedProcessEnv = Get-TowerScoutPodmanGpuImage
        if ($resolvedProcessEnv -ne "ghcr.io/j-schulein/towerscout:process-cuda121@sha256:{'d' * 64}") {{
            throw "process environment image should use only process environment digest: $resolvedProcessEnv"
        }}
        "ok"
        """
        result = _run_powershell(command)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "ok" in result.stdout
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


@pytest.mark.skipif(os.name != "nt", reason="PowerShell provisioner helpers are Windows-only")
def test_podman_gpu_image_reference_splitter_handles_registry_ports_and_digests():
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{PODMAN_GPU_LIB}"

    $parts = Get-TowerScoutImageReferenceParts -Image "localhost:5000/team/towerscout:cuda@sha256:{'a' * 64}"
    if ($parts.Repository -ne "localhost:5000/team/towerscout") {{
        throw "Repository split failed: $($parts.Repository)"
    }}
    if ($parts.Tag -ne "cuda") {{
        throw "Tag split failed: $($parts.Tag)"
    }}
    if ($parts.Digest -ne "sha256:{'a' * 64}") {{
        throw "Digest split failed: $($parts.Digest)"
    }}
    "ok"
    """
    result = _run_powershell(command)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout
