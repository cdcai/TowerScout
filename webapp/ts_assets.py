"""Runtime asset manifest and preflight checks for TowerScout."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

from ts_paths import get_base_dir

ASSET_MANIFEST_ENV_VAR = "TOWERSCOUT_ASSET_MANIFEST"
VERIFY_ASSET_HASHES_ENV_VAR = "TOWERSCOUT_VERIFY_ASSET_HASHES"
TRUSTED_MODEL_SHA256_ENV_VAR = "TOWERSCOUT_TRUSTED_MODEL_SHA256"
DEFAULT_MANIFEST_FILENAME = "asset_manifest.v1.json"
TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}
SHA256_PATTERN = re.compile(r"^[0-9A-Fa-f]{64}$")
_HASH_CACHE: Dict[tuple[str, int, int, int], str] = {}


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
        raise AssetManifestError(
            f"Asset manifest not found at {manifest_path}"
        ) from exc
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
            raise AssetManifestError(
                f"Asset {asset_id} bytes must be an integer."
            ) from exc
        if expected_bytes < 0:
            raise AssetManifestError(f"Asset {asset_id} bytes cannot be negative.")

    sha256 = str(asset.get("sha256") or "").strip()
    if sha256 and not SHA256_PATTERN.fullmatch(sha256):
        raise AssetManifestError(
            f"Asset {asset_id} sha256 must be a 64-character hex digest."
        )


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as asset_file:
        for chunk in iter(lambda: asset_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _hash_file_cached(path: Path) -> str:
    stat = path.stat()
    cache_key = (
        str(path.resolve()),
        stat.st_size,
        stat.st_mtime_ns,
        stat.st_ctime_ns,
    )
    cached = _HASH_CACHE.get(cache_key)
    if cached is not None:
        return cached
    actual_sha256 = _hash_file(path)
    stale_keys = [key for key in _HASH_CACHE if key[0] == cache_key[0]]
    for stale_key in stale_keys:
        _HASH_CACHE.pop(stale_key, None)
    _HASH_CACHE[cache_key] = actual_sha256
    return actual_sha256


def _trusted_model_digests() -> set[str]:
    configured = os.getenv(TRUSTED_MODEL_SHA256_ENV_VAR, "")
    digests = {
        value.strip().upper() for value in configured.split(",") if value.strip()
    }
    invalid = sorted(
        digest for digest in digests if not SHA256_PATTERN.fullmatch(digest)
    )
    if invalid:
        raise AssetManifestError(
            f"{TRUSTED_MODEL_SHA256_ENV_VAR} contains an invalid SHA-256 digest."
        )
    return digests


def verify_trusted_model(path: str | Path) -> Dict[str, Any]:
    """Verify a model against the release manifest or explicit local-admin allowlist."""
    model_path = Path(path).resolve()
    if not model_path.is_file():
        raise AssetManifestError(f"Trusted model file not found: {model_path}")

    manifest = load_asset_manifest()
    manifest_match = None
    for asset in manifest["assets"]:
        if asset.get("kind") != "model":
            continue
        expected_path = (get_base_dir() / asset["path"]).resolve()
        if expected_path == model_path:
            manifest_match = asset
            break

    actual_bytes = model_path.stat().st_size
    if manifest_match is not None:
        expected_bytes = manifest_match.get("bytes")
        expected_sha256 = str(manifest_match.get("sha256") or "").upper()
        if expected_bytes is None or not expected_sha256:
            raise AssetManifestError(
                f"Trusted model entry {manifest_match['id']} must declare bytes and sha256."
            )
        if actual_bytes != int(expected_bytes):
            raise AssetManifestError(
                f"Trusted model {manifest_match['id']} failed size verification."
            )
        actual_sha256 = _hash_file_cached(model_path)
        if actual_sha256 != expected_sha256:
            raise AssetManifestError(
                f"Trusted model {manifest_match['id']} failed SHA-256 verification."
            )
        return {
            "source": "release_manifest",
            "id": manifest_match["id"],
            "path": str(model_path),
            "bytes": actual_bytes,
            "sha256": actual_sha256,
        }

    actual_sha256 = _hash_file_cached(model_path)
    if actual_sha256 not in _trusted_model_digests():
        raise AssetManifestError(
            "Model is not a checksummed release model or an explicitly trusted local-admin file."
        )
    return {
        "source": "local_admin_allowlist",
        "id": "",
        "path": str(model_path),
        "bytes": actual_bytes,
        "sha256": actual_sha256,
    }


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

    should_verify_hash = verify_hashes or asset.get("kind") == "model"
    if should_verify_hash and expected_sha256:
        actual_sha256 = _hash_file_cached(asset_path)
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
            "verify_model_hashes": True,
            "assets": [],
            "missing": [],
            "corrupt": [],
            "optional_missing": [],
            "error": str(exc),
        }

    asset_details = [
        _check_asset(asset, should_verify_hashes) for asset in manifest["assets"]
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
        "verify_model_hashes": True,
        "assets": asset_details,
        "missing": summary["missing"],
        "corrupt": summary["corrupt"],
        "optional_missing": summary["optional_missing"],
    }
