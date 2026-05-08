"""
TowerScout configuration management utilities.

Handles API key validation, .env persistence, runtime reloads, and
lightweight performance summaries for setup and settings workflows.
"""

from __future__ import annotations

import csv
import os
import secrets
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable

import requests
from dotenv import dotenv_values, load_dotenv

from ts_errors import ConfigurationError, NetworkError
from ts_validation import TowerScoutValidator, ValidationError as InputValidationError

CONFIG_ENV_FILENAME = ".env"
GOOGLE_ENV_VAR = "GOOGLE_API_KEY"
AZURE_ENV_VAR = "AZURE_MAPS_SUBSCRIPTION_KEY"
DEFAULT_PROVIDER_ENV_VAR = "DEFAULT_MAP_PROVIDER"
FLASK_SECRET_KEY_ENV_VAR = "FLASK_SECRET_KEY"
SUPPORTED_PROVIDERS = {"google", "azure"}
VALIDATION_TIMEOUT_SECONDS = 5
PERFORMANCE_LOG_HEADERS = (
    "timestamp",
    "session_id",
    "tile_count",
    "estimated_time_seconds",
    "actual_model_time_seconds",
    "total_workflow_time_seconds",
    "detection_count",
    "detections_selected",
    "avg_confidence",
    "memory_usage_mb",
    "gpu_memory_usage_mb",
    "peak_memory_mb",
    "peak_gpu_memory_mb",
    "map_api_calls",
    "geocoding_api_calls",
    "map_provider",
    "detection_engine",
    "crop_tiles",
    "phase_timings_json",
)
INSECURE_TLS_ENV_VAR = "TOWERSCOUT_ALLOW_INSECURE_TLS"
TLS_CA_BUNDLE_ENV_VARS = ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE")
TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}

PLACEHOLDER_PATTERNS = (
    "your_google_maps_api_key_here",
    "your_azure_maps_subscription_key_here",
    "your_google_api_key",
    "your_azure_maps_",
)


def get_base_dir() -> Path:
    return Path(__file__).resolve().parent


def get_config_dir() -> Path:
    return get_base_dir() / "config"


def get_config_env_path() -> Path:
    return get_config_dir() / CONFIG_ENV_FILENAME


def get_legacy_env_path() -> Path:
    return get_base_dir() / CONFIG_ENV_FILENAME


def get_active_env_path() -> Path:
    config_env = get_config_env_path()
    if config_env.exists():
        return config_env

    legacy_env = get_legacy_env_path()
    if legacy_env.exists():
        return legacy_env

    return config_env


def ensure_env_file() -> Path:
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    config_env = get_config_env_path()
    if config_env.exists():
        return config_env

    legacy_env = get_legacy_env_path()
    if legacy_env.exists():
        shutil.copy2(legacy_env, config_env)
    else:
        config_env.touch()

    return config_env


def backup_env_file(env_path: Path) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    backup_path = env_path.with_name(f"{env_path.name}.backup.{timestamp}")
    shutil.copy2(env_path, backup_path)
    cleanup_old_backups(env_path)
    return backup_path


