"""
Current Flask route smoke and contract tests for TowerScout.

TASK-052 replaces stale route coverage that still targeted removed endpoints and
the pre-Sprint 05 detection contract.
"""

import json
import io
import shutil
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

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
