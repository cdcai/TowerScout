import os
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPAIR_SCRIPT = REPO_ROOT / "scripts" / "repair-provider-tls.ps1"
CERTIFICATE_STORE_LIB = (
    REPO_ROOT / "scripts" / "lib" / "TowerScoutCertificateStore.ps1"
)
COMPOSE_LIB = REPO_ROOT / "scripts" / "lib" / "TowerScoutCompose.ps1"


def _powershell_executable():
    return shutil.which("powershell.exe") or shutil.which("pwsh")


@pytest.mark.skipif(
    os.name != "nt",
    reason="PowerShell runtime helpers are Windows-only",
)
def test_port_environment_preserves_package_value_unless_explicitly_overridden():
    command = rf"""
    $ErrorActionPreference = "Stop"
    . "{COMPOSE_LIB}"

    $env:TOWERSCOUT_PORT = "5211"
    $preserved = Set-TowerScoutPortEnvironment
    if ($preserved -ne 5211 -or $env:TOWERSCOUT_PORT -ne "5211") {{
        throw "Omitted port did not preserve the package value."
    }}

    $overridden = Set-TowerScoutPortEnvironment -Port 5300
    if ($overridden -ne 5300 -or $env:TOWERSCOUT_PORT -ne "5300") {{
        throw "Explicit port did not override the package value."
    }}

    Remove-Item Env:TOWERSCOUT_PORT
    $omitted = Set-TowerScoutPortEnvironment
    if ($null -ne $omitted -or (Test-Path Env:TOWERSCOUT_PORT)) {{
        throw "Omitted source-checkout port should remain unset."
    }}

    $defaulted = Set-TowerScoutPortEnvironment -DefaultPort 5000
    if ($defaulted -ne 5000 -or $env:TOWERSCOUT_PORT -ne "5000") {{
        throw "Caller-requested default port was not applied."
    }}

    "ok"
    """
    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


@pytest.mark.skipif(
    os.name != "nt",
    reason="PowerShell runtime helpers are Windows-only",
)
def test_source_checkout_env_port_is_left_for_compose_when_process_env_is_empty(
    tmp_path,
):
    source_root = tmp_path / "source checkout"
    source_root.mkdir()
    (source_root / ".env.example").write_text(
        "TOWERSCOUT_PORT=5000\n",
        encoding="ascii",
    )
    (source_root / ".env").write_text(
        "TOWERSCOUT_PORT=5211\n",
        encoding="ascii",
    )
    (source_root / "release-manifest.v1.json").write_text(
        '{"release_version":"template"}\n',
        encoding="ascii",
    )

    command = rf"""
    $ErrorActionPreference = "Stop"
    . "{COMPOSE_LIB}"

    Remove-Item Env:TOWERSCOUT_PORT -ErrorAction SilentlyContinue
    Initialize-TowerScoutEnvFile -RootPath "{source_root}"
    $resolved = Set-TowerScoutPortEnvironment
    if ($null -ne $resolved) {{
        throw "Source checkout unexpectedly resolved a process port."
    }}
    if (Test-Path Env:TOWERSCOUT_PORT) {{
        throw "Source checkout unexpectedly set TOWERSCOUT_PORT."
    }}
    $fileValue = Get-TowerScoutEnvFileValueFromPath `
        -Path "{source_root / '.env'}" `
        -Name "TOWERSCOUT_PORT"
    if ($fileValue -ne "5211") {{
        throw "Source checkout .env port was not preserved."
    }}

    $launchPort = Set-TowerScoutPortEnvironment `
        -RootPath "{source_root}" `
        -DefaultPort 5000
    if ($launchPort -ne 5211 -or $env:TOWERSCOUT_PORT -ne "5211") {{
        throw "Launcher resolution did not honor the source checkout .env port."
    }}
    "ok"
    """
    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


def _create_repair_sandbox(tmp_path: Path, importer_exit_code: int) -> Path:
    scripts_dir = tmp_path / "package with spaces" / "scripts"
    lib_dir = scripts_dir / "lib"
    lib_dir.mkdir(parents=True)
    shutil.copy2(REPAIR_SCRIPT, scripts_dir / REPAIR_SCRIPT.name)
    shutil.copy2(
        CERTIFICATE_STORE_LIB,
        lib_dir / CERTIFICATE_STORE_LIB.name,
    )
    (scripts_dir / "import-tls-ca.cmd").write_text(
        "@echo off\r\n"
        "echo importer args:%*\r\n"
        "echo importer diagnostic one\r\n"
        "echo importer diagnostic two\r\n"
        f"exit /b {importer_exit_code}\r\n",
        encoding="ascii",
    )
    return scripts_dir / REPAIR_SCRIPT.name


@pytest.mark.skipif(os.name != "nt", reason="PowerShell repair wrapper is Windows-only")
@pytest.mark.parametrize("importer_exit_code", [0, 7])
def test_repair_wrapper_preserves_scalar_importer_exit_code(
    tmp_path,
    importer_exit_code,
):
    repair_script = _create_repair_sandbox(tmp_path, importer_exit_code)
    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(repair_script),
            "-Provider",
            "google",
            "-Engine",
            "docker",
            "-Gpu",
            "off",
            "-Port",
            "5211",
            "-Apply",
            "-CertificatePath",
            str(tmp_path / "certificate with spaces.pem"),
        ],
        cwd=repair_script.parent.parent,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == importer_exit_code, result.stdout + result.stderr
    assert "importer diagnostic one" in result.stdout
    assert "importer diagnostic two" in result.stdout
    assert "-Port 5211" in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="PowerShell repair wrapper is Windows-only")
def test_repair_wrapper_omits_port_when_operator_did_not_supply_one(tmp_path):
    repair_script = _create_repair_sandbox(tmp_path, 0)
    result = subprocess.run(
        [
            _powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(repair_script),
            "-Provider",
            "google",
            "-Engine",
            "docker",
            "-Gpu",
            "off",
            "-Apply",
            "-CertificatePath",
            str(tmp_path / "certificate with spaces.pem"),
        ],
        cwd=repair_script.parent.parent,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    importer_line = next(
        line for line in result.stdout.splitlines() if line.startswith("importer args:")
    )
    assert "-Port" not in importer_line
