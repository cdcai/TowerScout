from pathlib import Path
import shutil
import uuid
from unittest.mock import patch

import ts_runtime
from ts_zipcode import Zipcode_Provider


def test_zipcode_provider_uses_app_anchored_data_path(monkeypatch):
    base_dir = Path("C:/tower/webapp")
    expected_path = base_dir / "data" / "tl_2025_us_zcta520" / "tl_2025_us_zcta520.shp"

    monkeypatch.setattr("ts_zipcode.get_base_dir", lambda: base_dir)
    with patch("ts_zipcode.gpd.read_file") as mock_read_file:
        Zipcode_Provider()

    mock_read_file.assert_called_once_with(expected_path)


def test_readiness_payload_reports_setup_required_without_raw_provider_keys(monkeypatch):
    scratch_root = Path.cwd() / ".agent_work" / "pytest-temp" / f"task025-runtime-{uuid.uuid4().hex}"
    config_dir = scratch_root / "config"
    config_dir.mkdir(parents=True)
    env_path = config_dir / ".env"
    env_path.write_text("FLASK_SECRET_KEY=persisted-secret\n", encoding="utf-8")

    try:
        monkeypatch.setattr(ts_runtime.ts_config, "get_base_dir", lambda: scratch_root)
        monkeypatch.setattr(ts_runtime, "get_log_dir", lambda: scratch_root / "logs")
        monkeypatch.setattr(ts_runtime, "get_flask_session_dir", lambda: scratch_root / "flask_session")
        monkeypatch.setattr(ts_runtime, "get_session_tmp_root", lambda: scratch_root / "temp" / "session")
        monkeypatch.setattr(ts_runtime, "get_upload_dir", lambda: scratch_root / "uploads")
        monkeypatch.setattr(ts_runtime, "get_map_cache_dir", lambda: scratch_root / "cache" / "maps")
        monkeypatch.setattr(ts_runtime, "get_geocoding_cache_dir", lambda: scratch_root / "cache" / "geocoding")
        monkeypatch.setattr(ts_runtime, "get_base_dir", lambda: scratch_root)
        monkeypatch.setattr(
            ts_runtime.ts_assets,
            "build_asset_status",
            lambda: {
                "status": "ok",
                "manifest_version": "test-manifest",
                "assets": [],
                "missing": [],
                "corrupt": [],
                "optional_missing": [],
            },
        )
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("AZURE_MAPS_SUBSCRIPTION_KEY", raising=False)

        payload = ts_runtime.build_readiness_payload()

        assert payload["state"] == "setup_required"
        assert payload["components"]["config"]["needs_setup"] is True
        assert payload["components"]["config"]["secret_key_persisted"] is True
        assert "persisted-secret" not in str(payload)
    finally:
        shutil.rmtree(scratch_root, ignore_errors=True)


def test_readiness_payload_reports_manifest_errors_as_fatal(monkeypatch):
    scratch_root = Path.cwd() / ".agent_work" / "pytest-temp" / f"task025-runtime-{uuid.uuid4().hex}"
    config_dir = scratch_root / "config"
    config_dir.mkdir(parents=True)
    (config_dir / ".env").write_text(
        "FLASK_SECRET_KEY=persisted-secret\nGOOGLE_API_KEY=test-key\n",
        encoding="utf-8",
    )

    try:
        monkeypatch.setattr(ts_runtime.ts_config, "get_base_dir", lambda: scratch_root)
        monkeypatch.setattr(ts_runtime, "get_log_dir", lambda: scratch_root / "logs")
        monkeypatch.setattr(ts_runtime, "get_flask_session_dir", lambda: scratch_root / "flask_session")
        monkeypatch.setattr(ts_runtime, "get_session_tmp_root", lambda: scratch_root / "temp" / "session")
        monkeypatch.setattr(ts_runtime, "get_upload_dir", lambda: scratch_root / "uploads")
        monkeypatch.setattr(ts_runtime, "get_map_cache_dir", lambda: scratch_root / "cache" / "maps")
        monkeypatch.setattr(ts_runtime, "get_geocoding_cache_dir", lambda: scratch_root / "cache" / "geocoding")
        monkeypatch.setattr(ts_runtime, "get_base_dir", lambda: scratch_root)
        monkeypatch.setattr(
            ts_runtime.ts_assets,
            "build_asset_status",
            lambda: {
                "status": "error",
                "manifest_version": "",
                "assets": [],
                "missing": [],
                "corrupt": [],
                "optional_missing": [],
                "error": "Asset manifest JSON is invalid.",
            },
        )

        payload = ts_runtime.build_readiness_payload()

        assert payload["state"] == "fatal"
        assert "Repair the asset manifest" in payload["recovery"][0]
    finally:
        shutil.rmtree(scratch_root, ignore_errors=True)
