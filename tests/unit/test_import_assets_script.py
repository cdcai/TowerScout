from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPORT_ASSETS_SCRIPT = REPO_ROOT / "scripts" / "import-assets.ps1"


def test_import_assets_script_preserves_port_and_restarts_after_copy():
    script = IMPORT_ASSETS_SCRIPT.read_text(encoding="utf-8")

    port_assignment = script.index('$env:TOWERSCOUT_PORT = "$Port"')
    compose_start = script.index('@("up", "-d", "towerscout")')
    data_copy = script.index('"towerscout:/app/webapp/data/"')
    restart = script.index('"restart",')
    wait = script.index("Waiting for TowerScout to reload imported assets")
    verify = script.index("Verifying imported assets with TowerScout manifest")

    assert "[int] $Port" in script
    assert port_assignment < compose_start
    assert data_copy < restart < wait < verify
    assert "/api/health" in script
    assert "/api/readiness" in script
    assert "/getengines" in script
    assert "asset_status == 'ok'" in script
    assert "engine_count > 0" in script
