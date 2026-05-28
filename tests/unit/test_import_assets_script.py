from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPORT_ASSETS_SCRIPT = REPO_ROOT / "scripts" / "import-assets.ps1"
IMPORT_TLS_CA_SCRIPT = REPO_ROOT / "scripts" / "import-tls-ca.ps1"
START_SCRIPT = REPO_ROOT / "scripts" / "start.ps1"


def test_import_assets_script_preserves_port_and_restarts_after_copy():
    script = IMPORT_ASSETS_SCRIPT.read_text(encoding="utf-8")

    env_init = script.index("Initialize-TowerScoutEnvFile -RootPath $repoRoot")
    port_assignment = script.index('$env:TOWERSCOUT_PORT = "$Port"')
    compose_start = script.index('@("up", "-d", "towerscout")')
    data_copy = script.index('"towerscout:/app/webapp/data/"')
    restart = script.index('"restart",')
    wait = script.index("Waiting for TowerScout to reload imported assets")
    verify = script.index("Verifying imported assets with TowerScout manifest")

    assert "[int] $Port" in script
    assert env_init < port_assignment
    assert port_assignment < compose_start
    assert data_copy < restart < wait < verify
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
