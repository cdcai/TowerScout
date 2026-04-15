"""
Current integration smoke baseline for TowerScout.

TASK-052 replaces the quarantined legacy end-to-end harness with a smoke suite
that matches the current Flask route surface and the post-TASK-057 local YOLO
runtime contract.
"""

import gc
import json
import shutil
import uuid
from unittest.mock import Mock, patch

import pytest
import torch

import towerscout
from towerscout import SESSION_ID_KEY, app
from ts_errors import MapProviderError


def _ensure_engine_catalog_loaded():
    if towerscout.engines:
        return

    towerscout.get_custom_models()
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


def test_current_app_boot_and_core_route_surface(client, monkeypatch):
    monkeypatch.setenv("DEFAULT_MAP_PROVIDER", "azure")
    _ensure_engine_catalog_loaded()

    root_response = client.get("/")
    providers_response = client.get("/getproviders")
    engines_response = client.get("/getengines")
    google_key_response = client.get("/getgooglekey")
    azure_key_response = client.get("/getazurekey")
    config_status_response = client.get("/api/config/status")
    performance_response = client.get("/api/config/performance")
    progress_response = client.get("/api/detection/progress")

    assert root_response.status_code == 200
    assert b"TowerScout" in root_response.data

    assert providers_response.status_code == 200
    providers = json.loads(providers_response.data)
    assert [entry["id"] for entry in providers] == ["azure", "google"]

    assert engines_response.status_code == 200
    engines = json.loads(engines_response.data)
    assert len(engines) >= 1
    assert any(entry["id"] == "newest" for entry in engines)

    assert google_key_response.status_code == 200
    assert google_key_response.get_json()["apiKey"] == "test_google_key_123"

    assert azure_key_response.status_code == 200
    assert azure_key_response.get_json()["subscriptionKey"] == "test_azure_key_456"

    assert config_status_response.status_code == 200
    config_payload = config_status_response.get_json()
    assert config_payload["needs_setup"] is False
    assert config_payload["google"]["configured"] is True
    assert config_payload["azure"]["configured"] is True

    assert performance_response.status_code == 200
    performance_payload = performance_response.get_json()
    assert set(performance_payload) == {
        "avg_tiles_per_second",
        "session_count",
        "last_detection_timestamp",
    }

    assert progress_response.status_code == 200
    assert progress_response.get_json()["status"] == "idle"


def test_detection_smoke_loads_local_yolo_runtime_before_imagery_failure(client):
    _ensure_engine_catalog_loaded()

    if not towerscout.engines:
        pytest.skip("No YOLO engine metadata is available for the bounded smoke path.")

    engine_id, engine_meta = next(iter(towerscout.engines.items()))
    model_path = towerscout.YOLO_MODEL_DIR / engine_meta["file"]
    if not model_path.exists():
        pytest.skip(
            f"Bounded detection-readiness smoke requires model weights at {model_path}."
        )

    fake_map_provider = Mock()
    fake_map_provider.get_sat_maps.side_effect = MapProviderError(
        "Failed to download required imagery for 1 of 1 tile(s).",
        provider="google",
        details={
            "successful_tile_count": 0,
            "failed_tile_count": 1,
            "failed_tile_ids": [0],
        },
    )

    original_engine = engine_meta["engine"]
    engine_meta["engine"] = None
    session_tmpdir = towerscout.get_temp_dir() / "session" / f"task052-smoke-{uuid.uuid4().hex}"
    session_tmpdir.mkdir(parents=True, exist_ok=True)

    try:
        with patch("torch.load", new=torch.serialization.load), patch(
            "towerscout._parse_detection_request",
            return_value={
                "bounds": "37.7,-122.5,37.8,-122.4",
                "engine": engine_id,
                "provider": "google",
                "polygons": [],
                "estimate": None,
            },
        ), patch("towerscout._create_map_provider", return_value=fake_map_provider), patch(
            "towerscout._build_tiles_for_request",
            return_value=(
                [{"id": 0}],
                1,
                1,
                10.0,
                640,
                640,
                {
                    "candidate_tiles": 1,
                    "viewport_tiles": 1,
                    "retained_tiles": 1,
                },
            ),
        ), patch("towerscout._make_session_tmpdir", return_value=str(session_tmpdir)):
            response = client.post("/getobjects", data={"bounds": "ignored"})

        assert response.status_code == 502
        payload = response.get_json()
        assert "Imagery download failed" in payload["error"]
        assert engine_meta["engine"] is not None

        progress_payload = client.get("/api/detection/progress").get_json()
        assert progress_payload["title"] == "Imagery download failed"
        assert progress_payload["counts"]["imagery_tiles_total"] == 1
        assert progress_payload["counts"]["imagery_tiles_downloaded"] == 0
        assert progress_payload["counts"]["imagery_tiles_failed"] == 1
    finally:
        with client.session_transaction() as sess:
            session_id = sess.get(SESSION_ID_KEY)

        if session_id:
            towerscout.progress_tracker.clear(session_id)

        engine_meta["engine"] = original_engine
        shutil.rmtree(session_tmpdir, ignore_errors=True)
        gc.collect()
