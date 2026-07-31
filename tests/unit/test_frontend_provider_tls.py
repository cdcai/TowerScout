from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SETUP_WIZARD = REPO_ROOT / "webapp" / "js" / "src" / "setup-wizard.js"
SETUP_WIZARD_BUNDLE = REPO_ROOT / "webapp" / "js" / "towerscout.js"
SETTINGS = REPO_ROOT / "webapp" / "js" / "src" / "settings.js"
API_HELPERS = REPO_ROOT / "webapp" / "js" / "src" / "utils" / "apiHelpers.js"


def test_setup_and_settings_preserve_provider_tls_error_details():
    shared_source = API_HELPERS.read_text(encoding="utf-8")

    assert "error.payload = data" in shared_source
    assert "payload.validation_results || {}" in shared_source
    assert "payload.support_action || details.support_action" in shared_source
    assert "details.repair_command" in shared_source
    assert "Category:" in shared_source
    assert "window.TowerScoutConfigApi = {" in shared_source

    for path in (SETUP_WIZARD, SETTINGS):
        source = path.read_text(encoding="utf-8")
        assert "window.TowerScoutConfigApi.fetchJson" in source
        assert "window.TowerScoutConfigApi.providerFailureMessage" in source
        assert "window.TowerScoutConfigApi.saveFailureMessage" in source

    setup_source = SETUP_WIZARD.read_text(encoding="utf-8")
    setup_bundle = SETUP_WIZARD_BUNDLE.read_text(encoding="utf-8")
    assert "helper_available" in setup_source
    assert "getProviderValidationState" in setup_source
    assert "shouldShowProviderTlsRepair" in setup_source
    assert "getProviderTlsRepairViewModel" in setup_source
    assert "getProviderTlsRepairStartContract" in setup_source
    assert "refreshProviderTlsRepairHelperAvailability" in setup_source
    assert "requestProviderTlsRepairStatusAuthorization" in setup_source
    assert "pollProviderTlsRepairOperation" in setup_source
    assert "PROVIDER_TLS_REPAIR_ACTIVE_OPERATION_STORAGE_KEY" in setup_source
    assert "X-TowerScout-Operation-Authorization" in setup_source
    assert "rememberProviderTlsRepairOperationStatus" in setup_source
    assert "PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false" in setup_source
    assert "PROVIDER_TLS_REPAIR_BROWSER_MUTATION_ENABLED = false" in setup_bundle
    assert "PROVIDER_TLS_REPAIR_ALLOWED_START_BODY_FIELDS" in setup_source
    assert "operation_authorization" in setup_source
    assert "operation_active" in setup_source
    assert "TLS_REPAIR_CATEGORIES" in setup_source
    assert "repair_command" in setup_source
    assert "operation_authorization: authorization.operation_token" in setup_source
    assert "helper_base_url: helperBaseUrl" in setup_source
    assert "helper_available: helperAvailable" in setup_source
    assert "capability_enabled: capabilityEnabled" in setup_source
    assert "helper_capability_disabled" in setup_source
    assert "body: JSON.stringify({" in setup_source
    for rejected_field in (
        "engine",
        "gpu",
        "app_port",
        "restart_mode",
        "podman_provider",
        "script_path",
        "durable_token",
    ):
        assert rejected_field in setup_source
