from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SETUP_WIZARD = REPO_ROOT / "webapp" / "js" / "src" / "setup-wizard.js"
SETTINGS = REPO_ROOT / "webapp" / "js" / "src" / "settings.js"


def test_setup_and_settings_preserve_provider_tls_error_details():
    for path in (SETUP_WIZARD, SETTINGS):
        source = path.read_text(encoding="utf-8")

        assert "error.payload = data" in source
        assert "payload.validation_results || {}" in source
        assert "payload.support_action || details.support_action" in source
        assert "details.repair_command" in source
        assert "Category:" in source
