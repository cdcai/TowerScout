import pytest

import ts_host_helper


SESSION_ENV = {
    "TOWERSCOUT_HOST_HELPER_ENABLED": "1",
    "TOWERSCOUT_HOST_HELPER_PORT": "50123",
    "TOWERSCOUT_HOST_HELPER_SESSION_ID": "a" * 32,
    "TOWERSCOUT_HOST_HELPER_SESSION_KEY": "A" * 43,
    "TOWERSCOUT_CONTAINER_ENGINE": "docker",
    "TOWERSCOUT_GPU_MODE": "off",
    "TOWERSCOUT_HOST_PORT": "5005",
}


def test_host_helper_bridge_requires_complete_explicit_configuration():
    assert ts_host_helper.load_host_helper_bridge_config({}) is None
    assert ts_host_helper.load_host_helper_bridge_config(
        {
            **SESSION_ENV,
            "TOWERSCOUT_HOST_HELPER_ENABLED": "0",
        }
    ) is None
    assert ts_host_helper.load_host_helper_bridge_config(
        {
            **SESSION_ENV,
            "TOWERSCOUT_HOST_HELPER_PORT": "0",
        }
    ) is None
    assert ts_host_helper.load_host_helper_bridge_config(
        {
            **SESSION_ENV,
            "TOWERSCOUT_HOST_HELPER_SESSION_KEY": "short",
        }
    ) is None


def test_repairable_provider_bridge_issues_scoped_short_lived_authorization(
    monkeypatch,
):
    monkeypatch.setattr(
        ts_host_helper,
        "PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED",
        True,
    )
    bridge = ts_host_helper.build_provider_tls_repair_bridge(
        "google",
        "tls_ca_untrusted",
        environment=SESSION_ENV,
        now=1_800_000_000,
        include_start_authorization=True,
    )

    assert bridge["base_url"] == "http://127.0.0.1:50123"
    assert bridge["probe"]["path"] == "/health"
    assert bridge["probe"]["scope"] == "helper_probe"
    assert bridge["provider_tls_repair_capability"] is True
    assert bridge["expected_runtime"] == {
        "engine": "docker",
        "gpu": "off",
        "app_port": 5005,
    }
    operation = bridge["operation_authorization"]
    assert operation["operation_type"] == "provider_tls_repair"
    assert operation["operation_token"].startswith("v1.")
    assert "helper_token" not in str(bridge).lower()
    assert "durable" not in str(bridge).lower()

    config = ts_host_helper.load_host_helper_bridge_config(SESSION_ENV)
    payload = ts_host_helper.validate_browser_authorization(
        config,
        operation["operation_token"],
        expected_scope="provider_tls_repair",
        expected_provider="google",
        now=1_800_000_001,
    )
    assert payload["session_id"] == "a" * 32
    assert payload["operation_id"] == ""


def test_bridge_expected_runtime_defaults_to_standard_host_port():
    environment = dict(SESSION_ENV)
    environment.pop("TOWERSCOUT_HOST_PORT")

    bridge = ts_host_helper.build_provider_tls_repair_bridge(
        "google",
        "tls_ca_untrusted",
        environment=environment,
        now=1_800_000_000,
    )

    assert bridge["expected_runtime"]["app_port"] == 5000


def test_bridge_is_not_issued_for_non_repairable_failures():
    assert ts_host_helper.build_provider_tls_repair_bridge(
        "google",
        "invalid_provider_key",
        environment=SESSION_ENV,
    ) is None


def test_disabled_capability_never_issues_start_or_status_authorization():
    bridge = ts_host_helper.build_provider_tls_repair_bridge(
        "google",
        "tls_ca_untrusted",
        environment=SESSION_ENV,
    )

    assert bridge["provider_tls_repair_capability"] is False
    assert "operation_authorization" not in bridge
    assert (
        ts_host_helper.build_operation_status_bridge(
            "google",
            "b" * 32,
            environment=SESSION_ENV,
        )
        is None
    )
    assert ts_host_helper.build_provider_tls_repair_bridge(
        "",
        "tls_ca_untrusted",
        environment=SESSION_ENV,
    ) is None


def test_probe_only_bridge_does_not_issue_start_authorization(monkeypatch):
    monkeypatch.setattr(
        ts_host_helper,
        "PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED",
        True,
    )

    bridge = ts_host_helper.build_provider_tls_repair_bridge(
        "google",
        "tls_ca_untrusted",
        environment=SESSION_ENV,
        now=1_800_000_000,
    )

    assert bridge["provider_tls_repair_capability"] is True
    assert "operation_authorization" not in bridge


