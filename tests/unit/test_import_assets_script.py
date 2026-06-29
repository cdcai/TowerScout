from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPORT_ASSETS_SCRIPT = REPO_ROOT / "scripts" / "import-assets.ps1"
IMPORT_TLS_CA_SCRIPT = REPO_ROOT / "scripts" / "import-tls-ca.ps1"
REPAIR_PROVIDER_TLS_SCRIPT = REPO_ROOT / "scripts" / "repair-provider-tls.ps1"
REPAIR_PROVIDER_TLS_CMD = REPO_ROOT / "scripts" / "repair-provider-tls.cmd"
START_SCRIPT = REPO_ROOT / "scripts" / "start.ps1"


def test_import_assets_script_preserves_port_and_restarts_after_copy():
    script = IMPORT_ASSETS_SCRIPT.read_text(encoding="utf-8")

    env_init = script.index("Initialize-TowerScoutEnvFile -RootPath $repoRoot")
    port_assignment = script.index('$env:TOWERSCOUT_PORT = "$Port"')
    compose_start = script.index('@("up", "-d", "towerscout")')
    model_copy = script.index('-ContainerPath "/app/webapp/model_params/"')
    data_copy = script.index('-ContainerPath "/app/webapp/data/"')
    restart = script.index('"restart",')
    wait = script.index("Waiting for TowerScout to reload imported assets")
    verify = script.index("Verifying imported assets with TowerScout manifest")

    assert "[int] $Port" in script
    assert env_init < port_assignment
    assert port_assignment < compose_start
    assert "Copy-TowerScoutContainerPath" in script
    assert compose_start < model_copy < data_copy < restart < wait < verify
    assert "/api/health" in script
    assert "/api/readiness" in script
    assert "/getengines" in script
    assert "asset_status == 'ok'" in script
    assert "engine_count > 0" in script


def test_packaged_compose_entrypoints_initialize_env_before_starting_stack():
    start_script = START_SCRIPT.read_text(encoding="utf-8")
    tls_script = IMPORT_TLS_CA_SCRIPT.read_text(encoding="utf-8")

    start_env_init = start_script.index("Initialize-TowerScoutEnvFile -RootPath $repoRoot")
    start_compose = start_script.index("Invoke-TowerScoutCompose")
    tls_env_init = tls_script.index("Initialize-TowerScoutEnvFile -RootPath $repoRoot")
    tls_compose_start = tls_script.index('Write-Host "Starting TowerScout container')

    assert start_env_init < start_compose
    assert tls_env_init < tls_compose_start


def test_tls_ca_import_persists_bundle_paths_in_env_file():
    script = IMPORT_TLS_CA_SCRIPT.read_text(encoding="utf-8")

    verify = script.index("Verifying $resolvedVerifyProvider TLS through the combined CA bundle")
    persist = script.index("Set-TowerScoutEnvFileValues -RootPath $repoRoot")
    imported = script.index('Write-Host "Imported CA bundle:"')

    assert "function Set-TowerScoutEnvFileValues" in script
    assert "REQUESTS_CA_BUNDLE = $containerBundlePath" in script
    assert "SSL_CERT_FILE = $containerBundlePath" in script
    assert "Updated .env so future TowerScout starts use the combined CA bundle." in script
    assert "Restart TowerScout for the updated TLS settings to take effect." in script
    assert "TrimStart().StartsWith(\"#\")" in script
    assert "_tls_body" not in script
    assert "_tls_category" in script
    assert "except requests.exceptions.SSLError" in script
    assert "google_tls_category=tls_certificate_error" in script
    assert "ok = r.status_code in (200, 400, 401, 403)" in script
    assert "function Invoke-TowerScoutTlsProviderVerification" in script
    assert "Copy-TowerScoutFileIntoContainer -LocalPath $localVerifyPath" in script
    assert "/tmp/towerscout-tls-verify-$verifyId.py" in script
    assert '"python",' in script
    assert "$containerVerifyPath" in script
    assert not re.search(r'"python",\s*"-c"', script)
    assert "Provider TLS verification failed; .env was not updated." in script
    assert verify < persist < imported


def test_tls_ca_import_podman_copy_fallback_reuses_compose_container_lookup():
    script = IMPORT_TLS_CA_SCRIPT.read_text(encoding="utf-8")

    fallback = script.index("Compose provider did not support cp; falling back to direct podman cp.")

    assert 'Get-TowerScoutPodmanServiceContainerId -ServiceName "towerscout"' in script[fallback:]
    assert "Split-Path (Get-TowerScoutRepoRoot) -Leaf" not in script[fallback:]
    assert "--filter \"label=io.podman.compose.project=$projectName\"" not in script[fallback:]


def test_provider_tls_repair_wrapper_is_dry_run_first_and_delegates_to_importer():
    script = REPAIR_PROVIDER_TLS_SCRIPT.read_text(encoding="utf-8")
    cmd = REPAIR_PROVIDER_TLS_CMD.read_text(encoding="utf-8")

    assert "[switch] $Apply" in script
    assert "Dry run only" in script
    assert "Get-TowerScoutRemoteCertificateChain" in script
    assert "Select-TowerScoutTlsCaCandidate" in script
    assert "$callbackChainElements" in script
    assert "X509Certificate2]::new($chainCertificate.RawData)" in script
    assert "return $callbackChainElements" in script
    assert "if ($element.Index -eq 0)" in script
    assert "Multiple CA candidates have the same score" in script
    assert "Format-TowerScoutRepairCommand" in script
    assert "scripts\\repair-provider-tls.cmd" in script
    assert "scripts\\import-tls-ca.cmd" in script
    assert "Join-Path $PSScriptRoot \"import-tls-ca.cmd\"" in script
    assert "\"-Provider\", $Provider" in script
    assert "\"-Gpu\", $Gpu" in script
    assert "Support-sensitive local output" in script
    assert "issuer={0}" in script
    assert "Write-Host \"  $repairCommand\"" in script
    assert "Write-Host \"  $importCommand -Apply\"" not in script
    assert "No API keys or provider response bodies" in script
    assert "repair-provider-tls.ps1" in cmd
