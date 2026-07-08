"""
Current Flask route smoke and contract tests for TowerScout.

TASK-052 replaces stale route coverage that still targeted removed endpoints and
the pre-Sprint 05 detection contract.
"""

import json
import io
import shutil
import uuid
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ts_errors import NetworkError
import towerscout
from towerscout import SESSION_ID_KEY, app


def _ensure_engine_catalog_loaded():
    if towerscout.engines:
        return

    towerscout.get_custom_models()
    if not towerscout.engines:
        towerscout.engines["newest"] = {
            "id": "newest",
            "name": "newest",
            "file": "newest.pt",
            "engine": None,
            "ts": 0,
        }
    if towerscout.engines and towerscout.engine_default is None:
        towerscout.engine_default = sorted(
            towerscout.engines.items(),
            key=lambda item: -item[1]["ts"],
        )[0][0]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    return app.test_client()


def test_index_route_renders_towerscout_shell(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"TowerScout" in response.data
    assert b"/license" in response.data
    assert b"/docs/quick-start.html" in response.data
    assert b"/docs/project-overview.html" in response.data
    assert b"/docs/user-guide.html" in response.data
    assert b"https://pubmed.ncbi.nlm.nih.gov/38906615/" in response.data
    assert b"sciencedirect.com/science/article/pii/S2589750024000943" not in response.data
    assert b"Documentation Placeholder" not in response.data
    assert b"Video Guide Placeholder" not in response.data


def test_license_route_exposes_release_notices(client):
    response = client.get("/license")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b"TowerScout Source/licenses" in response.data
    assert b"/license.txt" in response.data
    assert b"THIRD_PARTY_NOTICES.md" in response.data
    assert b"Ultralytics YOLOv5" in response.data
    assert b"AGPL-3.0" in response.data
    assert b"SOURCE.txt" in response.data
    assert b"SBOM.txt" in response.data
    assert b"release-manifest.v1.json" in response.data
    assert b"GNU AFFERO GENERAL PUBLIC LICENSE" in response.data


def test_license_text_route_exposes_plain_text_notices(client):
    response = client.get("/license.txt")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert b"THIRD_PARTY_NOTICES.md" in response.data
    assert b"Ultralytics YOLOv5" in response.data
    assert b"AGPL-3.0" in response.data
    assert b"SOURCE.txt" in response.data
    assert b"SBOM.txt" in response.data
    assert b"release-manifest.v1.json" in response.data
    assert b"GNU AFFERO GENERAL PUBLIC LICENSE" in response.data


def test_docs_routes_expose_package_local_docs(client):
    index_response = client.get("/docs/")
    quick_start_response = client.get("/docs/quick-start.html")
    overview_response = client.get("/docs/project-overview.html")
    docker_cpu_response = client.get("/docs/docker-cpu-user-guide.md")
    docker_gpu_response = client.get("/docs/docker-gpu-user-guide.md")
    podman_cpu_response = client.get("/docs/podman-cpu-user-guide.md")
    podman_gpu_response = client.get("/docs/podman-gpu-user-guide.md")
    user_guide_response = client.get("/docs/user-guide.html")
    package_guide_response = client.get("/docs/package-guide.md")
    css_response = client.get("/docs/towerscout-docs.css")

    assert index_response.status_code == 200
    assert index_response.mimetype == "text/html"
    assert b"TowerScout Quick Start" in index_response.data
    assert b"Before You Start" in index_response.data
    assert b"You do not need Git, Python, Conda, Node.js, VS Code" in index_response.data
    assert quick_start_response.status_code == 200
    assert b"Document Metadata" in quick_start_response.data
    assert b"Runtime scope" in quick_start_response.data

    assert overview_response.status_code == 200
    assert overview_response.mimetype == "text/html"
    assert b"Project Overview" in overview_response.data
    assert b"What Users Need Installed" in overview_response.data
    assert b"source-code checkout" in overview_response.data
    assert docker_cpu_response.status_code == 200
    assert b"TowerScout Docker CPU User Guide" in docker_cpu_response.data
    assert docker_gpu_response.status_code == 200
    assert b"TowerScout Docker GPU User Guide" in docker_gpu_response.data
    assert podman_cpu_response.status_code == 200
    assert b"TowerScout Podman CPU User Guide" in podman_cpu_response.data
    assert podman_gpu_response.status_code == 200
    assert b"TowerScout Podman GPU User Guide" in podman_gpu_response.data

    assert user_guide_response.status_code == 200
    assert user_guide_response.mimetype == "text/html"
    assert b"User Guide" in user_guide_response.data
    assert b"Before Using This Guide" in user_guide_response.data
    assert b"Docker Desktop is installed, approved, and running" in user_guide_response.data
    assert b"qualified Podman path" in user_guide_response.data
    assert package_guide_response.status_code == 200
    assert b"TowerScout Package Guide" in package_guide_response.data
    assert b"CPU Application Package is the primary path" in package_guide_response.data
    assert b"12.1 Application Package" in package_guide_response.data
    assert b"support-assigned paths" in package_guide_response.data

    assert css_response.status_code == 200
    assert "text/css" in css_response.content_type


def test_legacy_doc_paths_are_compatibility_stubs(client):
    quick_start_response = client.get("/docs/v1-rc1-quick-start.html")
    user_guide_response = client.get("/docs/towerscout-user-guide.html")
    package_guide_response = client.get("/docs/v1-rc1-package-guide.md")

    assert quick_start_response.status_code == 200
    assert b"Quick Start Has Moved" in quick_start_response.data
    assert b"/docs/quick-start.html" in quick_start_response.data
    assert user_guide_response.status_code == 200
    assert b"User Guide Has Moved" in user_guide_response.data
    assert b"/docs/user-guide.html" in user_guide_response.data
    assert package_guide_response.status_code == 200
    assert b"Package Guide Has Moved" in package_guide_response.data
    assert b"docs/package-guide.md" in package_guide_response.data


@pytest.mark.parametrize("path", sorted(towerscout.PUBLIC_DOC_FILES))
def test_each_public_doc_is_served(client, path):
    response = client.get(f"/docs/{path}")

    assert response.status_code == 200
    assert response.data


@pytest.mark.parametrize(
    "path",
    [
        "../README.md",
        "..%2FREADME.md",
        "codex-skills/README.md",
        "support/oci-quick-start.md",
        "project-overview.html/",
        "project-overview.html/../user-guide.html",
        "project-overview.html%5C..%5Cuser-guide.html",
    ],
)
def test_docs_route_rejects_non_public_docs(client, path):
    response = client.get(f"/docs/{path}")

    assert response.status_code == 404


def test_provider_and_key_routes_match_current_boot_contract(client, monkeypatch):
    monkeypatch.setenv("DEFAULT_MAP_PROVIDER", "azure")
    _ensure_engine_catalog_loaded()

    providers_response = client.get("/getproviders")
    google_key_response = client.get("/getgooglekey")
    azure_key_response = client.get("/getazurekey")
    engines_response = client.get("/getengines")

    assert providers_response.status_code == 200
    providers = json.loads(providers_response.data)
    assert [entry["id"] for entry in providers] == ["azure", "google"]

    assert google_key_response.status_code == 200
    assert google_key_response.get_json()["apiKey"] == "test_google_key_123"

    assert azure_key_response.status_code == 200
    assert azure_key_response.get_json()["subscriptionKey"] == "test_azure_key_456"

    assert engines_response.status_code == 200
    engines = json.loads(engines_response.data)
    assert len(engines) >= 1
    assert any(entry["id"] == "newest" for entry in engines)


def test_health_and_readiness_routes_match_container_contract(client):
    health_response = client.get("/api/health")

    assert health_response.status_code == 200
    assert health_response.get_json() == {
        "status": "ok",
        "service": "towerscout",
    }

    with patch.object(
        towerscout.ts_runtime,
        "build_readiness_payload",
        return_value={
            "state": "ready",
            "components": {},
            "version": {},
            "runtime": {},
            "recovery": [],
        },
    ):
        readiness_response = client.get("/api/readiness")

    assert readiness_response.status_code == 200
    assert readiness_response.get_json()["state"] == "ready"


def test_readiness_route_uses_503_for_fatal_state(client):
    with patch.object(
        towerscout.ts_runtime,
        "build_readiness_payload",
        return_value={
            "state": "fatal",
            "components": {},
            "version": {},
            "runtime": {},
            "recovery": ["Check container volume permissions."],
        },
    ):
        readiness_response = client.get("/api/readiness")

    assert readiness_response.status_code == 503
    assert readiness_response.get_json()["state"] == "fatal"


def test_startup_preload_switch_supports_asset_light_container_start(monkeypatch):
    monkeypatch.delenv(towerscout.STARTUP_PRELOAD_ENV_VAR, raising=False)
    assert towerscout.should_preload_startup_assets() is True

    monkeypatch.setenv(towerscout.STARTUP_PRELOAD_ENV_VAR, "0")
    assert towerscout.should_preload_startup_assets() is False

    monkeypatch.setenv(towerscout.STARTUP_PRELOAD_ENV_VAR, "false")
    assert towerscout.should_preload_startup_assets() is False

    monkeypatch.setenv(towerscout.STARTUP_PRELOAD_ENV_VAR, "1")
    assert towerscout.should_preload_startup_assets() is True


def test_model_catalog_handles_empty_asset_volume(monkeypatch):
    original_engines = dict(towerscout.engines)
    original_default = towerscout.engine_default
    empty_model_dir = (
        Path(".agent_work")
        / "pytest-temp"
        / f"task025-empty-models-{uuid.uuid4().hex}"
    )
    empty_model_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(towerscout, "YOLO_MODEL_DIR", empty_model_dir)
    towerscout.engines.clear()
    try:
        assert towerscout.load_model_catalog() is False
        assert towerscout.engine_default is None
        assert towerscout.engines == {}
    finally:
        towerscout.engines.clear()
        towerscout.engines.update(original_engines)
        towerscout.engine_default = original_default
        shutil.rmtree(empty_model_dir, ignore_errors=True)


def test_ensure_yolo_config_dir_creates_config_path(monkeypatch):
    config_dir = (
        Path(".agent_work")
        / "pytest-temp"
        / f"task025-yolo-config-{uuid.uuid4().hex}"
    )
    monkeypatch.setenv("YOLO_CONFIG_DIR", str(config_dir))

    try:
        assert towerscout.ensure_yolo_config_dir() == str(config_dir)
        assert config_dir.is_dir()
    finally:
        shutil.rmtree(config_dir, ignore_errors=True)


def test_config_status_and_session_reset_routes_match_current_contract(client):
    with client.session_transaction() as sess:
        sess["custom_key"] = "custom_value"
        sess["tmpdirname"] = "C:\\nonexistent\\towerscout-test"

    status_response = client.get("/api/config/status")
    performance_response = client.get("/api/config/performance")
    reset_response = client.post("/api/config/reset-session")

    assert status_response.status_code == 200
    status_payload = status_response.get_json()
    assert status_payload["needs_setup"] is False
    assert status_payload["google"]["configured"] is True
    assert status_payload["azure"]["configured"] is True
    assert status_payload["default_map_provider"] in {"azure", "google"}
    assert status_payload["google"]["preview"].startswith("test")
    assert status_payload["azure"]["preview"].startswith("test")

    assert performance_response.status_code == 200
    performance_payload = performance_response.get_json()
    assert set(performance_payload) == {
        "avg_tiles_per_second",
        "session_count",
        "last_detection_timestamp",
    }

    assert reset_response.status_code == 200
    assert reset_response.get_json()["success"] is True
    with client.session_transaction() as sess:
        assert sess["needs_setup"] is False
        assert "custom_key" not in sess


def test_validate_key_route_reports_actionable_network_failure(client):
    validation_error = NetworkError(
        "google validation request failed",
        user_message=(
            "TowerScout could not reach Google Maps from the local server. "
            "Check internet or proxy access, then try again. If this is a managed network, "
            "contact support without sending API keys or raw network traces."
        ),
        details={
            "provider": "google",
            "category": "provider_validation_network",
            "support_action": "Confirm local/container network access to the provider validation endpoints.",
        },
    )

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch.object(
        towerscout.ts_config,
        "validate_api_key",
        side_effect=validation_error,
    ):
        response = client.post(
            "/api/config/validate-key",
            json={"provider": "google", "key": "AIzaSyEXAMPLE1234567890abcdefghijklmno"},
        )

    assert response.status_code == 502
    payload = response.get_json()
    assert "TowerScout could not reach Google Maps" in payload["message"]
    assert "without sending API keys or raw network traces" in payload["message"]
    assert payload["details"]["provider"] == "google"
    assert payload["details"]["category"] == "provider_validation_network"
    assert "AIzaSyEXAMPLE1234567890abcdefghijklmno" not in json.dumps(payload)


def test_save_keys_allows_valid_default_provider_when_other_provider_needs_tls_repair(client):
    google_tls_error = NetworkError(
        "google validation request failed TLS verification",
        user_message="TowerScout could not verify the Google Maps TLS certificate.",
        details={
            "provider": "google",
            "category": "tls_ca_untrusted",
            "support_action": "Run scripts\\repair-provider-tls.cmd for Google Maps.",
            "repair_command": "scripts\\repair-provider-tls.cmd -Provider google",
        },
    )

    def validate_provider(provider, _key):
        if provider == "google":
            raise google_tls_error
        return {
            "valid": True,
            "provider": "azure",
            "category": "tls_ok",
            "message": "Azure Maps subscription key validated successfully.",
        }

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch.object(
        towerscout.ts_config,
        "validate_api_key",
        side_effect=validate_provider,
    ), patch.object(towerscout.ts_config, "update_env_file") as mock_update, patch.object(
        towerscout,
        "refresh_runtime_config",
        return_value=False,
    ):
        response = client.post(
            "/api/config/save-keys",
            json={
                "google_api_key": "google-test-key",
                "azure_maps_subscription_key": "azure-test-key",
                "default_map_provider": "azure",
            },
        )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["persisted_providers"] == ["azure"]
    assert payload["validation_results"]["google"]["details"]["category"] == "tls_ca_untrusted"
    assert payload["validation_results"]["azure"]["valid"] is True
    mock_update.assert_called_once()
    updates = mock_update.call_args.args[0]
    assert updates == {
        "DEFAULT_MAP_PROVIDER": "azure",
        "AZURE_MAPS_SUBSCRIPTION_KEY": "azure-test-key",
    }


def test_save_keys_rejects_invalid_selected_default_provider(client):
    google_tls_error = NetworkError(
        "google validation request failed TLS verification",
        user_message="TowerScout could not verify the Google Maps TLS certificate.",
        details={"provider": "google", "category": "tls_ca_untrusted"},
    )

    def validate_provider(provider, _key):
        if provider == "google":
            raise google_tls_error
        return {"valid": True, "provider": "azure", "category": "tls_ok"}

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch.object(
        towerscout.ts_config,
        "validate_api_key",
        side_effect=validate_provider,
    ), patch.object(towerscout.ts_config, "update_env_file") as mock_update:
        response = client.post(
            "/api/config/save-keys",
            json={
                "google_api_key": "google-test-key",
                "azure_maps_subscription_key": "azure-test-key",
                "default_map_provider": "google",
            },
        )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert "default_map_provider" in payload["message"]
    assert payload["validation_results"]["google"]["details"]["category"] == "tls_ca_untrusted"
    assert payload["validation_results"]["azure"]["valid"] is True
    mock_update.assert_not_called()


def test_save_keys_derives_default_provider_when_omitted_and_one_provider_validates(client, monkeypatch):
    monkeypatch.setenv("DEFAULT_MAP_PROVIDER", "azure")
    monkeypatch.delenv("AZURE_MAPS_SUBSCRIPTION_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    def validate_provider(provider, _key):
        if provider == "google":
            return {"valid": True, "provider": "google", "category": "tls_ok"}
        raise AssertionError(f"Unexpected provider validation: {provider}")

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch.object(
        towerscout.ts_config,
        "validate_api_key",
        side_effect=validate_provider,
    ), patch.object(towerscout.ts_config, "update_env_file") as mock_update, patch.object(
        towerscout,
        "refresh_runtime_config",
        return_value=False,
    ):
        response = client.post(
            "/api/config/save-keys",
            json={
                "google_api_key": "google-test-key",
            },
        )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["default_map_provider"] == "google"
    assert payload["default_map_provider_derived"] is True
    assert payload["persisted_providers"] == ["google"]
    mock_update.assert_called_once()
    updates = mock_update.call_args.args[0]
    assert updates == {
        "DEFAULT_MAP_PROVIDER": "google",
        "GOOGLE_API_KEY": "google-test-key",
    }


def test_provider_tls_status_route_uses_keyless_provider_probe(client):
    with patch.object(
        towerscout.ts_config,
        "check_provider_tls_status",
        return_value={"provider": "google", "reachable": True, "category": "tls_ok"},
    ) as mock_status:
        response = client.get("/api/config/tls-status?provider=google")

    assert response.status_code == 200
    assert response.get_json()["category"] == "tls_ok"
    mock_status.assert_called_once_with("google")


def test_key_routes_do_not_log_key_previews(client, monkeypatch):
    google_key = "AIzaSyEXAMPLE1234567890abcdefghijklmno"
    azure_key = "azure-key-example-value-that-should-not-be-logged"
    monkeypatch.setattr(towerscout, "google_api_key", google_key)
    monkeypatch.setattr(towerscout, "azure_api_key", azure_key)

    with patch.object(towerscout.api_logger, "info") as mock_info:
        google_response = client.get("/getgooglekey")
        azure_response = client.get("/getazurekey")

    assert google_response.status_code == 200
    assert azure_response.status_code == 200
    logged_args = " ".join(str(call.args) for call in mock_info.call_args_list)
    assert google_key not in logged_args
    assert azure_key not in logged_args
    assert "starts with" not in logged_args


def test_detection_progress_defaults_to_idle(client):
    response = client.get("/api/detection/progress")

    assert response.status_code == 200
    assert "no-store" in response.headers["Cache-Control"]
    assert response.get_json() == {
        "status": "idle",
        "phase": "idle",
        "title": "No active detection",
        "detail": "No tower-detection run is currently active.",
        "counts": {},
        "cancel_requested": False,
        "tile_count": 0,
    }


def test_abort_route_marks_current_run_cancel_requested(client):
    session_id = "session-test-abort"
    run_token = f"{session_id}:run-token"

    with client.session_transaction() as sess:
        sess[SESSION_ID_KEY] = session_id

    towerscout.progress_tracker.start(
        session_id,
        run_token,
        provider="google",
        engine="newest",
        phase="running_model",
        title="Running model detection",
        detail="Processing tiles...",
        tile_count=4,
    )

    try:
        with patch.object(towerscout.exit_events, "signal") as mock_signal:
            response = client.post("/abort")

        assert response.status_code == 200
        assert response.data == b"ok"
        mock_signal.assert_called_once_with(run_token)

        progress_response = client.get("/api/detection/progress")
        assert progress_response.status_code == 200
        assert progress_response.get_json()["status"] == "cancel_requested"
    finally:
        towerscout.progress_tracker.clear(session_id, run_token=run_token)


def test_getobjects_post_invalid_self_intersecting_polygon(client):
    response = client.post(
        "/getobjects",
        data={
            "bounds": "37.7,-122.5,37.8,-122.4",
            "engine": "yolo",
            "provider": "google",
            "polygons": json.dumps(
                [[
                    [-122.5, 37.7],
                    [-122.4, 37.8],
                    [-122.5, 37.8],
                    [-122.4, 37.7],
                    [-122.5, 37.7],
                ]]
            ),
            "estimate": "yes",
        },
    )

    assert response.status_code == 400
    payload = response.get_json()
    message = payload.get("error") or payload.get("message", "")
    assert "self-intersection" in message.lower()


def test_estimate_detection_tiles_accepts_tile_stats_return_value(client):
    with patch(
        "towerscout._parse_detection_request",
        return_value={
            "bounds": "37.7,-122.5,37.8,-122.4",
            "engine": "newest",
            "provider": "azure",
            "polygons": [[[-122.5, 37.7], [-122.4, 37.7], [-122.4, 37.8], [-122.5, 37.8]]],
            "estimate": "yes",
        },
    ), patch("towerscout._create_map_provider", return_value=Mock()), patch(
        "towerscout._build_tiles_for_request",
        return_value=(
            [{"id": 0}, {"id": 1}],
            1,
            2,
            10.0,
            640,
            640,
            {
                "candidate_tiles": 2,
                "viewport_tiles": 2,
                "retained_tiles": 2,
            },
        ),
    ):
        response = client.post(
            "/api/detection/estimate",
            data={
                "bounds": "37.7,-122.5,37.8,-122.4",
                "engine": "newest",
                "provider": "azure",
                "polygons": "[]",
                "estimate": "yes",
            },
        )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["tileCount"] == 2
    assert "estimatedSeconds" in payload


def test_uploadmodel_saves_valid_model_into_runtime_directory(client, monkeypatch):
    model_dir = Path("C:/virtual-models")
    validated_file = Mock()
    validated_file.filename = "custom-model.pt"
    monkeypatch.setattr(towerscout, "YOLO_MODEL_DIR", model_dir)
    monkeypatch.setattr(towerscout, "EN_MODEL_DIR", model_dir)
    monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", True)

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch.object(
        towerscout.TowerScoutValidator,
        "validate_model_file",
        return_value=validated_file,
    ), patch("towerscout.add_model") as mock_add_model:
        response = client.post(
            "/uploadmodel",
            data={"model": (io.BytesIO(b"fake-model-weights"), "upload.pt")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert response.data == b"ok"
    validated_file.save.assert_called_once_with(str(model_dir / "custom-model.pt"))
    mock_add_model.assert_called_once_with("custom-model.pt")


def test_uploadmodel_disabled_by_default_blocks_model_upload(client, monkeypatch):
    monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", False)

    response = client.post(
        "/uploadmodel",
        data={"model": (io.BytesIO(b"fake-model-weights"), "upload.pt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 403
    assert b"Model upload is disabled" in response.data


def test_getdataset_exports_archive_with_current_session_contract(client):
    session_tmpdir = "session-temp"
    with client.session_transaction() as sess:
        sess["tmpdirname"] = session_tmpdir
        sess["detections"] = [{"index": 0, "detections": ["det-0"]}]
        sess["metadata"] = []

    with patch("towerscout.write_labels", return_value=[f"{session_tmpdir}/tile0.jpg"]) as mock_write_labels, patch(
        "towerscout.write_contents_file"
    ) as mock_write_contents, patch("towerscout.zipdir") as mock_zipdir, patch(
        "towerscout.send_from_directory",
        side_effect=lambda directory, filename: app.response_class(
            response=json.dumps({"directory": directory, "filename": filename}),
            status=200,
            mimetype="application/json",
        ),
    ):
        response = client.post(
            "/getdataset",
            data={
                "include": json.dumps([{"tile": 0, "detection": 0}]),
                "additions": json.dumps([]),
            },
        )

    assert response.status_code == 200
    assert response.get_json()["filename"] == "dataset.zip"
    mock_write_labels.assert_called_once()
    mock_write_contents.assert_called_once()
    mock_zipdir.assert_called_once_with(session_tmpdir, [f"{session_tmpdir}/tile0.jpg"])


def test_uploaddataset_restores_contents_into_session(client):
    restore_dir = "restored-session"
    stale_tmpdir = "stale-session"
    restored_tiles = [{"index": 0, "filename": "restored-tile-0.jpg"}]
    restored_results = [{"id": "restored-1", "lat": 1.0, "lng": 2.0}]
    restored_metadata = {"provider": "google"}
    contents_json = json.dumps(
        [
            [{"index": 0, "filename": "legacy-stem/tile-0.jpg"}],
            restored_results,
            restored_metadata,
        ]
    )
    validated_file = Mock()
    validated_file.filename = "dataset.zip"
    written_files = {}

    class FakeZipFile:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def namelist(self):
            return ["legacy-stem/train/images/tile-0.jpg", "contents.txt"]

        def open(self, name):
            payload = contents_json if name == "contents.txt" else "fake-image-bytes"
            return io.BytesIO(payload.encode("utf-8"))

    class RecordingBinaryFile(io.BytesIO):
        def __init__(self, path):
            super().__init__()
            self._path = path

        def __exit__(self, exc_type, exc, tb):
            written_files[self._path] = self.getvalue()
            self.close()
            return False

    def fake_open(path, mode="r", *args, **kwargs):
        normalized = str(path).replace("\\", "/")
        if "w" in mode:
            return RecordingBinaryFile(normalized)
        if normalized.endswith("/contents.txt") or normalized.endswith("contents.txt"):
            return io.StringIO(contents_json)
        raise FileNotFoundError(path)

    with client.session_transaction() as sess:
        sess["tmpdirname"] = stale_tmpdir

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch.object(
        towerscout.TowerScoutValidator,
        "validate_dataset_file",
        return_value=validated_file,
    ), patch("towerscout._make_session_tmpdir", return_value=restore_dir), patch(
        "towerscout.adapt_tiles",
        return_value=restored_tiles,
    ), patch(
        "towerscout.rmtree"
    ), patch(
        "towerscout.zipfile.ZipFile",
        FakeZipFile,
    ), patch("towerscout.os.path.exists", side_effect=lambda path: str(path).endswith("contents.txt")), patch(
        "builtins.open",
        side_effect=fake_open,
    ):
        response = client.post(
            "/uploaddataset",
            data={"dataset": (io.BytesIO(b"placeholder"), "upload.zip")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert response.get_json() == restored_results
    saved_archive_path = validated_file.save.call_args.args[0].replace("\\", "/")
    assert saved_archive_path == f"{restore_dir}/dataset.zip"
    assert any(path.endswith("tile-0.jpg") for path in written_files)
    with client.session_transaction() as sess:
        assert sess["tmpdirname"] == restore_dir
        assert sess["detections"] == restored_tiles
        assert json.loads(sess["results"]) == restored_results
        assert sess["metadata"] == restored_metadata


def _dataset_zip_bytes(entries):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zipf:
        for name, payload in entries.items():
            zipf.writestr(name, payload)
    archive.seek(0)
    return archive


@pytest.mark.parametrize(
    "unsafe_member",
    [
        "../contents.txt",
        "/absolute/evil.jpg",
        "C:/evil.jpg",
        "legacy-stem/train/images/../evil.jpg",
        "legacy-stem/train/images/./evil.jpg",
    ],
)
def test_uploaddataset_rejects_unsafe_zip_member_paths(client, tmp_path, unsafe_member):
    restore_dir = tmp_path / "restore-session"
    restore_dir.mkdir()
    outside_target = tmp_path / "evil.jpg"
    contents_json = json.dumps(
        [
            [{"index": 0, "filename": "legacy-stem/tile-0.jpg"}],
            [{"id": "restored-1", "lat": 1.0, "lng": 2.0}],
            {"provider": "google"},
        ]
    )
    archive = _dataset_zip_bytes(
        {
            "legacy-stem/train/images/tile-0.jpg": "fake-image-bytes",
            "contents.txt": contents_json,
            unsafe_member: "unsafe",
        }
    )

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
        "towerscout._make_session_tmpdir",
        return_value=str(restore_dir),
    ):
        response = client.post(
            "/uploaddataset",
            data={"dataset": (archive, "dataset.zip")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid dataset ZIP path"}
    assert not outside_target.exists()


def test_dataset_zip_member_validation_rejects_backslash_paths():
    with pytest.raises(towerscout.UnsafeDatasetArchiveError):
        towerscout._validate_dataset_zip_member_name(r"legacy-stem\train\images\evil.jpg")


def test_uploaddataset_restores_valid_export_zip_without_path_escape(client, tmp_path):
    restore_dir = tmp_path / "restore-session"
    restore_dir.mkdir()
    restored_results = [{"id": "restored-1", "lat": 1.0, "lng": 2.0}]
    restored_metadata = {"provider": "google"}
    contents_json = json.dumps(
        [
            [{"index": 0, "filename": "legacy-stem/tile-0.jpg"}],
            restored_results,
            restored_metadata,
        ]
    )
    archive = _dataset_zip_bytes(
        {
            "README.txt": "dataset readme",
            "legacy-stem/train/images/tile-0.jpg": "fake-image-bytes",
            "legacy-stem/train/labels/tile-0.txt": "0 0.1 0.2 0.3 0.4",
            "contents.txt": contents_json,
        }
    )

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
        "towerscout._make_session_tmpdir",
        return_value=str(restore_dir),
    ):
        response = client.post(
            "/uploaddataset",
            data={"dataset": (archive, "dataset.zip")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert response.get_json() == restored_results
    assert (restore_dir / "tile-0.jpg").read_text(encoding="utf-8") == "fake-image-bytes"
    assert (restore_dir / "tile-0.txt").read_text(encoding="utf-8") == "0 0.1 0.2 0.3 0.4"
    assert (restore_dir / "contents.txt").read_text(encoding="utf-8") == contents_json
    with client.session_transaction() as sess:
        assert sess["tmpdirname"] == str(restore_dir)
        assert json.loads(sess["results"]) == restored_results
        assert sess["metadata"] == restored_metadata
