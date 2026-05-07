import json
import shutil
import uuid
from pathlib import Path

import ts_assets


def _make_scratch_root() -> Path:
    root = Path.cwd() / ".agent_work" / "pytest-temp" / f"task025-assets-{uuid.uuid4().hex}"
    root.mkdir(parents=True)
    return root


def _write_manifest(root: Path, assets: list[dict]) -> Path:
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps({
            "schema_version": 1,
            "manifest_version": "test-assets",
            "assets": assets,
        }),
        encoding="utf-8",
    )
    return manifest_path


def test_asset_status_passes_for_present_file_with_hash_verification(monkeypatch):
    root = _make_scratch_root()
    try:
        asset_path = root / "model_params" / "yolov5" / "newest.pt"
        asset_path.parent.mkdir(parents=True)
        asset_path.write_bytes(b"asset-bytes")
        manifest_path = _write_manifest(
            root,
            [{
                "id": "yolo",
                "path": "model_params/yolov5/newest.pt",
                "required": True,
                "bytes": len(b"asset-bytes"),
                "sha256": "C092DF87AD240EFA9F032F792B57F5D3812A833B47DE33172F59CF70EE2F01C4",
            }],
        )
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))
        monkeypatch.setattr(ts_assets, "get_base_dir", lambda: root)

        status = ts_assets.build_asset_status(verify_hashes=True)

        assert status["status"] == "ok"
        assert status["manifest_version"] == "test-assets"
        assert status["assets"][0]["status"] == "ok"
        assert status["assets"][0]["sha256"] == "C092DF87AD240EFA9F032F792B57F5D3812A833B47DE33172F59CF70EE2F01C4"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_asset_status_reports_missing_required_file_as_degraded(monkeypatch):
    root = _make_scratch_root()
    try:
        manifest_path = _write_manifest(
            root,
            [{
                "id": "missing-yolo",
                "path": "model_params/yolov5/newest.pt",
                "required": True,
            }],
        )
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))
        monkeypatch.setattr(ts_assets, "get_base_dir", lambda: root)

        status = ts_assets.build_asset_status()

        assert status["status"] == "degraded"
        assert status["missing"] == ["missing-yolo"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_asset_status_reports_size_mismatch_as_corrupt(monkeypatch):
    root = _make_scratch_root()
    try:
        asset_path = root / "data" / "asset.bin"
        asset_path.parent.mkdir(parents=True)
        asset_path.write_bytes(b"short")
        manifest_path = _write_manifest(
            root,
            [{
                "id": "bad-size",
                "path": "data/asset.bin",
                "required": True,
                "bytes": 999,
            }],
        )
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))
        monkeypatch.setattr(ts_assets, "get_base_dir", lambda: root)

        status = ts_assets.build_asset_status()

        assert status["status"] == "degraded"
        assert status["corrupt"] == ["bad-size"]
        assert status["assets"][0]["reason"] == "size_mismatch"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_asset_status_allows_missing_optional_asset(monkeypatch):
    root = _make_scratch_root()
    try:
        manifest_path = _write_manifest(
            root,
            [{
                "id": "optional-metadata",
                "path": "data/metadata.xml",
                "required": False,
            }],
        )
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))
        monkeypatch.setattr(ts_assets, "get_base_dir", lambda: root)

        status = ts_assets.build_asset_status()

        assert status["status"] == "ok"
        assert status["optional_missing"] == ["optional-metadata"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_asset_status_reports_invalid_manifest_as_error(monkeypatch):
    root = _make_scratch_root()
    try:
        manifest_path = root / "manifest.json"
        manifest_path.write_text("{not-json", encoding="utf-8")
        monkeypatch.setenv("TOWERSCOUT_ASSET_MANIFEST", str(manifest_path))

        status = ts_assets.build_asset_status()

        assert status["status"] == "error"
        assert "invalid" in status["error"].lower()
    finally:
        shutil.rmtree(root, ignore_errors=True)
