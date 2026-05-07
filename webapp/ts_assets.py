"""Runtime asset manifest and preflight checks for TowerScout."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

from ts_paths import get_base_dir


ASSET_MANIFEST_ENV_VAR = "TOWERSCOUT_ASSET_MANIFEST"
VERIFY_ASSET_HASHES_ENV_VAR = "TOWERSCOUT_VERIFY_ASSET_HASHES"
DEFAULT_MANIFEST_FILENAME = "asset_manifest.v1.json"
TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}


class AssetManifestError(Exception):
    """Raised when the runtime asset manifest cannot be parsed or validated."""


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUTHY_ENV_VALUES


def get_manifest_path() -> Path:
    configured_path = os.getenv(ASSET_MANIFEST_ENV_VAR, "").strip()
    if configured_path:
        candidate = Path(configured_path)
        if not candidate.is_absolute():
            candidate = get_base_dir() / candidate
        return candidate
    return get_base_dir() / DEFAULT_MANIFEST_FILENAME


def load_asset_manifest(path: Path | None = None) -> Dict[str, Any]:
    manifest_path = path or get_manifest_path()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssetManifestError(f"Asset manifest not found at {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise AssetManifestError(f"Asset manifest JSON is invalid: {exc}") from exc

    if not isinstance(manifest, dict):
        raise AssetManifestError("Asset manifest root must be an object.")
    if manifest.get("schema_version") != 1:
        raise AssetManifestError("Asset manifest schema_version must be 1.")
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise AssetManifestError("Asset manifest assets must be a list.")

    seen_ids = set()
    for index, asset in enumerate(assets):
        _validate_asset_entry(asset, index, seen_ids)

    return manifest


def _validate_asset_entry(asset: Any, index: int, seen_ids: set[str]) -> None:
    if not isinstance(asset, dict):
        raise AssetManifestError(f"Asset entry {index} must be an object.")

    asset_id = str(asset.get("id") or "").strip()
    if not asset_id:
        raise AssetManifestError(f"Asset entry {index} is missing id.")
    if asset_id in seen_ids:
        raise AssetManifestError(f"Asset id {asset_id} is duplicated.")
    seen_ids.add(asset_id)

    path_value = str(asset.get("path") or "").strip()
    if not path_value:
        raise AssetManifestError(f"Asset {asset_id} is missing path.")
    if Path(path_value).is_absolute():
        raise AssetManifestError(f"Asset {asset_id} path must be relative to webapp.")

    if "bytes" in asset:
        try:
            expected_bytes = int(asset["bytes"])
        except (TypeError, ValueError) as exc:
            raise AssetManifestError(f"Asset {asset_id} bytes must be an integer.") from exc
        if expected_bytes < 0:
            raise AssetManifestError(f"Asset {asset_id} bytes cannot be negative.")

    sha256 = str(asset.get("sha256") or "").strip()
    if sha256 and len(sha256) != 64:
        raise AssetManifestError(f"Asset {asset_id} sha256 must be a 64-character hex digest.")


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as asset_file:
        for chunk in iter(lambda: asset_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _check_asset(asset: Dict[str, Any], verify_hashes: bool) -> Dict[str, Any]:
    asset_path = get_base_dir() / asset["path"]
    expected_bytes = asset.get("bytes")
    expected_sha256 = str(asset.get("sha256") or "").upper()
    required = bool(asset.get("required", True))
    detail: Dict[str, Any] = {
        "id": asset["id"],
        "kind": asset.get("kind", "asset"),
        "label": asset.get("label", asset["id"]),
        "path": str(asset_path),
        "required": required,
        "status": "ok",
        "recovery": asset.get("recovery", ""),
    }

    if not asset_path.exists():
        detail["status"] = "missing"
        return detail
    if not asset_path.is_file():
        detail["status"] = "corrupt"
        detail["reason"] = "not_a_file"
        return detail

    actual_bytes = asset_path.stat().st_size
    detail["bytes"] = actual_bytes
    if expected_bytes is not None and actual_bytes != int(expected_bytes):
        detail["status"] = "corrupt"
        detail["reason"] = "size_mismatch"
        detail["expected_bytes"] = int(expected_bytes)
        return detail

    if verify_hashes and expected_sha256:
        actual_sha256 = _hash_file(asset_path)
        detail["sha256"] = actual_sha256
        if actual_sha256 != expected_sha256:
            detail["status"] = "corrupt"
            detail["reason"] = "sha256_mismatch"
            detail["expected_sha256"] = expected_sha256

    return detail


def _summarize_assets(asset_details: Iterable[Dict[str, Any]]) -> Dict[str, List[str]]:
    missing = []
    corrupt = []
    optional_missing = []
    for detail in asset_details:
        if detail["status"] == "missing":
            if detail["required"]:
                missing.append(detail["id"])
            else:
                optional_missing.append(detail["id"])
        elif detail["status"] == "corrupt":
            corrupt.append(detail["id"])
    return {
        "missing": missing,
        "corrupt": corrupt,
        "optional_missing": optional_missing,
    }


def build_asset_status(verify_hashes: bool | None = None) -> Dict[str, Any]:
    should_verify_hashes = (
        _env_flag(VERIFY_ASSET_HASHES_ENV_VAR, False)
        if verify_hashes is None
        else verify_hashes
    )
    manifest_path = get_manifest_path()
    try:
        manifest = load_asset_manifest(manifest_path)
    except AssetManifestError as exc:
        return {
            "status": "error",
            "manifest_path": str(manifest_path),
            "manifest_version": "",
            "schema_version": None,
            "verify_hashes": should_verify_hashes,
            "assets": [],
            "missing": [],
            "corrupt": [],
            "optional_missing": [],
            "error": str(exc),
        }

    asset_details = [
        _check_asset(asset, should_verify_hashes)
        for asset in manifest["assets"]
    ]
    summary = _summarize_assets(asset_details)
    status = "ok"
    if summary["missing"] or summary["corrupt"]:
        status = "degraded"

    return {
        "status": status,
        "manifest_path": str(manifest_path),
        "manifest_version": manifest.get("manifest_version", ""),
        "schema_version": manifest.get("schema_version"),
        "verify_hashes": should_verify_hashes,
        "assets": asset_details,
        "missing": summary["missing"],
        "corrupt": summary["corrupt"],
        "optional_missing": summary["optional_missing"],
    }
