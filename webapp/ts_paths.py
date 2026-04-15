"""
Centralized filesystem paths for TowerScout.

This module anchors runtime and static paths to the webapp directory so
launch behavior stays consistent across `cd webapp` runs, repo-root pytest,
and CI imports.
"""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR.parent / "TowerScoutSite"
JS_DIR = BASE_DIR / "js"
IMG_DIR = BASE_DIR / "img"
CSS_DIR = BASE_DIR / "css"
TEMP_DIR = BASE_DIR / "temp"
CONFIG_DIR = BASE_DIR / "config"
CACHE_DIR = BASE_DIR / "cache"


def get_base_dir() -> Path:
    return BASE_DIR


def _resolve_app_path(raw_value: str | os.PathLike[str] | None, default_relative: str) -> Path:
    candidate = Path(raw_value) if raw_value else Path(default_relative)
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate
    return candidate


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_log_dir() -> Path:
    return ensure_dir(_resolve_app_path(os.getenv("TOWERSCOUT_LOG_DIR"), "logs"))


def get_log_file(filename: str) -> Path:
    return get_log_dir() / filename


def get_upload_dir() -> Path:
    return ensure_dir(_resolve_app_path(os.getenv("UPLOAD_DIR"), "uploads"))


def get_model_params_dir() -> Path:
    return ensure_dir(_resolve_app_path(os.getenv("MODEL_PARAMS_DIR"), "model_params"))


def get_yolov5_model_dir() -> Path:
    return ensure_dir(get_model_params_dir() / "yolov5")


def get_en_model_dir() -> Path:
    return ensure_dir(get_model_params_dir() / "EN")


def get_map_cache_dir() -> Path:
    return ensure_dir(CACHE_DIR / "maps")


def get_geocoding_cache_dir() -> Path:
    return ensure_dir(CACHE_DIR / "geocoding")


def get_flask_session_dir() -> Path:
    return ensure_dir(BASE_DIR / "flask_session")


def get_temp_dir() -> Path:
    return ensure_dir(TEMP_DIR)


def get_session_tmp_root() -> Path:
    return ensure_dir(get_temp_dir() / "session")
