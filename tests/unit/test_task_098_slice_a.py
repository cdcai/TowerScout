"""Task-098 Slice A local-runtime and custom-image security contracts."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from PIL import Image
from werkzeug.datastructures import FileStorage

import towerscout
from towerscout import app
from ts_validation import TowerScoutValidator, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "compose.yaml"


def _image_bytes(image_format: str) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4), color="white").save(buffer, format=image_format)
    return buffer.getvalue()


def _upload(filename: str, content: bytes) -> FileStorage:
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
        content_type="application/octet-stream",
    )


def test_normal_compose_package_publishes_only_on_loopback():
    compose = yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))

    assert compose["services"]["towerscout"]["ports"] == [
        "127.0.0.1:${TOWERSCOUT_PORT:-5000}:5000"
    ]


@pytest.mark.parametrize(
    ("filename", "image_format"),
    [
        ("sample.jpg", "JPEG"),
        ("sample.jpeg", "JPEG"),
        ("sample.png", "PNG"),
        ("sample.tif", "TIFF"),
        ("sample.tiff", "TIFF"),
    ],
)
def test_image_validation_accepts_supported_content(filename, image_format):
    uploaded = _upload(filename, _image_bytes(image_format))

    validated = TowerScoutValidator.validate_image_file(uploaded)

    assert validated is uploaded
    assert validated.stream.tell() == 0


@pytest.mark.parametrize(
    ("format_name", "content"),
    [
        ("EPS", b"%!PS-Adobe-3.0 EPSF-3.0\n"),
        ("JPEG2000", b"\x00\x00\x00\x0cjP  \r\n\x87\n"),
        ("McIDAS", b"\x00\x00\x00\x00\x00\x00\x00\x04"),
    ],
)
def test_renamed_unsupported_image_is_rejected_before_pillow(format_name, content):
    uploaded = _upload(f"renamed-{format_name}.png", content)

    with patch("PIL.Image.open") as image_open:
        with pytest.raises(ValidationError, match="JPEG, PNG, or TIFF"):
            TowerScoutValidator.validate_image_file(uploaded)

    image_open.assert_not_called()
    assert uploaded.stream.tell() == 0


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("broken.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00"),
        ("broken.png", b"\x89PNG\r\n\x1a\nnot-a-valid-png"),
        ("broken.tiff", b"II*\x00not-a-valid-tiff"),
    ],
)
def test_malformed_supported_image_is_rejected(filename, content):
    uploaded = _upload(filename, content)

    with pytest.raises(ValidationError, match="Malformed"):
        TowerScoutValidator.validate_image_file(uploaded)

    assert uploaded.stream.tell() == 0


def test_image_extension_must_match_detected_content():
    uploaded = _upload("renamed.jpg", _image_bytes("PNG"))

    with pytest.raises(ValidationError, match="does not match"):
        TowerScoutValidator.validate_image_file(uploaded)

    assert uploaded.stream.tell() == 0


def test_image_validation_preserves_fifty_mib_cap(monkeypatch):
    assert TowerScoutValidator.MAX_FILE_SIZE == 50 * 1024 * 1024
    content = _image_bytes("PNG")
    monkeypatch.setattr(TowerScoutValidator, "MAX_FILE_SIZE", len(content) - 1)

    with pytest.raises(ValidationError, match="File too large"):
        TowerScoutValidator.validate_image_file(_upload("sample.png", content))


def test_custom_image_route_rejects_unsupported_content_before_inference(
    monkeypatch, tmp_path
):
    app.config["TESTING"] = True
    monkeypatch.setattr(towerscout, "UPLOAD_DIR", tmp_path)

    with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True), patch(
        "towerscout.get_engine"
    ) as get_engine, patch("PIL.Image.open") as image_open:
        response = app.test_client().post(
            "/getobjectscustom",
            data={
                "engine": "yolo",
                "image": (
                    io.BytesIO(b"%!PS-Adobe-3.0 EPSF-3.0\n"),
                    "renamed.jpg",
                ),
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert "JPEG, PNG, or TIFF" in response.get_json()["error"]
    get_engine.assert_not_called()
    image_open.assert_not_called()
    assert list(tmp_path.iterdir()) == []


def test_custom_image_route_preserves_upload_rate_limit():
    app.config["TESTING"] = True

    with patch.object(
        towerscout.rate_limiter, "is_allowed", return_value=False
    ) as is_allowed:
        response = app.test_client().post("/getobjectscustom")

    assert response.status_code == 429
    assert response.get_json()["error"] == "Rate limit exceeded for image uploads"
    is_allowed.assert_called_once()
    assert is_allowed.call_args.kwargs == {
        "max_requests": 10,
        "window_seconds": 60,
    }
