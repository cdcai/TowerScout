"""Task-098 Slice D/G dependency and model-trust contracts."""

import hashlib
import io
import json
import re
import shutil
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import towerscout
import ts_assets
import ts_en
import ts_yolov5
from ts_assets import AssetManifestError
from towerscout import app

REPO_ROOT = Path(__file__).resolve().parents[2]
TORCH_VERSION = "2.6.0"
TORCHVISION_VERSION = "0.21.0"
MODEL_UPLOAD_KEY = "task098-model-upload-key-1234567890"
RUNTIME_CONTRACT = REPO_ROOT / "docs" / "support" / "oci-runtime-contract.md"
ASSET_CONTRACT = (
    REPO_ROOT / "docs" / "release" / "release-asset-bundle-contract.md"
)


def _scratch_root() -> Path:
    root = Path.cwd() / ".agent_work" / "pytest-temp" / f"task098-dg-{uuid.uuid4().hex}"
    root.mkdir(parents=True)
    return root


def _write_manifest(root: Path, model_path: Path, content: bytes) -> Path:
    relative_path = model_path.relative_to(root).as_posix()
    manifest_path = root / "asset_manifest.v1.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "manifest_version": "task098-test",
                "assets": [
                    {
                        "id": "trusted-test-model",
                        "kind": "model",
                        "path": relative_path,
                        "required": True,
                        "bytes": len(content),
                        "sha256": hashlib.sha256(content).hexdigest(),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest_path


def test_selected_torch_pair_is_pinned_consistently():
    requirements = (REPO_ROOT / "webapp" / "requirements.txt").read_text(
        encoding="utf-8"
    )
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    compose_build = (REPO_ROOT / "compose.build.yaml").read_text(encoding="utf-8")

    assert f"torch=={TORCH_VERSION}" in requirements
    assert f"torchvision=={TORCHVISION_VERSION}" in requirements
    assert f"ARG TOWERSCOUT_TORCH_VERSION={TORCH_VERSION}" in dockerfile
    assert f"ARG TOWERSCOUT_TORCHVISION_VERSION={TORCHVISION_VERSION}" in dockerfile
    assert f"TOWERSCOUT_TORCH_VERSION:-{TORCH_VERSION}" in compose_build
    assert f"TOWERSCOUT_TORCHVISION_VERSION:-{TORCHVISION_VERSION}" in compose_build


def test_cross_device_harness_is_commit_pinned_and_isolated():
    harness = (REPO_ROOT / "scripts" / "task098-qualify-ml.ps1").read_text(
        encoding="utf-8"
    )
    probe = (REPO_ROOT / "scripts" / "task098_ml_qualification.py").read_text(
        encoding="utf-8"
    )

    assert "status --porcelain --untracked-files=no" in harness
    assert "--pull" in harness
    assert "--no-cache" in harness
    assert "--rm" in harness
    assert "--read-only" in harness
    assert "--gpus" in harness
    assert "source_commit" in probe
    assert "output_matches_declared_tolerance" in probe
    assert "selected_devices_match_request" in probe


def test_release_model_hash_is_verified_by_default(monkeypatch):
    root = _scratch_root()
    try:
        content = b"trusted-model-content"
        model_path = root / "model_params" / "yolov5" / "newest.pt"
        model_path.parent.mkdir(parents=True)
        model_path.write_bytes(content)
        manifest_path = _write_manifest(root, model_path, content)
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))
        monkeypatch.setattr(ts_assets, "get_base_dir", lambda: root)

        result = ts_assets.verify_trusted_model(model_path)
        status = ts_assets.build_asset_status()

        assert result["source"] == "release_manifest"
        assert result["sha256"] == hashlib.sha256(content).hexdigest().upper()
        assert status["verify_hashes"] is False
        assert status["verify_model_hashes"] is True
        assert status["assets"][0]["sha256"] == result["sha256"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_release_model_hash_mismatch_is_rejected(monkeypatch):
    root = _scratch_root()
    try:
        expected = b"expected-model-content"
        model_path = root / "model_params" / "yolov5" / "newest.pt"
        model_path.parent.mkdir(parents=True)
        model_path.write_bytes(expected)
        manifest_path = _write_manifest(root, model_path, expected)
        model_path.write_bytes(b"tampered-model-content")
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))
        monkeypatch.setattr(ts_assets, "get_base_dir", lambda: root)

        with pytest.raises(AssetManifestError, match="verification"):
            ts_assets.verify_trusted_model(model_path)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_yolo_verifies_model_before_deserializing(monkeypatch):
    order = []
    fake_model = Mock()
    fake_model.cpu.return_value = None
    monkeypatch.setattr(ts_yolov5.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(ts_yolov5, "_validate_runtime_dependencies", lambda: None)
    monkeypatch.setattr(
        ts_yolov5,
        "verify_trusted_model",
        lambda _path: order.append("verify"),
    )
    monkeypatch.setattr(
        ts_yolov5,
        "_load_local_yolov5_model",
        lambda _path: order.append("load") or fake_model,
    )
    monkeypatch.setattr(
        ts_yolov5,
        "select_model_device",
        lambda *_args, **_kwargs: Mock(
            selected_device="cpu",
            requested_policy="cpu",
            fallback_reason=None,
        ),
    )

    ts_yolov5.YOLOv5_Detector("trusted.pt")

    assert order == ["verify", "load"]


def test_efficientnet_verifies_model_before_torch_load(monkeypatch):
    root = _scratch_root()
    try:
        model_path = root / "b5_unweighted_best.pt"
        model_path.write_bytes(b"trusted")
        order = []
        fake_model = Mock()
        fake_model.to.return_value = fake_model
        monkeypatch.setattr(ts_en, "get_en_model_dir", lambda: root)
        monkeypatch.setattr(
            ts_en,
            "verify_trusted_model",
            lambda _path: order.append("verify"),
        )
        monkeypatch.setattr(
            ts_en.EfficientNet,
            "from_name",
            lambda *_args, **_kwargs: fake_model,
        )
        monkeypatch.setattr(
            ts_en.torch,
            "load",
            lambda *_args, **_kwargs: order.append("load") or {},
        )
        monkeypatch.setattr(
            ts_en,
            "select_model_device",
            lambda *_args, **_kwargs: Mock(
                selected_device="cpu",
                requested_policy="cpu",
                fallback_reason=None,
            ),
        )

        ts_en.EN_Classifier()

        assert order[:2] == ["verify", "load"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "task098-secret"
    return app.test_client()


def test_model_upload_override_rejects_missing_key_from_container_peer(
    client, monkeypatch
):
    monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", True)
    monkeypatch.setenv("TOWERSCOUT_MODEL_UPLOAD_KEY", MODEL_UPLOAD_KEY)

    response = client.post(
        "/uploadmodel",
        data={"model": (io.BytesIO(b"model"), "custom.pt")},
        content_type="multipart/form-data",
        environ_base={
            "REMOTE_ADDR": "192.0.2.10",
            "HTTP_X_FORWARDED_FOR": "127.0.0.1",
        },
    )

    assert response.status_code == 403
    assert "authorization" in response.get_json()["error"].lower()


def test_model_upload_override_fails_closed_without_configured_key(client, monkeypatch):
    monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", True)
    monkeypatch.delenv("TOWERSCOUT_MODEL_UPLOAD_KEY", raising=False)

    response = client.post(
        "/uploadmodel",
        data={"model": (io.BytesIO(b"model"), "custom.pt")},
        content_type="multipart/form-data",
        headers={"X-TowerScout-Model-Upload-Key": MODEL_UPLOAD_KEY},
    )

    assert response.status_code == 503
    error = response.get_json()["error"].lower()
    assert "no valid model upload key" in error
    assert "configured" in error


def test_model_upload_override_accepts_key_from_container_peer_then_rejects_untrusted_file(
    client, monkeypatch
):
    root = _scratch_root()
    try:
        monkeypatch.setattr(towerscout, "MODEL_UPLOAD_ENABLED", True)
        monkeypatch.setattr(towerscout, "YOLO_MODEL_DIR", root)
        monkeypatch.setattr(towerscout, "EN_MODEL_DIR", root)
        monkeypatch.setenv("TOWERSCOUT_MODEL_UPLOAD_KEY", MODEL_UPLOAD_KEY)
        monkeypatch.delenv("TOWERSCOUT_TRUSTED_MODEL_SHA256", raising=False)

        with patch.object(towerscout.rate_limiter, "is_allowed", return_value=True):
            response = client.post(
                "/uploadmodel",
                data={"model": (io.BytesIO(b"untrusted"), "custom.pt")},
                content_type="multipart/form-data",
                headers={"X-TowerScout-Model-Upload-Key": MODEL_UPLOAD_KEY},
                environ_base={"REMOTE_ADDR": "172.17.0.1"},
            )

        assert response.status_code == 400
        assert "trust" in response.get_json()["error"].lower()
        assert not (root / "custom.pt").exists()
        assert list(root.glob(".custom.pt.*.pending")) == []
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_model_upload_container_and_frontend_contracts_require_the_dedicated_key():
    compose = (REPO_ROOT / "compose.yaml").read_text(encoding="utf-8")
    env_template = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    webapp_env_template = (REPO_ROOT / "webapp" / ".env.example").read_text(
        encoding="utf-8"
    )
    template = (
        REPO_ROOT / "webapp" / "templates" / "towerscout.html"
    ).read_text(encoding="utf-8")
    frontend = (
        REPO_ROOT / "webapp" / "js" / "src" / "towerscout.js"
    ).read_text(encoding="utf-8")

    assert "127.0.0.1:${TOWERSCOUT_PORT:-5000}:5000" in compose
    for variable in (
        "TOWERSCOUT_ENABLE_MODEL_UPLOAD",
        "TOWERSCOUT_MODEL_UPLOAD_KEY",
        "TOWERSCOUT_TRUSTED_MODEL_SHA256",
    ):
        assert variable in compose
        assert variable in env_template
        assert variable in webapp_env_template

    assert 'id="model_upload_key"' in template
    assert 'type="password"' in template
    assert 'autocomplete="off"' in template
    assert "X-TowerScout-Model-Upload-Key" in frontend
    assert "installed model \" + model" not in frontend


def test_current_runtime_and_release_contracts_have_no_cuda_121_reference():
    text_suffixes = {
        ".bat",
        ".cmd",
        ".example",
        ".html",
        ".js",
        ".json",
        ".md",
        ".ps1",
        ".py",
        ".sh",
        ".txt",
        ".yaml",
        ".yml",
    }
    scan_roots = (
        REPO_ROOT / "Dockerfile",
        REPO_ROOT / "compose.yaml",
        REPO_ROOT / "compose.build.yaml",
        REPO_ROOT / "compose.gpu.yaml",
        REPO_ROOT / "compose.gpu.podman.yaml",
        REPO_ROOT / ".env.example",
        REPO_ROOT / "webapp",
        REPO_ROOT / "scripts",
        REPO_ROOT / "docs",
        REPO_ROOT / "tests",
    )
    stale_pattern = re.compile(
        r"\b(?:cuda(?:\s+|[-_])?12\.1|cuda121|cu121)\b",
        flags=re.IGNORECASE,
    )
    stale_references = []

    for scan_root in scan_roots:
        paths = (scan_root,) if scan_root.is_file() else scan_root.rglob("*")
        for path in paths:
            if (
                not path.is_file()
                or path == Path(__file__).resolve()
                or path.suffix.lower() not in text_suffixes
                or "legacy" in {part.lower() for part in path.parts}
            ):
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            match = stale_pattern.search(content)
            if match:
                line_number = content.count("\n", 0, match.start()) + 1
                stale_references.append(
                    f"{path.relative_to(REPO_ROOT)}:{line_number}"
                )

    assert stale_references == []


def test_runtime_docs_distinguish_always_on_model_hashes_from_full_asset_hashes():
    runtime_contract = RUNTIME_CONTRACT.read_text(encoding="utf-8")
    asset_contract = ASSET_CONTRACT.read_text(encoding="utf-8")
    normalized_runtime_contract = " ".join(runtime_contract.split())
    normalized_asset_contract = " ".join(asset_contract.split())

    assert (
        "model assets are always SHA-256 verified"
        in normalized_runtime_contract
    )
    assert (
        "Model hash verification remains enabled."
        in normalized_asset_contract
    )
    assert (
        "model loading rejects it before deserialization"
        in normalized_asset_contract
    )
