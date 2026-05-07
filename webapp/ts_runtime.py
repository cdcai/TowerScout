"""Runtime health and readiness helpers for TowerScout."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict

import ts_assets
import ts_config
from ts_paths import (
    get_base_dir,
    get_flask_session_dir,
    get_geocoding_cache_dir,
    get_log_dir,
    get_map_cache_dir,
    get_session_tmp_root,
    get_upload_dir,
)


def _write_check(path: Path) -> Dict[str, Any]:
    detail: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "writable": False,
    }
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe_path = path / ".towerscout-write-check"
        probe_path.write_text("ok", encoding="utf-8")
        probe_path.unlink(missing_ok=True)
        detail["exists"] = True
        detail["writable"] = True
    except Exception as exc:
        detail["error"] = exc.__class__.__name__
    return detail


def _required_paths() -> Dict[str, Path]:
    return {
        "config": ts_config.get_config_dir(),
        "logs": get_log_dir(),
        "flask_session": get_flask_session_dir(),
        "session_temp": get_session_tmp_root(),
        "uploads": get_upload_dir(),
        "map_cache": get_map_cache_dir(),
        "geocoding_cache": get_geocoding_cache_dir(),
        "assets_root": get_base_dir() / "model_params",
        "data_root": get_base_dir() / "data",
    }


def _asset_status() -> Dict[str, Any]:
    return ts_assets.build_asset_status()


def _config_status() -> Dict[str, Any]:
    status = ts_config.get_env_status()
    env_path = Path(status["env_path"])
    file_has_secret = False
    if env_path.exists():
        values = ts_config.dotenv_values(env_path)
        file_has_secret = bool(str(values.get(ts_config.FLASK_SECRET_KEY_ENV_VAR) or "").strip())

    return {
        "status": "setup_required" if status["needs_setup"] else "ok",
        "env_path": str(env_path),
        "needs_setup": status["needs_setup"],
        "secret_key_persisted": file_has_secret,
        "providers": {
            "google": {"configured": status["google"]["configured"]},
            "azure": {"configured": status["azure"]["configured"]},
            "default": status["default_map_provider"],
        },
    }


def build_health_payload() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "towerscout",
    }


def build_readiness_payload() -> Dict[str, Any]:
    path_details = {
        name: _write_check(path)
        for name, path in _required_paths().items()
    }
    path_errors = [
        name for name, detail in path_details.items()
        if not detail.get("writable")
        and name in {"config", "logs", "flask_session", "session_temp", "uploads"}
    ]

    config = _config_status()
    assets = _asset_status()

    if path_errors or not config["secret_key_persisted"]:
        state = "fatal"
    elif assets["status"] == "error":
        state = "fatal"
    elif config["needs_setup"]:
        state = "setup_required"
    elif assets["status"] != "ok":
        state = "degraded"
    else:
        state = "ready"

    recovery = []
    if path_errors:
        recovery.append("Check container volume permissions for writable runtime paths.")
    if not config["secret_key_persisted"]:
        recovery.append("Ensure webapp/config/.env is writable so FLASK_SECRET_KEY can persist.")
    if config["needs_setup"]:
        recovery.append("Open Setup Wizard and configure Google Maps or Azure Maps.")
    if assets["status"] != "ok":
        if assets["status"] == "error":
            recovery.append("Repair the asset manifest packaged with TowerScout.")
        else:
            recovery.append("Import or bootstrap the missing runtime assets, then restart TowerScout.")

    return {
        "state": state,
        "components": {
            "config": config,
            "assets": assets,
            "paths": path_details,
        },
        "version": {
            "app": os.getenv("TOWERSCOUT_VERSION", "development"),
            "image_digest": os.getenv("TOWERSCOUT_IMAGE_DIGEST", ""),
            "asset_manifest": assets.get("manifest_version", ""),
        },
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "cuda_requested": os.getenv("TOWERSCOUT_ENABLE_CUDA", "false").lower() in {"1", "true", "yes", "on"},
            "container_engine": os.getenv("TOWERSCOUT_CONTAINER_ENGINE", ""),
        },
        "recovery": recovery,
    }