def test_expired_and_cross_provider_authorizations_are_rejected(monkeypatch):
    monkeypatch.setattr(
        ts_host_helper,
        "PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED",
        True,
    )
    bridge = ts_host_helper.build_provider_tls_repair_bridge(
        "azure",
        "tls_bundle_missing",
        environment=SESSION_ENV,
        now=1_800_000_000,
        include_start_authorization=True,
    )
    config = ts_host_helper.load_host_helper_bridge_config(SESSION_ENV)
    token = bridge["operation_authorization"]["operation_token"]

    with pytest.raises(ValueError, match="authorization_provider"):
        ts_host_helper.validate_browser_authorization(
            config,
            token,
            expected_scope="provider_tls_repair",
            expected_provider="google",
            now=1_800_000_001,
        )
    with pytest.raises(ValueError, match="authorization_expired"):
        ts_host_helper.validate_browser_authorization(
            config,
            token,
            expected_scope="provider_tls_repair",
            expected_provider="azure",
            now=1_800_000_420,
        )


def test_authorization_clock_skew_is_bounded(monkeypatch):
    monkeypatch.setattr(
        ts_host_helper,
        "PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED",
        True,
    )
    bridge = ts_host_helper.build_provider_tls_repair_bridge(
        "google",
        "tls_ca_untrusted",
        environment=SESSION_ENV,
        now=1_800_000_000,
        include_start_authorization=True,
    )
    config = ts_host_helper.load_host_helper_bridge_config(SESSION_ENV)
    token = bridge["operation_authorization"]["operation_token"]

    ts_host_helper.validate_browser_authorization(
        config,
        token,
        expected_scope="provider_tls_repair",
        expected_provider="google",
        now=1_800_000_419,
    )
    with pytest.raises(ValueError, match="authorization_expired"):
        ts_host_helper.validate_browser_authorization(
            config,
            token,
            expected_scope="provider_tls_repair",
            expected_provider="google",
            now=1_800_000_420,
        )


def test_status_authorization_is_bound_to_provider_and_operation(monkeypatch):
    monkeypatch.setattr(
        ts_host_helper,
        "PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED",
        True,
    )
    operation_id = "b" * 32
    bridge = ts_host_helper.build_operation_status_bridge(
        "google",
        operation_id,
        environment=SESSION_ENV,
        now=1_800_000_000,
    )
    config = ts_host_helper.load_host_helper_bridge_config(SESSION_ENV)
    token = bridge["status_authorization"]["authorization"]

    payload = ts_host_helper.validate_browser_authorization(
        config,
        token,
        expected_scope="operation_status",
        expected_provider="google",
        expected_operation_id=operation_id,
        now=1_800_000_001,
    )
    assert payload["operation_id"] == operation_id
    with pytest.raises(ValueError, match="authorization_operation"):
        ts_host_helper.validate_browser_authorization(
            config,
            token,
            expected_scope="operation_status",
            expected_provider="google",
            expected_operation_id="c" * 32,
            now=1_800_000_001,
        )


def test_payload_enrichment_keeps_availability_probe_driven_and_manual_fallback():
    payload = {
        "message": "TLS validation failed.",
        "details": {
            "provider": "azure",
            "category": "tls_ca_untrusted",
            "repairable": True,
            "helper_available": False,
            "repair_command": (
                ".\\scripts\\repair-provider-tls.cmd "
                "-Provider azure -Engine docker -Gpu off"
            ),
        },
    }

    enriched = ts_host_helper.enrich_provider_tls_repair_payload(
        payload,
        environment=SESSION_ENV,
        now=1_800_000_000,
    )

    assert enriched["helper_available"] is False
    assert enriched["details"]["helper_available"] is False
    assert enriched["details"]["repair_command"] == payload["details"]["repair_command"]
    assert enriched["details"]["helper_bridge"]["base_url"] == "http://127.0.0.1:50123"


def test_payload_enrichment_preserves_unrelated_network_errors():
    payload = {
        "message": "Tile request failed.",
        "details": {
            "category": "provider_network_blocked",
            "provider": "google",
        },
    }

    enriched = ts_host_helper.enrich_provider_tls_repair_payload(
        payload,
        environment=SESSION_ENV,
        now=1_800_000_000,
    )

    assert enriched == payload
