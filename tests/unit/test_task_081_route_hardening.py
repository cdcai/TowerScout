"""Task-081 Flask route hardening coverage."""

import io
import json
import shutil
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PIL import Image

import towerscout
from towerscout import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    return app.test_client()


def _png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), color="white").save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def test_debug_azure_maps_route_is_not_exposed_by_default(client):
    response = client.get("/debug-azure-maps")

    assert response.status_code == 404


def test_custom_image_upload_uses_sanitized_filename(monkeypatch):
    app.config["TESTING"] = True
    client = app.test_client()
    upload_dir = Path(".agent_work") / "pytest-temp" / f"task081-upload-{uuid.uuid4().hex}"
    upload_dir.mkdir(parents=True)
    fake_detector = Mock()
    fake_detector.detect.return_value = [[]]

    monkeypatch.setattr(towerscout, "UPLOAD_DIR", upload_dir)

    try:
        with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
            "towerscout.get_engine",
            return_value=fake_detector,
        ):
            response = client.post(
                "/getobjectscustom",
                data={
                    "engine": "yolo",
                    "image": (_png_bytes(), "../../unsafe image.png"),
                },
                content_type="multipart/form-data",
            )

        assert response.status_code == 200
        assert (upload_dir / "unsafe_image.png").is_file()
        assert not (upload_dir / ".." / ".." / "unsafe image.png").exists()
        fake_detector.detect.assert_called_once()
        assert fake_detector.detect.call_args.args[0][0]["filename"].endswith("unsafe_image.png")
    finally:
        shutil.rmtree(upload_dir, ignore_errors=True)


def test_model_upload_uses_sanitized_filename(client, monkeypatch):
    model_dir = Path(".agent_work") / "pytest-temp" / f"task081-model-{uuid.uuid4().hex}"
    model_dir.mkdir(parents=True)
    monkeypatch.setattr(towerscout, "YOLO_MODEL_DIR", model_dir)
    monkeypatch.setattr(towerscout, "EN_MODEL_DIR", model_dir)
    monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", True)

    try:
        with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
            "towerscout.add_model"
        ) as mock_add_model:
            response = client.post(
                "/uploadmodel",
                data={"model": (io.BytesIO(b"fake-model-weights"), "../../custom model.pt")},
                content_type="multipart/form-data",
            )

        assert response.status_code == 200
        assert (model_dir / "custom_model.pt").is_file()
        mock_add_model.assert_called_once_with("custom_model.pt")
    finally:
        shutil.rmtree(model_dir, ignore_errors=True)


def test_detection_request_blocks_before_inference_when_pilot_tile_cap_exceeded(client, monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_PILOT_MAX_TILES", "100")

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
        "towerscout._parse_detection_request",
        return_value={
            "bounds": "37.7,-122.5,37.8,-122.4",
            "engine": "newest",
            "provider": "azure",
            "polygons": [],
        },
    ), patch("towerscout.get_engine") as mock_get_engine, patch(
        "towerscout._create_map_provider",
        return_value=Mock(),
    ), patch(
        "towerscout._build_tiles_for_request",
        return_value=(
            [{"id": index} for index in range(101)],
            1,
            101,
            10.0,
            640,
            640,
            {
                "candidate_tiles": 101,
                "viewport_tiles": 101,
                "retained_tiles": 101,
            },
        ),
    ):
        response = client.post("/getobjects", data={"bounds": "x"})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["blockedByTileLimit"] is True
    assert payload["tileCount"] == 101
    assert payload["tileLimit"] == 100
    assert "current pilot limit" in payload["error"]
    mock_get_engine.assert_not_called()

    progress = client.get("/api/detection/progress").get_json()
    assert progress["title"] == "Detection blocked"
    assert "current pilot limit" in progress["detail"]


def test_tile_estimate_reports_pilot_tile_cap_without_breaking_shape(client, monkeypatch):
    monkeypatch.setenv("TOWERSCOUT_PILOT_MAX_TILES", "100")

    with patch(
        "towerscout._parse_detection_request",
        return_value={
            "bounds": "37.7,-122.5,37.8,-122.4",
            "engine": "newest",
            "provider": "azure",
            "polygons": [],
        },
    ), patch("towerscout._create_map_provider", return_value=Mock()), patch(
        "towerscout._build_tiles_for_request",
        return_value=(
            [{"id": index} for index in range(101)],
            1,
            101,
            10.0,
            640,
            640,
            {
                "candidate_tiles": 101,
                "viewport_tiles": 101,
                "retained_tiles": 101,
            },
        ),
    ):
        response = client.post("/api/detection/estimate", data={"bounds": "x"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["tileCount"] == 101
    assert "estimatedSeconds" in payload
    assert payload["tileLimit"] == 100
    assert payload["blockedByTileLimit"] is True
    assert "current pilot limit" in payload["message"]


def test_estimate_frontend_surfaces_pilot_tile_cap_warning():
    repo_root = Path(__file__).resolve().parents[2]
    search_js = (repo_root / "webapp" / "js" / "src" / "ui" / "search.js").read_text(
        encoding="utf-8"
    )

    assert "result.blockedByTileLimit === true" in search_js
    assert "error.blockedByTileLimit = true" in search_js
    assert "TowerScoutErrorHandler.showUserNotification(msg, 'warning', 8000)" in search_js
    assert "TowerScoutErrorHandler.handleNetworkError(error, estimate ? 'Tile Estimation'" in search_js
    assert search_js.index("if (result.blockedByTileLimit === true)") < search_js.index(
        "return {\n      tileCount,"
    )
    assert search_js.index("if (error.blockedByTileLimit)") < search_js.index(
        "TowerScoutErrorHandler.handleNetworkError(error, estimate ? 'Tile Estimation'"
    )


def test_dataset_upload_validation_sanitizes_filename():
    from werkzeug.datastructures import FileStorage

    uploaded = FileStorage(
        stream=io.BytesIO(b"fake zip"),
        filename="../../dataset export.zip",
        content_type="application/zip",
    )

    validated = towerscout.TowerScoutValidator.validate_dataset_file(uploaded)

    assert validated.filename == "dataset_export.zip"
    assert ".." not in validated.filename
    assert "/" not in validated.filename
    assert "\\" not in validated.filename
