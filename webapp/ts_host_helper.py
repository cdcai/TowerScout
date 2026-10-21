"""Short-lived browser authorization for the loopback TowerScout host helper.

The durable helper token remains in the package-local host state directory.
When the review-only bridge is explicitly configured by the Windows launcher,
the Flask app receives a separate per-launch HMAC key. The app uses that key
only to issue narrow, expiring browser credentials for helper discovery,
operation start, and operation status polling.
"""

from __future__ import annotations

import base64
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from typing import Any, Mapping


AUTHORIZATION_VERSION = "v1"
AUTHORIZATION_AUDIENCE = "towerscout-host-helper"
HELPER_PROBE_SCOPE = "helper_probe"
PROVIDER_TLS_REPAIR_SCOPE = "provider_tls_repair"
OPERATION_STATUS_SCOPE = "operation_status"
PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED = False

PROBE_AUTHORIZATION_TTL_SECONDS = 60
START_AUTHORIZATION_TTL_SECONDS = 120
STATUS_AUTHORIZATION_TTL_SECONDS = 900
MAX_AUTHORIZATION_TTL_SECONDS = STATUS_AUTHORIZATION_TTL_SECONDS
AUTHORIZATION_CLOCK_SKEW_SECONDS = 300

TLS_REPAIR_CATEGORIES = frozenset(
    {
        "tls_ca_untrusted",
        "tls_bundle_missing",
        "tls_bundle_unusable",
    }
)
PROVIDERS = frozenset({"google", "azure"})
SESSION_ID_RE = re.compile(r"^[a-f0-9]{32}$")
SESSION_KEY_RE = re.compile(r"^[A-Za-z0-9_-]{43}$")
OPERATION_ID_RE = re.compile(r"^[a-f0-9]{32}$")


@dataclass(frozen=True)
class HostHelperBridgeConfig:
    helper_port: int
    helper_session_id: str
    session_authorization_key: str

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.helper_port}"


