import asyncio
from unittest.mock import Mock

import ts_config
import ts_maps
from ts_errors import NetworkError
from ts_provider_http import (
    INVALID_PROVIDER_KEY,
    TLS_OK,
    classify_provider_response,
    provider_repair_command,
    redact_provider_url,
)


def test_redact_provider_url_hides_google_and_azure_key_values():
    redacted_google = redact_provider_url(
        "https://maps.googleapis.com/maps/api/geocode/json?address=test&key=AIzaSySecret"
    )
    redacted_azure = redact_provider_url(
        "https://atlas.microsoft.com/map/tile?subscription-key=azure-secret&zoom=19"
    )

    assert "AIzaSySecret" not in redacted_google
    assert "key=%5BREDACTED%5D" in redacted_google
    assert "azure-secret" not in redacted_azure
    assert "subscription-key=%5BREDACTED%5D" in redacted_azure


def test_classify_google_auth_failure_as_tls_ok_for_keyless_probe():
    response = Mock(status_code=200)
    body_json = {"status": "REQUEST_DENIED", "error_message": "API key is missing."}

    assert classify_provider_response(
        "google",
        response,
        body_json=body_json,
        auth_failure_is_tls_ok=True,
    ) == TLS_OK
    assert classify_provider_response("google", response, body_json=body_json) == INVALID_PROVIDER_KEY


def test_classify_azure_bad_request_as_tls_ok_for_keyless_probe():
    response = Mock(status_code=400)

    assert classify_provider_response(
        "azure",
        response,
        auth_failure_is_tls_ok=True,
    ) == TLS_OK


def test_provider_repair_command_uses_runtime_engine_and_gpu(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_CONTAINER_ENGINE", "podman")
    monkeypatch.setenv("TOWERSCOUT_GPU_MODE", "on")

    assert provider_repair_command("azure") == (
        ".\\scripts\\repair-provider-tls.cmd -Provider azure -Engine podman -Gpu on"
    )


def test_provider_repair_command_falls_back_to_safe_defaults(monkeypatch):
    monkeypatch.delenv("TOWERSCOUT_CONTAINER_ENGINE", raising=False)
    monkeypatch.delenv("TOWERSCOUT_GPU_MODE", raising=False)

    assert provider_repair_command("google") == (
        ".\\scripts\\repair-provider-tls.cmd -Provider google -Engine auto -Gpu off"
    )


def test_provider_repair_command_rejects_invalid_runtime_defaults(monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_CONTAINER_ENGINE", "cmd.exe")
    monkeypatch.setenv("TOWERSCOUT_GPU_MODE", "cuda && whoami")

    assert provider_repair_command("google") == (
        ".\\scripts\\repair-provider-tls.cmd -Provider google -Engine auto -Gpu off"
    )


def test_check_provider_tls_status_uses_keyless_google_probe(monkeypatch):
    response = Mock(status_code=200)
    response.json.return_value = {"status": "REQUEST_DENIED", "error_message": "API key is missing."}
    captured = {}

    def fake_get(provider, url, *, params, timeout, purpose):
        captured["provider"] = provider
        captured["url"] = url
        captured["params"] = params
        return response

    monkeypatch.setattr(ts_config, "provider_get", fake_get)

    result = ts_config.check_provider_tls_status("google")

    assert result["reachable"] is True
    assert result["category"] == TLS_OK
    assert captured["provider"] == "google"
    assert "key" not in captured["params"]


def test_check_provider_tls_status_treats_keyless_azure_400_as_reachable(monkeypatch):
    response = Mock(status_code=400)
    captured = {}

    def fake_get(provider, url, *, params, timeout, purpose):
        captured["provider"] = provider
        captured["url"] = url
        captured["params"] = params
        return response

    monkeypatch.setattr(ts_config, "provider_get", fake_get)

    result = ts_config.check_provider_tls_status("azure")

    assert result["reachable"] is True
    assert result["category"] == TLS_OK
    assert result["status_code"] == 400
    assert captured["provider"] == "azure"
    assert "subscription-key" not in captured["params"]


def test_check_provider_tls_status_preserves_tls_repair_metadata(monkeypatch):
    def fake_get(provider, url, *, params, timeout, purpose):
        raise NetworkError(
            "tls failed",
            details={
                "provider": provider,
                "category": "tls_ca_untrusted",
                "repairable": True,
                "helper_available": False,
                "repair_command": ".\\scripts\\repair-provider-tls.cmd -Provider google -Engine docker -Gpu off",
            },
            user_message="TLS validation failed.",
        )

    monkeypatch.setattr(ts_config, "provider_get", fake_get)

    result = ts_config.check_provider_tls_status("google")

    assert result["reachable"] is False
    assert result["category"] == "tls_ca_untrusted"
    assert result["repairable"] is True
    assert result["helper_available"] is False
    assert result["details"]["repair_command"].startswith(".\\scripts\\repair-provider-tls.cmd")


def test_ts_maps_build_connector_uses_shared_provider_ssl_context(monkeypatch):
    captured = {}

    def fake_tcp_connector(**kwargs):
        captured.update(kwargs)
        return "connector"

    monkeypatch.setattr(ts_maps, "create_provider_ssl_context", lambda provider: f"context:{provider}")
    monkeypatch.setattr(ts_maps.aiohttp, "TCPConnector", fake_tcp_connector)

    connector = ts_maps._build_connector("google")

    assert connector == "connector"
    assert captured["ssl"] == "context:google"
    assert captured["limit"] == 50
    assert captured["limit_per_host"] == 16


def test_ts_maps_tile_records_store_redacted_provider_url(monkeypatch, tmp_path):
    captured = {}

    class DemoMap(ts_maps.Map):
        def get_url(self, tile):
            return "https://maps.googleapis.com/maps/api/staticmap?center=0,0&key=AIzaSySecret"

    async def fake_gather_urls(urls, directory, filename, metadata):
        captured["urls"] = urls
        captured["directory"] = directory
        captured["filename"] = filename
        captured["metadata"] = metadata

    monkeypatch.setattr(ts_maps, "gather_urls", fake_gather_urls)
    loop = asyncio.new_event_loop()
    tile = {"id": 7}
    try:
        DemoMap().get_sat_maps([tile], loop, str(tmp_path), "tile-")
    finally:
        loop.close()

    assert captured["urls"] == [tile["url"]]
    assert "AIzaSySecret" in tile["url"]
    assert "AIzaSySecret" not in tile["provider_url_redacted"]
    assert "key=%5BREDACTED%5D" in tile["provider_url_redacted"]
