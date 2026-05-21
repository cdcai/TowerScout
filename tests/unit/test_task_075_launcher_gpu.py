"""Task-075 launcher GPU mode helper tests."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def _powershell_executable():
    return shutil.which("powershell.exe") or shutil.which("pwsh")


@pytest.mark.skipif(os.name != "nt", reason="PowerShell launcher helpers are Windows-only")
def test_gpu_launcher_helpers_use_cpu_safe_auto_and_build_indexes():
    powershell = _powershell_executable()
    if powershell is None:
        pytest.skip("PowerShell executable not found")

    helper_path = REPO_ROOT / "scripts" / "lib" / "TowerScoutCompose.ps1"
    command = f"""
    $ErrorActionPreference = "Stop"
    . "{helper_path}"

    $env:PYTORCH_INDEX_URL = "https://download.pytorch.org/whl/cu121"
    Set-TowerScoutGpuEnvironment -Gpu off -Build
    if ($env:TOWERSCOUT_DEVICE -ne "cpu") {{
        throw "Expected -Gpu off to force TOWERSCOUT_DEVICE=cpu."
    }}
    if ($env:PYTORCH_INDEX_URL -ne "https://download.pytorch.org/whl/cpu") {{
        throw "Expected -Gpu off -Build to force the CPU PyTorch index."
    }}
    if ($env:TOWERSCOUT_PYTORCH_FLAVOR -ne "cpu") {{
        throw "Expected -Gpu off -Build to set TOWERSCOUT_PYTORCH_FLAVOR=cpu."
    }}

    $env:TOWERSCOUT_GPU_AUTO_OVERLAY = "0"
    if (Test-TowerScoutUseGpuOverlay -EngineName docker -Gpu auto) {{
        throw "Expected -Gpu auto to skip the GPU overlay without explicit validation override."
    }}

    $env:TOWERSCOUT_GPU_AUTO_OVERLAY = "1"
    if (-not (Test-TowerScoutUseGpuOverlay -EngineName docker -Gpu auto)) {{
        throw "Expected -Gpu auto to use the GPU overlay when explicit validation override is set."
    }}

    if (-not (Test-TowerScoutUseGpuOverlay -EngineName docker -Gpu on)) {{
        throw "Expected -Gpu on to request the GPU overlay."
    }}

    $env:PYTORCH_INDEX_URL = "https://download.pytorch.org/whl/cpu"
    Set-TowerScoutGpuEnvironment -Gpu auto -Build
    if ($env:TOWERSCOUT_DEVICE -ne "auto") {{
        throw "Expected -Gpu auto to set TOWERSCOUT_DEVICE=auto."
    }}
    if ($env:PYTORCH_INDEX_URL -ne "https://download.pytorch.org/whl/cu121") {{
        throw "Expected -Gpu auto -Build to select the CUDA PyTorch index."
    }}
    if ($env:TOWERSCOUT_PYTORCH_FLAVOR -ne "cuda121") {{
        throw "Expected -Gpu auto -Build to set TOWERSCOUT_PYTORCH_FLAVOR=cuda121."
    }}

    "ok"
    """

    result = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout
