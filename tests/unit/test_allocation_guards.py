import io
from unittest.mock import patch

import pytest
from PIL import Image
from werkzeug.datastructures import FileStorage

import towerscout
from ts_maps import Map
from ts_validation import TowerScoutValidator, ValidationError


class _FixedTileMap(Map):
    def get_static_map_wh(
        self,
        lat=None,
        lng=None,
        zoom=19,
        sx=640,
        sy=640,
        crop_tiles=False,
    ):
        return 1.0, 1.0, 1.0, 1.0, 1.0


def _image_upload(width, height):
    stream = io.BytesIO()
    Image.new("RGB", (width, height), color="white").save(stream, format="PNG")
    stream.seek(0)
    return FileStorage(
        stream=stream,
        filename="fixture.png",
        content_type="image/png",
    )


def test_map_candidate_limit_accepts_cap_and_rejects_one_over():
    map_provider = _FixedTileMap()

    tiles, nx, ny, *_ = map_provider.make_tiles(
        "0,0,2,2",
        overlap_percent=0,
        max_candidate_tiles=4,
    )

    assert (nx, ny) == (2, 2)
    assert len(tiles) == 4

    with pytest.raises(ValidationError, match="candidate tile limit"):
        map_provider.make_tiles(
            "0,0,2,2",
            overlap_percent=0,
            max_candidate_tiles=3,
        )


def test_request_tile_builder_passes_candidate_budget(monkeypatch):
    class RejectingMap:
        def make_tiles(self, bounds, overlap_percent=5, crop_tiles=False, max_candidate_tiles=None):
            assert bounds == "0,0,2,2"
            assert crop_tiles is True
            assert max_candidate_tiles == 3
            raise ValidationError(
                "Selected area exceeds the candidate tile limit. Select a smaller area.",
                field="bounds",
            )

    monkeypatch.setattr(TowerScoutValidator, "MAX_CANDIDATE_TILES", 3)

    with pytest.raises(ValidationError, match="candidate tile limit"):
        towerscout._build_tiles_for_request(
            RejectingMap(),
            "0,0,2,2",
            [],
            True,
        )


def test_image_edge_limit_accepts_cap_and_rejects_one_over(monkeypatch):
    monkeypatch.setattr(TowerScoutValidator, "MAX_IMAGE_EDGE", 4)
    monkeypatch.setattr(TowerScoutValidator, "MAX_IMAGE_PIXELS", 100)

    assert TowerScoutValidator.validate_image_file(_image_upload(4, 4))
    with pytest.raises(ValidationError, match="Image dimensions"):
        TowerScoutValidator.validate_image_file(_image_upload(5, 4))


def test_image_pixel_limit_accepts_cap_and_rejects_one_over(monkeypatch):
    monkeypatch.setattr(TowerScoutValidator, "MAX_IMAGE_EDGE", 10)
    monkeypatch.setattr(TowerScoutValidator, "MAX_IMAGE_PIXELS", 16)

    assert TowerScoutValidator.validate_image_file(_image_upload(4, 4))
    with pytest.raises(ValidationError, match="image pixel limit"):
        TowerScoutValidator.validate_image_file(_image_upload(5, 4))


def test_detection_route_rejects_candidate_grid_before_model(monkeypatch):
    towerscout.app.config["TESTING"] = True
    monkeypatch.setattr(TowerScoutValidator, "MAX_CANDIDATE_TILES", 3)

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
        "towerscout._parse_detection_request",
        return_value={
            "bounds": "0,0,2,2",
            "engine": "newest",
            "provider": "azure",
            "polygons": [],
        },
    ), patch(
        "towerscout._create_map_provider",
        return_value=_FixedTileMap(),
    ), patch("towerscout.get_engine") as get_engine:
        response = towerscout.app.test_client().post(
            "/getobjects",
            data={"bounds": "x"},
        )

    assert response.status_code == 400
    assert "candidate tile limit" in response.get_json()["error"]
    get_engine.assert_not_called()


def test_custom_image_route_rejects_dimensions_before_model(monkeypatch, tmp_path):
    towerscout.app.config["TESTING"] = True
    monkeypatch.setattr(towerscout, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(TowerScoutValidator, "MAX_IMAGE_EDGE", 4)
    monkeypatch.setattr(TowerScoutValidator, "MAX_IMAGE_PIXELS", 100)
    upload = _image_upload(5, 4)

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
        "towerscout.get_engine"
    ) as get_engine:
        response = towerscout.app.test_client().post(
            "/getobjectscustom",
            data={
                "engine": "yolo",
                "image": (upload.stream, upload.filename),
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert "Image dimensions" in response.get_json()["error"]
    get_engine.assert_not_called()