"""Run the Windows importer with a synthetic engine; no real container/store changes."""
import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell importer")
@pytest.mark.parametrize("verify_exit", [0, 7])
@pytest.mark.parametrize("duplicate_entries", [False, True])
@pytest.mark.parametrize("recorded_ca", [False, True])
def test_candidate_activation_preserves_old_files_and_failure_config(tmp_path, verify_exit, duplicate_entries, recorded_ca):
    scripts = tmp_path / "scripts"
    lib = scripts / "lib"
    lib.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/import-tls-ca.ps1", scripts)
    (lib / "TowerScoutCertificateStore.ps1").write_text("# unused synthetic store\n")
    original = "REQUESTS_CA_BUNDLE=/old/working.pem\nSSL_CERT_FILE=/old/working.pem\nKEEP=value\n"
    approved_name = "recorded-ca.pem" if recorded_ca else "local-ca.pem"
    if recorded_ca:
        original += f"TOWERSCOUT_TLS_APPROVED_CA=/app/webapp/config/certs/{approved_name}\n"
    if duplicate_entries:
        original += "REQUESTS_CA_BUNDLE=/old/working.pem\nSSL_CERT_FILE=/old/working.pem\n"
    (tmp_path / ".env").write_text(original, encoding="ascii")
    (tmp_path / "old-working.pem").write_text("previous working bundle")
    (tmp_path / "local-ca.pem").write_text("previous approved CA")
    fake = r'''
function Get-TowerScoutRepoRoot { return (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) }
function Initialize-TowerScoutEnvFile { param($RootPath) }
function Set-TowerScoutPortEnvironment { param($Port) }
function Get-TowerScoutEnvFileValueFromPath { param($Path,$Name)
    $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^$Name=" } | Select-Object -Last 1
    if ($line) { return ($line -split '=',2)[1] }
    return ''
}
function Copy-TowerScoutContainerPath { param($Engine,$LocalPath,$ContainerPath,[switch]$Build,$Gpu)
    Copy-Item -LiteralPath $LocalPath -Destination (Join-Path (Get-TowerScoutRepoRoot) ([IO.Path]::GetFileName($ContainerPath)))
    $script:TowerScoutComposeExitCode=0
}
function Invoke-TowerScoutCompose { param($Engine,[switch]$Build,$Gpu,[string[]]$ComposeArguments)
    $script:TowerScoutComposeExitCode=0
    if ($ComposeArguments -contains '/app/webapp/ts_trust.py') {
        $candidate=$ComposeArguments[-1]
        Set-Content -LiteralPath (Join-Path (Get-TowerScoutRepoRoot) ([IO.Path]::GetFileName($candidate))) -Value 'validated candidate'
    }
    if ($ComposeArguments -contains 'env') { $script:TowerScoutComposeExitCode=VERIFY_EXIT }
}
'''.replace("VERIFY_EXIT", str(verify_exit))
    (lib / "TowerScoutCompose.ps1").write_text(fake, encoding="ascii")
    result = subprocess.run([
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
        str(scripts / "import-tls-ca.ps1"), "-Engine", "docker", "-RefreshExisting",
        "-VerifyProvider", "google",
    ], capture_output=True, text=True, timeout=30)
    assert result.returncode == verify_exit, result.stdout + result.stderr
    assert (tmp_path / "old-working.pem").read_text() == "previous working bundle"
    assert (tmp_path / "local-ca.pem").read_text() == "previous approved CA"
    after = (tmp_path / ".env").read_text()
    if verify_exit:
        assert after == original
    else:
        assert "KEEP=value" in after
        assert f"TOWERSCOUT_TLS_APPROVED_CA=/app/webapp/config/certs/{approved_name}" in after
        assert "/old/working.pem" not in after
        for key in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "TOWERSCOUT_TLS_APPROVED_CA"):
            assert sum(line.startswith(key + "=") for line in after.splitlines()) == 1
        backups = list(tmp_path.glob(".env.backup.tls-*"))
        assert len(backups) == 1 and backups[0].read_text() == original