def _enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _decode_base64url(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _encode_base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def load_host_helper_bridge_config(
    environment: Mapping[str, str] | None = None,
) -> HostHelperBridgeConfig | None:
    env = os.environ if environment is None else environment
    if not _enabled(env.get("TOWERSCOUT_HOST_HELPER_ENABLED")):
        return None

    try:
        helper_port = int((env.get("TOWERSCOUT_HOST_HELPER_PORT") or "").strip())
    except (TypeError, ValueError):
        return None
    if helper_port < 1 or helper_port > 65535:
        return None

    helper_session_id = (
        env.get("TOWERSCOUT_HOST_HELPER_SESSION_ID") or ""
    ).strip().lower()
    session_authorization_key = (
        env.get("TOWERSCOUT_HOST_HELPER_SESSION_KEY") or ""
    ).strip()
    if not SESSION_ID_RE.fullmatch(helper_session_id):
        return None
    if not SESSION_KEY_RE.fullmatch(session_authorization_key):
        return None
    try:
        decoded_key = _decode_base64url(session_authorization_key)
    except (ValueError, TypeError):
        return None
    if len(decoded_key) != 32:
        return None

    return HostHelperBridgeConfig(
        helper_port=helper_port,
        helper_session_id=helper_session_id,
        session_authorization_key=session_authorization_key,
    )


def _normalize_provider(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized not in PROVIDERS:
        raise ValueError("Provider is not allowlisted for host-helper authorization.")
    return normalized


def _normalize_operation_id(operation_id: str | None) -> str:
    normalized = (operation_id or "").strip().lower()
    if normalized and not OPERATION_ID_RE.fullmatch(normalized):
        raise ValueError("Operation id is invalid.")
    return normalized


def _expected_runtime(environment: Mapping[str, str]) -> dict[str, Any]:
    try:
        app_port = int(
            (environment.get("TOWERSCOUT_HOST_PORT") or "5000").strip()
        )
    except (TypeError, ValueError):
        app_port = 0
    return {
        "engine": (
            environment.get("TOWERSCOUT_CONTAINER_ENGINE", "") or ""
        ).strip().lower(),
        "gpu": (
            environment.get("TOWERSCOUT_GPU_MODE", "") or ""
        ).strip().lower(),
        "app_port": app_port,
    }


def issue_browser_authorization(
    config: HostHelperBridgeConfig,
    *,
    scope: str,
    provider: str,
    operation_id: str | None = None,
    ttl_seconds: int,
    now: int | None = None,
) -> dict[str, Any]:
    if scope not in {
        HELPER_PROBE_SCOPE,
        PROVIDER_TLS_REPAIR_SCOPE,
        OPERATION_STATUS_SCOPE,
    }:
        raise ValueError("Host-helper authorization scope is not allowlisted.")
    if ttl_seconds < 1 or ttl_seconds > MAX_AUTHORIZATION_TTL_SECONDS:
        raise ValueError("Host-helper authorization TTL is outside the allowed range.")

    normalized_provider = _normalize_provider(provider)
    normalized_operation_id = _normalize_operation_id(operation_id)
    if scope == OPERATION_STATUS_SCOPE and not normalized_operation_id:
        raise ValueError("Operation status authorization requires an operation id.")
    if scope != OPERATION_STATUS_SCOPE and normalized_operation_id:
        raise ValueError("Only operation status authorization may include an operation id.")

    issued_at = int(time.time()) if now is None else int(now)
    expires_at = issued_at + ttl_seconds
    payload = {
        "aud": AUTHORIZATION_AUDIENCE,
        "exp": expires_at,
        "iat": issued_at,
        "nonce": secrets.token_urlsafe(12),
        "operation_id": normalized_operation_id,
        "provider": normalized_provider,
        "scope": scope,
        "session_id": config.helper_session_id,
        "v": 1,
    }
    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    payload_segment = _encode_base64url(payload_bytes)
    signing_input = f"{AUTHORIZATION_VERSION}.{payload_segment}".encode("ascii")
    key_bytes = _decode_base64url(config.session_authorization_key)
    signature = hmac.new(key_bytes, signing_input, hashlib.sha256).digest()
    token = (
        f"{AUTHORIZATION_VERSION}.{payload_segment}."
        f"{_encode_base64url(signature)}"
    )
    expires_at_text = datetime.fromtimestamp(
        expires_at,
        tz=timezone.utc,
    ).isoformat().replace("+00:00", "Z")
    return {
        "operation_type": (
            "provider_tls_repair"
            if scope in {PROVIDER_TLS_REPAIR_SCOPE, OPERATION_STATUS_SCOPE}
            else "helper_probe"
        ),
        "scope": scope,
        "expires_at": expires_at_text,
        "authorization": token,
    }


def validate_browser_authorization(
    config: HostHelperBridgeConfig,
    token: str,
    *,
    expected_scope: str,
    expected_provider: str,
    expected_operation_id: str | None = None,
    now: int | None = None,
) -> dict[str, Any]:
    """Validate a browser authorization for unit and cross-runtime contracts."""

    try:
        version, payload_segment, signature_segment = token.split(".")
        if version != AUTHORIZATION_VERSION:
            raise ValueError("authorization_version")
        signing_input = f"{version}.{payload_segment}".encode("ascii")
        key_bytes = _decode_base64url(config.session_authorization_key)
        expected_signature = hmac.new(
            key_bytes,
            signing_input,
            hashlib.sha256,
        ).digest()
        supplied_signature = _decode_base64url(signature_segment)
        if not hmac.compare_digest(expected_signature, supplied_signature):
            raise ValueError("authorization_signature")
        payload = json.loads(_decode_base64url(payload_segment).decode("ascii"))
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("authorization_invalid") from exc

    current_time = int(time.time()) if now is None else int(now)
    issued_at = int(payload.get("iat", 0))
    expires_at = int(payload.get("exp", 0))
    expected_operation = _normalize_operation_id(expected_operation_id)
    if payload.get("aud") != AUTHORIZATION_AUDIENCE:
        raise ValueError("authorization_audience")
    if payload.get("v") != 1 or payload.get("scope") != expected_scope:
        raise ValueError("authorization_scope")
    if payload.get("session_id") != config.helper_session_id:
        raise ValueError("authorization_session")
    if payload.get("provider") != _normalize_provider(expected_provider):
        raise ValueError("authorization_provider")
    if (payload.get("operation_id") or "") != expected_operation:
        raise ValueError("authorization_operation")
    if issued_at > current_time + AUTHORIZATION_CLOCK_SKEW_SECONDS:
        raise ValueError("authorization_not_yet_valid")
    if expires_at <= current_time - AUTHORIZATION_CLOCK_SKEW_SECONDS:
        raise ValueError("authorization_expired")
    if expires_at - issued_at < 1 or expires_at - issued_at > MAX_AUTHORIZATION_TTL_SECONDS:
        raise ValueError("authorization_ttl")
    return payload


def build_provider_tls_repair_bridge(
    provider: str,
    category: str | None,
    *,
    environment: Mapping[str, str] | None = None,
    now: int | None = None,
    include_start_authorization: bool = False,
) -> dict[str, Any] | None:
    if category not in TLS_REPAIR_CATEGORIES or provider not in PROVIDERS:
        return None
    config = load_host_helper_bridge_config(environment)
    if config is None:
        return None

    probe = issue_browser_authorization(
        config,
        scope=HELPER_PROBE_SCOPE,
        provider=provider,
        ttl_seconds=PROBE_AUTHORIZATION_TTL_SECONDS,
        now=now,
    )
    env = os.environ if environment is None else environment
    bridge = {
        "base_url": config.base_url,
        "probe": {
            "path": "/health",
            **probe,
        },
        "expected_runtime": _expected_runtime(env),
        "provider_tls_repair_capability": (
            PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED
        ),
    }
    if PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED and include_start_authorization:
        operation = issue_browser_authorization(
            config,
            scope=PROVIDER_TLS_REPAIR_SCOPE,
            provider=provider,
            ttl_seconds=START_AUTHORIZATION_TTL_SECONDS,
            now=now,
        )
        bridge["operation_authorization"] = {
            "operation_type": "provider_tls_repair",
            "expires_at": operation["expires_at"],
            "operation_token": operation["authorization"],
        }
    return bridge


def build_operation_status_bridge(
    provider: str,
    operation_id: str,
    *,
    environment: Mapping[str, str] | None = None,
    now: int | None = None,
) -> dict[str, Any] | None:
    if not PROVIDER_TLS_REPAIR_CAPABILITY_ENABLED:
        return None
    config = load_host_helper_bridge_config(environment)
    if config is None:
        return None
    normalized_operation_id = _normalize_operation_id(operation_id)
    authorization = issue_browser_authorization(
        config,
        scope=OPERATION_STATUS_SCOPE,
        provider=provider,
        operation_id=normalized_operation_id,
        ttl_seconds=STATUS_AUTHORIZATION_TTL_SECONDS,
        now=now,
    )
    return {
        "base_url": config.base_url,
        "operation_id": normalized_operation_id,
        "status_authorization": {
            "operation_type": "provider_tls_repair",
            "scope": OPERATION_STATUS_SCOPE,
            "expires_at": authorization["expires_at"],
            "authorization": authorization["authorization"],
        },
    }


def enrich_provider_tls_repair_payload(
    payload: Mapping[str, Any],
    *,
    environment: Mapping[str, str] | None = None,
    now: int | None = None,
    include_start_authorization: bool = False,
) -> dict[str, Any]:
    """Attach a review-only helper bridge after logging has already occurred."""

    enriched = deepcopy(dict(payload))
    details = dict(enriched.get("details") or {})
    provider = str(
        enriched.get("provider") or details.get("provider") or ""
    ).strip().lower()
    category = enriched.get("category") or details.get("category")
    if provider not in PROVIDERS or category not in TLS_REPAIR_CATEGORIES:
        return enriched

    bridge = build_provider_tls_repair_bridge(
        provider,
        category,
        environment=environment,
        now=now,
        include_start_authorization=include_start_authorization,
    )

    # Availability is established only by the browser's authenticated probe.
    details["helper_available"] = False
    enriched["helper_available"] = False
    if bridge is not None:
        details["helper_bridge"] = bridge
        enriched["helper_bridge"] = bridge
    enriched["details"] = details
    return enriched