def cleanup_old_backups(env_path: Path, keep: int = 5) -> None:
    backups = sorted(
        env_path.parent.glob(f"{env_path.name}.backup.*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )
    for backup in backups[keep:]:
        backup.unlink(missing_ok=True)


@contextmanager
def env_file_lock(lock_path: Path):
    """Best-effort cross-platform advisory lock for env writes."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+") as lock_file:
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0)
            lock_file.write("0")
            lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def is_placeholder(value: str | None) -> bool:
    if not value:
        return True
    lowered = value.strip().lower()
    if not lowered:
        return True
    return any(pattern in lowered for pattern in PLACEHOLDER_PATTERNS)


def validate_provider_name(provider: str) -> str:
    normalized = TowerScoutValidator.validate_provider(provider)
    if normalized not in SUPPORTED_PROVIDERS:
        raise InputValidationError(f"Unsupported provider '{normalized}'")
    return normalized


def sanitize_api_key(key: str, field_name: str) -> str:
    sanitized = TowerScoutValidator.sanitize_string(key, max_length=512)
    if not sanitized:
        raise InputValidationError(f"{field_name} is required")
    return sanitized


def _allow_insecure_tls() -> bool:
    return os.getenv(INSECURE_TLS_ENV_VAR, "").strip().lower() in TRUTHY_ENV_VALUES


def _configured_tls_bundle_error() -> NetworkError | None:
    for env_var in TLS_CA_BUNDLE_ENV_VARS:
        configured_path = os.getenv(env_var, "").strip()
        if not configured_path:
            continue

        if not Path(configured_path).is_file():
            return NetworkError(
                f"Configured TLS CA bundle path does not exist: {env_var}={configured_path}",
                user_message=(
                    "The configured TLS CA bundle was not found. "
                    "Run scripts/import-tls-ca.cmd for the selected Docker or Podman engine, "
                    "or update REQUESTS_CA_BUNDLE and SSL_CERT_FILE to a valid certificate bundle."
                ),
                details={
                    "env_var": env_var,
                    "configured_path": configured_path,
                    "support_action": "Run scripts/import-tls-ca.cmd for the selected container engine.",
                },
            )

    return None


def _validation_get(url: str, params: Dict[str, Any]) -> requests.Response:
    verify_tls = not _allow_insecure_tls()
    if verify_tls:
        bundle_error = _configured_tls_bundle_error()
        if bundle_error is not None:
            raise bundle_error

        response = requests.get(
            url,
            params=params,
            timeout=VALIDATION_TIMEOUT_SECONDS,
        )
        setattr(response, "_tls_verification_bypassed", False)
        return response

    response = requests.get(
        url,
        params=params,
        timeout=VALIDATION_TIMEOUT_SECONDS,
        verify=False,
    )
    setattr(response, "_tls_verification_bypassed", True)
    return response


def _apply_tls_warning(result: Dict[str, Any], response: requests.Response) -> Dict[str, Any]:
    if getattr(response, "_tls_verification_bypassed", False):
        result["warning"] = (
            "TLS certificate verification is disabled because "
            f"{INSECURE_TLS_ENV_VAR}=1 is enabled in the local environment."
        )
        result["tls_verification_bypassed"] = True
    return result


def _validate_google_key(key: str) -> Dict[str, Any]:
    static_response = _validation_get(
        "https://maps.googleapis.com/maps/api/staticmap",
        {
            "center": "0,0",
            "zoom": 1,
            "size": "1x1",
            "key": key,
        },
    )

    if static_response.status_code != 200:
        return _apply_tls_warning({
            "valid": False,
            "message": f"Google Maps validation failed with status {static_response.status_code}."
        }, static_response)

    geocode_response = _validation_get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        {
            "latlng": "40.714956,-74.015074",
            "location_type": "ROOFTOP|RANGE_INTERPOLATED",
            "result_type": "street_address|premise|subpremise",
            "key": key,
        },
    )

    if geocode_response.status_code != 200:
        return _apply_tls_warning({
            "valid": False,
            "message": (
                "Google Maps key passed Static Maps validation but Geocoding API "
                f"validation failed with status {geocode_response.status_code}."
            )
        }, geocode_response)

    try:
        geocode_data = geocode_response.json()
    except ValueError:
        return _apply_tls_warning({
            "valid": False,
            "message": "Google Geocoding validation returned invalid JSON."
        }, geocode_response)

    geocode_status = geocode_data.get("status")
    if geocode_status == "OK":
        return _apply_tls_warning(
            {
                "valid": True,
                "message": "Google Maps API key validated successfully for map and geocoding access."
            },
            geocode_response
        )

    geocode_error = geocode_data.get("error_message") or geocode_status or "Unknown geocoding error"
    return _apply_tls_warning(
        {
            "valid": False,
            "message": (
                "Google Maps key is not authorized for the Geocoding API. "
                f"Google returned: {geocode_error}"
            )
        },
        geocode_response
    )


def _validate_azure_key(key: str) -> Dict[str, Any]:
    attribution_response = _validation_get(
        "https://atlas.microsoft.com/map/attribution",
        {
            "api-version": "2024-04-01",
            "subscription-key": key,
        },
    )

    if attribution_response.status_code == 200:
        return _apply_tls_warning(
            {"valid": True, "message": "Azure Maps subscription key validated successfully."},
            attribution_response
        )

    search_response = _validation_get(
        "https://atlas.microsoft.com/search/address/json",
        {
            "api-version": "1.0",
            "subscription-key": key,
            "query": "Seattle",
            "limit": 1,
            "countrySet": "US",
        },
    )

    if search_response.status_code == 200:
        return _apply_tls_warning(
            {
                "valid": True,
                "message": "Azure Maps subscription key validated successfully."
            },
            search_response
        )

    return _apply_tls_warning({
        "valid": False,
        "message": (
            "Azure Maps validation failed with statuses "
            f"{attribution_response.status_code} (attribution) and {search_response.status_code} (search)."
        )
    }, search_response)


def validate_api_key(provider: str, key: str) -> Dict[str, Any]:
    validated_provider = validate_provider_name(provider)
    sanitized_key = sanitize_api_key(key, f"{validated_provider}_api_key")

    try:
        result = (
            _validate_google_key(sanitized_key)
            if validated_provider == "google"
            else _validate_azure_key(sanitized_key)
        )
    except requests.Timeout as exc:
        raise NetworkError(
            f"{validated_provider} validation request timed out",
            timeout=VALIDATION_TIMEOUT_SECONDS,
            cause=exc,
            user_message="Validation timed out. Please try again."
        ) from exc
    except requests.RequestException as exc:
        raise NetworkError(
            f"{validated_provider} validation request failed",
            cause=exc,
            user_message="Could not reach the provider validation service."
        ) from exc
    except OSError as exc:
        raise NetworkError(
            f"{validated_provider} validation request failed because TLS configuration is invalid",
            cause=exc,
            user_message=(
                "The configured TLS CA bundle could not be used. "
                "Run scripts/import-tls-ca.cmd for the selected Docker or Podman engine, "
                "or update REQUESTS_CA_BUNDLE and SSL_CERT_FILE to a valid certificate bundle."
            ),
        ) from exc

    result["provider"] = validated_provider
    result["tested_at"] = datetime.utcnow().isoformat() + "Z"
    return result


def _read_env_lines(env_path: Path) -> list[str]:
    if not env_path.exists():
        return []
    return env_path.read_text(encoding="utf-8").splitlines()


def _apply_updates_to_lines(lines: Iterable[str], updates: Dict[str, str]) -> list[str]:
    remaining = dict(updates)
    updated_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            updated_lines.append(line)
            continue

        key, _sep, _value = line.partition("=")
        normalized_key = key.strip()
        if normalized_key in remaining:
            updated_lines.append(f"{normalized_key}={remaining.pop(normalized_key)}")
        else:
            updated_lines.append(line)

    for key, value in remaining.items():
        updated_lines.append(f"{key}={value}")

    return updated_lines


def _validate_env_syntax(env_path: Path) -> None:
    try:
        dotenv_values(env_path)
    except Exception as exc:
        raise ConfigurationError(
            f"Updated env file could not be parsed: {exc}",
            user_message="Saved settings were invalid and have been rolled back.",
            cause=exc
        ) from exc


def reload_runtime_environment(env_path: Path | None = None) -> Path:
    active_env_path = env_path or get_active_env_path()
    if active_env_path.exists():
        load_dotenv(active_env_path, override=True)
    return active_env_path


def update_env_file(updates: Dict[str, str]) -> bool:
    if not updates:
        return True

    env_path = ensure_env_file()
    lock_path = env_path.with_suffix(env_path.suffix + ".lock")
    validated_updates = {
        key: TowerScoutValidator.sanitize_string(str(value), max_length=512)
        for key, value in updates.items()
        if value is not None
    }

    backup_path = None
    with env_file_lock(lock_path):
        if env_path.exists():
            backup_path = backup_env_file(env_path)

        original_lines = _read_env_lines(env_path)
        updated_lines = _apply_updates_to_lines(original_lines, validated_updates)

        fd, temp_name = tempfile.mkstemp(prefix="towerscout-config-", suffix=".env", dir=str(env_path.parent))
        os.close(fd)
        temp_path = Path(temp_name)

        try:
            temp_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
            _validate_env_syntax(temp_path)
            shutil.move(str(temp_path), env_path)
            reload_runtime_environment(env_path)
        except Exception:
            temp_path.unlink(missing_ok=True)
            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, env_path)
                reload_runtime_environment(env_path)
            raise

    return True


def ensure_persistent_flask_secret_key() -> str:
    """Return a stable Flask secret, creating it in config/.env when missing."""
    env_path = ensure_env_file()
    env_values = dotenv_values(env_path) if env_path.exists() else {}
    file_secret = str(env_values.get(FLASK_SECRET_KEY_ENV_VAR) or "").strip()
    if file_secret:
        os.environ[FLASK_SECRET_KEY_ENV_VAR] = file_secret
        return file_secret

    env_secret = str(os.getenv(FLASK_SECRET_KEY_ENV_VAR, "") or "").strip()
    secret_value = env_secret or secrets.token_urlsafe(48)
    update_env_file({FLASK_SECRET_KEY_ENV_VAR: secret_value})
    os.environ[FLASK_SECRET_KEY_ENV_VAR] = secret_value
    return secret_value


def get_env_status() -> Dict[str, Any]:
    active_env_path = get_active_env_path()
    env_values = dotenv_values(active_env_path) if active_env_path.exists() else {}

    google_key = env_values[GOOGLE_ENV_VAR] if GOOGLE_ENV_VAR in env_values else os.getenv(GOOGLE_ENV_VAR, "")
    azure_key = env_values[AZURE_ENV_VAR] if AZURE_ENV_VAR in env_values else os.getenv(AZURE_ENV_VAR, "")
    default_provider_raw = (
        env_values[DEFAULT_PROVIDER_ENV_VAR]
        if DEFAULT_PROVIDER_ENV_VAR in env_values
        else os.getenv(DEFAULT_PROVIDER_ENV_VAR, "azure")
    )
    default_provider = str(default_provider_raw or "azure").lower()

    google_configured = not is_placeholder(google_key)
    azure_configured = not is_placeholder(azure_key)
    needs_setup = not (google_configured or azure_configured)

    return {
        "google": {"configured": google_configured, "valid": google_configured},
        "azure": {"configured": azure_configured, "valid": azure_configured},
        "default_map_provider": default_provider if default_provider in SUPPORTED_PROVIDERS else "azure",
        "needs_setup": needs_setup,
        "env_path": str(active_env_path),
    }


def get_recent_performance_stats() -> Dict[str, Any]:
    log_candidates = [
        get_base_dir() / "logs" / "performance.log",
        Path(os.getcwd()) / "logs" / "performance.log",
    ]

    log_path = next((path for path in log_candidates if path.exists()), None)
    if log_path is None:
        return {
            "avg_tiles_per_second": 0.0,
            "session_count": 0,
            "last_detection_timestamp": None,
        }

    rows: list[Dict[str, Any]] = []
    with open(log_path, newline="", encoding="utf-8") as csv_file:
        raw_rows = list(csv.reader(csv_file))

    if raw_rows:
        first_row = [value.strip() for value in raw_rows[0]]
        has_header = tuple(first_row) == PERFORMANCE_LOG_HEADERS
        data_rows = raw_rows[1:] if has_header else raw_rows

        for raw_row in data_rows:
            if not raw_row:
                continue
            normalized_row = list(raw_row[:len(PERFORMANCE_LOG_HEADERS)])
            if len(normalized_row) < len(PERFORMANCE_LOG_HEADERS):
                normalized_row.extend([""] * (len(PERFORMANCE_LOG_HEADERS) - len(normalized_row)))
            rows.append(dict(zip(PERFORMANCE_LOG_HEADERS, normalized_row)))

    recent_rows = rows[-5:]
    if not recent_rows:
        return {
            "avg_tiles_per_second": 0.0,
            "session_count": 0,
            "last_detection_timestamp": None,
        }

    per_session_values = []
    for row in recent_rows:
        try:
            tile_count = float(row.get("tile_count", 0) or 0)
            total_time = float(row.get("total_workflow_time_seconds", 0) or 0)
            if tile_count > 0 and total_time > 0:
                per_session_values.append(tile_count / total_time)
        except (TypeError, ValueError):
            continue

    avg_tiles_per_second = sum(per_session_values) / len(per_session_values) if per_session_values else 0.0

    return {
        "avg_tiles_per_second": round(avg_tiles_per_second, 2),
        "session_count": len(recent_rows),
        "last_detection_timestamp": recent_rows[-1].get("timestamp"),
    }
